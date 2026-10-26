"""Real PostgreSQL control-plane integration, never engineering execution proof."""

from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from orba.orchestration_models import OrchestrationEvent, OrchestrationTask
from orba.orchestration_service import checksum
from orba.pm_service import phase
from orba.scheduler_models import (
    ClaimRequest,
    HandoffRecord,
    TaskDispatch,
    TaskLease,
    WorkerCredential,
)
from scripts.worker_admin import alter_worker
from scripts.worker_client import validate_handoff
from tests.scheduler_support import acquire, act, operation, ready, worker


def test_real_claim_manifest_acknowledgment_and_read(client):
    project, run, ident, token, headers = ready(client)
    response = acquire(client, run, headers)
    assert response.status_code == 201, response.text
    handoff = response.json()
    assert handoff["lease"]["state"] == "claimed"
    manifest = handoff["manifest"]
    assert manifest["snapshot_hash"] == run["snapshot_hash"]
    assert manifest["architecture"]["id"] == run["architecture_id"]
    assert manifest["product_plan"]["id"] == run["source_plan_id"]
    assert checksum({k: v for k, v in manifest.items() if k != "checksum"}) == manifest["checksum"]
    registered = client.get("/api/v1/workers/me", headers=headers).json()
    validate_handoff(handoff, registered)
    result = act(client, handoff, headers)
    assert result.status_code == 200, result.text
    acknowledged = result.json()
    assert acknowledged["lease"]["acknowledged_at"]
    assert acknowledged["lease"]["state"] == "acknowledged"
    duplicate = act(client, handoff, headers)
    assert duplicate.json() == acknowledged
    status = client.get(f"/api/v1/projects/{project}/orchestration-runs/{run['id']}/scheduler")
    assert status.status_code == 200, status.text
    assert status.json()["dispatches"][0]["leases"][0]["worker_id"] == ident
    assert (
        client.get(f"/api/v1/projects/{project}/orchestration-runs/{run['id']}").status_code == 200
    )
    with Session(client.app.state.engine) as db:
        assert db.scalar(select(func.count()).select_from(TaskLease)) == 1
        assert db.scalar(select(func.count()).select_from(HandoffRecord)) == 1
        assert db.scalar(select(func.count()).select_from(ClaimRequest)) == 1
        assert {row.execution_status for row in db.scalars(select(OrchestrationTask))} == {
            "awaiting_executor"
        }
        saved = db.get(WorkerCredential, UUID(token[9:].split(".")[0]))
        assert saved.token_hash != token and len(saved.token_hash) == 64
        events = db.scalars(select(OrchestrationEvent).order_by(OrchestrationEvent.sequence)).all()
        assert [row.sequence for row in events] == list(range(1, len(events) + 1))
        assert events[-1].event_type == "handoff_acknowledged"


@pytest.mark.parametrize(
    "authorization", [None, "Bearer bad", "Bearer orba_wkr_bad.token", "Basic not-a-worker"]
)
def test_worker_auth_is_separate_from_browser_session(client, authorization):
    headers = {"Authorization": authorization} if authorization else {}
    result = client.post(
        "/api/v1/workers/claim", headers=headers, json={"request_id": str(uuid4())}
    )
    assert result.status_code == 401
    with Session(client.app.state.engine) as db:
        assert db.scalar(select(func.count()).select_from(TaskLease)) == 0


def test_same_key_replay_conflict_capacity_and_recovery(client):
    _, run, _, _, headers = ready(client)
    ident = uuid4()
    first = acquire(client, run, headers, ident)
    assert first.status_code == 201, first.text
    repeated = acquire(client, run, headers, ident)
    assert repeated.status_code == 200 and repeated.json() == first.json()
    recovered = client.get(f"/api/v1/workers/claims/{ident}", headers=headers)
    assert recovered.json() == first.json()
    conflict = client.post(
        "/api/v1/workers/claim", headers=headers, json={"request_id": str(ident), "run_id": None}
    )
    assert conflict.status_code == 409
    assert acquire(client, run, headers).status_code == 409


@pytest.mark.parametrize("action", ["disable", "revoke", "rotate"])
def test_revocation_and_rotation_invalidate_ownership(client, action):
    _, run, ident, _, headers = ready(client)
    response = acquire(client, run, headers)
    assert response.status_code == 201, response.text
    handoff = response.json()
    assert act(client, handoff, headers).status_code == 200
    with phase(client.app.state.engine) as db:
        alter_worker(db, UUID(ident), action, client.app.state.settings.scheduler_policy())
    assert act(client, handoff, headers).status_code == 401
    assert acquire(client, run, headers).status_code == 401
    with Session(client.app.state.engine) as db:
        assert db.get(TaskLease, UUID(handoff["lease"]["id"])).state == "revoked"
        assert db.scalar(select(TaskDispatch)).state == "needs_reconciliation"


@pytest.mark.parametrize("change", [{"fence_epoch": 2}, {"manifest_checksum": "0" * 64}])
def test_forged_ownership_is_rejected_with_persisted_event(client, change):
    _, run, _, _, headers = ready(client)
    handoff = acquire(client, run, headers).json()
    assert act(client, handoff, headers, **change).status_code == 409
    with Session(client.app.state.engine) as db:
        assert db.get(TaskLease, UUID(handoff["lease"]["id"])).state == "claimed"
        assert (
            db.scalar(
                select(OrchestrationEvent).order_by(OrchestrationEvent.sequence.desc())
            ).event_type
            == "worker_lease_rejected"
        )


@pytest.mark.parametrize(
    "change",
    [
        {"fence_epoch": True},
        {"fence_epoch": "1"},
        {"contract_version": True},
        {"manifest_checksum": None},
        {"state": "verified_complete"},
    ],
)
def test_strict_worker_inputs_reject_coercion_and_completion(client, change):
    _, run, _, _, headers = ready(client)
    handoff = acquire(client, run, headers).json()
    assert act(client, handoff, headers, **change).status_code == 422


def test_other_worker_cannot_ack_or_read_claim(client):
    _, run, _, _, headers = ready(client)
    claim_id = uuid4()
    handoff = acquire(client, run, headers, claim_id).json()
    _, _, other = worker(client, run)
    assert act(client, handoff, other).status_code == 404
    assert client.get(f"/api/v1/workers/claims/{claim_id}", headers=other).status_code == 404
    assert client.post(
        f"/api/v1/workers/leases/{handoff['lease']['id']}/complete",
        headers=headers,
        json=operation(handoff),
    ).status_code in {404, 405}

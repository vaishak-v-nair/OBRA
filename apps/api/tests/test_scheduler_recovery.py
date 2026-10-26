"""Real PostgreSQL concurrent ownership, expiration and atomic recovery tests."""

import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from orba.orchestration_models import OrchestrationEvent, OrchestrationRun, OrchestrationTask
from orba.pm_service import db_now, phase
from orba.scheduler_models import (
    HandoffRecord,
    LeaseHeartbeat,
    TaskDispatch,
    TaskLease,
    WorkerIdentity,
)
from orba.scheduler_service import tick
from tests.orchestration_support import body, initialize, path
from tests.scheduler_support import acquire, act, ready, worker

FAST = {
    "scheduler_ack_seconds": 2,
    "scheduler_lease_seconds": 5,
    "scheduler_max_lease_seconds": 10,
    "scheduler_heartbeat_seconds": 1,
}


def until(client, deadline, offset=0.04):
    """Wait for a protocol deadline measured against DB time, not an arbitrary delay."""
    from datetime import datetime

    with Session(client.app.state.engine) as db:
        remaining = (datetime.fromisoformat(deadline) - db_now(db)).total_seconds() + offset
    if remaining > 0:
        threading.Event().wait(remaining)


def race(*calls):
    barrier = threading.Barrier(len(calls))

    def run(call):
        barrier.wait(timeout=5)
        return call()

    with ThreadPoolExecutor(max_workers=len(calls)) as pool:
        futures = [pool.submit(run, call) for call in calls]
        return [future.result(timeout=15) for future in futures]


def test_preack_expiration_fences_old_worker_and_new_owner(client):
    _, run, _, _, a = ready(client, config=FAST)
    _, _, b = worker(client, run)
    old = acquire(client, run, a).json()
    until(client, old["lease"]["acknowledge_by"])
    tick(client.app.state.engine, client.app.state.settings.scheduler_policy(), uuid4())
    response = acquire(client, run, b)
    assert response.status_code == 201, response.text
    newer = response.json()
    assert newer["lease"]["fence_epoch"] > old["lease"]["fence_epoch"]
    assert act(client, old, a).status_code == 409
    assert act(client, old, a, "heartbeat", request_id=str(uuid4())).status_code == 409
    assert act(client, newer, b).status_code == 200
    with Session(client.app.state.engine) as db:
        assert db.get(TaskLease, UUID(old["lease"]["id"])).state == "expired"
        assert db.get(TaskLease, UUID(newer["lease"]["id"])).state == "acknowledged"
        assert (
            db.scalar(
                select(func.count())
                .select_from(TaskLease)
                .where(TaskLease.state.in_(("claimed", "acknowledged")))
            )
            == 1
        )


def test_postack_crash_requires_reconciliation_never_redispatch(client):
    project, run, _, _, headers = ready(client, config=FAST)
    handoff = acquire(client, run, headers).json()
    assert act(client, handoff, headers).status_code == 200
    until(client, handoff["lease"]["expires_at"])
    tick(client.app.state.engine, client.app.state.settings.scheduler_policy(), uuid4())
    assert act(client, handoff, headers, "heartbeat", request_id=str(uuid4())).status_code == 409
    assert acquire(client, run, headers).status_code == 204
    status = client.get(path(project, f"/{run['id']}/scheduler")).json()
    assert status["dispatches"][0]["state"] == "needs_reconciliation"
    with Session(client.app.state.engine) as db:
        assert db.get(TaskLease, UUID(handoff["lease"]["id"])).state == "expired"
        assert db.scalar(select(func.count()).select_from(TaskLease)) == 1
        assert {task.execution_status for task in db.scalars(select(OrchestrationTask))} == {
            "awaiting_executor"
        }


def test_real_heartbeat_receipt_duplicate_and_hard_bound(client):
    _, run, _, _, headers = ready(client, config=FAST)
    handoff = acquire(client, run, headers).json()
    ack = act(client, handoff, headers).json()
    assert act(client, handoff, headers, "heartbeat", request_id=str(uuid4())).status_code == 429
    from datetime import datetime

    until(
        client,
        (
            datetime.fromisoformat(ack["lease"]["acknowledged_at"]) + timedelta(seconds=1)
        ).isoformat(),
    )
    request_id = str(uuid4())
    response = act(client, handoff, headers, "heartbeat", request_id=request_id)
    assert response.status_code == 200, response.text
    renewed = response.json()
    assert renewed["lease"]["last_heartbeat_at"]
    assert renewed["lease"]["expires_at"] <= renewed["lease"]["max_expires_at"]
    duplicate = act(client, handoff, headers, "heartbeat", request_id=request_id)
    assert duplicate.status_code == 200 and duplicate.json() == renewed
    assert renewed["manifest"] == handoff["manifest"]  # Initial wire deadlines never mutate.
    with Session(client.app.state.engine) as db:
        assert db.scalar(select(func.count()).select_from(LeaseHeartbeat)) == 1
        assert (
            db.scalar(
                select(func.count())
                .select_from(OrchestrationEvent)
                .where(OrchestrationEvent.event_type == "lease_renewed")
            )
            == 1
        )


def test_concurrent_workers_one_task_have_one_valid_owner(client):
    _, run, _, _, a = ready(client)
    _, _, b = worker(client, run)
    results = race(lambda: acquire(client, run, a), lambda: acquire(client, run, b))
    assert sorted(row.status_code for row in results) == [201, 204]
    with Session(client.app.state.engine) as db:
        assert db.scalar(select(func.count()).select_from(TaskLease)) == 1
        assert db.scalar(select(func.count()).select_from(HandoffRecord)) == 1
        assert db.scalar(select(TaskDispatch)).attempts == 1


def test_concurrent_same_key_network_replay_has_one_lease(client):
    _, run, _, _, headers = ready(client)
    key = uuid4()
    results = race(
        lambda: acquire(client, run, headers, key), lambda: acquire(client, run, headers, key)
    )
    assert sorted(row.status_code for row in results) == [200, 201]
    assert results[0].json()["lease"]["id"] == results[1].json()["lease"]["id"]


def test_heartbeat_vs_expiration_cannot_revive_stale_ownership(client):
    _, run, _, _, headers = ready(client, config=FAST)
    handoff = acquire(client, run, headers).json()
    assert act(client, handoff, headers).status_code == 200
    until(client, handoff["lease"]["expires_at"], offset=-0.02)
    policy = client.app.state.settings.scheduler_policy()
    results = race(
        lambda: act(client, handoff, headers, "heartbeat", request_id=str(uuid4())),
        lambda: tick(client.app.state.engine, policy, uuid4()),
    )
    assert results[0].status_code in {200, 409}
    with Session(client.app.state.engine) as db:
        lease = db.get(TaskLease, UUID(handoff["lease"]["id"]))
        dispatch = db.get(TaskDispatch, lease.dispatch_id)
        assert (lease.state, dispatch.state) in {
            ("acknowledged", "leased"),
            ("expired", "needs_reconciliation"),
        }
        assert db.scalar(select(func.count()).select_from(TaskLease)) == 1


def test_cancel_vs_claim_invalidates_all_ownership(client):
    project, run, _, _, headers = ready(client)
    current = client.get(path(project, f"/{run['id']}")).json()
    results = race(
        lambda: acquire(client, run, headers),
        lambda: client.post(
            path(project, f"/{run['id']}/cancel"), json={"expected_revision": current["revision"]}
        ),
    )
    assert results[0].status_code in {201, 204}
    assert results[1].status_code in {200, 409}
    if results[1].status_code == 409:
        current = client.get(path(project, f"/{run['id']}")).json()
        assert (
            client.post(
                path(project, f"/{run['id']}/cancel"),
                json={"expected_revision": current["revision"]},
            ).status_code
            == 200
        )
    with Session(client.app.state.engine) as db:
        assert db.get(OrchestrationRun, UUID(run["id"])).status == "cancelled"
        assert (
            db.scalar(
                select(func.count())
                .select_from(TaskLease)
                .where(TaskLease.state.in_(("claimed", "acknowledged")))
            )
            == 0
        )
        assert {d.state for d in db.scalars(select(TaskDispatch))} == {"cancelled"}


def test_failed_claim_transaction_has_no_orphaned_lease(client, monkeypatch):
    _, run, _, _, headers = ready(client)
    from orba import scheduler_service as service

    def broken(*args, **kwargs):
        raise HTTPException(
            503, "Controlled isolated persistence failure before manifest publication."
        )

    monkeypatch.setattr(service, "manifest_for", broken)
    assert acquire(client, run, headers).status_code == 503
    with Session(client.app.state.engine) as db:
        assert db.scalar(select(func.count()).select_from(TaskLease)) == 0
        assert db.scalar(select(TaskDispatch)).state == "queued"
        assert db.scalar(select(TaskDispatch)).fence_epoch == 0
        assert (
            db.scalar(
                select(func.count())
                .select_from(OrchestrationEvent)
                .where(OrchestrationEvent.event_type == "lease_claimed")
            )
            == 0
        )


@pytest.mark.parametrize(
    "acknowledged,expected", [(False, "withdrawn"), (True, "needs_reconciliation")]
)
def test_explicit_release_preserves_acknowledgment_uncertainty(client, acknowledged, expected):
    _, run, _, _, headers = ready(client)
    handoff = acquire(client, run, headers).json()
    if acknowledged:
        assert act(client, handoff, headers).status_code == 200
    assert act(client, handoff, headers, "release").status_code == 200
    with Session(client.app.state.engine) as db:
        assert db.scalar(select(TaskDispatch)).state == expected
    assert act(client, handoff, headers).status_code == 409


def test_scheduler_restart_and_deterministic_dispatch_preserve_sources(client):
    _, _source, _, run = initialize(client)
    _, _, headers = worker(client, run)
    policy = client.app.state.settings.scheduler_policy()
    first = tick(client.app.state.engine, policy, uuid4())
    second = tick(client.app.state.engine, policy, uuid4())
    assert first["queued"] == 1 and second["queued"] == 0
    with Session(client.app.state.engine) as db:
        dispatch = db.scalar(select(TaskDispatch))
        assert db.get(OrchestrationTask, dispatch.task_id).key == "storage"
        assert db.scalar(select(func.count()).select_from(TaskDispatch)) == 1
        assert db.get(OrchestrationRun, UUID(run["id"])).snapshot_hash == run["snapshot_hash"]
    assert acquire(client, run, headers).status_code == 201


def test_mismatched_scheduler_policy_fails_closed(client):
    _, _run, _, _, _ = ready(client)
    policy = client.app.state.settings.scheduler_policy().model_copy(update={"global_capacity": 9})
    with pytest.raises(HTTPException, match="503"):
        tick(client.app.state.engine, policy, uuid4())


def test_stale_worker_withdraws_reservation_without_forging_liveness(client):
    _, _run, ident, _, _ = ready(client)
    with phase(client.app.state.engine) as db:
        row = db.get(WorkerIdentity, UUID(ident))
        row.last_authenticated_at = db_now(db) - timedelta(seconds=61)
    tick(client.app.state.engine, client.app.state.settings.scheduler_policy(), uuid4())
    with Session(client.app.state.engine) as db:
        assert db.scalar(select(TaskDispatch)).state == "withdrawn"
        assert db.get(WorkerIdentity, UUID(ident)).last_authenticated_at < db_now(db) - timedelta(
            seconds=60
        )


@pytest.mark.parametrize(
    "table,column", [("handoff_records", "checksum"), ("orchestration_events", "event_type")]
)
def test_audit_records_are_append_only_in_postgresql(client, table, column):
    _, run, _, _, headers = ready(client)
    assert acquire(client, run, headers).status_code == 201
    with pytest.raises(IntegrityError), client.app.state.engine.begin() as db:
        db.execute(text(f"UPDATE {table} SET {column}={column}"))


def test_no_unregistered_capability_or_cross_workspace_claim(client):
    _, _, _, run = initialize(client)
    _, _, headers = worker(client, run, capabilities=["documentation"])
    tick(client.app.state.engine, client.app.state.settings.scheduler_policy(), uuid4())
    assert acquire(client, run, headers).status_code == 204
    other = client.post("/api/v1/workspaces", json={"name": "Other worker scope"}).json()
    _, _, foreign = worker(client, run, workspace=other["id"], project=False)
    assert acquire(client, run, foreign).status_code == 404
    with Session(client.app.state.engine) as db:
        assert db.scalar(select(func.count()).select_from(TaskLease)) == 0


def test_preack_redispatch_is_bounded_and_terminal_replay_never_claims_new_task(client):
    _, run, _, _, headers = ready(client, config=FAST | {"scheduler_max_attempts": 1})
    request_id = uuid4()
    handoff = acquire(client, run, headers, request_id).json()
    until(client, handoff["lease"]["acknowledge_by"])
    tick(client.app.state.engine, client.app.state.settings.scheduler_policy(), uuid4())
    assert acquire(client, run, headers).status_code == 204
    assert acquire(client, run, headers, request_id).status_code == 409
    with Session(client.app.state.engine) as db:
        dispatch = db.scalar(select(TaskDispatch))
        assert dispatch.state == "exhausted" and dispatch.attempts == 1
        assert db.scalar(select(func.count()).select_from(TaskLease)) == 1


def test_postgresql_unique_constraint_independently_rejects_competing_active_lease(client):
    _, run, _, _, headers = ready(client)
    handoff = acquire(client, run, headers).json()
    with Session(client.app.state.engine) as db:
        original = db.get(TaskLease, UUID(handoff["lease"]["id"]))
        values = {
            column.name: getattr(original, column.name) for column in TaskLease.__table__.columns
        }
    values["id"] = uuid4()
    with pytest.raises(IntegrityError), Session(client.app.state.engine) as db, db.begin():
        db.add(TaskLease(**values))
        db.flush()


def test_capacity_reservations_are_global_and_per_run(client):
    client.app.state.settings = client.app.state.settings.model_copy(
        update={"scheduler_global_capacity": 1, "scheduler_run_capacity": 1}
    )
    project, source, _, run = initialize(client)
    _, _, _headers = worker(client, run)
    second = client.post(path(project), json=body(source))
    assert second.status_code == 201
    policy = client.app.state.settings.scheduler_policy()
    assert tick(client.app.state.engine, policy, uuid4())["queued"] == 1
    assert tick(client.app.state.engine, policy, uuid4())["queued"] == 0
    with Session(client.app.state.engine) as db:
        assert db.scalar(select(func.count()).select_from(TaskDispatch)) == 1
        assert db.scalar(select(TaskDispatch)).run_id == UUID(run["id"])


def test_revocation_racing_claim_rechecks_authority_after_lock_wait(client):
    from scripts.worker_admin import alter_worker

    _, run, ident, _, headers = ready(client)

    def revoke():
        with phase(client.app.state.engine) as db:
            alter_worker(db, UUID(ident), "revoke", client.app.state.settings.scheduler_policy())
        return "revoked"

    responses = race(lambda: acquire(client, run, headers), revoke)
    assert responses[0].status_code in {201, 401}
    assert responses[1] == "revoked"
    with Session(client.app.state.engine) as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(TaskLease)
                .where(TaskLease.state.in_(("claimed", "acknowledged")))
            )
            == 0
        )
    assert acquire(client, run, headers).status_code == 401

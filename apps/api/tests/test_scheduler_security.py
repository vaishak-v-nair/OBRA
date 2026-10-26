"""Actual user/worker boundary, source approval and strict policy validation."""

from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from orba.models import WorkspaceMember
from orba.pm_service import db_now, phase
from orba.scheduler_models import (
    SchedulerState,
    TaskDispatch,
    TaskLease,
    WorkerCredential,
    WorkerIdentity,
)
from orba.scheduler_schemas import SchedulerPolicy
from orba.scheduler_service import coordination, credential_pair, tick
from tests.conftest import register
from tests.orchestration_support import path
from tests.pm_support import identity, seed
from tests.scheduler_support import acquire, act, ready


@pytest.mark.parametrize(
    "value",
    [
        {"acknowledge_seconds": 30},
        {"lease_seconds": 121},
        {"heartbeat_seconds": 30},
        {"max_lease_seconds": 10},
        {"global_capacity": True},
        {"batch_size": 0},
        {"max_attempts": 99},
        {"run_capacity": 9},
    ],
)
def test_invalid_scheduler_policy_fails_before_dispatch(value):
    with pytest.raises(ValidationError):
        SchedulerPolicy(**value)


def replace_approved_plan(client, project):
    ident = seed(client, project)  # Human-authored source fixture, not AI evidence.
    route = f"/api/v1/projects/{project}/pm-plans/{ident}"
    saved = client.get(route)
    assert saved.status_code == 200
    plan = saved.json()
    approval = client.post(
        route + "/approve", json={"version": plan["version"], "expected_revision": plan["revision"]}
    )
    assert approval.status_code == 200, approval.text


def test_source_supersession_prevents_claim_and_withdraws_queue(client):
    project, run, _, _, headers = ready(client)
    replace_approved_plan(client, project)
    assert acquire(client, run, headers).status_code == 409
    tick(client.app.state.engine, client.app.state.settings.scheduler_policy(), uuid4())
    with Session(client.app.state.engine) as db:
        assert db.scalar(select(TaskDispatch)).state == "withdrawn"
        assert db.scalar(select(func.count()).select_from(TaskLease)) == 0


def test_source_supersession_prevents_unacknowledged_handoff_acceptance(client):
    project, run, _, _, headers = ready(client)
    response = acquire(client, run, headers)
    assert response.status_code == 201
    handoff = response.json()
    replace_approved_plan(client, project)
    assert act(client, handoff, headers).status_code == 409
    with Session(client.app.state.engine) as db:
        assert db.get(TaskLease, UUID(handoff["lease"]["id"])).acknowledged_at is None


def test_viewer_can_inspect_but_browser_cannot_administer_workers(client):
    project, run, _, _, _ = ready(client)
    actor, _ = identity(client)
    with phase(client.app.state.engine) as db:
        member = db.scalar(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == UUID(run["workspace_id"]),
                WorkspaceMember.user_id == actor,
            )
        )
        member.role = "viewer"
    response = client.get(path(project, f"/{run['id']}/scheduler"))
    assert response.status_code == 200
    assert "token_hash" not in response.text and "credential_id" not in response.text
    assert client.get("/api/v1/workers/me").status_code == 401
    assert client.post(
        "/api/v1/workers/register", json={"capabilities": ["backend"]}
    ).status_code in {404, 405}


def test_unrelated_user_cannot_inspect_scheduling_state(client):
    project, run, _, _, _ = ready(client)
    register(client, "unrelated-scheduler@example.com")
    response = client.get(path(project, f"/{run['id']}/scheduler"))
    assert response.status_code == 404
    assert run["snapshot_hash"] not in response.text


def test_expired_worker_credential_rejects_real_authentication(client):
    _, run, _, token, _ = ready(client)
    # Authored historical credential fixture in isolated PG. Real production
    # authentication must reject its actual past deadline; no clock is mocked.
    with phase(client.app.state.engine) as db:
        coordination(db)
        credential = db.get(WorkerCredential, UUID(token[9:].split(".")[0]))
        worker = db.get(WorkerIdentity, credential.worker_id)
        worker.credential_version += 1
        historical, expired_token = credential_pair(worker, db_now(db) - timedelta(seconds=120), 60)
        db.add(historical)
    assert acquire(client, run, {"Authorization": "Bearer " + expired_token}).status_code == 401


@pytest.mark.parametrize("damage", ["missing", "boolean", "numeric_string"])
def test_malformed_persisted_policy_cannot_pass_equal_value_comparison(client, damage):
    _, run, _, _, headers = ready(
        client, config={"scheduler_global_capacity": 1, "scheduler_run_capacity": 1}
    )
    with phase(client.app.state.engine) as db:
        row = db.get(SchedulerState, 1)
        broken = dict(row.policy)
        if damage == "missing":
            broken.pop("global_capacity")
        else:
            broken["global_capacity"] = True if damage == "boolean" else "1"
        # JSON equality considers True == 1, so ORM change detection would omit
        # that malformed update. Persist it explicitly; verify actual SQL data
        # independently before exercising the production strict-policy guard.
        db.execute(update(SchedulerState).where(SchedulerState.id == 1).values(policy=broken))
    with Session(client.app.state.engine) as db:
        stored = db.get(SchedulerState, 1).policy
        if damage == "missing":
            assert "global_capacity" not in stored
        else:
            expected_type = bool if damage == "boolean" else str
            assert type(stored["global_capacity"]) is expected_type
    assert acquire(client, run, headers).status_code == 503
    with Session(client.app.state.engine) as db:
        assert db.scalar(select(func.count()).select_from(TaskLease)) == 0

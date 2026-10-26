"""Real PostgreSQL credential deadlines and lock waits; no mocked authentication."""

import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path
from time import monotonic
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from orba.models import Workspace
from orba.orchestration_models import OrchestrationEvent, OrchestrationRun, OrchestrationTask
from orba.scheduler_models import (
    ClaimRequest,
    HandoffRecord,
    TaskDispatch,
    TaskLease,
    WorkerCredential,
    WorkerIdentity,
)
from orba.scheduler_service import coordination, credential_pair, parse_credential
from orba.transactions import db_now, phase
from scripts.worker_admin import alter_worker
from tests.report_safety import WorkerHeaders
from tests.scheduler_support import acquire, act, ready, worker


def snapshot(engine):
    """Independent SQL records, never response-supplied claimed counts."""
    with Session(engine) as db:
        dispatch = db.scalar(select(TaskDispatch))
        return {
            "dispatch": {
                "id": str(dispatch.id),
                "state": dispatch.state,
                "attempts": dispatch.attempts,
                "fence_epoch": dispatch.fence_epoch,
            },
            "leases": db.scalar(select(func.count()).select_from(TaskLease)),
            "handoffs": db.scalar(select(func.count()).select_from(HandoffRecord)),
            "claim_receipts": db.scalar(select(func.count()).select_from(ClaimRequest)),
            "events": [
                [row.sequence, row.event_type, row.run_revision]
                for row in db.scalars(
                    select(OrchestrationEvent).order_by(OrchestrationEvent.sequence)
                )
            ],
            "execution_statuses": list(db.scalars(select(OrchestrationTask.execution_status))),
            "runs": [
                [str(row.id), row.status, row.revision, row.last_event_sequence]
                for row in db.scalars(select(OrchestrationRun).order_by(OrchestrationRun.id))
            ],
        }


def short_credential(client, worker_id, remaining=0.7):
    """Historical issuance fixture, real hash/DB deadline, normal 60s lifetime.

    No runtime policy/clock is altered: create a new credential version issued
    almost60s ago, so its actual immutable remaining lifetime is short.
    """
    with phase(client.app.state.engine) as db:
        coordination(db)
        worker = db.get(WorkerIdentity, UUID(worker_id))
        worker.credential_version += 1
        moment = db_now(db)
        credential, token = credential_pair(worker, moment - timedelta(seconds=60 - remaining), 60)
        db.add(credential)
        expires = credential.expires_at
    return WorkerHeaders(Authorization="Bearer " + token), expires


def observed_block(observer, holder_pid, future):
    limit = monotonic() + 1
    while monotonic() < limit:
        row = (
            observer.execute(
                text(
                    "SELECT pid,wait_event_type,wait_event,clock_timestamp() AS observed_at "
                    "FROM pg_stat_activity WHERE datname=current_database() "
                    "AND :holder = ANY(pg_blocking_pids(pid)) AND wait_event_type='Lock'"
                ),
                {"holder": holder_pid},
            )
            .mappings()
            .first()
        )
        if row:
            return dict(row)
        assert not future.done(), "Request ended before reaching the intended PostgreSQL lock."
        threading.Event().wait(0.002)
    raise AssertionError("No real PostgreSQL request lock contention was observed.")


def wait_db(observer, deadline, future=None):
    limit = monotonic() + 5
    while (moment := observer.scalar(text("SELECT clock_timestamp()"))) < deadline:
        assert monotonic() < limit, "Bounded PostgreSQL deadline observation failed."
        if future is not None:
            assert not future.done(), "Request ended while the independent lock remained held."
        threading.Event().wait(0.002)
    return moment


def save_evidence(label, value):
    if directory := os.environ.get("ORBA_CREDENTIAL_RACE_EVIDENCE_DIR"):
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        with (path / f"{label}-race.json").open("x", encoding="utf-8") as output:
            json.dump(value, output, indent=2)


def blocked_until_expiry(client, run, worker_id, *, lock="workspace"):
    engine = client.app.state.engine
    before = snapshot(engine)
    issued = short_credential(client, worker_id) if lock in {"worker", "credential"} else None
    with engine.connect() as holder, holder.begin():
        holder_pid = holder.scalar(text("SELECT pg_backend_pid()"))
        targets = {
            "workspace": (Workspace, UUID(run["workspace_id"])),
            "task_fk": (OrchestrationTask, UUID(run["tasks"][0]["id"])),
            "worker": (WorkerIdentity, UUID(worker_id)),
        }
        if lock == "credential":
            targets[lock] = (WorkerCredential, parse_credential(issued[0]["Authorization"][7:]))
        model, ident = targets[lock]
        holder.execute(select(model.id).where(model.id == ident).with_for_update())
        headers, expires = issued or short_credential(client, worker_id)
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as observer:
            initial = observer.scalar(text("SELECT clock_timestamp()"))
            assert initial < expires, "Credential must be valid before starting the real claim."
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(acquire, client, run, headers)
                try:
                    observed = observed_block(observer, holder_pid, future)
                    assert observed["observed_at"] < expires
                    released_at = wait_db(observer, expires, future)
                finally:
                    holder.commit()
                response = future.result(timeout=10)
    after = snapshot(engine)
    save_evidence(
        lock,
        {
            "scenario": lock,
            "holder_pid": holder_pid,
            "claim_pid": observed["pid"],
            "wait_event_type": observed["wait_event_type"],
            "wait_event": observed["wait_event"],
            "credential_valid_at_start": initial.isoformat(),
            "lock_observed_at": observed["observed_at"].isoformat(),
            "credential_expires_at": expires.isoformat(),
            "lock_released_at": released_at.isoformat(),
            "response_status": response.status_code,
            "before_sql": before,
            "after_sql": after,
            "model_generation_requests": 0,
            "execution_performed": False,
        },
    )
    return response, before, after


def test_credential_expiring_during_workspace_lock_is_rejected(client):
    _, run, worker_id, _, _ = ready(client)
    response, before, after = blocked_until_expiry(client, run, worker_id)
    assert response.status_code == 401
    assert after == before
    assert after["leases"] == after["handoffs"] == after["claim_receipts"] == 0
    assert after["dispatch"]["attempts"] == after["dispatch"]["fence_epoch"] == 0


def test_credential_expiring_during_publication_fk_wait_rolls_back(client):
    _, run, worker_id, _, _ = ready(client)
    response, before, after = blocked_until_expiry(client, run, worker_id, lock="task_fk")
    assert response.status_code == 401
    assert after == before


@pytest.mark.parametrize("lock", ["worker", "credential"])
def test_credential_expiring_during_authorization_row_wait_is_rejected(client, lock):
    _, run, worker_id, _, _ = ready(client)
    response, before, after = blocked_until_expiry(client, run, worker_id, lock=lock)
    assert response.status_code == 401
    assert after == before


@pytest.mark.parametrize("action", ["revoke", "disable", "rotate"])
def test_operator_invalidation_during_coordination_wait_rejects_old_credential(client, action):
    engine = client.app.state.engine
    _, run, ident, _, headers = ready(client)
    before = snapshot(engine)
    with phase(engine) as holder:
        coordination(holder, client.app.state.settings.scheduler_policy())
        pid = holder.scalar(text("SELECT pg_backend_pid()"))
        with (
            engine.connect().execution_options(isolation_level="AUTOCOMMIT") as observer,
            ThreadPoolExecutor(max_workers=1) as pool,
        ):
            future = pool.submit(acquire, client, run, headers)
            try:
                blocked = observed_block(observer, pid, future)
                _, new_token = alter_worker(
                    holder, UUID(ident), action, client.app.state.settings.scheduler_policy()
                )
                holder.flush()
            finally:
                holder.commit()
            response = future.result(timeout=10)
    after = snapshot(engine)
    save_evidence(
        action,
        {
            "scenario": "operator_" + action,
            "holder_pid": pid,
            "claim_pid": blocked["pid"],
            "wait_event_type": blocked["wait_event_type"],
            "wait_event": blocked["wait_event"],
            "lock_observed_at": blocked["observed_at"].isoformat(),
            "response_status": response.status_code,
            "before_sql": before,
            "after_sql": after,
        },
    )
    assert response.status_code == 401
    assert after == before
    if action == "rotate":
        replacement = WorkerHeaders(Authorization="Bearer " + new_token)
        assert acquire(client, run, replacement).status_code == 201


def test_credential_expired_before_entry_has_no_publication(client):
    _, run, worker_id, _, _ = ready(client)
    headers, _ = short_credential(client, worker_id, remaining=-0.1)
    before = snapshot(client.app.state.engine)
    assert acquire(client, run, headers).status_code == 401
    assert snapshot(client.app.state.engine) == before


def test_current_worker_can_claim_despite_unrelated_expired_credential(client):
    _, run, worker_id, _, headers = ready(client)
    unrelated_id, _, _ = worker(client, run)
    expired, _ = short_credential(client, unrelated_id, remaining=-0.1)
    assert acquire(client, run, expired).status_code == 401
    response = acquire(client, run, headers)
    assert response.status_code == 201
    with Session(client.app.state.engine) as db:
        leases = db.scalars(select(TaskLease)).all()
        assert len(leases) == 1 and str(leases[0].worker_id) == worker_id


@pytest.mark.parametrize("field", ["workspace_id", "project_id"])
def test_scope_loss_cannot_bypass_immutable_binding_or_foreign_scope(client, field):
    engine = client.app.state.engine
    _, run, worker_id, _, headers = ready(client)
    other = client.post("/api/v1/workspaces", json={"name": "Other scoped worker"}).json()
    # Scope changes are unsupported and rejected by actual immutable PG triggers.
    # Never disable those triggers to invent a production scope-changing path.
    with pytest.raises(IntegrityError), phase(engine) as db:
        coordination(db)
        row = db.get(WorkerIdentity, UUID(worker_id))
        setattr(row, field, UUID(other["id"]) if field == "workspace_id" else None)
        db.flush()
    _, _, foreign = worker(client, run, workspace=other["id"], project=False)
    before = snapshot(engine)
    assert acquire(client, run, foreign).status_code == 404
    assert snapshot(engine) == before
    assert acquire(client, run, headers).status_code == 201


@pytest.mark.parametrize("operation", ["replay", "recovery", "acknowledge", "release", "heartbeat"])
def test_related_handoff_paths_recheck_expiry_after_workspace_wait(client, operation):
    engine = client.app.state.engine
    _, run, worker_id, _, _ = ready(
        client,
        config={
            "scheduler_ack_seconds": 2,
            "scheduler_lease_seconds": 5,
            "scheduler_max_lease_seconds": 10,
            "scheduler_heartbeat_seconds": 1,
        },
    )
    headers, expires = short_credential(
        client, worker_id, remaining=2.5 if operation == "heartbeat" else 0.85
    )
    key = uuid4()
    first = acquire(client, run, headers, key)
    assert first.status_code == 201
    handoff = first.json()
    if operation == "heartbeat":
        assert act(client, handoff, headers).status_code == 200
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as observer:
            wait_db(observer, expires - timedelta(seconds=0.7))
    before = snapshot(engine)

    def request():
        if operation == "recovery":
            return client.get(f"/api/v1/workers/claims/{key}", headers=headers)
        if operation == "replay":
            return acquire(client, run, headers, key)
        return act(
            client,
            handoff,
            headers,
            operation,
            **({"request_id": str(uuid4())} if operation == "heartbeat" else {}),
        )

    with engine.connect() as holder, holder.begin():
        pid = holder.scalar(text("SELECT pg_backend_pid()"))
        holder.execute(
            select(Workspace.id).where(Workspace.id == UUID(run["workspace_id"])).with_for_update()
        )
        with (
            engine.connect().execution_options(isolation_level="AUTOCOMMIT") as observer,
            ThreadPoolExecutor(max_workers=1) as pool,
        ):
            future = pool.submit(request)
            try:
                blocked = observed_block(observer, pid, future)
                assert blocked["observed_at"] < expires
                released = wait_db(observer, expires, future)
            finally:
                holder.commit()
            response = future.result(timeout=10)
    after = snapshot(engine)
    save_evidence(
        operation,
        {
            "scenario": operation,
            "holder_pid": pid,
            "request_pid": blocked["pid"],
            "wait_event_type": blocked["wait_event_type"],
            "lock_observed_at": blocked["observed_at"].isoformat(),
            "credential_expires_at": expires.isoformat(),
            "lock_released_at": released.isoformat(),
            "response_status": response.status_code,
            "before_sql": before,
            "after_sql": after,
        },
    )
    assert response.status_code == 401
    assert after == before

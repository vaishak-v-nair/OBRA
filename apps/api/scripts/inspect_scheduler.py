"""Independent guarded read-only SQL inspection; no HTTP cache or worker simulation."""

import argparse
import json
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from orba.db import make_engine
from orba.orchestration_models import OrchestrationRun
from orba.scheduler_models import (
    HandoffRecord,
    LeaseHeartbeat,
    SchedulerState,
    TaskDispatch,
    TaskLease,
    WorkerCredential,
    WorkerIdentity,
)
from orba.scheduler_schemas import DispatchRead, WorkerRead, lease_read
from orba.transactions import db_now
from scripts.inspect_orchestration import inspect as inspect_source
from scripts.prepare_tests import TEST_URL
from scripts.test_database import guard_test_url


def inspect(run_id):
    guard_test_url(TEST_URL)
    source = inspect_source(run_id)  # Separate authoritative immutable source/task/graph SQL audit.
    engine = make_engine(TEST_URL)
    try:
        with Session(engine) as db, db.begin():
            db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY"))
            run = db.get(OrchestrationRun, run_id)
            if not run or run.revision != source["revision"]:
                raise ValueError(
                    "Run changed between independent SQL reads; inspect again explicitly."
                )
            dispatches = db.scalars(
                select(TaskDispatch)
                .where(TaskDispatch.run_id == run_id)
                .order_by(TaskDispatch.created_at, TaskDispatch.id)
            ).all()
            records, worker_ids, lease_ids = [], set(), []
            for dispatch in dispatches:
                leases = db.scalars(
                    select(TaskLease)
                    .where(TaskLease.dispatch_id == dispatch.id)
                    .order_by(TaskLease.created_at, TaskLease.id)
                ).all()
                worker_ids.update(lease.worker_id for lease in leases)
                lease_ids.extend(lease.id for lease in leases)
                worker = db.get(WorkerIdentity, leases[-1].worker_id) if leases else None
                data = {
                    field: getattr(dispatch, field)
                    for field in DispatchRead.model_fields
                    if field not in {"leases", "worker_name"}
                }
                data.update(
                    leases=[lease_read(lease) for lease in leases],
                    worker_name=worker.display_name if worker else None,
                )
                records.append(
                    DispatchRead.model_validate(data).model_dump(mode="json")
                    | {
                        "project_id": str(dispatch.project_id),
                        "workspace_id": str(dispatch.workspace_id),
                    }
                )
            return {
                "scheduler_state": {
                    "tick_count": db.get(SchedulerState, 1).tick_count,
                    "last_tick_at": db.get(SchedulerState, 1).last_tick_at.isoformat(),
                    "process_id": str(db.get(SchedulerState, 1).process_id),
                    "policy": db.get(SchedulerState, 1).policy,
                },
                "orchestration": source,
                "dispatches": records,
                "workers": [
                    WorkerRead.model_validate(w, from_attributes=True).model_dump(mode="json")
                    for w in db.scalars(
                        select(WorkerIdentity)
                        .where(WorkerIdentity.id.in_(worker_ids))
                        .order_by(WorkerIdentity.id)
                    )
                ],
                "credentials": [
                    {
                        field: getattr(c, field).isoformat()
                        if hasattr(getattr(c, field), "isoformat")
                        else str(getattr(c, field))
                        if isinstance(getattr(c, field), UUID)
                        else getattr(c, field)
                        for field in (
                            "id",
                            "worker_id",
                            "version",
                            "created_at",
                            "expires_at",
                            "revoked_at",
                        )
                    }
                    for c in db.scalars(
                        select(WorkerCredential)
                        .where(WorkerCredential.worker_id.in_(worker_ids))
                        .order_by(WorkerCredential.id)
                    )
                ],
                "handoffs": [
                    {
                        "id": str(h.id),
                        "lease_id": str(h.lease_id),
                        "checksum": h.checksum,
                        "manifest": h.manifest,
                        "created_at": h.created_at.isoformat(),
                    }
                    for h in db.scalars(
                        select(HandoffRecord)
                        .where(HandoffRecord.lease_id.in_(lease_ids))
                        .order_by(HandoffRecord.id)
                    )
                ],
                "heartbeats": [
                    {
                        "id": str(h.id),
                        "lease_id": str(h.lease_id),
                        "request_id": str(h.request_id),
                        "request_hash": h.request_hash,
                        "accepted_at": h.accepted_at.isoformat(),
                        "expires_at": h.expires_at.isoformat(),
                    }
                    for h in db.scalars(
                        select(LeaseHeartbeat)
                        .where(LeaseHeartbeat.lease_id.in_(lease_ids))
                        .order_by(LeaseHeartbeat.accepted_at)
                    )
                ],
                "run_revision_rechecked": run.revision,
                "inspected_at": db_now(db).isoformat(),
            }
    finally:
        engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=UUID, required=True)
    print(json.dumps(inspect(parser.parse_args().run)))

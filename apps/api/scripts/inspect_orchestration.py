"""Independent read-only SQL audit in guarded orba_test, no HTTP/model/executor."""

import argparse
import hashlib
import json
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from orba.architect_models import ArchitectRun, ArchitectureVersion
from orba.architect_schemas import Task
from orba.db import make_engine
from orba.orchestration_graph import evaluate
from orba.orchestration_models import (
    OrchestrationDependency,
    OrchestrationEvent,
    OrchestrationRun,
    OrchestrationTask,
)
from orba.orchestration_schemas import EventRead, TaskRead
from orba.pm_models import ProductManagerRun
from scripts.prepare_tests import TEST_URL
from scripts.test_database import guard_test_url


def require(condition, message):
    # Verification must remain active under Python -O; assertions are test syntax.
    if not condition:
        raise ValueError("Independent SQL audit: " + message)


def inspect(run_id):
    guard_test_url(TEST_URL)
    engine = make_engine(TEST_URL)
    try:
        with Session(engine) as db, db.begin():
            db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY"))
            run = db.get(OrchestrationRun, run_id)
            if not run:
                raise ValueError("Saved test run not found.")
            tasks = db.scalars(
                select(OrchestrationTask)
                .where(OrchestrationTask.run_id == run_id)
                .order_by(OrchestrationTask.display_order)
            ).all()
            require(tasks, "required task query returned no persisted task records.")
            edges = db.scalars(
                select(OrchestrationDependency)
                .where(OrchestrationDependency.run_id == run_id)
                .order_by(OrchestrationDependency.display_order)
            ).all()
            events = db.scalars(
                select(OrchestrationEvent)
                .where(OrchestrationEvent.run_id == run_id)
                .order_by(OrchestrationEvent.sequence)
            ).all()
            graph = evaluate(
                [Task.model_validate(task.definition) for task in tasks],
                cancelled=run.status == "cancelled",
            )
            snapshot = run.source_snapshot
            computed = hashlib.sha256(
                json.dumps(
                    snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=False
                ).encode("utf-8")
            ).hexdigest()
            keys = {task.id: task.key for task in tasks}
            snapshot_tasks = [
                {
                    "source_task_id": str(task.source_task_id),
                    "display_order": task.display_order,
                    "definition": task.definition,
                }
                for task in tasks
            ]
            snapshot_edges = [
                {
                    "source_dependency_id": str(edge.source_dependency_id),
                    "prerequisite": keys[edge.prerequisite_id],
                    "dependent": keys[edge.dependent_id],
                    "display_order": edge.display_order,
                }
                for edge in edges
            ]
            states = {node["key"]: node for node in graph["nodes"]}
            architecture = db.get(ArchitectureVersion, run.architecture_id)
            require(
                tasks and computed == run.snapshot_hash, "missing tasks or invalid snapshot hash."
            )
            require(
                snapshot_tasks == snapshot["tasks"] and snapshot_edges == snapshot["dependencies"],
                "task/dependency rows differ from canonical source snapshot.",
            )
            require(
                {(edge["prerequisite"], edge["dependent"]) for edge in snapshot_edges}
                == {(edge["prerequisite"], edge["dependent"]) for edge in graph["edges"]},
                "dependency rows differ from computed graph.",
            )
            require(
                all(
                    task.eligibility == states[task.key]["eligibility"]
                    and task.execution_status == states[task.key]["execution_status"]
                    for task in tasks
                ),
                "persisted task states differ from dependency evaluation.",
            )
            require(
                bool(events)
                and [event.sequence for event in events]
                == list(range(1, run.last_event_sequence + 1))
                and events[-1].new_state == run.status
                and all(event.details == {"execution_performed": False} for event in events),
                "lifecycle ledger is missing, inconsistent or claims execution.",
            )
            return {
                "run_id": str(run.id),
                "project_id": str(run.project_id),
                "workspace_id": str(run.workspace_id),
                "creator_id": str(run.creator_id),
                "client_request_id": str(run.client_request_id),
                "architecture_id": str(run.architecture_id),
                "architecture_version": run.architecture_version,
                "architecture_revision": run.architecture_revision,
                "architecture_hash": run.architecture_hash,
                "source_plan_id": str(run.source_plan_id),
                "source_version": run.source_version,
                "source_revision": run.source_revision,
                "source_hash": run.source_hash,
                "source_approved_by": str(architecture.approved_by),
                "source_approved_at": architecture.approved_at.isoformat(),
                "source_snapshot": snapshot,
                "snapshot_hash": computed,
                "hash_valid": True,
                "relational_snapshot_valid": True,
                "status": run.status,
                "revision": run.revision,
                "created_at": run.created_at.isoformat(),
                "cancelled_at": run.cancelled_at.isoformat() if run.cancelled_at else None,
                "counts": {
                    "tasks": len(tasks),
                    "dependencies": len(edges),
                    "events": len(events),
                    "traces": len(snapshot["traces"]),
                },
                "graph": graph,
                "tasks": [
                    {
                        **TaskRead.model_validate(task, from_attributes=True).model_dump(
                            mode="json"
                        ),
                        "project_id": str(task.project_id),
                        "architecture_id": str(task.architecture_id),
                    }
                    for task in tasks
                ],
                "dependencies": [
                    {
                        **{
                            key: str(getattr(edge, key))
                            for key in (
                                "id",
                                "run_id",
                                "project_id",
                                "source_dependency_id",
                                "prerequisite_id",
                                "dependent_id",
                            )
                        },
                        "display_order": edge.display_order,
                    }
                    for edge in edges
                ],
                "events": [
                    {
                        **EventRead.model_validate(event, from_attributes=True).model_dump(
                            mode="json"
                        ),
                        "project_id": str(event.project_id),
                    }
                    for event in events
                ],
                "generation_records": {
                    model.__tablename__: db.scalar(select(func.count()).select_from(model))
                    for model in (ProductManagerRun, ArchitectRun)
                },
                "audit_model_requests": 0,
                "execution_performed": False,
                "execution_class": "real_local_control_plane",
            }
    finally:
        engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=UUID, required=True)
    args = parser.parse_args()
    print(json.dumps(inspect(args.run)))


if __name__ == "__main__":
    main()

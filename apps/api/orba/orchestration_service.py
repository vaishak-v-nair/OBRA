"""Short transactional control-plane operations. No model, worker or executor calls."""

import hashlib
import logging
from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import select

from orba.architect_models import (
    ArchitectureComponent,
    ArchitectureVersion,
    EngineeringTask,
    RequirementTrace,
    TaskDependency,
)
from orba.architect_repository import get_architecture, safe_document
from orba.architect_schemas import Task
from orba.orchestration_graph import evaluate
from orba.orchestration_models import (
    OrchestrationDependency,
    OrchestrationEvent,
    OrchestrationRun,
    OrchestrationTask,
)
from orba.orchestration_schemas import RunRead, TaskRead
from orba.pm_errors import PMError
from orba.pm_models import ProductPlan
from orba.pm_schemas import canonical
from orba.pm_service import check_session, lock_project, phase

HASH_VERSION = "orba-orchestration-canonical-json-v1"
logger = logging.getLogger(__name__)
TRANSITIONS = {
    "created": {"awaiting_executor"},
    "awaiting_executor": {"cancelled"},
    "cancelled": set(),
}


class OrchestrationError(PMError):
    def body(self):
        result = super().body()
        result["error"]["docs"] = "#orchestration-foundation"
        return result


def checksum(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def conflict(code, message):
    raise OrchestrationError(409, code, message)


def get_run(db, project_id, run_id, *, lock=False):
    query = select(OrchestrationRun).where(
        OrchestrationRun.id == run_id, OrchestrationRun.project_id == project_id
    )
    run = db.scalar(query.with_for_update() if lock else query.with_for_update(read=True))
    if run is None:
        raise HTTPException(404, "Orchestration run not found.")
    return run


def require_approval(artifact, report):
    """Approval is a human binding to this exact revision, not just a state label."""
    dispositions = artifact.approval_dispositions
    obligations = {item["id"] for item in report["review_obligations"]}
    valid = bool(artifact.approved_by and artifact.approved_at and report["approvable"])
    valid = valid and isinstance(dispositions, dict) and set(dispositions) == obligations
    if valid:
        for value in dispositions.values():
            try:
                valid = valid and (
                    value["actor_id"] == str(artifact.approved_by)
                    and value["revision"] == artifact.revision
                    and datetime.fromisoformat(value["decided_at"]) == artifact.approved_at
                    and isinstance(value["reason"], str)
                    and bool(value["reason"].strip())
                )
            except (KeyError, ValueError, TypeError):
                valid = False
    if not valid:
        conflict(
            "source_approval_invalid",
            "The saved architecture approval is incomplete or inconsistent. Review its exact revision before creating a run.",
        )


def snapshot_source(db, project, artifact):
    document, source, current, report = safe_document(db, artifact)
    if not current:
        conflict(
            "source_changed",
            "The architecture belongs to an earlier approved Product Plan. Approve an architecture for the current agreement first.",
        )
    require_approval(artifact, report)
    graph = evaluate(document.tasks)
    plan = db.get(ProductPlan, artifact.source_plan_id)
    if not plan.approved_by or not plan.approved_at:
        conflict(
            "source_approval_invalid",
            "The source Product Plan has no valid human approval binding.",
        )
    tasks = db.scalars(
        select(EngineeringTask)
        .where(EngineeringTask.architecture_id == artifact.id)
        .order_by(EngineeringTask.display_order, EngineeringTask.id)
    ).all()
    by_key = {task.key: task for task in tasks}
    keys = {task.id: task.key for task in tasks}
    components = dict(
        db.execute(
            select(ArchitectureComponent.id, ArchitectureComponent.key).where(
                ArchitectureComponent.architecture_id == artifact.id
            )
        ).all()
    )
    edges = db.scalars(
        select(TaskDependency)
        .where(TaskDependency.architecture_id == artifact.id)
        .order_by(TaskDependency.dependent_id, TaskDependency.display_order, TaskDependency.id)
    ).all()
    traces = db.scalars(
        select(RequirementTrace)
        .where(RequirementTrace.architecture_id == artifact.id)
        .order_by(RequirementTrace.display_order, RequirementTrace.id)
    ).all()
    snapshot = {
        "hash_version": HASH_VERSION,
        "project_id": str(project.id),
        "workspace_id": str(project.workspace_id),
        "architecture": {
            "id": str(artifact.id),
            "version": artifact.version,
            "revision": artifact.revision,
            "hash": artifact.content_hash,
            "approved_by": str(artifact.approved_by),
            "approved_at": artifact.approved_at.isoformat(),
            "approval_dispositions": artifact.approval_dispositions,
            "document": document.model_dump(mode="json"),
        },
        "product_plan": {
            "id": str(plan.id),
            "version": plan.version,
            "revision": plan.revision,
            "hash": plan.content_hash,
            "approved_by": str(plan.approved_by),
            "approved_at": plan.approved_at.isoformat(),
            "document": source.model_dump(mode="json"),
        },
        "tasks": [
            {
                "source_task_id": str(by_key[task.key].id),
                "display_order": index,
                "definition": task.model_dump(mode="json"),
            }
            for index, task in enumerate(document.tasks)
        ],
        "dependencies": [
            {
                "source_dependency_id": str(edge.id),
                "prerequisite": keys[edge.prerequisite_id],
                "dependent": keys[edge.dependent_id],
                "display_order": index,
            }
            for index, edge in enumerate(edges)
        ],
        "traces": [
            {
                "source_trace_id": str(trace.id),
                "story_id": str(trace.story_id),
                "task_key": keys.get(trace.task_id),
                "component_key": components.get(trace.component_id),
            }
            for trace in traces
        ],
    }
    return snapshot, graph


def append_event(db, run, event_type, previous, new, actor, moment, *, task=None):
    # Callers hold the run row lock, or own a new uncommitted run. No public event writer.
    run.last_event_sequence += 1
    db.add(
        OrchestrationEvent(
            id=uuid4(),
            run_id=run.id,
            project_id=run.project_id,
            task_id=task.id if task else None,
            sequence=run.last_event_sequence,
            run_revision=run.revision,
            event_type=event_type,
            actor_type="user" if actor else "system",
            actor_id=actor,
            occurred_at=moment,
            previous_state=previous,
            new_state=new,
            details={"execution_performed": False},
        )
    )


def transition(db, run, target, actor, moment, *, expected_revision):
    if run.revision != expected_revision:
        conflict(
            "run_revision_conflict",
            "The run changed. Refresh its saved revision before cancelling.",
        )
    if target not in TRANSITIONS.get(run.status, set()):
        conflict(
            "unsupported_transition",
            "This transition is unavailable. Stage05A does not execute or complete engineering tasks.",
        )
    if target == "cancelled" and actor is None:
        conflict("unsupported_transition", "Cancellation requires an authorized human actor.")
    previous = run.status
    run.status, run.revision, run.updated_at = target, run.revision + 1, moment
    if target == "cancelled":
        run.cancelled_at = moment
    db.flush()  # run cancellation must exist before the task trigger permits cancellation.
    if target == "cancelled":
        tasks = db.scalars(
            select(OrchestrationTask)
            .where(OrchestrationTask.run_id == run.id)
            .order_by(OrchestrationTask.display_order)
        ).all()
        for task in tasks:
            task.execution_status, task.updated_at = "cancelled", moment
            append_event(
                db,
                run,
                "task_cancelled",
                "awaiting_executor",
                "cancelled",
                actor,
                moment,
                task=task,
            )
    append_event(db, run, "run_" + target, previous, target, actor, moment)
    db.flush()


def create_run(engine, project_id, actor, session_id, payload):
    request_hash = checksum(payload.model_dump(mode="json"))
    with phase(engine) as db:
        project = lock_project(db, project_id, actor)
        moment = check_session(db, session_id, actor)
        prior = db.scalar(
            select(OrchestrationRun)
            .where(
                OrchestrationRun.project_id == project_id,
                OrchestrationRun.creator_id == actor,
                OrchestrationRun.client_request_id == payload.client_request_id,
            )
            .with_for_update()
        )
        if prior:
            if prior.request_hash != request_hash:
                conflict(
                    "idempotency_conflict",
                    "This request ID belongs to different source inputs. Inspect the original run; use a new ID only for a deliberate new run.",
                )
            result = detail(db, prior)
            created = False
        else:
            artifact = get_architecture(db, project_id, payload.architecture_id)
            if artifact.state != "approved" or (artifact.version, artifact.revision) != (
                payload.architecture_version,
                payload.architecture_revision,
            ):
                conflict(
                    "architecture_not_approved",
                    "Select the exact current approved architecture version and revision before creating an orchestration run.",
                )
            snapshot, _ = snapshot_source(db, project, artifact)
            run = OrchestrationRun(
                id=uuid4(),
                project_id=project_id,
                workspace_id=project.workspace_id,
                architecture_id=artifact.id,
                architecture_version=artifact.version,
                architecture_revision=artifact.revision,
                architecture_hash=artifact.content_hash,
                source_plan_id=artifact.source_plan_id,
                source_version=artifact.source_version,
                source_revision=artifact.source_revision,
                source_hash=artifact.source_hash,
                creator_id=actor,
                client_request_id=payload.client_request_id,
                request_hash=request_hash,
                source_snapshot=snapshot,
                snapshot_hash=checksum(snapshot),
                hash_version=HASH_VERSION,
                status="created",
                revision=1,
                last_event_sequence=0,
                created_at=moment,
                updated_at=moment,
            )
            db.add(run)
            db.flush()
            task_ids = {}
            for item in snapshot["tasks"]:
                definition = item["definition"]
                ident = task_ids[definition["key"]] = uuid4()
                db.add(
                    OrchestrationTask(
                        id=ident,
                        run_id=run.id,
                        project_id=project_id,
                        architecture_id=artifact.id,
                        source_task_id=item["source_task_id"],
                        key=definition["key"],
                        definition=definition,
                        display_order=item["display_order"],
                        eligibility="eligible"
                        if not definition["dependencies"]
                        else "waiting_prerequisites",
                        execution_status="awaiting_executor",
                        created_at=moment,
                        updated_at=moment,
                    )
                )
            db.flush()
            for edge in snapshot["dependencies"]:
                db.add(
                    OrchestrationDependency(
                        id=uuid4(),
                        run_id=run.id,
                        project_id=project_id,
                        source_dependency_id=edge["source_dependency_id"],
                        prerequisite_id=task_ids[edge["prerequisite"]],
                        dependent_id=task_ids[edge["dependent"]],
                        display_order=edge["display_order"],
                    )
                )
            db.flush()
            append_event(db, run, "run_created", None, "created", actor, moment)
            transition(db, run, "awaiting_executor", None, moment, expected_revision=1)
            result, created = detail(db, run), True
        check_session(db, session_id, actor)
    # phase exits/commits before a result escapes. Uncertain commits never trigger replay.
    logger.info(
        "orchestration_commit run_id=%s request_id=%s action=%s status=%s",
        result["id"],
        payload.client_request_id,
        "create" if created else "replay",
        result["status"],
    )
    return result, created


def summary(run):
    return RunRead.model_validate(run, from_attributes=True).model_dump()


def materialized(db, run):
    """Audit the relational snapshot against its immutable canonical source."""
    try:
        snapshot = run.source_snapshot
        if run.hash_version != HASH_VERSION or checksum(snapshot) != run.snapshot_hash:
            raise ValueError("Checksum mismatch")
        architecture, source = snapshot["architecture"], snapshot["product_plan"]
        if (
            str(run.project_id),
            str(run.workspace_id),
            str(run.architecture_id),
            run.architecture_version,
            run.architecture_revision,
            run.architecture_hash,
            str(run.source_plan_id),
            run.source_version,
            run.source_revision,
            run.source_hash,
        ) != (
            snapshot["project_id"],
            snapshot["workspace_id"],
            architecture["id"],
            architecture["version"],
            architecture["revision"],
            architecture["hash"],
            source["id"],
            source["version"],
            source["revision"],
            source["hash"],
        ):
            raise ValueError("Binding mismatch")
        tasks = db.scalars(
            select(OrchestrationTask)
            .where(OrchestrationTask.run_id == run.id)
            .order_by(OrchestrationTask.display_order)
        ).all()
        definitions = [Task.model_validate(task.definition) for task in tasks]
        graph = evaluate(definitions, cancelled=run.status == "cancelled")
        expected_tasks = [
            {
                "source_task_id": str(task.source_task_id),
                "display_order": task.display_order,
                "definition": task.definition,
            }
            for task in tasks
        ]
        if expected_tasks != snapshot["tasks"]:
            raise ValueError("Task snapshot mismatch")
        by_id = {task.id: task.key for task in tasks}
        edges = db.scalars(
            select(OrchestrationDependency)
            .where(OrchestrationDependency.run_id == run.id)
            .order_by(OrchestrationDependency.display_order)
        ).all()
        expected_edges = [
            {
                "source_dependency_id": str(edge.source_dependency_id),
                "prerequisite": by_id[edge.prerequisite_id],
                "dependent": by_id[edge.dependent_id],
                "display_order": edge.display_order,
            }
            for edge in edges
        ]
        if expected_edges != snapshot["dependencies"] or {
            (edge["prerequisite"], edge["dependent"]) for edge in expected_edges
        } != {(edge["prerequisite"], edge["dependent"]) for edge in graph["edges"]}:
            raise ValueError("Dependency snapshot mismatch")
        nodes = {node["key"]: node for node in graph["nodes"]}
        if any(
            task.eligibility != nodes[task.key]["eligibility"]
            or task.execution_status != nodes[task.key]["execution_status"]
            for task in tasks
        ):
            raise ValueError("Task state mismatch")
        events = db.scalars(
            select(OrchestrationEvent)
            .where(OrchestrationEvent.run_id == run.id)
            .order_by(OrchestrationEvent.sequence)
        ).all()
        if (
            run.status not in {"awaiting_executor", "cancelled"}
            or [event.sequence for event in events] != list(range(1, run.last_event_sequence + 1))
            or len(events) != (len(tasks) + 3 if run.status == "cancelled" else 2)
            or [event.event_type for event in events[:2]]
            != ["run_created", "run_awaiting_executor"]
            or events[-1].new_state != run.status
            or any(event.details != {"execution_performed": False} for event in events)
        ):
            raise ValueError("Lifecycle ledger mismatch")
        return tasks, graph
    except (ValueError, KeyError, TypeError, ValidationError):
        conflict(
            "snapshot_integrity_error",
            "The persisted orchestration snapshot failed integrity checks. No execution is certified. Contact the local operator.",
        )


def detail(db, run):
    tasks, graph = materialized(db, run)
    current = db.scalar(
        select(ArchitectureVersion).where(
            ArchitectureVersion.id == run.architecture_id,
            ArchitectureVersion.project_id == run.project_id,
        )
    )
    plan = db.get(ProductPlan, run.source_plan_id)
    return summary(run) | {
        "tasks": [
            TaskRead.model_validate(task, from_attributes=True).model_dump() for task in tasks
        ],
        "graph": graph,
        "source_current": bool(
            current
            and current.state == "approved"
            and current.content_hash == run.architecture_hash
            and current.revision == run.architecture_revision
            and current.version == run.architecture_version
            and plan
            and plan.state == "approved"
            and plan.content_hash == run.source_hash
            and plan.version == run.source_version
            and plan.revision == run.source_revision
        ),
    }

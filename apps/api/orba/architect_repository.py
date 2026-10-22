"""Transaction-local, bounded assembly. Callers own root locks and authority."""

import hashlib
from uuid import uuid4

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import delete, func, select

from orba.architect_models import (
    ArchitectRun,
    ArchitectureComponent,
    ArchitectureVersion,
    EngineeringTask,
    RequirementTrace,
    TaskDependency,
)
from orba.architect_schemas import ArchitectureDocument
from orba.architect_traceability import coverage
from orba.pm_errors import PMError
from orba.pm_models import ProductPlan, ProductStory
from orba.pm_repository import content_hash as source_hash
from orba.pm_repository import read_document as read_source
from orba.pm_schemas import canonical
from orba.task_graph import analyze

HASH_VERSION = "orba-architect-canonical-json-v1"


class ArchitectError(PMError):
    def body(self):
        value = super().body()
        value["error"]["docs"] = "#architect-setup"
        return value


def document_hash(document):
    return hashlib.sha256(canonical(document.model_dump(mode="json")).encode()).hexdigest()


def get_architecture(db, project_id, architecture_id, *, write=False):
    value = db.scalar(
        select(ArchitectureVersion)
        .where(
            ArchitectureVersion.id == architecture_id, ArchitectureVersion.project_id == project_id
        )
        .with_for_update(read=not write)
    )
    if value is None:
        raise HTTPException(404, "Architecture not found.")
    return value


def source_document(db, artifact, *, current=False):
    plan = db.scalar(
        select(ProductPlan)
        .where(
            ProductPlan.id == artifact.source_plan_id, ProductPlan.project_id == artifact.project_id
        )
        .with_for_update(read=True)
    )
    if plan is None:
        raise HTTPException(404, "Product plan not found.")
    try:
        document = read_source(db, plan)
        if (plan.version, plan.revision, plan.content_hash) != (
            artifact.source_version,
            artifact.source_revision,
            artifact.source_hash,
        ) or source_hash(document) != plan.content_hash:
            raise ValueError("Source integrity mismatch")
    except (ValueError, ValidationError):
        raise ArchitectError(
            409,
            "source_integrity_error",
            "The saved source failed integrity validation. It cannot authorize publication or approval.",
        ) from None
    if current and plan.state != "approved":
        raise ArchitectError(
            409,
            "source_changed",
            "The source is no longer the current approved Product Plan. Generate explicitly from the current agreement.",
        )
    return document, plan.state == "approved"


def read_document(db, artifact):
    components = db.scalars(
        select(ArchitectureComponent)
        .where(ArchitectureComponent.architecture_id == artifact.id)
        .order_by(ArchitectureComponent.display_order)
    ).all()
    tasks = db.scalars(
        select(EngineeringTask)
        .where(EngineeringTask.architecture_id == artifact.id)
        .order_by(EngineeringTask.display_order)
    ).all()
    edges = db.scalars(
        select(TaskDependency)
        .where(TaskDependency.architecture_id == artifact.id)
        .order_by(TaskDependency.dependent_id, TaskDependency.display_order)
    ).all()
    traces = db.execute(
        select(RequirementTrace.task_id, RequirementTrace.component_id, ProductStory.key)
        .join(ProductStory, ProductStory.id == RequirementTrace.story_id)
        .where(RequirementTrace.architecture_id == artifact.id)
        .order_by(RequirementTrace.display_order)
    ).all()
    task_keys = {item.id: item.key for item in tasks}
    dependencies, story_refs = {}, {}
    for edge in edges:
        dependencies.setdefault(edge.dependent_id, []).append(task_keys[edge.prerequisite_id])
    for task_id, component_id, story_key in traces:
        story_refs.setdefault(task_id or component_id, []).append(story_key)
    body = dict(artifact.content)
    body["components"] = [
        dict(item.content, key=item.key, story_refs=story_refs.get(item.id, []))
        for item in components
    ]
    body["tasks"] = [
        dict(
            item.content,
            key=item.key,
            category=item.category,
            priority=item.priority,
            planning_state=item.planning_state,
            story_refs=story_refs.get(item.id, []),
            dependencies=dependencies.get(item.id, []),
        )
        for item in tasks
    ]
    return ArchitectureDocument.model_validate(body)


def safe_document(db, artifact):
    try:
        value = read_document(db, artifact)
        if artifact.hash_version != HASH_VERSION or document_hash(value) != artifact.content_hash:
            raise ValueError("Architecture integrity mismatch")
        source, current = source_document(db, artifact)
        report = coverage(value, source)
    except (ValueError, ValidationError, KeyError):
        raise ArchitectError(
            409,
            "architecture_integrity_error",
            "Saved architecture failed document, source or graph integrity checks. It cannot be approved.",
        ) from None
    return value, source, current, report


def write_document(db, artifact, document, source):
    coverage(document, source)  # Reject invalid source references before any child deletion.
    old_tasks = dict(
        db.execute(
            select(EngineeringTask.key, EngineeringTask.id).where(
                EngineeringTask.architecture_id == artifact.id
            )
        ).all()
    )
    old_components = dict(
        db.execute(
            select(ArchitectureComponent.key, ArchitectureComponent.id).where(
                ArchitectureComponent.architecture_id == artifact.id
            )
        ).all()
    )
    for model in (RequirementTrace, TaskDependency, EngineeringTask, ArchitectureComponent):
        db.execute(delete(model).where(model.architecture_id == artifact.id))
    artifact.content = document.model_dump(mode="json", exclude={"components", "tasks"})
    artifact.content_hash, artifact.hash_version = document_hash(document), HASH_VERSION
    task_ids, component_ids = {}, {}
    for index, item in enumerate(document.components):
        ident = old_components.get(item.key, uuid4())
        component_ids[item.key] = ident
        db.add(
            ArchitectureComponent(
                id=ident,
                architecture_id=artifact.id,
                project_id=artifact.project_id,
                key=item.key,
                content=item.model_dump(mode="json", exclude={"key", "story_refs"}),
                display_order=index,
            )
        )
    for index, item in enumerate(document.tasks):
        ident = old_tasks.get(item.key, uuid4())
        task_ids[item.key] = ident
        db.add(
            EngineeringTask(
                id=ident,
                architecture_id=artifact.id,
                project_id=artifact.project_id,
                key=item.key,
                priority=item.priority,
                category=item.category,
                planning_state=item.planning_state,
                content=item.model_dump(
                    mode="json",
                    exclude={
                        "key",
                        "priority",
                        "category",
                        "planning_state",
                        "story_refs",
                        "dependencies",
                    },
                ),
                display_order=index,
            )
        )
    db.flush()
    source_ids = dict(
        db.execute(
            select(ProductStory.key, ProductStory.id).where(
                ProductStory.plan_id == artifact.source_plan_id
            )
        ).all()
    )
    for target, values, ids in (
        ("component_id", document.components, component_ids),
        ("task_id", document.tasks, task_ids),
    ):
        for item in values:
            for index, key in enumerate(item.story_refs):
                db.add(
                    RequirementTrace(
                        architecture_id=artifact.id,
                        project_id=artifact.project_id,
                        source_plan_id=artifact.source_plan_id,
                        story_id=source_ids[key],
                        task_id=ids[item.key] if target == "task_id" else None,
                        component_id=ids[item.key] if target == "component_id" else None,
                        display_order=index,
                    )
                )
    for task in document.tasks:
        for index, prerequisite in enumerate(task.dependencies):
            db.add(
                TaskDependency(
                    architecture_id=artifact.id,
                    project_id=artifact.project_id,
                    prerequisite_id=task_ids[prerequisite],
                    dependent_id=task_ids[task.key],
                    display_order=index,
                )
            )
    db.flush()


def create_architecture(
    db,
    project_id,
    actor_id,
    source,
    document,
    *,
    run_id=None,
    copied_from=None,
    copy_request_id=None,
    copy_request_hash=None,
):
    version = (
        db.scalar(
            select(func.max(ArchitectureVersion.version)).where(
                ArchitectureVersion.project_id == project_id
            )
        )
        or 0
    ) + 1
    artifact = ArchitectureVersion(
        id=uuid4(),
        project_id=project_id,
        source_plan_id=source.id,
        source_version=source.version,
        source_revision=source.revision,
        source_hash=source.content_hash,
        version=version,
        revision=1,
        state="draft",
        content={},
        content_hash="",
        hash_version=HASH_VERSION,
        creator_id=actor_id,
        editor_id=actor_id,
        generating_run_id=run_id,
        copied_from_id=copied_from,
        copy_request_id=copy_request_id,
        copy_request_hash=copy_request_hash,
    )
    db.add(artifact)
    db.flush()
    write_document(db, artifact, document, read_source(db, source))
    return artifact


def summary(artifact):
    fields = (
        "id",
        "project_id",
        "source_plan_id",
        "source_version",
        "source_revision",
        "source_hash",
        "version",
        "revision",
        "state",
        "content_hash",
        "hash_version",
        "creator_id",
        "editor_id",
        "approved_by",
        "approved_at",
        "created_at",
        "updated_at",
        "generating_run_id",
        "copied_from_id",
        "copy_request_id",
        "approval_dispositions",
    )
    return {key: getattr(artifact, key) for key in fields}


def run_summary(db, run, *, architecture_id=None):
    if architecture_id is None:
        architecture_id = db.scalar(
            select(ArchitectureVersion.id).where(ArchitectureVersion.generating_run_id == run.id)
        )
    fields = (
        "id",
        "project_id",
        "workspace_id",
        "initiator_id",
        "client_request_id",
        "source_plan_id",
        "source_version",
        "source_revision",
        "source_hash",
        "status",
        "provider",
        "requested_model",
        "returned_model",
        "prompt_version",
        "created_at",
        "started_at",
        "completed_at",
        "deadline_at",
        "provider_response_id",
        "provider_request_id",
        "usage",
        "error_category",
        "diagnostic_id",
    )
    return {key: getattr(run, key) for key in fields} | {"architecture_id": architecture_id}


def detail(db, artifact):
    document, source, current, report = safe_document(db, artifact)
    run = db.get(ArchitectRun, artifact.generating_run_id) if artifact.generating_run_id else None
    return summary(artifact) | {
        "document": document,
        "source_document": source.model_dump(mode="json"),
        "source_current": current,
        "graph": analyze(document.tasks),
        "coverage": report,
        "generation": run_summary(db, run) if run else None,
    }

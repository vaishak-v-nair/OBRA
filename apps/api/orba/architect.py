"""Authenticated architecture proposals and dependency views; never task execution."""

import hashlib
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import select

from orba.architect_models import ArchitectRun, ArchitectureVersion
from orba.architect_provider import ArchitectModelProvider, GeminiArchitectProvider
from orba.architect_repository import (
    ArchitectError,
    create_architecture,
    detail,
    get_architecture,
    run_summary,
    safe_document,
    source_document,
    summary,
    write_document,
)
from orba.architect_schemas import (
    ArchitectRunCreate,
    ArchitectRunDetail,
    ArchitectRunRead,
    ArchitectureApprove,
    ArchitectureCopy,
    ArchitectureCoverageRead,
    ArchitectureGraphRead,
    ArchitectureRead,
    ArchitectureSummary,
    ArchitectureTasksRead,
    ArchitectureUpdate,
)
from orba.architect_service import capability, expire_architect_runs, generate
from orba.architect_traceability import coverage
from orba.pm import detach
from orba.pm import safe_document as safe_source
from orba.pm_errors import validation_details
from orba.pm_models import ProductPlan
from orba.pm_repository import plan_detail
from orba.pm_schemas import Page, PlanRead, canonical
from orba.pm_service import APPROVERS, check_session, lock_project, phase
from orba.security import DB, Identity, authorized_project, csrf_guard

router = APIRouter(prefix="/api/v1/projects/{project_id}", tags=["Architect"])
Limit = Annotated[int, Query(ge=1, le=50)]
Offset = Annotated[int, Query(ge=0)]


def model_provider(request: Request):
    config = request.app.state.settings
    return GeminiArchitectProvider(config) if config.architect_settings().pm_configured else None


@router.get("/architect-source", response_model=PlanRead | None)
def approved_source(project_id: UUID, request: Request, identity: Identity, session: DB):
    actor, _ = detach(identity, session)
    with phase(request.app.state.engine) as db:
        authorized_project(db, project_id, actor)
        source = db.scalar(
            select(ProductPlan)
            .where(ProductPlan.project_id == project_id, ProductPlan.state == "approved")
            .with_for_update(read=True)
        )
        if source is None:
            return None
        safe_source(db, source)
        return plan_detail(db, source)


@router.post("/architect-runs", response_model=ArchitectRunRead, dependencies=[Depends(csrf_guard)])
def create_run(
    project_id: UUID,
    payload: ArchitectRunCreate,
    request: Request,
    response: Response,
    identity: Identity,
    session: DB,
    provider: Annotated[ArchitectModelProvider | None, Depends(model_provider)],
):
    actor, session_id = detach(identity, session)
    value, created = generate(
        request.app.state.engine,
        request.app.state.settings,
        project_id,
        actor,
        session_id,
        payload,
        provider=provider,
        started=getattr(request.state, "pm_started_at", None),
    )
    if value["status"] in {"failed", "interrupted"}:
        raise ArchitectError(
            409,
            value["error_category"] or "run_failed",
            "This Architect request already ended. Inspect it before explicitly starting a new request.",
            run_id=value["id"],
            diagnostic_id=value["diagnostic_id"],
        )
    response.status_code = (201 if created else 200) if value["status"] == "succeeded" else 202
    return value


@router.get("/architect-runs", response_model=Page[ArchitectRunRead])
def list_runs(
    project_id: UUID,
    request: Request,
    identity: Identity,
    session: DB,
    limit: Limit = 20,
    offset: Offset = 0,
    client_request_id: UUID | None = None,
):
    actor, _ = detach(identity, session)
    with phase(request.app.state.engine) as db:
        authorized_project(db, project_id, actor)
        expire_architect_runs(db, project_id)
        query = select(ArchitectRun).where(ArchitectRun.project_id == project_id)
        if client_request_id:
            query = query.where(
                ArchitectRun.client_request_id == client_request_id,
                ArchitectRun.initiator_id == actor,
            )
        runs = db.scalars(
            query.order_by(ArchitectRun.created_at.desc(), ArchitectRun.id.desc())
            .limit(limit)
            .offset(offset)
            .with_for_update(read=True)
        ).all()
        results = (
            dict(
                db.execute(
                    select(ArchitectureVersion.generating_run_id, ArchitectureVersion.id).where(
                        ArchitectureVersion.generating_run_id.in_([item.id for item in runs])
                    )
                ).all()
            )
            if runs
            else {}
        )
        return {
            "items": [run_summary(db, item, architecture_id=results.get(item.id)) for item in runs],
            "limit": limit,
            "offset": offset,
            "next_offset": offset + limit if len(runs) == limit else None,
            "capability": capability(request.app.state.settings),
        }


@router.get("/architect-runs/{run_id}", response_model=ArchitectRunDetail)
def read_run(project_id: UUID, run_id: UUID, request: Request, identity: Identity, session: DB):
    actor, _ = detach(identity, session)
    with phase(request.app.state.engine) as db:
        authorized_project(db, project_id, actor)
        expire_architect_runs(db, project_id)
        run = db.scalar(
            select(ArchitectRun)
            .where(ArchitectRun.id == run_id, ArchitectRun.project_id == project_id)
            .with_for_update(read=True)
        )
        if run is None:
            raise HTTPException(404, "Architect run not found.")
        return run_summary(db, run) | {"input_snapshot": run.input_snapshot}


@router.get("/architectures", response_model=Page[ArchitectureSummary])
def list_architectures(
    project_id: UUID,
    request: Request,
    identity: Identity,
    session: DB,
    limit: Limit = 20,
    offset: Offset = 0,
    copy_request_id: UUID | None = None,
):
    actor, _ = detach(identity, session)
    with phase(request.app.state.engine) as db:
        authorized_project(db, project_id, actor)
        query = select(ArchitectureVersion).where(ArchitectureVersion.project_id == project_id)
        if copy_request_id:
            query = query.where(
                ArchitectureVersion.copy_request_id == copy_request_id,
                ArchitectureVersion.creator_id == actor,
            )
        items = db.scalars(
            query.order_by(ArchitectureVersion.version.desc()).limit(limit).offset(offset)
        ).all()
        return {
            "items": [summary(item) for item in items],
            "limit": limit,
            "offset": offset,
            "next_offset": offset + limit if len(items) == limit else None,
        }


@router.get("/architectures/{architecture_id}", response_model=ArchitectureRead)
def read_architecture(
    project_id: UUID, architecture_id: UUID, request: Request, identity: Identity, session: DB
):
    actor, _ = detach(identity, session)
    with phase(request.app.state.engine) as db:
        authorized_project(db, project_id, actor)
        return detail(db, get_architecture(db, project_id, architecture_id))


@router.put(
    "/architectures/{architecture_id}",
    response_model=ArchitectureRead,
    dependencies=[Depends(csrf_guard)],
)
def update_architecture(
    project_id: UUID,
    architecture_id: UUID,
    payload: ArchitectureUpdate,
    request: Request,
    identity: Identity,
    session: DB,
):
    actor, session_id = detach(identity, session)
    with phase(request.app.state.engine) as db:
        lock_project(db, project_id, actor)
        artifact = get_architecture(db, project_id, architecture_id, write=True)
        check_session(db, session_id, actor)
        if artifact.state != "draft" or artifact.revision != payload.expected_revision:
            raise ArchitectError(
                409,
                "architecture_revision_conflict",
                "Only the exact saved draft revision can be edited. Keep local input while reviewing the latest saved version.",
            )
        _, source, _, _ = safe_document(db, artifact)
        try:
            coverage(payload.document, source)
        except ValueError as exc:
            raise ArchitectError(
                422,
                "architecture_validation_error",
                "Correct the source references before saving.",
                details=validation_details(exc),
            ) from None
        write_document(db, artifact, payload.document, source)
        artifact.revision += 1
        artifact.editor_id, artifact.updated_at = actor, check_session(db, session_id, actor)
        db.flush()
        return detail(db, artifact)


@router.post(
    "/architectures/{architecture_id}/approve",
    response_model=ArchitectureRead,
    dependencies=[Depends(csrf_guard)],
)
def approve_architecture(
    project_id: UUID,
    architecture_id: UUID,
    payload: ArchitectureApprove,
    request: Request,
    identity: Identity,
    session: DB,
):
    actor, session_id = detach(identity, session)
    with phase(request.app.state.engine) as db:
        lock_project(db, project_id, actor, APPROVERS)
        artifact = get_architecture(db, project_id, architecture_id, write=True)
        moment = check_session(db, session_id, actor)
        if artifact.revision != payload.expected_revision or artifact.version != payload.version:
            raise ArchitectError(
                409,
                "architecture_revision_conflict",
                "Approval must identify the exact saved architecture version and revision.",
            )
        if artifact.state == "approved":
            return detail(db, artifact)
        if artifact.state != "draft":
            raise ArchitectError(
                409,
                "architecture_not_draft",
                "Historical approvals are immutable. Create a draft copy.",
            )
        _, _, _, report = safe_document(db, artifact)
        source_document(db, artifact, current=True)
        obligations = {item["id"] for item in report["review_obligations"]}
        if not report["approvable"] or set(payload.acknowledgments) != obligations:
            raise ArchitectError(
                422,
                "architecture_review_incomplete",
                "Resolve missing coverage, clarification tasks and all exact saved-revision review obligations before approval.",
                details=[
                    {
                        "field": "coverage",
                        "message": "Review linked requirements and blocking decisions.",
                    }
                ],
            )
        current = db.scalar(
            select(ArchitectureVersion)
            .where(
                ArchitectureVersion.project_id == project_id,
                ArchitectureVersion.state == "approved",
            )
            .with_for_update()
        )
        if current and current.version >= artifact.version:
            raise ArchitectError(
                409,
                "approval_version_conflict",
                "A newer architecture is already approved. Review its version first.",
            )
        if current:
            current.state = "superseded"
            db.flush()
        artifact.state, artifact.approved_by, artifact.approved_at, artifact.updated_at = (
            "approved",
            actor,
            moment,
            moment,
        )
        artifact.approval_dispositions = {
            key: {
                "reason": reason,
                "actor_id": str(actor),
                "decided_at": moment.isoformat(),
                "revision": artifact.revision,
            }
            for key, reason in payload.acknowledgments.items()
        }
        db.flush()
        check_session(db, session_id, actor)
        return detail(db, artifact)


@router.post(
    "/architectures/{architecture_id}/draft",
    response_model=ArchitectureRead,
    dependencies=[Depends(csrf_guard)],
)
def copy_architecture(
    project_id: UUID,
    architecture_id: UUID,
    payload: ArchitectureCopy,
    request: Request,
    response: Response,
    identity: Identity,
    session: DB,
):
    actor, session_id = detach(identity, session)
    request_hash = hashlib.sha256(
        canonical({"source_id": str(architecture_id), **payload.model_dump(mode="json")}).encode()
    ).hexdigest()
    with phase(request.app.state.engine) as db:
        lock_project(db, project_id, actor)
        source_artifact = get_architecture(db, project_id, architecture_id, write=True)
        check_session(db, session_id, actor)
        existing = db.scalar(
            select(ArchitectureVersion).where(
                ArchitectureVersion.project_id == project_id,
                ArchitectureVersion.creator_id == actor,
                ArchitectureVersion.copy_request_id == payload.client_request_id,
            )
        )
        if existing:
            if existing.copy_request_hash != request_hash:
                raise ArchitectError(
                    409, "idempotency_conflict", "This copy request ID belongs to different input."
                )
            return detail(db, get_architecture(db, project_id, existing.id))
        if (source_artifact.version, source_artifact.revision) != (
            payload.version,
            payload.expected_revision,
        ):
            raise ArchitectError(
                409,
                "architecture_revision_conflict",
                "The source revision changed. Choose its saved version again.",
            )
        document, _, _, _ = safe_document(db, source_artifact)
        artifact = create_architecture(
            db,
            project_id,
            actor,
            db.get(ProductPlan, source_artifact.source_plan_id),
            document,
            copied_from=source_artifact.id,
            copy_request_id=payload.client_request_id,
            copy_request_hash=request_hash,
        )
        check_session(db, session_id, actor)
        response.status_code = 201
        return detail(db, artifact)


@router.get("/architectures/{architecture_id}/tasks", response_model=ArchitectureTasksRead)
@router.get("/architectures/{architecture_id}/graph", response_model=ArchitectureGraphRead)
@router.get("/architectures/{architecture_id}/coverage", response_model=ArchitectureCoverageRead)
def architecture_view(
    project_id: UUID, architecture_id: UUID, request: Request, identity: Identity, session: DB
):
    actor, _ = detach(identity, session)
    with phase(request.app.state.engine) as db:
        authorized_project(db, project_id, actor)
        artifact = get_architecture(db, project_id, architecture_id)
        value = detail(db, artifact)
        kind = request.url.path.rsplit("/", 1)[-1]
        return {
            "architecture_id": artifact.id,
            "version": artifact.version,
            "revision": artifact.revision,
            "content_hash": artifact.content_hash,
            "source_current": value["source_current"],
            kind: value["document"].tasks if kind == "tasks" else value[kind],
        }

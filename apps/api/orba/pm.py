"""Authenticated project-scoped PM routes; business state stays in the API."""

import hashlib
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import ValidationError
from sqlalchemy import select

from orba.pm_errors import PMError, validation_details
from orba.pm_models import ProductManagerRun, ProductPlan
from orba.pm_provider import GeminiProductManagerProvider, ProductManagerModelProvider
from orba.pm_repository import (
    content_hash,
    create_plan,
    plan_detail,
    plan_summary,
    read_document,
    run_summary,
    write_document,
)
from orba.pm_schemas import (
    Page,
    PlanApprove,
    PlanCopy,
    PlanRead,
    PlanSummary,
    PlanUpdate,
    RunCreate,
    RunDetail,
    RunRead,
    attribute_edits,
    canonical,
    document_nodes,
)
from orba.pm_service import (
    APPROVERS,
    capability,
    check_session,
    expire_runs,
    generate,
    lock_project,
    phase,
)
from orba.security import DB, Identity, authorized_project, csrf_guard

router = APIRouter(prefix="/api/v1/projects/{project_id}", tags=["Product Manager"])
Limit = Annotated[int, Query(ge=1, le=50)]
Offset = Annotated[int, Query(ge=0)]


def model_provider(request: Request):
    """Production selects only Gemini. Tests may override this native dependency."""
    settings = request.app.state.settings
    return GeminiProductManagerProvider(settings) if settings.pm_configured else None


def detach(identity, db):
    actor, session = identity.user_id, identity.id
    db.close()  # Release the dependency's checked-out transaction before slow work.
    return actor, session


def get_plan(db, project_id, plan_id, *, lock=False):
    query = select(ProductPlan).where(
        ProductPlan.project_id == project_id, ProductPlan.id == plan_id
    )
    plan = db.scalar(query.with_for_update(read=lock == "read") if lock else query)
    if plan is None:
        raise HTTPException(404, "Product plan not found.")
    return plan


def safe_document(db, plan):
    try:
        document = read_document(db, plan)
        if content_hash(document) != plan.content_hash:
            raise ValueError("Saved document hash mismatch")
        return document
    except (ValidationError, ValueError):
        raise PMError(
            409,
            "plan_integrity_error",
            "The saved plan failed integrity validation. A local operator must inspect its records; it cannot be approved.",
        ) from None


@router.post("/pm-runs", response_model=RunRead, dependencies=[Depends(csrf_guard)])
def create_run(
    project_id: UUID,
    payload: RunCreate,
    request: Request,
    response: Response,
    identity: Identity,
    session: DB,
    provider: Annotated[ProductManagerModelProvider | None, Depends(model_provider)],
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
        raise PMError(
            409,
            value["error_category"] or "run_failed",
            "This request already ended without a product plan. Inspect it before explicitly starting a new request.",
            run_id=value["id"],
            diagnostic_id=value["diagnostic_id"],
        )
    response.status_code = (201 if created else 200) if value["status"] == "succeeded" else 202
    return value


@router.get("/pm-runs", response_model=Page[RunRead])
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
        expire_runs(db, project_id)
        query = select(ProductManagerRun).where(ProductManagerRun.project_id == project_id)
        if client_request_id:
            query = query.where(
                ProductManagerRun.client_request_id == client_request_id,
                ProductManagerRun.initiator_id == actor,
            )
        runs = db.scalars(
            query.order_by(ProductManagerRun.created_at.desc(), ProductManagerRun.id.desc())
            .limit(limit)
            .offset(offset)
            .with_for_update(read=True)
        ).all()
        # One bounded result lookup, not one query per history item.
        plans = (
            dict(
                db.execute(
                    select(ProductPlan.generating_run_id, ProductPlan.id).where(
                        ProductPlan.generating_run_id.in_([r.id for r in runs])
                    )
                ).all()
            )
            if runs
            else {}
        )
        items = [run_summary(db, run, plan_id=plans.get(run.id)) for run in runs]
        return {
            "items": items,
            "limit": limit,
            "offset": offset,
            "next_offset": offset + limit if len(items) == limit else None,
            "capability": capability(request.app.state.settings),
        }


@router.get("/pm-runs/{run_id}", response_model=RunDetail)
def get_run(project_id: UUID, run_id: UUID, request: Request, identity: Identity, session: DB):
    actor, _ = detach(identity, session)
    with phase(request.app.state.engine) as db:
        authorized_project(db, project_id, actor)
        expire_runs(db, project_id)
        run = db.scalar(
            select(ProductManagerRun)
            .where(ProductManagerRun.id == run_id, ProductManagerRun.project_id == project_id)
            .with_for_update(read=True)
        )
        if run is None:
            raise HTTPException(404, "Planning run not found.")
        return run_summary(db, run) | {"input_snapshot": run.input_snapshot}


@router.get("/pm-plans", response_model=Page[PlanSummary])
def list_plans(
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
        query = select(ProductPlan).where(ProductPlan.project_id == project_id)
        if copy_request_id:
            query = query.where(
                ProductPlan.copy_request_id == copy_request_id, ProductPlan.creator_id == actor
            )
        plans = db.scalars(
            query.order_by(ProductPlan.version.desc()).limit(limit).offset(offset)
        ).all()
        return {
            "items": [plan_summary(plan) for plan in plans],
            "limit": limit,
            "offset": offset,
            "next_offset": offset + limit if len(plans) == limit else None,
        }


@router.get("/pm-plans/{plan_id}", response_model=PlanRead)
def read_plan(project_id: UUID, plan_id: UUID, request: Request, identity: Identity, session: DB):
    actor, _ = detach(identity, session)
    with phase(request.app.state.engine) as db:
        authorized_project(db, project_id, actor)
        # Keep root revision and its relational graph coherent across the
        # bounded assembly queries. Editors lock this same root FOR UPDATE.
        plan = get_plan(db, project_id, plan_id, lock="read")
        safe_document(db, plan)
        return plan_detail(db, plan)


@router.put("/pm-plans/{plan_id}", response_model=PlanRead, dependencies=[Depends(csrf_guard)])
def update_plan(
    project_id: UUID,
    plan_id: UUID,
    payload: PlanUpdate,
    request: Request,
    identity: Identity,
    session: DB,
):
    actor, session_id = detach(identity, session)
    with phase(request.app.state.engine) as db:
        lock_project(db, project_id, actor)
        plan = get_plan(db, project_id, plan_id, lock=True)
        moment = check_session(db, session_id, actor)
        if plan.state != "draft" or plan.revision != payload.expected_revision:
            raise PMError(
                409,
                "plan_revision_conflict",
                "Only the exact saved draft revision can be edited. Your local changes should be kept while you inspect the latest version.",
            )
        old = safe_document(db, plan)
        try:
            document = attribute_edits(old, payload.document, actor, moment.isoformat())
        except (ValidationError, ValueError) as exc:
            raise PMError(
                422,
                "invalid_draft",
                "The draft failed validation. Correct the indicated fields.",
                details=validation_details(exc),
            ) from None
        write_document(db, plan, document)
        plan.revision += 1
        plan.editor_id, plan.updated_at = actor, moment
        db.flush()
        check_session(db, session_id, actor)
        value = plan_detail(db, plan)
    return value


@router.post(
    "/pm-plans/{plan_id}/approve", response_model=PlanRead, dependencies=[Depends(csrf_guard)]
)
def approve_plan(
    project_id: UUID,
    plan_id: UUID,
    payload: PlanApprove,
    request: Request,
    identity: Identity,
    session: DB,
):
    actor, session_id = detach(identity, session)
    with phase(request.app.state.engine) as db:
        lock_project(db, project_id, actor, APPROVERS)
        plan = get_plan(db, project_id, plan_id, lock=True)
        moment = check_session(db, session_id, actor)
        if plan.revision != payload.expected_revision or plan.version != payload.version:
            raise PMError(
                409,
                "plan_revision_conflict",
                "Approval must identify the exact saved plan version and revision.",
            )
        if plan.state == "approved":
            return plan_detail(db, plan)  # Idempotent confirmation of the same exact artifact.
        if plan.state != "draft":
            raise PMError(
                409,
                "plan_not_draft",
                "This historical version is immutable. Create a draft copy to propose corrections.",
            )
        document = safe_document(db, plan)
        if any(c.blocking and c.disposition == "unresolved" for c in document.confirmations):
            raise PMError(
                422,
                "unresolved_confirmations",
                "Resolve or explicitly defer every blocking confirmation with a reason before approval.",
            )
        if any(
            c.disposition != "unresolved" and (not c.actor_id or not c.decided_at)
            for c in document.confirmations
        ):
            raise PMError(
                422,
                "incomplete_plan",
                "Confirmation dispositions need a recorded human actor and timestamp before approval.",
            )
        if any(
            node.source.kind == "human" and not node.source.actor_id
            for _, node in document_nodes(document)
        ):
            raise PMError(
                422,
                "incomplete_plan",
                "Human-edited requirements need a recorded editor before approval.",
            )
        current = db.scalar(
            select(ProductPlan)
            .where(ProductPlan.project_id == project_id, ProductPlan.state == "approved")
            .with_for_update()
        )
        if current and current.version >= plan.version:
            raise PMError(
                409,
                "approval_version_conflict",
                "A newer agreement is already approved. Review that version before proposing another draft.",
            )
        if current:
            current.state = "superseded"
            db.flush()  # Release the unique current-approval slot atomically in this transaction.
        plan.state, plan.approved_by, plan.approved_at, plan.updated_at = (
            "approved",
            actor,
            moment,
            moment,
        )
        db.flush()
        check_session(db, session_id, actor)
        value = plan_detail(db, plan)
    return value


@router.post(
    "/pm-plans/{plan_id}/draft", response_model=PlanRead, dependencies=[Depends(csrf_guard)]
)
def copy_plan(
    project_id: UUID,
    plan_id: UUID,
    payload: PlanCopy,
    request: Request,
    response: Response,
    identity: Identity,
    session: DB,
):
    actor, session_id = detach(identity, session)
    request_hash = hashlib.sha256(
        canonical({"source_plan_id": str(plan_id), **payload.model_dump(mode="json")}).encode()
    ).hexdigest()
    with phase(request.app.state.engine) as db:
        lock_project(db, project_id, actor)
        source = get_plan(db, project_id, plan_id, lock=True)
        check_session(db, session_id, actor)
        existing = db.scalar(
            select(ProductPlan).where(
                ProductPlan.project_id == project_id,
                ProductPlan.creator_id == actor,
                ProductPlan.copy_request_id == payload.client_request_id,
            )
        )
        if existing:
            if existing.copy_request_hash != request_hash:
                raise PMError(
                    409,
                    "idempotency_conflict",
                    "This copy request ID belongs to different source input.",
                )
            response.status_code = 200
            return plan_detail(db, existing)
        if source.revision != payload.expected_revision or source.version != payload.version:
            raise PMError(
                409,
                "plan_revision_conflict",
                "The source revision changed. Select its saved version again before copying.",
            )
        document = safe_document(db, source)
        plan = create_plan(
            db,
            project_id,
            actor,
            document,
            source=source,
            copy_id=payload.client_request_id,
            copy_hash=request_hash,
        )
        response.status_code = 201
        check_session(db, session_id, actor)
        value = plan_detail(db, plan)
    return value

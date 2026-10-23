"""Authenticated deterministic control-plane API. No task execution mutations."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy import select

from orba.architect_models import ArchitectureVersion
from orba.architect_repository import summary as architecture_summary
from orba.architect_schemas import ArchitectureSummary
from orba.orchestration_models import OrchestrationEvent, OrchestrationRun
from orba.orchestration_schemas import (
    EventRead,
    EventsRead,
    GraphRead,
    RunCancel,
    RunCreate,
    RunDetail,
    RunRead,
    TasksRead,
)
from orba.orchestration_service import (
    create_run,
    detail,
    get_run,
    materialized,
    snapshot_source,
    summary,
    transition,
)
from orba.pm import detach
from orba.pm_schemas import Page
from orba.pm_service import check_session, lock_project, phase
from orba.security import DB, Identity, authorized_project, csrf_guard

router = APIRouter(
    prefix="/api/v1/projects/{project_id}/orchestration-runs", tags=["Orchestration"]
)


@router.post("", response_model=RunDetail, dependencies=[Depends(csrf_guard)])
def create(
    project_id: UUID,
    payload: RunCreate,
    request: Request,
    response: Response,
    identity: Identity,
    session: DB,
):
    actor, session_id = detach(identity, session)
    result, created = create_run(request.app.state.engine, project_id, actor, session_id, payload)
    response.status_code = 201 if created else 200
    return result


@router.get("/source", response_model=ArchitectureSummary | None)
def approved_architecture(project_id: UUID, request: Request, identity: Identity, session: DB):
    actor, _ = detach(identity, session)
    with phase(request.app.state.engine) as db:
        project = authorized_project(db, project_id, actor)
        artifact = db.scalar(
            select(ArchitectureVersion)
            .where(
                ArchitectureVersion.project_id == project_id,
                ArchitectureVersion.state == "approved",
            )
            .with_for_update(read=True)
        )
        if artifact is None:
            return None
        snapshot_source(db, project, artifact)
        return architecture_summary(artifact)


@router.get("", response_model=Page[RunRead])
def history(
    project_id: UUID,
    request: Request,
    identity: Identity,
    session: DB,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    client_request_id: UUID | None = None,
):
    actor, _ = detach(identity, session)
    with phase(request.app.state.engine) as db:
        authorized_project(db, project_id, actor)
        query = select(OrchestrationRun).where(OrchestrationRun.project_id == project_id)
        if client_request_id:
            query = query.where(
                OrchestrationRun.creator_id == actor,
                OrchestrationRun.client_request_id == client_request_id,
            )
        rows = db.scalars(
            query.order_by(OrchestrationRun.created_at.desc(), OrchestrationRun.id.desc())
            .offset(offset)
            .limit(limit + 1)
        ).all()
        return {
            "items": [summary(row) for row in rows[:limit]],
            "limit": limit,
            "offset": offset,
            "next_offset": offset + limit if len(rows) > limit else None,
        }


@router.get("/{run_id}", response_model=RunDetail)
def read(project_id: UUID, run_id: UUID, request: Request, identity: Identity, session: DB):
    actor, _ = detach(identity, session)
    with phase(request.app.state.engine) as db:
        authorized_project(db, project_id, actor)
        return detail(db, get_run(db, project_id, run_id))


@router.get("/{run_id}/tasks", response_model=TasksRead)
def tasks(project_id: UUID, run_id: UUID, request: Request, identity: Identity, session: DB):
    actor, _ = detach(identity, session)
    with phase(request.app.state.engine) as db:
        authorized_project(db, project_id, actor)
        run = get_run(db, project_id, run_id)
        result = detail(db, run)
        return {"run_id": run.id, "snapshot_hash": run.snapshot_hash, "items": result["tasks"]}


@router.get("/{run_id}/graph", response_model=GraphRead)
def graph(project_id: UUID, run_id: UUID, request: Request, identity: Identity, session: DB):
    actor, _ = detach(identity, session)
    with phase(request.app.state.engine) as db:
        authorized_project(db, project_id, actor)
        _, result = materialized(db, get_run(db, project_id, run_id))
        return result


@router.get("/{run_id}/events", response_model=EventsRead)
def events(
    project_id: UUID,
    run_id: UUID,
    request: Request,
    identity: Identity,
    session: DB,
    after: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
):
    actor, _ = detach(identity, session)
    with phase(request.app.state.engine) as db:
        authorized_project(db, project_id, actor)
        get_run(db, project_id, run_id)
        rows = db.scalars(
            select(OrchestrationEvent)
            .where(OrchestrationEvent.run_id == run_id, OrchestrationEvent.sequence > after)
            .order_by(OrchestrationEvent.sequence)
            .limit(limit + 1)
        ).all()
        return {
            "run_id": run_id,
            "items": [
                EventRead.model_validate(row, from_attributes=True).model_dump()
                for row in rows[:limit]
            ],
            "next_sequence": rows[limit - 1].sequence if len(rows) > limit else None,
        }


@router.post("/{run_id}/cancel", response_model=RunDetail, dependencies=[Depends(csrf_guard)])
def cancel(
    project_id: UUID,
    run_id: UUID,
    payload: RunCancel,
    request: Request,
    identity: Identity,
    session: DB,
):
    actor, session_id = detach(identity, session)
    with phase(request.app.state.engine) as db:
        lock_project(db, project_id, actor)
        run = get_run(db, project_id, run_id, lock=True)
        moment = check_session(db, session_id, actor)
        transition(db, run, "cancelled", actor, moment, expected_revision=payload.expected_revision)
        result = detail(db, run)
        check_session(db, session_id, actor)
    return result

"""Worker Bearer APIs are separate from ambient user cookies; no completion route."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Request, Response

from orba.orchestration_service import get_run
from orba.pm import detach
from orba.pm_service import phase
from orba.scheduler_schemas import (
    Claim,
    HandoffRead,
    Heartbeat,
    LeaseOperation,
    SchedulerRead,
    WorkerRead,
)
from orba.scheduler_service import (
    claim,
    claim_recovery,
    inspect_scheduler,
    lease_operation,
    worker_me,
)
from orba.security import DB, Identity, authorized_project

router = APIRouter(tags=["Worker protocol"])


def bearer(authorization):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            401, "Use a dedicated worker Bearer credential. Browser sessions cannot claim work."
        )
    return authorization[7:]


@router.get("/api/v1/workers/me", response_model=WorkerRead)
def me(request: Request, authorization: Annotated[str | None, Header()] = None):
    return worker_me(
        request.app.state.engine,
        request.app.state.settings.scheduler_policy(),
        bearer(authorization),
    )


@router.post("/api/v1/workers/claim", response_model=HandoffRead | None)
def acquire(
    payload: Claim,
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
):
    result, created = claim(
        request.app.state.engine,
        request.app.state.settings.scheduler_policy(),
        bearer(authorization),
        payload,
    )
    if result is None:
        return Response(status_code=204)
    response.status_code = 201 if created else 200
    return result


@router.get("/api/v1/workers/claims/{request_id}", response_model=HandoffRead)
def recover_claim(
    request_id: UUID, request: Request, authorization: Annotated[str | None, Header()] = None
):
    return claim_recovery(
        request.app.state.engine,
        request.app.state.settings.scheduler_policy(),
        bearer(authorization),
        request_id,
    )


@router.post("/api/v1/workers/leases/{lease_id}/acknowledge", response_model=HandoffRead)
def acknowledge(
    lease_id: UUID,
    payload: LeaseOperation,
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
):
    return lease_operation(
        request.app.state.engine,
        request.app.state.settings.scheduler_policy(),
        bearer(authorization),
        lease_id,
        payload,
        "acknowledge",
    )


@router.post("/api/v1/workers/leases/{lease_id}/heartbeat", response_model=HandoffRead)
def heartbeat(
    lease_id: UUID,
    payload: Heartbeat,
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
):
    return lease_operation(
        request.app.state.engine,
        request.app.state.settings.scheduler_policy(),
        bearer(authorization),
        lease_id,
        payload,
        "heartbeat",
    )


@router.post("/api/v1/workers/leases/{lease_id}/release", response_model=HandoffRead)
def release(
    lease_id: UUID,
    payload: LeaseOperation,
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
):
    return lease_operation(
        request.app.state.engine,
        request.app.state.settings.scheduler_policy(),
        bearer(authorization),
        lease_id,
        payload,
        "release",
    )


@router.get(
    "/api/v1/projects/{project_id}/orchestration-runs/{run_id}/scheduler",
    response_model=SchedulerRead,
)
def status(project_id: UUID, run_id: UUID, request: Request, identity: Identity, session: DB):
    actor, _ = detach(identity, session)
    with phase(request.app.state.engine) as db:
        authorized_project(db, project_id, actor)
        return inspect_scheduler(db, get_run(db, project_id, run_id))

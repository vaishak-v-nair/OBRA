import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException as StarletteHTTPException

from orba.architect import router as architect_router
from orba.architect_service import expire_architect_runs
from orba.auth import router as auth_router
from orba.config import Settings
from orba.db import get_session, make_engine
from orba.models import Project
from orba.orchestration import router as orchestration_router
from orba.pm import router as pm_router
from orba.pm_errors import PMError
from orba.pm_middleware import PMBodyLimitMiddleware
from orba.pm_service import expire_runs, phase
from orba.schemas import ProjectCreate, ProjectRead, ProjectUpdate
from orba.security import DB, Identity, authorized_project, csrf_guard, membership, require_role
from orba.workspaces import router as workspace_router

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings()
    engine = make_engine(config.database_url)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        stop = asyncio.Event()

        def reconcile():
            try:
                with phase(engine) as db:
                    expire_runs(db)
                    expire_architect_runs(db)
            except SQLAlchemyError as exc:
                logger.error("PM lease reconciliation unavailable (%s)", type(exc).__name__)

        async def monitor():
            while not stop.is_set():
                await run_in_threadpool(reconcile)
                try:
                    await asyncio.wait_for(stop.wait(), timeout=5)
                except TimeoutError:
                    pass

        task = asyncio.create_task(monitor())
        try:
            yield
        finally:
            stop.set()
            await task
            engine.dispose()

    app = FastAPI(title="ORBA API", version="0.1.0", lifespan=lifespan)
    app.state.engine = engine
    app.state.settings = config
    app.include_router(auth_router)
    app.include_router(workspace_router)
    app.include_router(pm_router)
    app.include_router(architect_router)
    app.include_router(orchestration_router)
    app.add_middleware(PMBodyLimitMiddleware)

    @app.exception_handler(PMError)
    async def pm_error(request: Request, exc: PMError):
        logger.info(
            "PM failure code=%s run_id=%s diagnostic_id=%s", exc.code, exc.run_id, exc.diagnostic_id
        )
        return JSONResponse(
            status_code=exc.status,
            content=exc.body(),
            headers={"Retry-After": str(exc.retry_after)} if exc.retry_after else None,
        )

    @app.middleware("http")
    async def private_responses(request: Request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        details = [
            {"field": ".".join(map(str, e["loc"])), "message": e["msg"]} for e in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Check the submitted fields.",
                    "details": details,
                }
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            headers=exc.headers,
            content={
                "error": {
                    "code": "not_found" if exc.status_code == 404 else "http_error",
                    "message": str(exc.detail),
                }
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error(request: Request, exc: SQLAlchemyError):
        logger.error("Database operation failed (%s)", type(exc).__name__)
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": "database_unavailable",
                    "message": "Database unavailable. Try again shortly.",
                }
            },
        )

    @app.get("/health/live")
    def live():
        return {"status": "alive"}

    @app.get("/health/ready")
    def ready(session: Annotated[Session, Depends(get_session)]):
        # Check both connectivity and the migrated schema required to serve projects.
        session.execute(
            text(
                "SELECT p.id,p.title,p.description,p.status,p.created_at,p.updated_at,p.workspace_id,p.creator_id,s.token_hash,u.email,w.is_legacy,m.role,i.token_hash,a.key,r.deadline_at,r.status,pl.content_hash,pl.revision,e.plan_id,st.epic_id,c.story_id FROM projects p CROSS JOIN sessions s CROSS JOIN users u CROSS JOIN workspaces w CROSS JOIN workspace_members m CROSS JOIN workspace_invitations i CROSS JOIN login_attempts a CROSS JOIN product_manager_runs r CROSS JOIN product_plans pl CROSS JOIN product_epics e CROSS JOIN product_stories st CROSS JOIN product_acceptance_criteria c LIMIT 0"
            )
        )
        session.execute(
            text(
                "SELECT ar.source_plan_id,av.revision,ac.architecture_id,t.planning_state,d.prerequisite_id,tr.story_id FROM architect_runs ar CROSS JOIN architecture_versions av CROSS JOIN architecture_components ac CROSS JOIN engineering_tasks t CROSS JOIN task_dependencies d CROSS JOIN requirement_traces tr LIMIT 0"
            )
        )
        session.execute(
            text(
                "SELECT r.snapshot_hash,t.execution_status,d.prerequisite_id,e.sequence FROM orchestration_runs r CROSS JOIN orchestration_tasks t CROSS JOIN orchestration_dependencies d CROSS JOIN orchestration_events e LIMIT 0"
            )
        )
        return {"status": "ready"}

    @app.post(
        "/api/v1/projects",
        response_model=ProjectRead,
        status_code=201,
        dependencies=[Depends(csrf_guard)],
    )
    def create_project(payload: ProjectCreate, identity: Identity, session: DB):
        _, caller = membership(session, payload.workspace_id, identity.user_id, lock=True)
        require_role(caller, {"owner", "admin", "member"})
        project = Project(**payload.model_dump(), creator_id=identity.user_id)
        session.add(project)
        session.commit()
        session.refresh(project)
        return project

    @app.get("/api/v1/projects", response_model=list[ProjectRead])
    def list_projects(
        identity: Identity,
        session: DB,
        workspace_id: UUID,
        limit: Annotated[int, Query(ge=1, le=100)] = 50,
        offset: Annotated[int, Query(ge=0)] = 0,
    ):
        membership(session, workspace_id, identity.user_id)
        return session.scalars(
            select(Project)
            .where(Project.workspace_id == workspace_id)
            .order_by(Project.created_at.desc(), Project.id.desc())
            .offset(offset)
            .limit(limit)
        ).all()

    @app.get("/api/v1/projects/{project_id}", response_model=ProjectRead)
    def get_project(project_id: UUID, identity: Identity, session: DB):
        return authorized_project(session, project_id, identity.user_id)

    @app.patch(
        "/api/v1/projects/{project_id}",
        response_model=ProjectRead,
        dependencies=[Depends(csrf_guard)],
    )
    def update_project(project_id: UUID, payload: ProjectUpdate, identity: Identity, session: DB):
        project = get_project(project_id, identity, session)
        _, caller = membership(session, project.workspace_id, identity.user_id, lock=True)
        require_role(caller, {"owner", "admin", "member"})
        project.title, project.description = payload.title, payload.description
        session.commit()
        session.refresh(project)
        return project

    return app


app = create_app()

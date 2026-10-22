"""One bounded PM request lifecycle. There is no background execution or takeover.

reserve pending(commit) -> running(commit confirmed) -> ONE real provider call
    -> validate -> original authority/lease -> full graph + success(ONE commit)
failure -> terminal record only; uncertain commit -> GET reconciliation, never replay execution.
"""

import asyncio
import hashlib
from contextlib import contextmanager
from datetime import timedelta
from time import monotonic
from uuid import uuid4

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from orba.models import AuthSession, Project, User
from orba.pm_errors import PMError, validation_details
from orba.pm_models import ProductManagerRun, ProductPlan
from orba.pm_provider import (
    INPUT_LIMIT_MESSAGE,
    INVALID_UNICODE_MESSAGE,
    PROMPT_HASH,
    PROMPT_VERSION,
    PROVIDER,
    GeminiProductManagerProvider,
    ProviderFailure,
    request_metrics,
)
from orba.pm_repository import create_plan, read_document, run_summary
from orba.pm_schemas import (
    HASH_VERSION,
    ProductDocument,
    canonical,
    document_nodes,
    node_text,
    validate_generated,
)
from orba.pm_timing import RunTiming
from orba.pm_timing import logger as timing_logger
from orba.security import authorized_project, membership, require_role

AUTHORS = {"owner", "admin", "member"}
APPROVERS = {"owner", "admin"}
ACTIVE = {"pending", "running"}


@contextmanager
def phase(engine):
    with Session(engine) as db, db.begin():
        db.execute(text("SET LOCAL lock_timeout='1s'"))
        db.execute(text("SET LOCAL statement_timeout='2s'"))
        db.execute(text("SET LOCAL transaction_timeout='10s'"))
        yield db


def db_now(db):
    return db.scalar(select(func.clock_timestamp()))


def lock_project(db, project_id, actor_id, roles=AUTHORS):
    visible = authorized_project(db, project_id, actor_id)
    _, member = membership(db, visible.workspace_id, actor_id, lock=True)
    require_role(member, roles)
    project = db.scalar(select(Project).where(Project.id == project_id).with_for_update())
    return project


def check_session(db, session_id, actor_id):
    session = db.scalar(select(AuthSession).where(AuthSession.id == session_id).with_for_update())
    user = db.scalar(select(User).where(User.id == actor_id).with_for_update())
    moment = db_now(db)  # AFTER lock waiting; transaction-start now() is insufficient.
    if (
        not session
        or not user
        or session.user_id != actor_id
        or session.revoked_at
        or session.expires_at <= moment
        or user.status != "active"
    ):
        raise HTTPException(401, "Your initiating session expired or was revoked. Sign in again.")
    return moment


def expire_runs(db, project_id=None, *, model=ProductManagerRun):
    query = select(model).where(
        model.status.in_(ACTIVE),
        model.deadline_at <= func.clock_timestamp(),
    )
    if project_id is not None:
        query = query.where(model.project_id == project_id)
    for run in db.scalars(
        query.order_by(model.deadline_at).limit(100).with_for_update(skip_locked=True)
    ):
        run.status, run.completed_at = "interrupted", db_now(db)
        run.error_category, run.diagnostic_id = "interrupted", uuid4()
        run.diagnostic = dict(run.diagnostic or {}) | {"exception_type": "ExpiredExecutionLease"}
        timing_logger.info(
            "%s_timing run_id=%s stage=lease_expiration_detected attempt=1 "
            "proposed_state=interrupted error_category=interrupted",
            "pm" if model is ProductManagerRun else "architect",
            run.id,
        )


def capability(config):
    return {
        "provider": PROVIDER,
        "configured": config.pm_configured,
        "model": config.pm_model,
        "timeout_seconds": config.pm_timeout_seconds,
        "max_output_tokens": config.pm_max_output_tokens,
        "setup_message": None
        if config.pm_configured
        else "Set GEMINI_API_KEY and ORBA_PM_MODEL in the root .env, then restart the API. Configuration does not prove provider access.",
    }


def _snapshot(db, project, payload, config):
    result = {
        "title": project.title,
        "description": project.description,
        "brief": payload.brief,
        "instructions": payload.instructions,
        "context_nodes": {},
    }
    if payload.context_plan_id:
        context = db.scalar(
            select(ProductPlan).where(
                ProductPlan.id == payload.context_plan_id, ProductPlan.project_id == project.id
            )
        )
        if context is None:
            raise HTTPException(404, "Product plan not found.")
        if context.revision != payload.context_revision:
            raise PMError(
                409,
                "context_conflict",
                "The selected context revision changed. Choose its saved revision again.",
            )
        document = read_document(db, context)
        for parent, node in document_nodes(document):
            value = {
                "text": node_text(node),
                "parent": parent,
                "origin": node.source.inherited_kind or node.source.kind,
            }
            if hasattr(node, "disposition"):
                value |= {
                    "disposition": node.disposition,
                    "reason": node.reason,
                    "blocking": node.blocking,
                    "active": node.active,
                    "actor_id": node.actor_id,
                    "decided_at": node.decided_at,
                }
            result["context_nodes"][node.key] = value
        result["context_plan"] = {
            "id": str(context.id),
            "revision": context.revision,
            "version": context.version,
            "hash": context.content_hash,
        }
        if len(canonical(result["context_nodes"])) > 20000:
            raise PMError(
                422,
                "context_too_large",
                "The selected plan exceeds the bounded context limit. Use a concise brief without prior-plan context.",
            )
    if len(canonical(result)) > 48000:
        raise PMError(422, "input_too_large", INPUT_LIMIT_MESSAGE)
    if request_metrics(result)["input_bytes"] > config.pm_max_input_bytes:
        raise PMError(422, "input_too_large", INPUT_LIMIT_MESSAGE)
    return result


def reserve(engine, config, project_id, actor_id, session_id, payload):
    try:
        request_hash = hashlib.sha256(
            canonical(payload.model_dump(mode="json")).encode("utf-8")
        ).hexdigest()
    except UnicodeEncodeError:
        raise PMError(422, "validation_error", INVALID_UNICODE_MESSAGE) from None
    executor_id = uuid4()
    with phase(engine) as db:
        # Global admission precedes workspace locks, always, and is transaction-scoped.
        db.execute(text("SELECT pg_advisory_xact_lock(1330790977,3)"))
        project = lock_project(db, project_id, actor_id)
        expire_runs(db, project_id)
        moment = check_session(db, session_id, actor_id)
        existing = db.scalar(
            select(ProductManagerRun).where(
                ProductManagerRun.project_id == project_id,
                ProductManagerRun.initiator_id == actor_id,
                ProductManagerRun.client_request_id == payload.client_request_id,
            )
        )
        if existing:
            if existing.hash_version != HASH_VERSION or existing.request_hash != request_hash:
                raise PMError(
                    409,
                    "idempotency_conflict",
                    "This request ID belongs to different input. Check its run or explicitly start a new request.",
                    run_id=existing.id,
                )
            return existing.id, None, None
        active = db.scalar(
            select(ProductManagerRun.id).where(
                ProductManagerRun.project_id == project_id, ProductManagerRun.status.in_(ACTIVE)
            )
        )
        if active:
            raise PMError(
                409,
                "project_generation_active",
                "This project already has an active planning request. Your new request was not admitted. Check status.",
                run_id=active,
            )
        from orba.planning_admission import check_limits

        check_limits(db, config, actor_id, moment)
        snapshot = _snapshot(db, project, payload, config)
        run = ProductManagerRun(
            id=uuid4(),
            project_id=project_id,
            workspace_id=project.workspace_id,
            initiator_id=actor_id,
            initiating_session_id=session_id,
            executor_id=executor_id,
            client_request_id=payload.client_request_id,
            request_hash=request_hash,
            snapshot_hash=hashlib.sha256(canonical(snapshot).encode()).hexdigest(),
            hash_version=HASH_VERSION,
            input_snapshot=snapshot,
            status="pending",
            provider=PROVIDER,
            requested_model=config.pm_model,
            prompt_version=PROMPT_VERSION,
            prompt_hash=PROMPT_HASH,
            diagnostic={
                "generation_configuration": {
                    "thinking_level": config.pm_thinking_level,
                    "max_input_bytes": config.pm_max_input_bytes,
                    "max_output_tokens": config.pm_max_output_tokens,
                    **request_metrics(snapshot),
                }
            },
            deadline_at=moment + timedelta(seconds=20),
        )
        db.add(run)
        db.flush()
        run_id = run.id
    # A commit exception never reaches here. No dispatch after uncertain reservation.
    return run_id, executor_id, snapshot


def mark_running(
    engine, config, run_id, executor_id, *, model=ProductManagerRun, validate_source=None
):
    with phase(engine) as db:
        initial = db.get(model, run_id)
        project = lock_project(db, initial.project_id, initial.initiator_id)
        run = db.scalar(select(model).where(model.id == run_id).with_for_update())
        moment = check_session(db, run.initiating_session_id, run.initiator_id)
        if (
            run.executor_id != executor_id
            or run.status != "pending"
            or run.deadline_at <= moment
            or run.workspace_id != project.workspace_id
        ):
            raise PMError(
                409,
                "run_interrupted",
                "This execution lease is no longer available. Check the run before starting again.",
                run_id=run_id,
            )
        if validate_source is not None:
            validate_source(db, run)
        run.status, run.started_at = "running", moment
        run.deadline_at = moment + timedelta(seconds=config.pm_timeout_seconds + 45)


def _metadata(run, result):
    if result:
        run.returned_model, run.provider_response_id, run.provider_request_id = (
            result.model,
            result.response_id,
            result.request_id,
        )
        run.usage = result.usage


def record_failure(
    engine, run_id, category, diagnostic, result=None, status="failed", *, model=ProductManagerRun
):
    failure_started = monotonic()
    try:
        with phase(engine) as db:
            run = db.scalar(select(model).where(model.id == run_id).with_for_update())
            if run is None:
                raise PMError(
                    503,
                    "run_outcome_unknown",
                    "The execution record could not be confirmed.",
                    run_id=run_id,
                )
            if run.status in ACTIVE:
                moment = db_now(db)
                run.status, run.completed_at = (
                    "interrupted" if run.deadline_at <= moment else status,
                    moment,
                )
                run.error_category, run.diagnostic_id, run.diagnostic = (
                    category,
                    uuid4(),
                    dict(run.diagnostic or {}) | diagnostic,
                )
            if run.status != "succeeded" and result is not None and run.usage is None:
                # Late genuine metadata can enrich a terminal interruption; its status
                # and completion evidence remain unchanged. It never creates a plan.
                _metadata(run, result)
            diagnostic_id, final_state = run.diagnostic_id, run.status
        timing_logger.info(
            "%s_timing run_id=%s stage=failure_commit_acknowledged stage_duration_ms=%.3f attempt=1 "
            "final_state=%s error_category=%s provider_http_status=%s",
            "pm" if model is ProductManagerRun else "architect",
            run_id,
            max(0, monotonic() - failure_started) * 1000,
            final_state,
            category,
            diagnostic.get("provider_http_status", "-"),
        )
        return diagnostic_id
    except SQLAlchemyError:
        raise PMError(
            503,
            "run_outcome_unknown",
            "The failure record could not be saved. Check this run after the database reconnects; its outcome is unconfirmed.",
            run_id=run_id,
        ) from None


def generate(
    engine, config, project_id, actor_id, session_id, payload, *, provider=None, started=None
):
    started = started if started is not None else monotonic()
    timing = RunTiming()
    try:
        with timing.measure("admission_transaction"):
            run_id, executor, snapshot = reserve(
                engine, config, project_id, actor_id, session_id, payload
            )
        timing.run_id = run_id
        timing.event("admission_commit_acknowledged", "pending" if executor else "replay")
    except SQLAlchemyError:
        raise PMError(
            503,
            "run_outcome_unknown",
            "Planning admission could not be confirmed. Check status using this request ID; do not submit another request automatically.",
        ) from None
    if executor is None:
        with phase(engine) as db:
            run = db.get(ProductManagerRun, run_id)
            return run_summary(db, run), False
    result = None
    try:
        if not config.pm_configured and provider is None:
            raise ProviderFailure("pm_not_configured", capability(config)["setup_message"], 503)
        with timing.measure("running_transaction"):
            mark_running(engine, config, run_id, executor)  # Commit BEFORE dispatch.
        timing.event("running_commit_acknowledged", "running")
    except SQLAlchemyError:
        raise PMError(
            503,
            "run_outcome_unknown",
            "The execution start could not be confirmed. No provider call was dispatched. Check its status; replay does not resume it.",
            run_id=run_id,
        ) from None
    except (HTTPException, PMError) as exc:
        diagnostic = record_failure(
            engine,
            run_id,
            "authorization_changed",
            timing.diagnostic({"exception_type": type(exc).__name__}),
        )
        raise PMError(
            getattr(exc, "status_code", 409),
            "authorization_changed",
            "Planning authority or execution lease changed before dispatch.",
            run_id=run_id,
            diagnostic_id=diagnostic,
        ) from None
    except ProviderFailure as exc:
        diagnostic = record_failure(engine, run_id, exc.category, timing.diagnostic(exc.diagnostic))
        raise PMError(
            exc.status, exc.category, exc.message, run_id=run_id, diagnostic_id=diagnostic
        ) from None
    try:
        if monotonic() - started > 60:
            raise ProviderFailure(
                "run_interrupted",
                "Planning startup exceeded its bounded budget. Start a new request explicitly.",
            )
        with timing.measure("provider_call"):
            result = asyncio.run(
                (provider or GeminiProductManagerProvider(config)).generate(snapshot)
            )
        timing.event("provider_response_received", "running")
        with timing.measure("validation"):
            document = validate_generated(
                ProductDocument.model_validate_json(result.output), snapshot
            )
        timing.event("output_validated", "running")
    except ProviderFailure as exc:
        diagnostic = record_failure(
            engine, run_id, exc.category, timing.diagnostic(exc.diagnostic), exc.result
        )
        raise PMError(
            exc.status, exc.category, exc.message, run_id=run_id, diagnostic_id=diagnostic
        ) from None
    except (ValidationError, ValueError) as exc:
        diagnostic = record_failure(
            engine,
            run_id,
            "invalid_model_response",
            timing.diagnostic(
                {
                    "exception_type": type(exc).__name__,
                    "validation": [
                        {"field": d["field"], "type": d["type"]} for d in validation_details(exc)
                    ],
                }
            ),
            result,
        )
        raise PMError(
            502,
            "invalid_model_response",
            "The model response failed the product-document contract. No draft was saved.",
            run_id=run_id,
            diagnostic_id=diagnostic,
        ) from None
    except (asyncio.CancelledError, KeyboardInterrupt):
        record_failure(
            engine,
            run_id,
            "interrupted",
            timing.diagnostic({"exception_type": "ExecutionCancelled"}),
            result,
            "interrupted",
        )
        raise
    except (RuntimeError, TypeError, AttributeError, OverflowError) as exc:
        diagnostic = record_failure(
            engine,
            run_id,
            "provider_request_failed",
            timing.diagnostic({"exception_type": type(exc).__name__}),
            result,
        )
        raise PMError(
            502,
            "provider_request_failed",
            "The model request could not complete. Check configuration and the run reference.",
            run_id=run_id,
            diagnostic_id=diagnostic,
        ) from None
    try:
        with timing.measure("persistence_transaction"), phase(engine) as db:
            project = lock_project(db, project_id, actor_id)
            run = db.scalar(
                select(ProductManagerRun).where(ProductManagerRun.id == run_id).with_for_update()
            )
            moment = check_session(db, session_id, actor_id)
            if (
                run.status != "running"
                or run.executor_id != executor
                or run.deadline_at <= moment
                or monotonic() - started > 285
                or run.workspace_id != project.workspace_id
            ):
                raise PMError(
                    409,
                    "run_interrupted",
                    "The execution lease expired. The response was not published as a plan.",
                    run_id=run_id,
                )
            with timing.measure("persistence_flush"):
                create_plan(db, project_id, actor_id, document, run_id=run.id)
                db.flush()
            _metadata(run, result)
            # Time-based session expiry can advance during graph writes even
            # while logout/revocation is serialized by the locked session row.
            moment = check_session(db, session_id, actor_id)
            run.status, run.completed_at = "succeeded", moment
            if run.deadline_at <= run.completed_at:
                raise PMError(
                    409,
                    "run_interrupted",
                    "The plan could not be committed within its execution lease.",
                    run_id=run_id,
                )
            run.diagnostic = dict(run.diagnostic or {}) | timing.diagnostic(
                {"dispatch_phase": "validated_publication"}
            )
        timing.event("publication_commit_acknowledged", "succeeded")
        with phase(engine) as db:
            run = db.get(ProductManagerRun, run_id)
            return run_summary(db, run), True
    except (HTTPException, PMError) as exc:
        category = "authorization_changed" if isinstance(exc, HTTPException) else "interrupted"
        diagnostic = record_failure(
            engine,
            run_id,
            category,
            timing.diagnostic({"exception_type": type(exc).__name__}),
            result,
            "failed" if category == "authorization_changed" else "interrupted",
        )
        raise PMError(
            getattr(exc, "status_code", 409),
            category,
            "The plan was not published because session authority or execution deadline changed.",
            run_id=run_id,
            diagnostic_id=diagnostic,
        ) from None
    except SQLAlchemyError:
        # Final COMMIT may have succeeded even if its acknowledgement was lost.
        # Never replace that terminal success with failed. A fresh read is evidence.
        try:
            with phase(engine) as db:
                run = db.get(ProductManagerRun, run_id)
                if run and run.status == "succeeded":
                    timing.event("publication_reconciled_by_read", "succeeded")
                    return run_summary(db, run), True
        except SQLAlchemyError:
            pass
        raise PMError(
            503,
            "run_outcome_unknown",
            "Plan persistence could not be confirmed. Check this run before any new generation.",
            run_id=run_id,
        ) from None

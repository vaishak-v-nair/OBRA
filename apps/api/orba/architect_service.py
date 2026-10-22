"""Approved PRD -> one bounded request -> validated atomic proposal; no execution."""

import asyncio
import hashlib
from datetime import timedelta
from time import monotonic
from uuid import uuid4

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from orba.architect_models import ArchitectRun
from orba.architect_provider import (
    PROMPT_HASH,
    PROMPT_VERSION,
    GeminiArchitectProvider,
    request_metrics,
)
from orba.architect_repository import (
    ArchitectError,
    create_architecture,
    run_summary,
    source_document,
)
from orba.architect_schemas import ArchitectureDocument
from orba.architect_traceability import coverage
from orba.planning_admission import check_limits
from orba.pm_errors import PMError
from orba.pm_models import ProductPlan
from orba.pm_provider import PROVIDER, ProviderFailure
from orba.pm_repository import content_hash, read_document
from orba.pm_schemas import canonical
from orba.pm_service import (
    ACTIVE,
    _metadata,
    check_session,
    expire_runs,
    lock_project,
    mark_running,
    phase,
    record_failure,
)
from orba.pm_timing import RunTiming


def capability(config):
    selected = config.architect_settings()
    return {
        "provider": PROVIDER,
        "configured": selected.pm_configured,
        "model": selected.pm_model,
        "timeout_seconds": selected.pm_timeout_seconds,
        "max_output_tokens": selected.pm_max_output_tokens,
        "setup_message": None
        if selected.pm_configured
        else "Set ORBA_ARCHITECT_MODEL and a server-side Gemini credential, then restart the API. Setup does not prove live generation works.",
    }


def expire_architect_runs(db, project_id=None):
    expire_runs(db, project_id, model=ArchitectRun)


def reserve(engine, config, project_id, actor_id, session_id, payload):
    try:
        request_hash = hashlib.sha256(
            canonical(payload.model_dump(mode="json")).encode("utf-8")
        ).hexdigest()
    except UnicodeEncodeError:
        raise ArchitectError(
            422,
            "validation_error",
            "Architect input must contain valid Unicode. No generation was started.",
        ) from None
    with phase(engine) as db:
        db.execute(text("SELECT pg_advisory_xact_lock(1330790977,3)"))
        project = lock_project(db, project_id, actor_id)
        expire_architect_runs(db, project_id)
        moment = check_session(db, session_id, actor_id)
        existing = db.scalar(
            select(ArchitectRun).where(
                ArchitectRun.project_id == project_id,
                ArchitectRun.initiator_id == actor_id,
                ArchitectRun.client_request_id == payload.client_request_id,
            )
        )
        # Historical exact replay is resolved before every new-source/config/cap check.
        if existing:
            if existing.request_hash != request_hash:
                raise ArchitectError(
                    409,
                    "idempotency_conflict",
                    "This request ID belongs to different input. Inspect its original run.",
                    run_id=existing.id,
                )
            return existing.id, None, None
        active = db.scalar(
            select(ArchitectRun.id).where(
                ArchitectRun.project_id == project_id, ArchitectRun.status.in_(ACTIVE)
            )
        )
        if active:
            raise ArchitectError(
                409,
                "project_generation_active",
                "This project already has an active Architect request. The new request was not admitted.",
                run_id=active,
            )
        source = db.scalar(
            select(ProductPlan)
            .where(ProductPlan.id == payload.source_plan_id, ProductPlan.project_id == project_id)
            .with_for_update(read=True)
        )
        if source is None:
            raise HTTPException(404, "Product plan not found.")
        if source.state != "approved" or (source.version, source.revision) != (
            payload.source_version,
            payload.source_revision,
        ):
            raise ArchitectError(
                409,
                "approved_source_required",
                "Select the exact current approved Product Plan. Draft or superseded requirements cannot start architecture generation.",
            )
        document = read_document(db, source)
        if content_hash(document) != source.content_hash:
            raise ArchitectError(
                409,
                "source_integrity_error",
                "The saved source failed integrity validation. No generation was started.",
            )
        snapshot = {
            "project_id": str(project.id),
            "project_title": project.title,
            "source": {
                "id": str(source.id),
                "version": source.version,
                "revision": source.revision,
                "hash": source.content_hash,
            },
            "approved_product_plan": document.model_dump(mode="json"),
            "constraints": payload.constraints,
        }
        metrics = request_metrics(config, snapshot)
        if metrics["input_bytes"] > config.architect_max_input_bytes:
            raise ArchitectError(
                422,
                "input_too_large",
                "The approved source and constraints exceed the bounded Architect input budget. No request was admitted.",
            )
        check_limits(db, config, actor_id, moment)
        run = ArchitectRun(
            id=uuid4(),
            project_id=project_id,
            workspace_id=project.workspace_id,
            source_plan_id=source.id,
            source_version=source.version,
            source_revision=source.revision,
            source_hash=source.content_hash,
            initiator_id=actor_id,
            initiating_session_id=session_id,
            executor_id=uuid4(),
            client_request_id=payload.client_request_id,
            request_hash=request_hash,
            snapshot_hash=hashlib.sha256(canonical(snapshot).encode()).hexdigest(),
            input_snapshot=snapshot,
            status="pending",
            provider=PROVIDER,
            requested_model=config.architect_model,
            prompt_version=PROMPT_VERSION,
            prompt_hash=PROMPT_HASH,
            diagnostic={
                "agent": "architect",
                "generation_configuration": {
                    "thinking_level": config.architect_thinking_level,
                    "max_input_bytes": config.architect_max_input_bytes,
                    "max_output_tokens": config.architect_max_output_tokens,
                    "timeout_seconds": config.architect_timeout_seconds,
                    **metrics,
                },
            },
            deadline_at=moment + timedelta(seconds=20),
        )
        db.add(run)
        db.flush()
        result = run.id, run.executor_id, snapshot
    return result


def fail(engine, run_id, category, diagnostic, result=None, status="failed"):
    return record_failure(
        engine,
        run_id,
        category,
        {"agent": "architect", **diagnostic},
        result,
        status,
        model=ArchitectRun,
    )


async def bounded_call(provider, snapshot, timeout):
    async with asyncio.timeout(timeout + 10):
        return await provider.generate(snapshot)


def generate(
    engine, config, project_id, actor_id, session_id, payload, *, provider=None, started=None
):
    timing, result = RunTiming("architect"), None
    started = started if started is not None else monotonic()
    try:
        with timing.measure("admission_transaction"):
            run_id, executor, snapshot = reserve(
                engine, config, project_id, actor_id, session_id, payload
            )
    except SQLAlchemyError:
        raise ArchitectError(
            503,
            "run_outcome_unknown",
            "Architect admission could not be confirmed. Recover by request ID; never automatically resubmit.",
        ) from None
    timing.run_id = run_id
    timing.event("admission_commit_acknowledged", "pending" if executor else "replay")
    if executor is None:
        with phase(engine) as db:
            return run_summary(db, db.get(ArchitectRun, run_id)), False
    try:
        if provider is None and not config.architect_settings().pm_configured:
            raise ProviderFailure(
                "architect_not_configured", capability(config)["setup_message"], 503
            )
        with timing.measure("running_transaction"):
            mark_running(
                engine,
                config.architect_settings(),
                run_id,
                executor,
                model=ArchitectRun,
                validate_source=lambda db, run: source_document(db, run, current=True),
            )
        timing.event("running_commit_acknowledged", "running")
    except ProviderFailure as exc:
        diagnostic = fail(engine, run_id, exc.category, timing.diagnostic(exc.diagnostic))
        raise ArchitectError(
            exc.status, exc.category, exc.message, run_id=run_id, diagnostic_id=diagnostic
        ) from None
    except SQLAlchemyError:
        raise ArchitectError(
            503,
            "run_outcome_unknown",
            "Architect execution start was not confirmed; no provider request was dispatched. Recover by GET.",
            run_id=run_id,
        ) from None
    except (HTTPException, PMError) as exc:
        diagnostic = fail(engine, run_id, "authorization_changed", timing.diagnostic())
        raise ArchitectError(
            getattr(exc, "status_code", getattr(exc, "status", 409)),
            "authorization_changed",
            "Initiating authority changed before dispatch.",
            run_id=run_id,
            diagnostic_id=diagnostic,
        ) from None
    try:
        if monotonic() - started > 60:
            raise ProviderFailure(
                "run_interrupted", "Architect startup exceeded its bounded budget."
            )
        with timing.measure("provider_call"):
            result = asyncio.run(
                bounded_call(
                    provider or GeminiArchitectProvider(config),
                    snapshot,
                    config.architect_timeout_seconds,
                )
            )
        timing.event("provider_response_received", "running")
        with timing.measure("validation"):
            document = ArchitectureDocument.model_validate_json(result.output)
            from orba.pm_schemas import ProductDocument

            coverage(document, ProductDocument.model_validate(snapshot["approved_product_plan"]))
        timing.event("output_validated", "running")
    except ProviderFailure as exc:
        diagnostic = fail(
            engine, run_id, exc.category, timing.diagnostic(exc.diagnostic), exc.result
        )
        raise ArchitectError(
            exc.status, exc.category, exc.message, run_id=run_id, diagnostic_id=diagnostic
        ) from None
    except (ValidationError, ValueError) as exc:
        diagnostic = fail(
            engine,
            run_id,
            "invalid_model_response",
            timing.diagnostic({"exception_type": type(exc).__name__}),
            result,
        )
        raise ArchitectError(
            502,
            "invalid_model_response",
            "The architecture response failed schema, source-reference or DAG validation. No architecture was saved.",
            run_id=run_id,
            diagnostic_id=diagnostic,
        ) from None
    except TimeoutError:
        diagnostic = fail(
            engine,
            run_id,
            "provider_timeout",
            timing.diagnostic({"error_origin": "local_envelope_timeout"}),
            result,
        )
        raise ArchitectError(
            504,
            "provider_timeout",
            "Architecture generation timed out. No new architecture was saved. Existing plans are safe; inspect status before retrying.",
            run_id=run_id,
            diagnostic_id=diagnostic,
        ) from None
    except (asyncio.CancelledError, KeyboardInterrupt):
        fail(engine, run_id, "interrupted", timing.diagnostic(), result, "interrupted")
        raise
    except (RuntimeError, TypeError, AttributeError, OverflowError) as exc:
        diagnostic = fail(
            engine,
            run_id,
            "provider_request_failed",
            timing.diagnostic({"exception_type": type(exc).__name__}),
            result,
        )
        raise ArchitectError(
            502,
            "provider_request_failed",
            "The Architect request could not complete. No proposal was published.",
            run_id=run_id,
            diagnostic_id=diagnostic,
        ) from None
    try:
        with timing.measure("persistence_transaction"), phase(engine) as db:
            project = lock_project(db, project_id, actor_id)
            run = db.scalar(select(ArchitectRun).where(ArchitectRun.id == run_id).with_for_update())
            moment = check_session(db, session_id, actor_id)
            if (
                run.status != "running"
                or run.executor_id != executor
                or run.deadline_at <= moment
                or monotonic() - started > 285
                or run.workspace_id != project.workspace_id
            ):
                raise ArchitectError(
                    409, "run_interrupted", "The execution lease is no longer valid."
                )
            source_document(db, run, current=True)
            source = db.get(ProductPlan, run.source_plan_id)
            with timing.measure("persistence_flush"):
                create_architecture(db, project_id, actor_id, source, document, run_id=run.id)
                db.flush()
            _metadata(run, result)
            moment = check_session(db, session_id, actor_id)
            if moment >= run.deadline_at:
                raise ArchitectError(
                    409, "run_interrupted", "Architecture persistence exceeded its execution lease."
                )
            run.status, run.completed_at = "succeeded", moment
            run.diagnostic = dict(run.diagnostic or {}) | timing.diagnostic(
                {"dispatch_phase": "validated_publication"}
            )
        timing.event("publication_commit_acknowledged", "succeeded")
        with phase(engine) as db:
            return run_summary(db, db.get(ArchitectRun, run_id)), True
    except (HTTPException, ArchitectError) as exc:
        category = "authorization_changed" if isinstance(exc, HTTPException) else exc.code
        diagnostic = fail(engine, run_id, category, timing.diagnostic(), result)
        raise ArchitectError(
            getattr(exc, "status_code", getattr(exc, "status", 409)),
            category,
            "Architecture was not published because source, authority or execution lease changed.",
            run_id=run_id,
            diagnostic_id=diagnostic,
        ) from None
    except SQLAlchemyError as persistence_error:
        try:
            with phase(engine) as db:
                run = db.scalar(
                    select(ArchitectRun).where(ArchitectRun.id == run_id).with_for_update()
                )
                if run and run.status == "succeeded":
                    return run_summary(db, run), True
                confirmed_incomplete = bool(
                    run and run.status in ACTIVE and run.executor_id == executor
                )
            if confirmed_incomplete:
                diagnostic = fail(
                    engine,
                    run_id,
                    "persistence_failed",
                    timing.diagnostic({"exception_type": type(persistence_error).__name__}),
                    result,
                )
                raise ArchitectError(
                    503,
                    "persistence_failed",
                    "Database persistence failed; no architecture was committed. The run records the failure.",
                    run_id=run_id,
                    diagnostic_id=diagnostic,
                )
        except SQLAlchemyError:
            pass
        raise ArchitectError(
            503,
            "run_outcome_unknown",
            "Architecture commit could not be confirmed. Inspect this run before starting a new generation.",
            run_id=run_id,
        ) from None

"""PostgreSQL-serialized scheduling and receipt protocol; never an executor."""

import hmac
import secrets
from datetime import timedelta
from uuid import UUID, uuid4

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import func, select

from orba.architect_models import ArchitectureVersion
from orba.models import Project, Workspace
from orba.orchestration_models import OrchestrationEvent, OrchestrationRun, OrchestrationTask
from orba.orchestration_service import checksum, conflict, detail, materialized, snapshot_source
from orba.pm_errors import PMError
from orba.scheduler_models import (
    ClaimRequest,
    HandoffRecord,
    LeaseHeartbeat,
    SchedulerState,
    TaskDispatch,
    TaskLease,
    WorkerCredential,
    WorkerIdentity,
)
from orba.scheduler_schemas import (
    ControlDetails,
    DispatchRead,
    HandoffManifest,
    SchedulerPolicy,
    SchedulerRead,
    WorkerRead,
    lease_read,
)
from orba.security import digest
from orba.transactions import db_now, phase

ACTIVE = ("claimed", "acknowledged")


def coordination(db, policy=None):
    """First lock in every control-plane mutation, including human cancellation.

    This is a local-throughput choice, not a process mutex or fairness algorithm.
    Database constraints independently prohibit competing active task ownership.
    """
    state = db.scalar(select(SchedulerState).where(SchedulerState.id == 1).with_for_update())
    if state is None:
        raise HTTPException(503, "Scheduler schema is not initialized. Apply migrations.")
    if policy is not None:
        value = policy.model_dump(mode="json")
        if state.policy is None:
            state.policy = value
        else:
            try:
                if not isinstance(state.policy, dict) or set(state.policy) != set(value):
                    raise ValueError
                saved = SchedulerPolicy.model_validate(state.policy).model_dump(mode="json")
            except (ValidationError, ValueError):
                raise HTTPException(
                    503,
                    "Saved scheduler policy is malformed. Ask the local operator to inspect it; no claim was admitted.",
                ) from None
            if saved != value:
                raise HTTPException(
                    503,
                    "Scheduler policy differs from the saved policy. Align API and scheduler configuration; do not retry claims automatically.",
                )
    return state


def lock_run(db, run_id):
    row = db.get(OrchestrationRun, run_id)
    if row is None:
        raise HTTPException(404, "Run not found.")
    db.scalar(select(Workspace).where(Workspace.id == row.workspace_id).with_for_update())
    db.scalar(select(Project).where(Project.id == row.project_id).with_for_update())
    return db.scalar(
        select(OrchestrationRun)
        .where(OrchestrationRun.id == run_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )


def source_current(db, run):
    if run.status != "awaiting_executor":
        conflict("run_not_dispatchable", "This run is not dispatchable. Refresh its saved state.")
    materialized(db, run)
    project = db.get(Project, run.project_id)
    artifact = db.get(ArchitectureVersion, run.architecture_id)
    if artifact is None or artifact.state != "approved":
        conflict(
            "source_changed",
            "The source architecture is no longer approved. Create a new run from the current approved source.",
        )
    snapshot, _ = snapshot_source(db, project, artifact)
    if checksum(snapshot) != run.snapshot_hash:
        conflict(
            "source_changed",
            "The current approved source differs from this immutable run. Review the current agreement.",
        )


def control_event(db, run, kind, *, dispatch=None, lease=None, worker=None, reason):
    moment = db_now(db)
    run.revision += 1
    run.last_event_sequence += 1
    run.updated_at = moment
    metadata = ControlDetails(
        execution_performed=False,
        dispatch_id=dispatch.id if dispatch else None,
        lease_id=lease.id if lease else None,
        worker_id=lease.worker_id if lease else worker.id if worker else None,
        fence_epoch=lease.fence_epoch if lease else dispatch.fence_epoch if dispatch else None,
        reason=reason,
    )
    db.add(
        OrchestrationEvent(
            id=uuid4(),
            run_id=run.id,
            project_id=run.project_id,
            task_id=dispatch.task_id if dispatch else None,
            sequence=run.last_event_sequence,
            run_revision=run.revision,
            event_type=kind,
            actor_type="system",
            actor_id=None,
            occurred_at=moment,
            previous_state=run.status,
            new_state=run.status,
            details=metadata.model_dump(mode="json"),
        )
    )
    db.flush()


def parse_credential(token):
    try:
        if not isinstance(token, str) or len(token) > 160 or not token.startswith("orba_wkr_"):
            raise ValueError
        ident, secret = token[9:].split(".")
        if len(secret) < 40:
            raise ValueError
        return UUID(ident)
    except (ValueError, TypeError):
        raise HTTPException(401, "A valid worker credential is required.") from None


def check_credential(worker, credential, token, moment):
    """One credential predicate, also used at the final DB publication clock."""
    if (
        not credential
        or not worker
        or not hmac.compare_digest(credential.token_hash, digest(token))
        or credential.revoked_at
        or credential.expires_at <= moment
        or not worker.enabled
        or credential.version != worker.credential_version
    ):
        raise HTTPException(
            401,
            "Worker credential is invalid, expired, disabled or revoked. Ask the local operator to review provisioning.",
        )


def authenticate(db, token, *, activity=False, lock=False):
    ident = parse_credential(token)
    credential = db.scalar(
        select(WorkerCredential)
        .where(WorkerCredential.id == ident)
        .execution_options(populate_existing=True)
    )
    worker_query = (
        select(WorkerIdentity)
        .where(WorkerIdentity.id == credential.worker_id)
        .execution_options(populate_existing=True)
        if credential
        else None
    )
    worker = (
        db.scalar(worker_query.with_for_update() if lock else worker_query) if credential else None
    )
    if lock and credential:
        # Called only after coordination and any workspace/project/run locks.
        # Worker precedes credential; both are reloaded after their lock waits.
        credential = db.scalar(
            select(WorkerCredential)
            .where(WorkerCredential.id == ident)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
    moment = db_now(db)
    check_credential(worker, credential, token, moment)
    if activity:
        worker.last_authenticated_at = moment
        worker.updated_at = moment
    return worker, credential


def publication_guard(db, token, *, run=None, capability=None, ownership_deadline=None):
    """Linearize admission at a fresh DB clock after all publication-write waits.

    Flush every tentative mutation first. Current worker/credential rows are then
    locked and reloaded; their authorization cannot change before commit. Expiry
    uses clock_timestamp, not transaction-start time. Nothing may mutate the ORM
    after this guard. Later HTTP delivery is not this authorization instant.
    """
    db.flush()
    worker, credential = authenticate(db, token, lock=True)
    moment = db_now(db)
    check_credential(worker, credential, token, moment)
    if run is not None and not worker_scope(worker, run):
        raise HTTPException(404, "Run not found.")
    if capability is not None and capability not in worker.capabilities:
        raise HTTPException(403, "This worker is not authorized for the required capability.")
    if ownership_deadline is not None and ownership_deadline <= moment:
        conflict(
            "lease_expired", "Lease ownership expired before publication. Recover its saved state."
        )


def credential_pair(worker, moment, lifetime):
    ident = uuid4()
    token = f"orba_wkr_{ident}.{secrets.token_urlsafe(32)}"
    credential = WorkerCredential(
        id=ident,
        worker_id=worker.id,
        version=worker.credential_version,
        token_hash=digest(token),
        created_at=moment,
        expires_at=moment + timedelta(seconds=lifetime),
    )
    return credential, token


def provision(db, payload):
    coordination(db)
    workspace = db.scalar(
        select(Workspace).where(Workspace.id == payload.workspace_id).with_for_update()
    )
    if not workspace or workspace.is_legacy:
        raise ValueError("Provisioning requires an existing nonlegacy workspace.")
    if payload.project_id:
        project = db.scalar(
            select(Project)
            .where(Project.id == payload.project_id, Project.workspace_id == workspace.id)
            .with_for_update()
        )
        if not project:
            raise ValueError("Worker project must belong to its workspace.")
    moment = db_now(db)
    worker = WorkerIdentity(
        id=uuid4(),
        workspace_id=workspace.id,
        project_id=payload.project_id,
        display_name=payload.display_name,
        capabilities=payload.capabilities,
        max_leases=payload.max_leases,
        worker_type="protocol_only",
        enabled=True,
        credential_version=1,
        created_at=moment,
        updated_at=moment,
    )
    db.add(worker)
    db.flush()
    credential, token = credential_pair(worker, moment, payload.lifetime_seconds)
    db.add(credential)
    db.flush()
    return worker, token


def worker_scope(worker, run):
    return worker.workspace_id == run.workspace_id and (
        worker.project_id is None or worker.project_id == run.project_id
    )


def worker_matches(db, task, run, policy, moment):
    workers = db.scalars(
        select(WorkerIdentity)
        .where(
            WorkerIdentity.workspace_id == run.workspace_id,
            WorkerIdentity.enabled.is_(True),
            WorkerIdentity.last_authenticated_at
            > moment - timedelta(seconds=policy.worker_liveness_seconds),
        )
        .order_by(WorkerIdentity.id)
    ).all()
    for worker in workers:
        if (
            worker_scope(worker, run)
            and task.definition["category"] in worker.capabilities
            and db.scalar(
                select(WorkerCredential.id).where(
                    WorkerCredential.worker_id == worker.id,
                    WorkerCredential.version == worker.credential_version,
                    WorkerCredential.revoked_at.is_(None),
                    WorkerCredential.expires_at > moment,
                )
            )
        ):
            return True
    return False


def end_lease(db, run, dispatch, lease, policy, state, reason):
    if lease.state not in ACTIVE:
        return
    acknowledged = lease.acknowledged_at is not None
    lease.state, lease.reason, lease.ended_at = state, reason, db_now(db)
    dispatch.fence_epoch += (
        1  # invalidation also fences; gaps between ownership epochs are intentional.
    )
    dispatch.updated_at = lease.ended_at
    dispatch.state = (
        "cancelled"
        if state == "cancelled"
        else "needs_reconciliation"
        if acknowledged
        else "exhausted"
        if dispatch.attempts >= policy.max_attempts
        else "withdrawn"
    )
    kind = (
        "lease_expired"
        if state == "expired"
        else "lease_released"
        if state == "released"
        else "lease_revoked"
    )
    control_event(db, run, kind, dispatch=dispatch, lease=lease, reason=reason)
    if dispatch.state in {"needs_reconciliation", "exhausted"}:
        control_event(
            db,
            run,
            "task_requires_reconciliation" if acknowledged else "dispatch_exhausted",
            dispatch=dispatch,
            reason=reason,
        )


def recover(db, policy, *, run_id=None, worker_id=None, lease_id=None):
    query = select(TaskLease).where(TaskLease.state.in_(ACTIVE))
    if run_id is not None:
        query = query.where(TaskLease.run_id == run_id)
    if worker_id is not None:
        query = query.where(TaskLease.worker_id == worker_id)
    if lease_id is not None:
        query = query.where(TaskLease.id == lease_id)
    for lease in db.scalars(query.order_by(TaskLease.id)).all():
        run = lock_run(db, lease.run_id)
        moment = db_now(db)
        credential = db.get(WorkerCredential, lease.credential_id)
        worker = db.get(WorkerIdentity, lease.worker_id)
        expired = lease.expires_at <= moment or (
            lease.state == "claimed" and lease.acknowledge_by <= moment
        )
        revoked = (
            credential.revoked_at is not None
            or credential.expires_at <= moment
            or not worker.enabled
            or worker.credential_version != lease.credential_version
        )
        if expired or revoked or run.status == "cancelled":
            dispatch = db.get(TaskDispatch, lease.dispatch_id)
            end_lease(
                db,
                run,
                dispatch,
                lease,
                policy,
                "cancelled" if run.status == "cancelled" else "revoked" if revoked else "expired",
                "run_cancelled"
                if run.status == "cancelled"
                else "credential_invalidated"
                if revoked
                else "ack_deadline"
                if lease.state == "claimed"
                else "lease_deadline",
            )


def deterministic_tasks(db):
    tasks = db.scalars(
        select(OrchestrationTask)
        .join(OrchestrationRun, OrchestrationRun.id == OrchestrationTask.run_id)
        .where(
            OrchestrationRun.status == "awaiting_executor",
            OrchestrationTask.eligibility == "eligible",
            OrchestrationTask.execution_status == "awaiting_executor",
        )
    ).all()
    runs = {row.run_id: db.get(OrchestrationRun, row.run_id) for row in tasks}
    return sorted(
        tasks,
        key=lambda row: (
            row.definition["priority"],
            runs[row.run_id].created_at,
            row.display_order,
            str(row.id),
        ),
    )


def tick(engine, policy, process_id):
    with phase(engine) as db:
        state = coordination(db, policy)
        recover(db, policy)
        queued = 0
        if state.process_id and state.process_id != process_id:
            pending_runs = db.scalars(
                select(TaskDispatch.run_id)
                .where(TaskDispatch.state.in_(("queued", "leased")))
                .distinct()
                .order_by(TaskDispatch.run_id)
                .limit(policy.batch_size)
            ).all()
            for run_id in pending_runs:
                observed = lock_run(db, run_id)
                if observed.status == "awaiting_executor":
                    control_event(
                        db, observed, "scheduler_recovered", reason="new_scheduler_process_observed"
                    )
        # Queued reservations cannot pin capacity after worker or source loss.
        for dispatch in db.scalars(
            select(TaskDispatch).where(TaskDispatch.state == "queued").order_by(TaskDispatch.id)
        ).all():
            run = lock_run(db, dispatch.run_id)
            task = db.get(OrchestrationTask, dispatch.task_id)
            valid = True
            try:
                source_current(db, run)
            except (HTTPException, PMError):
                valid = False
            if not valid or not worker_matches(db, task, run, policy, db_now(db)):
                dispatch.state, dispatch.updated_at = "withdrawn", db_now(db)
                control_event(
                    db,
                    run,
                    "dispatch_withdrawn",
                    dispatch=dispatch,
                    reason="source_or_worker_unavailable",
                )
        for task in deterministic_tasks(db):
            if queued >= policy.batch_size:
                break
            outstanding = db.scalar(
                select(func.count())
                .select_from(TaskDispatch)
                .where(TaskDispatch.state.in_(("queued", "leased")))
            )
            if outstanding >= policy.global_capacity:
                break
            run = lock_run(db, task.run_id)
            count = db.scalar(
                select(func.count())
                .select_from(TaskDispatch)
                .where(TaskDispatch.run_id == run.id, TaskDispatch.state.in_(("queued", "leased")))
            )
            if count >= policy.run_capacity:
                continue
            dispatch = db.scalar(select(TaskDispatch).where(TaskDispatch.task_id == task.id))
            if dispatch and dispatch.state != "withdrawn":
                continue
            try:
                source_current(db, run)
            except (HTTPException, PMError):
                continue
            moment = db_now(db)
            if not worker_matches(db, task, run, policy, moment):
                continue
            if dispatch is None:
                dispatch = TaskDispatch(
                    id=uuid4(),
                    task_id=task.id,
                    run_id=run.id,
                    project_id=run.project_id,
                    workspace_id=run.workspace_id,
                    required_capability=task.definition["category"],
                    state="queued",
                    attempts=0,
                    fence_epoch=0,
                    created_at=moment,
                    updated_at=moment,
                )
                db.add(dispatch)
            else:
                dispatch.state, dispatch.updated_at = "queued", moment
            db.flush()
            control_event(
                db,
                run,
                "dispatch_queued",
                dispatch=dispatch,
                reason="eligible_root_with_registered_worker",
            )
            queued += 1
        state.tick_count += 1
        state.last_tick_at, state.process_id = db_now(db), process_id
        result = {
            "tick": state.tick_count,
            "queued": queued,
            "observed_at": state.last_tick_at.isoformat(),
            "process_id": str(process_id),
            "execution_performed": False,
        }
    return result


def manifest_for(db, run, task, dispatch, lease):
    handoff_id = uuid4()
    value = {
        "contract_version": 1,
        "handoff_id": str(handoff_id),
        "worker_id": str(lease.worker_id),
        "workspace_id": str(run.workspace_id),
        "project_id": str(run.project_id),
        "run_id": str(run.id),
        "task_id": str(task.id),
        "source_task_id": str(task.source_task_id),
        "source_task_key": task.key,
        "architecture": {
            "id": str(run.architecture_id),
            "version": run.architecture_version,
            "revision": run.architecture_revision,
            "hash": run.architecture_hash,
        },
        "product_plan": {
            "id": str(run.source_plan_id),
            "version": run.source_version,
            "revision": run.source_revision,
            "hash": run.source_hash,
        },
        "snapshot_hash": run.snapshot_hash,
        "title": task.definition["title"],
        "description": task.definition["description"],
        "acceptance_criteria": task.definition["acceptance_criteria"],
        "requirement_traces": [
            x for x in run.source_snapshot["traces"] if x["task_key"] == task.key
        ],
        "dependencies": [],
        "required_capability": dispatch.required_capability,
        "lease_id": str(lease.id),
        "fence_epoch": lease.fence_epoch,
        "acknowledge_by": lease.acknowledge_by.isoformat(),
        "initial_expires_at": lease.expires_at.isoformat(),
        "max_expires_at": lease.max_expires_at.isoformat(),
        "execution_policy": "protocol_only_no_execution",
    }
    # Canonicalize the typed wire representation first (including UTC timestamps).
    value["checksum"] = "0" * 64
    normalized = HandoffManifest.model_validate(value).model_dump(mode="json")
    normalized["checksum"] = checksum({k: v for k, v in normalized.items() if k != "checksum"})
    manifest = HandoffManifest.model_validate(normalized)
    record = HandoffRecord(
        id=handoff_id,
        lease_id=lease.id,
        manifest=manifest.model_dump(mode="json"),
        checksum=manifest.checksum,
        created_at=lease.created_at,
    )
    db.add(record)
    return record


def handoff_read(db, lease):
    record = db.scalar(select(HandoffRecord).where(HandoffRecord.lease_id == lease.id))
    if record is None or record.checksum != checksum(
        {k: v for k, v in record.manifest.items() if k != "checksum"}
    ):
        conflict(
            "handoff_integrity",
            "The saved handoff failed validation. Ask the local operator to inspect the record.",
        )
    return {
        "lease": lease_read(lease),
        "manifest": HandoffManifest.model_validate(record.manifest).model_dump(mode="json"),
        "execution_performed": False,
    }


def claim(engine, policy, token, payload):
    with phase(engine) as db:
        authenticate(db, token)
        coordination(db, policy)
        # Do not dirty/implicitly lock a worker before workspace/project/run locks.
        worker, credential = authenticate(db, token)
        recover(db, policy, worker_id=worker.id)
        request_hash = checksum(payload.model_dump(mode="json"))
        prior = db.scalar(
            select(ClaimRequest).where(
                ClaimRequest.worker_id == worker.id, ClaimRequest.request_id == payload.request_id
            )
        )
        if prior:
            if prior.request_hash != request_hash:
                conflict(
                    "claim_idempotency_conflict",
                    "This claim ID belongs to different inputs. Recover the original claim first.",
                )
            lease = db.get(TaskLease, prior.lease_id)
            run = lock_run(db, lease.run_id)
            worker, credential = authenticate(db, token, activity=True, lock=True)
            if lease.state not in ACTIVE or lease.credential_id != credential.id:
                conflict(
                    "claim_terminal",
                    "The original claim is terminal. Inspect its state; a new request is a deliberate new claim.",
                )
            result, created = handoff_read(db, lease), False
        else:
            if payload.run_id:
                run = db.get(OrchestrationRun, payload.run_id)
                if not run or not worker_scope(worker, run):
                    raise HTTPException(404, "Run not found.")
            active = db.scalar(
                select(func.count())
                .select_from(TaskLease)
                .where(TaskLease.worker_id == worker.id, TaskLease.state.in_(ACTIVE))
            )
            if active >= worker.max_leases:
                conflict(
                    "worker_capacity",
                    "This worker already holds its maximum active leases. Recover or release existing ownership first.",
                )
            candidates = deterministic_tasks(db)
            result, created = None, False
            for task in candidates:
                run = db.get(OrchestrationRun, task.run_id)
                if (
                    not worker_scope(worker, run)
                    or (payload.run_id and run.id != payload.run_id)
                    or task.definition["category"] not in worker.capabilities
                ):
                    continue
                dispatch = db.scalar(
                    select(TaskDispatch).where(
                        TaskDispatch.task_id == task.id, TaskDispatch.state == "queued"
                    )
                )
                if not dispatch:
                    continue
                run = lock_run(db, run.id)
                source_current(db, run)
                worker, credential = authenticate(db, token, activity=True, lock=True)
                if not worker_scope(worker, run):
                    raise HTTPException(404, "Run not found.")
                if task.definition["category"] not in worker.capabilities:
                    raise HTTPException(
                        403, "This worker is not authorized for the required capability."
                    )
                moment = db_now(db)
                dispatch.attempts += 1
                dispatch.fence_epoch += 1
                dispatch.state, dispatch.updated_at = "leased", moment
                lease = TaskLease(
                    id=uuid4(),
                    dispatch_id=dispatch.id,
                    task_id=task.id,
                    run_id=run.id,
                    project_id=run.project_id,
                    workspace_id=run.workspace_id,
                    worker_id=worker.id,
                    credential_id=credential.id,
                    credential_version=credential.version,
                    fence_epoch=dispatch.fence_epoch,
                    state="claimed",
                    created_at=moment,
                    acknowledge_by=moment + timedelta(seconds=policy.acknowledge_seconds),
                    expires_at=moment + timedelta(seconds=policy.lease_seconds),
                    max_expires_at=moment + timedelta(seconds=policy.max_lease_seconds),
                )
                db.add(lease)
                db.flush()
                manifest_for(db, run, task, dispatch, lease)
                db.add(
                    ClaimRequest(
                        worker_id=worker.id,
                        request_id=payload.request_id,
                        request_hash=request_hash,
                        lease_id=lease.id,
                        created_at=moment,
                    )
                )
                control_event(
                    db,
                    run,
                    "lease_claimed",
                    dispatch=dispatch,
                    lease=lease,
                    reason="atomic_worker_claim",
                )
                control_event(
                    db,
                    run,
                    "handoff_available",
                    dispatch=dispatch,
                    lease=lease,
                    reason="immutable_manifest_committed",
                )
                result, created = handoff_read(db, lease), True
                break
        worker, _ = authenticate(db, token, activity=True, lock=True)
        publication_guard(
            db,
            token,
            run=run if result else None,
            capability=result["manifest"]["required_capability"] if result else None,
            ownership_deadline=(
                min(
                    lease.expires_at,
                    lease.acknowledge_by if lease.state == "claimed" else lease.max_expires_at,
                )
                if result
                else None
            ),
        )
    return result, created


def worker_me(engine, policy, token):
    with phase(engine) as db:
        authenticate(db, token)
        coordination(db, policy)
        worker, _ = authenticate(db, token, activity=True, lock=True)
        result = WorkerRead.model_validate(worker, from_attributes=True).model_dump(mode="json")
        publication_guard(db, token)
    return result


def claim_recovery(engine, policy, token, request_id):
    with phase(engine) as db:
        authenticate(db, token)
        coordination(db, policy)
        worker, _ = authenticate(db, token)
        recover(db, policy, worker_id=worker.id)
        receipt = db.scalar(
            select(ClaimRequest).where(
                ClaimRequest.worker_id == worker.id, ClaimRequest.request_id == request_id
            )
        )
        if receipt is None:
            raise HTTPException(404, "No committed claim was found for this worker and request ID.")
        lease = db.get(TaskLease, receipt.lease_id)
        run = lock_run(db, lease.run_id)
        authenticate(db, token, activity=True, lock=True)
        result = handoff_read(db, lease)
        publication_guard(db, token, run=run)
    return result


def lease_operation(engine, policy, token, lease_id, payload, operation):
    error = None
    with phase(engine) as db:
        authenticate(db, token)
        coordination(db, policy)
        worker, credential = authenticate(db, token)
        lease = db.get(TaskLease, lease_id)
        if not lease or lease.worker_id != worker.id:
            raise HTTPException(404, "Lease not found.")
        run = lock_run(db, lease.run_id)
        worker, credential = authenticate(db, token, activity=True, lock=True)
        dispatch = db.get(TaskDispatch, lease.dispatch_id)
        recover(db, policy, lease_id=lease.id)
        moment = db_now(db)
        ownership_deadline = min(
            lease.expires_at,
            lease.acknowledge_by if lease.state == "claimed" else lease.max_expires_at,
        )
        record = db.scalar(select(HandoffRecord).where(HandoffRecord.lease_id == lease.id))
        valid = (
            lease.state in ACTIVE
            and lease.credential_id == credential.id
            and lease.fence_epoch == dispatch.fence_epoch == payload.fence_epoch
            and run.status == "awaiting_executor"
            and record.checksum == payload.manifest_checksum
            and payload.contract_version == 1
        )
        if valid and operation == "acknowledge":
            try:
                source_current(db, run)
            except (HTTPException, PMError):
                valid = False
        if not valid:
            # Persist a genuine scoped rejection before raising, not a rolled-back event.
            if run.status == "awaiting_executor":
                control_event(
                    db,
                    run,
                    "worker_lease_rejected",
                    dispatch=dispatch,
                    lease=lease,
                    reason="stale_or_invalid_ownership",
                )
            error = (
                409,
                "Lease ownership, source, epoch or manifest is no longer valid. Recover the saved claim; do not retry with a new identity automatically.",
            )
        elif operation == "acknowledge":
            if lease.state == "claimed":
                lease.state, lease.acknowledged_at = "acknowledged", moment
                control_event(
                    db,
                    run,
                    "handoff_acknowledged",
                    dispatch=dispatch,
                    lease=lease,
                    reason="exact_manifest_received",
                )
        elif operation == "heartbeat":
            if lease.state != "acknowledged":
                error = (409, "Acknowledge the current handoff before sending heartbeats.")
            else:
                request_hash = checksum(payload.model_dump(mode="json"))
                prior = db.scalar(
                    select(LeaseHeartbeat).where(
                        LeaseHeartbeat.lease_id == lease.id,
                        LeaseHeartbeat.request_id == payload.request_id,
                    )
                )
                if prior and prior.request_hash != request_hash:
                    error = (409, "Heartbeat request ID conflicts with its original inputs.")
                elif not prior:
                    last = lease.last_heartbeat_at or lease.acknowledged_at
                    if (moment - last).total_seconds() < policy.heartbeat_seconds:
                        error = (
                            429,
                            "Heartbeat is too early. Wait the configured minimum interval; no renewal was recorded.",
                        )
                    else:
                        lease.expires_at = min(
                            moment + timedelta(seconds=policy.lease_seconds), lease.max_expires_at
                        )
                        lease.last_heartbeat_at = moment
                        db.add(
                            LeaseHeartbeat(
                                lease_id=lease.id,
                                request_id=payload.request_id,
                                request_hash=request_hash,
                                accepted_at=moment,
                                expires_at=lease.expires_at,
                            )
                        )
                        control_event(
                            db,
                            run,
                            "lease_renewed",
                            dispatch=dispatch,
                            lease=lease,
                            reason="authenticated_heartbeat",
                        )
        elif operation == "release":
            end_lease(db, run, dispatch, lease, policy, "released", "worker_released")
        result = handoff_read(db, lease)
        publication_guard(
            db,
            token,
            run=run,
            ownership_deadline=ownership_deadline if not error and operation != "release" else None,
        )
    if error:
        raise HTTPException(*error)
    return result


def invalidate_run(db, run, policy):
    for dispatch in db.scalars(
        select(TaskDispatch).where(TaskDispatch.run_id == run.id).order_by(TaskDispatch.id)
    ):
        lease = db.scalar(
            select(TaskLease).where(
                TaskLease.dispatch_id == dispatch.id, TaskLease.state.in_(ACTIVE)
            )
        )
        if lease:
            end_lease(db, run, dispatch, lease, policy, "cancelled", "run_cancelled")
        else:
            dispatch.state, dispatch.updated_at = "cancelled", db_now(db)


def inspect_scheduler(db, run):
    detail(db, run)  # Reuse authoritative snapshot and graph integrity checks.
    state = db.get(SchedulerState, 1)
    rows = []
    for dispatch in db.scalars(
        select(TaskDispatch)
        .where(TaskDispatch.run_id == run.id)
        .order_by(TaskDispatch.created_at, TaskDispatch.id)
    ):
        leases = db.scalars(
            select(TaskLease)
            .where(TaskLease.dispatch_id == dispatch.id)
            .order_by(TaskLease.created_at, TaskLease.id)
        ).all()
        worker = db.get(WorkerIdentity, leases[-1].worker_id) if leases else None
        value = DispatchRead.model_validate(
            {
                **{
                    field: getattr(dispatch, field)
                    for field in (
                        "id",
                        "task_id",
                        "run_id",
                        "required_capability",
                        "state",
                        "attempts",
                        "fence_epoch",
                        "created_at",
                        "updated_at",
                    )
                },
                "leases": [lease_read(lease) for lease in leases],
                "worker_name": worker.display_name if worker else None,
            }
        ).model_dump(mode="json")
        rows.append(value)
    return SchedulerRead(
        run_id=run.id,
        snapshot_hash=run.snapshot_hash,
        observed_at=db_now(db),
        last_tick_at=state.last_tick_at,
        tick_count=state.tick_count,
        policy=state.policy,
        dispatches=rows,
    ).model_dump(mode="json")

"""Fail-closed evidence reconciliation; never a source of execution facts."""

import json
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AwareDatetime, Field, StrictBool, ValidationError

from orba.orchestration_schemas import EventRead
from orba.orchestration_service import checksum
from orba.scheduler_schemas import (
    DispatchRead,
    HandoffManifest,
    HandoffRead,
    LeaseRead,
    SchedulerPolicy,
    SchedulerRead,
    WorkerRead,
    validate_control_event,
)
from scripts.orchestration_proof import (
    SHA256,
    SQL,
    Count,
    EvidenceModel,
    LocalProof,
    Positive,
)
from scripts.orchestration_proof import (
    validate_proof as validate_foundation,
)
from scripts.verification import EvidenceError


class Worker(WorkerRead, EvidenceModel):
    pass


class Lease(LeaseRead, EvidenceModel):
    pass


class Manifest(HandoffManifest, EvidenceModel):
    pass


class Handoff(HandoffRead, EvidenceModel):
    lease: Lease
    manifest: Manifest
    execution_performed: StrictBool


class Dispatch(DispatchRead, EvidenceModel):
    leases: list[Lease]


class Status(SchedulerRead, EvidenceModel):
    dispatches: list[Dispatch]
    execution_performed: StrictBool


class Event(EventRead, EvidenceModel):
    project_id: UUID
    sequence: Positive
    run_revision: Positive
    occurred_at: AwareDatetime


class FinalSource(SQL):
    events: Annotated[list[Event], Field(min_length=1)]


class Credential(EvidenceModel):
    id: UUID
    worker_id: UUID
    version: Positive
    created_at: AwareDatetime
    expires_at: AwareDatetime
    revoked_at: AwareDatetime | None


class SQLDispatch(Dispatch):
    project_id: UUID
    workspace_id: UUID


class SQLHandoff(EvidenceModel):
    id: UUID
    lease_id: UUID
    checksum: SHA256
    manifest: Manifest
    created_at: AwareDatetime


class HeartbeatRecord(EvidenceModel):
    id: UUID
    lease_id: UUID
    request_id: UUID
    request_hash: SHA256
    accepted_at: AwareDatetime
    expires_at: AwareDatetime


class SchedulerSnapshot(EvidenceModel):
    tick_count: Positive
    last_tick_at: AwareDatetime
    process_id: UUID
    policy: SchedulerPolicy


class IndependentSQL(EvidenceModel):
    scheduler_state: SchedulerSnapshot
    orchestration: FinalSource
    dispatches: Annotated[list[SQLDispatch], Field(min_length=1)]
    workers: Annotated[list[Worker], Field(min_length=1)]
    credentials: Annotated[list[Credential], Field(min_length=1)]
    handoffs: Annotated[list[SQLHandoff], Field(min_length=1)]
    heartbeats: Annotated[list[HeartbeatRecord], Field(min_length=1)]
    run_revision_rechecked: Positive
    inspected_at: AwareDatetime


class ProcessCommand(EvidenceModel):
    receipt_id: UUID
    name: str
    argv: Annotated[list[str], Field(min_length=1)]
    pid: Positive
    exit_code: Annotated[int, Field(strict=True)] | None
    signal: str | None
    expected_termination: StrictBool
    started_at: AwareDatetime
    completed_at: AwareDatetime


class SchedulerProof(EvidenceModel):
    proof_version: Positive
    stage: Literal["stage05b-scheduler"]
    result: Literal["PASS"]
    execution_class: Literal["real_local_worker_protocol"]
    started_at: AwareDatetime
    completed_at: AwareDatetime
    foundation: LocalProof
    worker: Worker
    acknowledged_api: Handoff
    heartbeat_api: Handoff
    final_api: Status
    independent_sql: IndependentSQL
    process_commands: Annotated[list[ProcessCommand], Field(min_length=5)]
    stale_epoch_status: Positive
    foreign_worker_status: Positive
    unauthorized_user_status: Positive
    revoked_worker_status: Positive
    model_generation_requests: Count
    executed_tasks: Count
    browser_rendered: StrictBool
    reload_persisted: StrictBool
    protected_ui_hidden: StrictBool
    incomplete_proof_rejected: StrictBool


def require(condition, message):
    if not condition:
        raise EvidenceError("Scheduler proof: " + message)


def unique(rows, name):
    values = [str(row.id) for row in rows]
    require(len(values) == len(set(values)), "Duplicate " + name + " identities.")


def cross_records(proof, raw):
    """Reconcile SQL references, not merely internally consistent claimed counts."""
    sql, run = proof.independent_sql, proof.foundation.run_api
    source = sql.orchestration
    require(
        proof.final_api.tick_count == sql.scheduler_state.tick_count
        and proof.final_api.last_tick_at == sql.scheduler_state.last_tick_at
        and proof.final_api.policy == sql.scheduler_state.policy,
        "API scheduler observation contradicts SQL state.",
    )
    require(proof.final_api.snapshot_hash == source.snapshot_hash, "API snapshot checksum differs.")
    require(
        source.counts.traces == len(source.source_snapshot.traces),
        "Trace counts differ from source.",
    )
    registered = next(w for w in sql.workers if w.id == proof.worker.id)
    require(
        registered.enabled
        and registered.model_dump(exclude={"last_authenticated_at"})
        == proof.worker.model_dump(exclude={"last_authenticated_at"}),
        "API worker authorization contradicts SQL registry.",
    )
    lease = sql.dispatches[0].leases[0]
    dispatch = sql.dispatches[0]
    task = next(t for t in source.tasks if t.id == lease.task_id)
    manifest = sql.handoffs[0].manifest
    require(
        lease.dispatch_id == dispatch.id
        and lease.run_id == run.id
        and lease.project_id == run.project_id
        and lease.workspace_id == run.workspace_id,
        "SQL lease crossed source or dispatch identity.",
    )
    require(
        registered.workspace_id == run.workspace_id
        and (registered.project_id is None or registered.project_id == run.project_id),
        "Registered worker scope does not authorize run.",
    )
    for received in (proof.acknowledged_api, proof.heartbeat_api):
        for field in (
            "id",
            "dispatch_id",
            "task_id",
            "run_id",
            "project_id",
            "workspace_id",
            "worker_id",
            "credential_version",
            "fence_epoch",
            "created_at",
            "acknowledge_by",
            "max_expires_at",
            "acknowledged_at",
        ):
            require(
                getattr(received.lease, field) == getattr(lease, field),
                "API/SQL lease binding differs: " + field,
            )
    expected_traces = [
        trace
        for trace in raw["independent_sql"]["orchestration"]["source_snapshot"]["traces"]
        if trace["task_key"] == task.key
    ]
    require(
        [trace.model_dump(mode="json") for trace in manifest.requirement_traces] == expected_traces,
        "Manifest traces differ from immutable source.",
    )
    require(
        manifest.acknowledge_by == lease.acknowledge_by
        and manifest.max_expires_at == lease.max_expires_at
        and lease.created_at < lease.acknowledged_at <= lease.acknowledge_by
        and lease.last_heartbeat_at < lease.expires_at <= lease.max_expires_at,
        "Lease deadlines/acknowledgment are inconsistent.",
    )
    last = max(sql.heartbeats, key=lambda h: h.accepted_at)
    require(
        last.accepted_at == lease.last_heartbeat_at and last.expires_at == lease.expires_at,
        "SQL heartbeat receipt contradicts lease renewal.",
    )
    for receipt in sql.heartbeats:
        require(
            receipt.request_hash
            == checksum(
                {
                    "fence_epoch": lease.fence_epoch,
                    "contract_version": 1,
                    "manifest_checksum": manifest.checksum,
                    "request_id": str(receipt.request_id),
                }
            ),
            "Heartbeat request checksum is forged.",
        )
    require(
        [e.id for e in source.events[:2]] == [e.id for e in proof.foundation.initial_sql.events],
        "Initial lifecycle event identities changed.",
    )
    for event in source.events:
        require(
            event.run_id == run.id and event.project_id == run.project_id,
            "Event crossed source scope.",
        )
        if event.sequence <= 2:
            continue
        metadata = event.details
        if event.event_type != "scheduler_recovered":
            require(
                event.task_id == task.id and metadata["dispatch_id"] == str(dispatch.id),
                "Event dispatch/task references contradict SQL.",
            )
        if metadata.get("lease_id") is not None:
            require(
                metadata["lease_id"] == str(lease.id)
                and metadata["worker_id"] == str(lease.worker_id)
                and metadata["fence_epoch"] == lease.fence_epoch,
                "Event ownership contradicts SQL.",
            )
    require(
        len({c.name for c in proof.process_commands}) == len(proof.process_commands),
        "Duplicate native process receipt names.",
    )
    require(
        all(
            proof.started_at <= c.started_at <= c.completed_at <= proof.completed_at
            for c in proof.process_commands
        ),
        "Native process receipt outside current attempt.",
    )


def validate_proof(raw):
    try:
        proof = SchedulerProof.model_validate_json(json.dumps(raw))
        data = proof.model_dump(mode="json")
        # Strict numeric and bool types are declared at every evidence boundary.
        # UTC wire spellings may differ; canonical snapshot bytes below must not.
        require(proof.proof_version == 1, "Unsupported proof version.")
        foundation = validate_foundation(raw["foundation"])
        run = proof.foundation.run_api
        sql = proof.independent_sql
        source = sql.orchestration
        require(source.run_id == run.id == proof.final_api.run_id, "Run identity mismatch.")
        require(
            source.project_id == run.project_id and source.workspace_id == run.workspace_id,
            "Scope identity mismatch.",
        )
        for field in (
            "architecture_id",
            "architecture_version",
            "architecture_revision",
            "architecture_hash",
            "source_plan_id",
            "source_version",
            "source_revision",
            "source_hash",
            "snapshot_hash",
        ):
            require(
                getattr(source, field) == getattr(run, field), "Source binding mismatch: " + field
            )
        require(
            source.source_snapshot == proof.foundation.initial_sql.source_snapshot
            and checksum(raw["independent_sql"]["orchestration"]["source_snapshot"])
            == source.snapshot_hash,
            "Immutable canonical snapshot mismatch.",
        )
        require(
            raw["independent_sql"]["orchestration"]["tasks"]
            == raw["foundation"]["initial_sql"]["tasks"],
            "SQL task definitions were normalized or changed.",
        )
        require(
            source.tasks == proof.foundation.initial_sql.tasks
            and source.dependencies == proof.foundation.initial_sql.dependencies
            and source.graph == proof.foundation.initial_sql.graph,
            "SQL task/dependency/graph records changed.",
        )
        require(
            source.counts.tasks == len(source.tasks) > 0
            and source.counts.dependencies == len(source.dependencies),
            "Missing or contradictory persisted tasks/edges.",
        )
        require(
            source.counts.events == len(source.events)
            and [e.sequence for e in source.events] == list(range(1, len(source.events) + 1)),
            "Event sequence is incomplete.",
        )
        require(
            source.revision == sql.run_revision_rechecked == source.events[-1].run_revision,
            "SQL was not read consistently.",
        )
        require(
            all(validate_control_event(e) for e in source.events),
            "Invalid or execution-claiming event.",
        )
        kinds = {e.event_type for e in source.events}
        require(
            {
                "dispatch_queued",
                "lease_claimed",
                "handoff_available",
                "handoff_acknowledged",
                "lease_renewed",
                "lease_expired",
                "task_requires_reconciliation",
                "worker_lease_rejected",
            }
            <= kinds,
            "Required actual lifecycle events are missing.",
        )
        require(
            not source.execution_performed
            and source.status == "awaiting_executor"
            and not source.audit_model_requests
            and not source.generation_records.product_manager_runs
            and not source.generation_records.architect_runs,
            "Unexpected execution or model generation.",
        )
        for rows, name in (
            (source.tasks, "task"),
            (source.dependencies, "edge"),
            (source.events, "event"),
            (sql.dispatches, "dispatch"),
            (sql.workers, "worker"),
            (sql.credentials, "credential"),
            (sql.handoffs, "handoff"),
            (sql.heartbeats, "heartbeat"),
        ):
            unique(rows, name)
        require(
            proof.worker.id in {w.id for w in sql.workers}, "Authenticated worker missing from SQL."
        )
        credentials = [
            c
            for c in sql.credentials
            if c.worker_id == proof.worker.id and c.version == proof.worker.credential_version
        ]
        require(
            len(credentials) == 1
            and credentials[0].revoked_at is None
            and credentials[0].expires_at > proof.heartbeat_api.lease.last_heartbeat_at,
            "Credential authorization proof is missing or invalid.",
        )
        api_dispatches = proof.final_api.dispatches
        require(
            [
                d.model_dump(mode="json", exclude={"project_id", "workspace_id"})
                for d in sql.dispatches
            ]
            == [d.model_dump(mode="json") for d in api_dispatches],
            "API dispatch/lease state differs from independent SQL.",
        )
        tasks = {t.id: t for t in source.tasks}
        leases = [lease for d in sql.dispatches for lease in d.leases]
        unique(leases, "lease")
        require(len(leases) == 1, "Local verification must reuse one actual lease.")
        lease = leases[0]
        dispatch = next(d for d in sql.dispatches if d.task_id == lease.task_id)
        require(
            dispatch.project_id == source.project_id
            and dispatch.workspace_id == source.workspace_id
            and dispatch.run_id == source.run_id,
            "Dispatch crossed source scope.",
        )
        require(
            lease.task_id in tasks and tasks[lease.task_id].eligibility == "eligible",
            "A blocked or absent task was leased.",
        )
        require(
            all(tasks[d.task_id].eligibility == "eligible" for d in sql.dispatches),
            "Dependency-blocked task was dispatched.",
        )
        require(
            dispatch.state == "needs_reconciliation"
            and lease.state == "expired"
            and lease.acknowledged_at
            and lease.last_heartbeat_at
            and lease.ended_at,
            "Acknowledged crash recovery was not independently persisted.",
        )
        require(
            dispatch.fence_epoch > lease.fence_epoch and dispatch.attempts == 1,
            "Ownership was not fenced or duplicated.",
        )
        for received, expected_state in (
            (proof.acknowledged_api, "acknowledged"),
            (proof.heartbeat_api, "acknowledged"),
        ):
            require(
                received.lease.id == lease.id
                and received.lease.worker_id == proof.worker.id
                and received.lease.fence_epoch == lease.fence_epoch
                and received.lease.state == expected_state
                and not received.execution_performed,
                "Received lease contradicts SQL identity/state.",
            )
        require(
            proof.heartbeat_api.lease.last_heartbeat_at == lease.last_heartbeat_at,
            "Actual heartbeat missing from SQL lease.",
        )
        require(len(sql.handoffs) == 1, "Missing or duplicate handoff records.")
        handoff = sql.handoffs[0]
        manifest = handoff.manifest
        require(
            handoff.lease_id == lease.id == manifest.lease_id and manifest.handoff_id == handoff.id,
            "Handoff identity mismatch.",
        )
        require(
            manifest == proof.heartbeat_api.manifest == proof.acknowledged_api.manifest,
            "Immutable handoff changed across receipt.",
        )
        require(
            handoff.checksum
            == manifest.checksum
            == checksum(manifest.model_dump(mode="json", exclude={"checksum"})),
            "Canonical manifest checksum mismatch.",
        )
        require(
            manifest.worker_id == lease.worker_id == proof.worker.id
            and manifest.task_id == lease.task_id
            and manifest.run_id == run.id
            and manifest.workspace_id == run.workspace_id
            and manifest.project_id == run.project_id,
            "Manifest scope or ownership mismatch.",
        )
        task = tasks[lease.task_id]
        require(
            manifest.source_task_id == task.source_task_id
            and manifest.source_task_key == task.key
            and manifest.title == task.definition.title
            and manifest.description == task.definition.description
            and manifest.acceptance_criteria == task.definition.acceptance_criteria,
            "Manifest is not the immutable source task.",
        )
        require(
            manifest.architecture.id == run.architecture_id
            and manifest.architecture.version == run.architecture_version
            and manifest.architecture.revision == run.architecture_revision
            and manifest.architecture.hash == run.architecture_hash,
            "Manifest architecture source mismatch.",
        )
        require(
            manifest.product_plan.id == run.source_plan_id
            and manifest.product_plan.version == run.source_version
            and manifest.product_plan.revision == run.source_revision
            and manifest.product_plan.hash == run.source_hash
            and manifest.snapshot_hash == run.snapshot_hash,
            "Manifest PRD source mismatch.",
        )
        require(
            manifest.required_capability in proof.worker.capabilities
            and manifest.required_capability == task.definition.category
            and not manifest.dependencies,
            "Invalid root handoff capability or prerequisites.",
        )
        require(
            len(sql.heartbeats) >= 1 and all(h.lease_id == lease.id for h in sql.heartbeats),
            "Independent heartbeat records are missing.",
        )
        require(
            proof.stale_epoch_status == 409
            and proof.foreign_worker_status == 404
            and proof.unauthorized_user_status == 404
            and proof.revoked_worker_status == 401,
            "Negative authorization paths did not reject.",
        )
        require(
            proof.browser_rendered
            and proof.reload_persisted
            and proof.protected_ui_hidden
            and proof.incomplete_proof_rejected
            and not proof.executed_tasks
            and not proof.model_generation_requests
            and not proof.final_api.execution_performed,
            "Missing browser/negative checks or false execution claim.",
        )
        names = {c.name for c in proof.process_commands}
        require(
            {"provision", "worker-start", "scheduler-start", "worker-restart", "scheduler-restart"}
            <= names,
            "Required real processes/restarts are missing.",
        )
        require(
            all(
                c.pid > 0
                and c.started_at <= c.completed_at
                and (
                    (
                        c.name == "scheduler-interrupted"
                        and c.expected_termination
                        and (c.exit_code not in (None, 0) or c.signal is not None)
                    )
                    or (
                        not c.expected_termination
                        and type(c.exit_code) is int
                        and c.exit_code == 0
                        and c.signal is None
                    )
                )
                for c in proof.process_commands
            ),
            "A native protocol process failed or lacks an actual exit.",
        )
        require(
            "scheduler-interrupted" in names,
            "Actual pending scheduler termination was not observed.",
        )
        require(
            proof.started_at
            <= proof.foundation.started_at
            <= proof.foundation.completed_at
            <= proof.completed_at
            and proof.started_at <= sql.inspected_at <= proof.completed_at,
            "Evidence interval is inconsistent.",
        )
        cross_records(proof, raw)
        return data | {"foundation": foundation}
    except EvidenceError:
        raise
    except (ValidationError, KeyError, TypeError, ValueError, StopIteration, AttributeError):
        raise EvidenceError(
            "Scheduler proof is incomplete, malformed or contradictory; no success is certified."
        ) from None

"""Strict control-plane contracts. No execution result is accepted anywhere."""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, StrictBool, model_validator

Positive = Annotated[int, Field(strict=True, ge=1)]
Counter = Annotated[int, Field(strict=True, ge=0)]
Hash = Annotated[str, Field(strict=True, pattern=r"^[0-9a-f]{64}$")]
Capability = Literal[
    "frontend",
    "backend",
    "database",
    "infrastructure",
    "integration",
    "security",
    "testing",
    "documentation",
]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)


class SchedulerPolicy(Contract):
    acknowledge_seconds: Annotated[int, Field(strict=True, ge=2, le=60)] = 10
    lease_seconds: Annotated[int, Field(strict=True, ge=5, le=120)] = 30
    max_lease_seconds: Annotated[int, Field(strict=True, ge=10, le=600)] = 120
    heartbeat_seconds: Annotated[int, Field(strict=True, ge=1, le=30)] = 10
    worker_liveness_seconds: Annotated[int, Field(strict=True, ge=10, le=600)] = 60
    global_capacity: Annotated[int, Field(strict=True, ge=1, le=64)] = 8
    run_capacity: Annotated[int, Field(strict=True, ge=1, le=16)] = 2
    max_attempts: Annotated[int, Field(strict=True, ge=1, le=5)] = 3
    batch_size: Annotated[int, Field(strict=True, ge=1, le=32)] = 8

    @model_validator(mode="after")
    def deadlines(self):
        if not self.acknowledge_seconds < self.lease_seconds <= self.max_lease_seconds:
            raise ValueError(
                "Require acknowledgment deadline < lease duration <= hard lease maximum."
            )
        if self.heartbeat_seconds >= self.lease_seconds or self.run_capacity > self.global_capacity:
            raise ValueError(
                "Heartbeat interval must be below lease duration; run capacity must fit global capacity."
            )
        return self


class Provision(Contract):
    workspace_id: UUID
    project_id: UUID | None = None
    display_name: Annotated[str, Field(min_length=1, max_length=100)]
    capabilities: Annotated[list[Capability], Field(min_length=1, max_length=8)]
    max_leases: Annotated[int, Field(strict=True, ge=1, le=4)] = 1
    lifetime_seconds: Annotated[int, Field(strict=True, ge=60, le=2592000)] = 86400

    @model_validator(mode="after")
    def unique_capabilities(self):
        if not self.display_name.strip() or len(set(self.capabilities)) != len(self.capabilities):
            raise ValueError("A nonblank name and unique authorized capabilities are required.")
        return self


class SourceRef(Contract):
    id: UUID
    version: Positive
    revision: Positive
    hash: Hash


class DependencyContext(Contract):
    task_id: UUID
    source_task_key: str
    execution_status: Literal["awaiting_executor"]


class RequirementReference(Contract):
    source_trace_id: UUID
    story_id: UUID
    task_key: Annotated[str, Field(min_length=1, max_length=64)] | None
    component_key: Annotated[str, Field(min_length=1, max_length=64)] | None


class HandoffManifest(Contract):
    contract_version: Annotated[int, Field(strict=True, ge=1, le=1)]
    handoff_id: UUID
    worker_id: UUID
    workspace_id: UUID
    project_id: UUID
    run_id: UUID
    task_id: UUID
    source_task_id: UUID
    source_task_key: str
    architecture: SourceRef
    product_plan: SourceRef
    snapshot_hash: Hash
    title: Annotated[str, Field(min_length=1)]
    description: Annotated[str, Field(min_length=1)]
    acceptance_criteria: Annotated[list[str], Field(min_length=1)]
    requirement_traces: list[RequirementReference]
    dependencies: list[DependencyContext]
    required_capability: Capability
    lease_id: UUID
    fence_epoch: Positive
    acknowledge_by: AwareDatetime
    initial_expires_at: AwareDatetime
    max_expires_at: AwareDatetime
    execution_policy: Literal["protocol_only_no_execution"]
    checksum: Hash


class Claim(Contract):
    request_id: UUID
    run_id: UUID | None = None


class LeaseOperation(Contract):
    fence_epoch: Positive
    contract_version: Annotated[int, Field(strict=True, ge=1, le=1)]
    manifest_checksum: Hash


class Heartbeat(LeaseOperation):
    request_id: UUID


class WorkerRead(Contract):
    id: UUID
    worker_type: Literal["protocol_only"]
    display_name: str
    workspace_id: UUID
    project_id: UUID | None
    capabilities: list[Capability]
    max_leases: Positive
    enabled: StrictBool
    credential_version: Positive
    last_authenticated_at: AwareDatetime


class LeaseRead(Contract):
    id: UUID
    dispatch_id: UUID
    task_id: UUID
    run_id: UUID
    project_id: UUID
    workspace_id: UUID
    worker_id: UUID
    credential_version: Positive
    fence_epoch: Positive
    state: Literal["claimed", "acknowledged", "expired", "released", "revoked", "cancelled"]
    created_at: AwareDatetime
    acknowledge_by: AwareDatetime
    expires_at: AwareDatetime
    max_expires_at: AwareDatetime
    acknowledged_at: AwareDatetime | None
    last_heartbeat_at: AwareDatetime | None
    ended_at: AwareDatetime | None
    reason: str | None


class HandoffRead(Contract):
    lease: LeaseRead
    manifest: HandoffManifest
    execution_performed: Literal[False] = False


class DispatchRead(Contract):
    id: UUID
    task_id: UUID
    run_id: UUID
    required_capability: Capability
    state: Literal[
        "queued", "withdrawn", "leased", "needs_reconciliation", "exhausted", "cancelled"
    ]
    attempts: Counter
    fence_epoch: Counter
    created_at: AwareDatetime
    updated_at: AwareDatetime
    leases: list[LeaseRead]
    worker_name: str | None


class SchedulerRead(Contract):
    run_id: UUID
    snapshot_hash: Hash
    observed_at: AwareDatetime
    last_tick_at: AwareDatetime | None
    tick_count: Counter
    policy: SchedulerPolicy | None
    dispatches: list[DispatchRead]
    execution_performed: Literal[False] = False


class ControlDetails(Contract):
    execution_performed: Literal[False]
    dispatch_id: UUID | None
    lease_id: UUID | None
    worker_id: UUID | None
    fence_epoch: Counter | None
    reason: Annotated[str, Field(min_length=1, max_length=64)]


def validate_control_event(event):
    from orba.scheduler_models import BASE_EVENTS, CONTROL_EVENTS

    if not isinstance(event.details, dict):
        return False
    if (
        type(event.details.get("execution_performed")) is not bool
        or event.details["execution_performed"] is not False
    ):
        return False
    if event.event_type in BASE_EVENTS:
        return event.details == {"execution_performed": False}
    if event.event_type not in CONTROL_EVENTS:
        return False
    data = ControlDetails.model_validate(event.details)
    if event.actor_type != "system" or event.actor_id is not None:
        return False
    if event.event_type != "scheduler_recovered" and (
        not event.task_id or not data.dispatch_id or data.fence_epoch is None
    ):
        return False
    if event.event_type.startswith(("lease_", "handoff_", "worker_")) and (
        not data.lease_id or not data.worker_id or not data.fence_epoch
    ):
        return False
    return event.previous_state == event.new_state == "awaiting_executor"


def lease_read(lease):
    return LeaseRead.model_validate(lease, from_attributes=True).model_dump(mode="json")


def json_time(moment: datetime):
    return moment.isoformat()

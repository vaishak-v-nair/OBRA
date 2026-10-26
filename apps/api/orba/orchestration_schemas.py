"""Typed control-plane contracts. No executor result or completion input exists."""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from orba.architect_schemas import Task
from orba.pm_schemas import RequestModel

RunState = Literal["created", "awaiting_executor", "cancelled"]
Eligibility = Literal["eligible", "waiting_prerequisites"]
ExecutionState = Literal["awaiting_executor", "cancelled"]


class RunCreate(RequestModel):
    client_request_id: UUID
    architecture_id: UUID
    architecture_version: Annotated[int, Field(ge=1)]
    architecture_revision: Annotated[int, Field(ge=1)]


class RunCancel(RequestModel):
    expected_revision: Annotated[int, Field(ge=1)]


class RunRead(BaseModel):
    id: UUID
    project_id: UUID
    workspace_id: UUID
    architecture_id: UUID
    architecture_version: int
    architecture_revision: int
    architecture_hash: str
    source_plan_id: UUID
    source_version: int
    source_revision: int
    source_hash: str
    creator_id: UUID
    client_request_id: UUID
    snapshot_hash: str
    hash_version: str
    status: RunState
    revision: int
    last_event_sequence: int
    created_at: datetime
    updated_at: datetime
    cancelled_at: datetime | None
    execution_performed: Literal[False] = False


class TaskRead(BaseModel):
    id: UUID
    run_id: UUID
    source_task_id: UUID
    key: str
    definition: Task
    eligibility: Eligibility
    execution_status: ExecutionState
    display_order: int
    created_at: datetime
    updated_at: datetime


class GraphNode(BaseModel):
    key: str
    eligibility: Eligibility
    execution_status: ExecutionState
    explanation: str
    prerequisites: list[str]
    dependents: list[str]
    ancestors: list[str]
    impact: list[str]


class GraphRead(BaseModel):
    valid: Literal[True]
    edge_convention: Literal["prerequisite -> dependent"]
    topological_order: list[str]
    roots: list[str]
    eligible: list[str]
    blocked: list[str]
    nodes: list[GraphNode]
    edges: list[dict[str, str]]
    execution_performed: Literal[False]


class RunDetail(RunRead):
    tasks: list[TaskRead]
    graph: GraphRead
    source_current: bool


class TasksRead(BaseModel):
    run_id: UUID
    snapshot_hash: str
    items: list[TaskRead]


class EventRead(BaseModel):
    id: UUID
    run_id: UUID
    task_id: UUID | None
    sequence: int
    run_revision: int
    event_type: Literal[
        "run_created",
        "run_awaiting_executor",
        "run_cancelled",
        "task_cancelled",
        "dispatch_queued",
        "dispatch_withdrawn",
        "lease_claimed",
        "handoff_available",
        "handoff_acknowledged",
        "lease_renewed",
        "lease_expired",
        "lease_released",
        "lease_revoked",
        "worker_lease_rejected",
        "worker_disabled",
        "task_requires_reconciliation",
        "dispatch_exhausted",
        "scheduler_recovered",
    ]
    actor_type: Literal["system", "user"]
    actor_id: UUID | None
    occurred_at: datetime
    previous_state: str | None
    new_state: str
    details: dict


class EventsRead(BaseModel):
    run_id: UUID
    items: list[EventRead]
    next_sequence: int | None

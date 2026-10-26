"""Durable ownership only. These records never certify engineering execution."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from orba.db import Base

CONTROL_EVENTS = (
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
)
BASE_EVENTS = ("run_created", "run_awaiting_executor", "run_cancelled", "task_cancelled")
EVENT_CHECK = "event_type IN (" + ",".join(repr(x) for x in BASE_EVENTS + CONTROL_EVENTS) + ")"


class WorkerIdentity(Base):
    __tablename__ = "worker_identities"
    __table_args__ = (
        UniqueConstraint("id", "workspace_id", name="uq_worker_workspace"),
        ForeignKeyConstraint(
            ["project_id", "workspace_id"],
            ["projects.id", "projects.workspace_id"],
            name="fk_worker_project_scope",
        ),
        CheckConstraint("worker_type='protocol_only'", name="worker_type"),
        CheckConstraint(
            "max_leases BETWEEN 1 AND 4 AND credential_version > 0", name="worker_limits"
        ),
        CheckConstraint(
            "jsonb_typeof(capabilities)='array' AND jsonb_array_length(capabilities)>0",
            name="worker_capabilities",
        ),
        Index("ix_worker_scope", "workspace_id", "enabled"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id"))
    project_id: Mapped[UUID | None]
    worker_type: Mapped[str] = mapped_column(String(32), default="protocol_only")
    display_name: Mapped[str] = mapped_column(String(100))
    capabilities: Mapped[list] = mapped_column(JSONB)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    max_leases: Mapped[int] = mapped_column(Integer, default=1)
    credential_version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_authenticated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class WorkerCredential(Base):
    __tablename__ = "worker_credentials"
    __table_args__ = (
        UniqueConstraint("id", "worker_id", "version", name="uq_worker_credential_owner"),
        UniqueConstraint("worker_id", "version", name="uq_worker_credential_version"),
        CheckConstraint(
            "version > 0 AND token_hash ~ '^[0-9a-f]{64}$'", name="worker_credential_hash"
        ),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True)
    worker_id: Mapped[UUID] = mapped_column(ForeignKey("worker_identities.id"))
    version: Mapped[int]
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class SchedulerState(Base):
    __tablename__ = "scheduler_state"
    __table_args__ = (CheckConstraint("id=1 AND tick_count >= 0", name="scheduler_singleton"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    policy: Mapped[dict | None] = mapped_column(JSONB)
    tick_count: Mapped[int] = mapped_column(Integer, default=0)
    last_tick_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    process_id: Mapped[UUID | None]


class TaskDispatch(Base):
    __tablename__ = "task_dispatches"
    __table_args__ = (
        UniqueConstraint("task_id", name="uq_dispatch_task"),
        UniqueConstraint("id", "task_id", "run_id", "project_id", name="uq_dispatch_owner"),
        ForeignKeyConstraint(
            ["task_id", "run_id", "project_id"],
            [
                "orchestration_tasks.id",
                "orchestration_tasks.run_id",
                "orchestration_tasks.project_id",
            ],
            name="fk_dispatch_task",
        ),
        ForeignKeyConstraint(
            ["project_id", "workspace_id"],
            ["projects.id", "projects.workspace_id"],
            name="fk_dispatch_workspace",
        ),
        CheckConstraint(
            "state IN ('queued','withdrawn','leased','needs_reconciliation','exhausted','cancelled')",
            name="dispatch_state",
        ),
        CheckConstraint("attempts >= 0 AND fence_epoch >= 0", name="dispatch_counters"),
        Index("ix_dispatch_state", "state", "created_at"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    task_id: Mapped[UUID]
    run_id: Mapped[UUID]
    project_id: Mapped[UUID]
    workspace_id: Mapped[UUID]
    required_capability: Mapped[str] = mapped_column(String(32))
    state: Mapped[str] = mapped_column(String(32))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    fence_epoch: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class TaskLease(Base):
    __tablename__ = "task_leases"
    __table_args__ = (
        ForeignKeyConstraint(
            ["dispatch_id", "task_id", "run_id", "project_id"],
            [
                "task_dispatches.id",
                "task_dispatches.task_id",
                "task_dispatches.run_id",
                "task_dispatches.project_id",
            ],
            name="fk_lease_dispatch",
        ),
        ForeignKeyConstraint(
            ["worker_id", "workspace_id"],
            ["worker_identities.id", "worker_identities.workspace_id"],
            name="fk_lease_worker_scope",
        ),
        ForeignKeyConstraint(
            ["credential_id", "worker_id", "credential_version"],
            ["worker_credentials.id", "worker_credentials.worker_id", "worker_credentials.version"],
            name="fk_lease_credential",
        ),
        ForeignKeyConstraint(
            ["project_id", "workspace_id"],
            ["projects.id", "projects.workspace_id"],
            name="fk_lease_workspace",
        ),
        CheckConstraint("fence_epoch > 0", name="lease_epoch"),
        CheckConstraint(
            "state IN ('claimed','acknowledged','expired','released','revoked','cancelled')",
            name="lease_state",
        ),
        CheckConstraint(
            "created_at < acknowledge_by AND acknowledge_by < max_expires_at AND expires_at <= max_expires_at AND created_at < expires_at",
            name="lease_deadlines",
        ),
        CheckConstraint(
            "(state IN ('claimed','acknowledged')) = (ended_at IS NULL)", name="lease_terminal"
        ),
        Index(
            "uq_active_task_lease",
            "task_id",
            unique=True,
            postgresql_where=text("state IN ('claimed','acknowledged')"),
        ),
        Index("ix_lease_worker_state", "worker_id", "state"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    dispatch_id: Mapped[UUID]
    task_id: Mapped[UUID]
    run_id: Mapped[UUID]
    project_id: Mapped[UUID]
    workspace_id: Mapped[UUID]
    worker_id: Mapped[UUID]
    credential_id: Mapped[UUID]
    credential_version: Mapped[int]
    fence_epoch: Mapped[int]
    state: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    acknowledge_by: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    max_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reason: Mapped[str | None] = mapped_column(String(64))


class HandoffRecord(Base):
    __tablename__ = "handoff_records"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    lease_id: Mapped[UUID] = mapped_column(ForeignKey("task_leases.id"), unique=True)
    manifest: Mapped[dict] = mapped_column(JSONB)
    checksum: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    __table_args__ = (CheckConstraint("checksum ~ '^[0-9a-f]{64}$'", name="handoff_checksum"),)


class ClaimRequest(Base):
    __tablename__ = "worker_claim_requests"
    __table_args__ = (UniqueConstraint("worker_id", "request_id", name="uq_worker_claim_request"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    worker_id: Mapped[UUID] = mapped_column(ForeignKey("worker_identities.id"))
    request_id: Mapped[UUID]
    request_hash: Mapped[str] = mapped_column(String(64))
    lease_id: Mapped[UUID] = mapped_column(ForeignKey("task_leases.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class LeaseHeartbeat(Base):
    __tablename__ = "lease_heartbeats"
    __table_args__ = (
        UniqueConstraint("lease_id", "request_id", name="uq_lease_heartbeat_request"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    lease_id: Mapped[UUID] = mapped_column(ForeignKey("task_leases.id"))
    request_id: Mapped[UUID]
    request_hash: Mapped[str] = mapped_column(String(64))
    accepted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

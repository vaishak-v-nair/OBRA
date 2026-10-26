"""Stage05A control plane. Definitions are snapshots; no execution evidence exists."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from orba.db import Base
from orba.scheduler_models import EVENT_CHECK


class OrchestrationRun(Base):
    __tablename__ = "orchestration_runs"
    __table_args__ = (
        UniqueConstraint("id", "project_id", name="uq_orch_run_project"),
        UniqueConstraint("id", "project_id", "architecture_id", name="uq_orch_run_architecture"),
        UniqueConstraint("project_id", "creator_id", "client_request_id", name="uq_orch_request"),
        ForeignKeyConstraint(
            ["project_id", "workspace_id"],
            ["projects.id", "projects.workspace_id"],
            name="fk_orch_workspace",
        ),
        ForeignKeyConstraint(
            ["architecture_id", "project_id", "source_plan_id"],
            [
                "architecture_versions.id",
                "architecture_versions.project_id",
                "architecture_versions.source_plan_id",
            ],
            name="fk_orch_architecture",
        ),
        CheckConstraint(
            "status IN ('created','awaiting_executor','cancelled')", name="orch_status"
        ),
        CheckConstraint("revision > 0 AND last_event_sequence >= 0", name="orch_counters"),
        CheckConstraint(
            "architecture_version > 0 AND architecture_revision > 0 AND source_version > 0 AND source_revision > 0",
            name="orch_source_versions",
        ),
        CheckConstraint(
            "(status = 'cancelled') = (cancelled_at IS NOT NULL)", name="orch_cancellation"
        ),
        Index("ix_orch_project_time", "project_id", "created_at", "id"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID]
    workspace_id: Mapped[UUID]
    architecture_id: Mapped[UUID]
    architecture_version: Mapped[int]
    architecture_revision: Mapped[int]
    architecture_hash: Mapped[str] = mapped_column(String(64))
    source_plan_id: Mapped[UUID]
    source_version: Mapped[int]
    source_revision: Mapped[int]
    source_hash: Mapped[str] = mapped_column(String(64))
    creator_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    client_request_id: Mapped[UUID]
    request_hash: Mapped[str] = mapped_column(String(64))
    snapshot_hash: Mapped[str] = mapped_column(String(64))
    hash_version: Mapped[str] = mapped_column(String(64))
    source_snapshot: Mapped[dict] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(32), default="created")
    revision: Mapped[int] = mapped_column(Integer, default=1)
    last_event_sequence: Mapped[int] = mapped_column(Integer, default=0)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class OrchestrationTask(Base):
    __tablename__ = "orchestration_tasks"
    __table_args__ = (
        UniqueConstraint("id", "run_id", "project_id", name="uq_orch_task_owner"),
        UniqueConstraint("run_id", "key", name="uq_orch_task_key"),
        UniqueConstraint("run_id", "source_task_id", name="uq_orch_task_source"),
        ForeignKeyConstraint(
            ["run_id", "project_id", "architecture_id"],
            [
                "orchestration_runs.id",
                "orchestration_runs.project_id",
                "orchestration_runs.architecture_id",
            ],
            name="fk_orch_task_run",
        ),
        ForeignKeyConstraint(
            ["source_task_id", "architecture_id", "project_id"],
            [
                "engineering_tasks.id",
                "engineering_tasks.architecture_id",
                "engineering_tasks.project_id",
            ],
            name="fk_orch_task_source",
        ),
        CheckConstraint(
            "eligibility IN ('eligible','waiting_prerequisites')", name="orch_task_eligibility"
        ),
        CheckConstraint(
            "execution_status IN ('awaiting_executor','cancelled')", name="orch_task_execution"
        ),
        CheckConstraint("display_order >= 0", name="orch_task_order"),
        Index("ix_orch_task_run_order", "run_id", "display_order"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    run_id: Mapped[UUID]
    project_id: Mapped[UUID]
    architecture_id: Mapped[UUID]
    source_task_id: Mapped[UUID]
    key: Mapped[str] = mapped_column(String(64))
    # One task definition, including title/description/criteria/priority/category/traces.
    # These are materialized from the immutable source snapshot for bounded queries.
    definition: Mapped[dict] = mapped_column(JSONB)
    display_order: Mapped[int]
    eligibility: Mapped[str] = mapped_column(String(32))
    execution_status: Mapped[str] = mapped_column(String(32), default="awaiting_executor")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class OrchestrationDependency(Base):
    __tablename__ = "orchestration_dependencies"
    __table_args__ = (
        UniqueConstraint("run_id", "prerequisite_id", "dependent_id", name="uq_orch_edge"),
        ForeignKeyConstraint(
            ["run_id", "project_id"],
            ["orchestration_runs.id", "orchestration_runs.project_id"],
            name="fk_orch_edge_run",
        ),
        ForeignKeyConstraint(
            ["prerequisite_id", "run_id", "project_id"],
            [
                "orchestration_tasks.id",
                "orchestration_tasks.run_id",
                "orchestration_tasks.project_id",
            ],
            name="fk_orch_prerequisite",
        ),
        ForeignKeyConstraint(
            ["dependent_id", "run_id", "project_id"],
            [
                "orchestration_tasks.id",
                "orchestration_tasks.run_id",
                "orchestration_tasks.project_id",
            ],
            name="fk_orch_dependent",
        ),
        CheckConstraint("prerequisite_id != dependent_id", name="orch_edge_self"),
        CheckConstraint("display_order >= 0", name="orch_edge_order"),
        Index("ix_orch_edge_run", "run_id"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    run_id: Mapped[UUID]
    project_id: Mapped[UUID]
    source_dependency_id: Mapped[UUID] = mapped_column(ForeignKey("task_dependencies.id"))
    prerequisite_id: Mapped[UUID]
    dependent_id: Mapped[UUID]
    display_order: Mapped[int]


class OrchestrationEvent(Base):
    __tablename__ = "orchestration_events"
    __table_args__ = (
        UniqueConstraint("run_id", "sequence", name="uq_orch_event_sequence"),
        ForeignKeyConstraint(
            ["run_id", "project_id"],
            ["orchestration_runs.id", "orchestration_runs.project_id"],
            name="fk_orch_event_run",
        ),
        ForeignKeyConstraint(
            ["task_id", "run_id", "project_id"],
            [
                "orchestration_tasks.id",
                "orchestration_tasks.run_id",
                "orchestration_tasks.project_id",
            ],
            name="fk_orch_event_task",
        ),
        CheckConstraint("sequence > 0 AND run_revision > 0", name="orch_event_counters"),
        CheckConstraint(
            EVENT_CHECK,
            name="orch_event_type",
        ),
        CheckConstraint(
            "(actor_type='system' AND actor_id IS NULL) OR (actor_type='user' AND actor_id IS NOT NULL)",
            name="orch_event_actor",
        ),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    run_id: Mapped[UUID]
    project_id: Mapped[UUID]
    task_id: Mapped[UUID | None]
    sequence: Mapped[int]
    run_revision: Mapped[int]
    event_type: Mapped[str] = mapped_column(String(40))
    actor_type: Mapped[str] = mapped_column(String(16))
    actor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    previous_state: Mapped[str | None] = mapped_column(String(32))
    new_state: Mapped[str] = mapped_column(String(32))
    details: Mapped[dict] = mapped_column(JSONB)

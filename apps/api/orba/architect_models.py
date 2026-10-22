"""Additive Architect persistence. All tasks are unexecuted planning proposals."""

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
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from orba.db import Base
from orba.models import Timestamps


class ArchitectRun(Base):
    __tablename__ = "architect_runs"
    __table_args__ = (
        UniqueConstraint("id", "project_id", name="uq_arch_run_project"),
        UniqueConstraint("project_id", "initiator_id", "client_request_id", name="uq_arch_request"),
        ForeignKeyConstraint(
            ["project_id", "workspace_id"],
            ["projects.id", "projects.workspace_id"],
            name="fk_arch_run_workspace",
        ),
        ForeignKeyConstraint(
            ["source_plan_id", "project_id"],
            ["product_plans.id", "product_plans.project_id"],
            name="fk_arch_run_source",
        ),
        CheckConstraint(
            "status IN ('pending','running','succeeded','failed','interrupted')",
            name="arch_run_status",
        ),
        CheckConstraint(
            "(status IN ('pending','running') AND completed_at IS NULL) OR (status IN ('succeeded','failed','interrupted') AND completed_at IS NOT NULL)",
            name="arch_run_completion",
        ),
        CheckConstraint(
            "status != 'succeeded' OR (error_category IS NULL AND started_at IS NOT NULL)",
            name="arch_run_success_metadata",
        ),
        CheckConstraint(
            "source_version > 0 AND source_revision > 0", name="arch_run_source_versions"
        ),
        Index(
            "uq_arch_project_active",
            "project_id",
            unique=True,
            postgresql_where=text("status IN ('pending','running')"),
        ),
        Index(
            "ix_arch_active_deadline",
            "deadline_at",
            postgresql_where=text("status IN ('pending','running')"),
        ),
        Index("ix_arch_actor_time", "initiator_id", "created_at"),
        Index("ix_arch_project_time", "project_id", "created_at"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID]
    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id"))
    source_plan_id: Mapped[UUID]
    source_version: Mapped[int]
    source_revision: Mapped[int]
    source_hash: Mapped[str] = mapped_column(String(64))
    initiator_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    initiating_session_id: Mapped[UUID] = mapped_column(ForeignKey("sessions.id"))
    executor_id: Mapped[UUID] = mapped_column(default=uuid4)
    client_request_id: Mapped[UUID]
    request_hash: Mapped[str] = mapped_column(String(64))
    snapshot_hash: Mapped[str] = mapped_column(String(64))
    input_snapshot: Mapped[dict] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    provider: Mapped[str] = mapped_column(String(40))
    requested_model: Mapped[str | None] = mapped_column(String(160))
    returned_model: Mapped[str | None] = mapped_column(String(160))
    prompt_version: Mapped[str] = mapped_column(String(40))
    prompt_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deadline_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    provider_response_id: Mapped[str | None] = mapped_column(String(200))
    provider_request_id: Mapped[str | None] = mapped_column(String(200))
    usage: Mapped[dict | None] = mapped_column(JSONB)
    error_category: Mapped[str | None] = mapped_column(String(60))
    diagnostic_id: Mapped[UUID | None]
    diagnostic: Mapped[dict | None] = mapped_column(JSONB)


class ArchitectureVersion(Timestamps, Base):
    __tablename__ = "architecture_versions"
    __table_args__ = (
        UniqueConstraint("id", "project_id", name="uq_arch_version_project"),
        UniqueConstraint("id", "project_id", "source_plan_id", name="uq_arch_version_source"),
        UniqueConstraint("project_id", "version", name="uq_arch_version"),
        UniqueConstraint("generating_run_id", name="uq_arch_version_run"),
        UniqueConstraint(
            "project_id", "creator_id", "copy_request_id", name="uq_arch_copy_request"
        ),
        ForeignKeyConstraint(
            ["source_plan_id", "project_id"],
            ["product_plans.id", "product_plans.project_id"],
            name="fk_arch_version_source",
        ),
        ForeignKeyConstraint(
            ["generating_run_id", "project_id"],
            ["architect_runs.id", "architect_runs.project_id"],
            name="fk_arch_version_run",
        ),
        ForeignKeyConstraint(
            ["copied_from_id", "project_id"],
            ["architecture_versions.id", "architecture_versions.project_id"],
            name="fk_arch_copy_source",
        ),
        CheckConstraint("state IN ('draft','approved','superseded')", name="arch_version_state"),
        CheckConstraint(
            "version > 0 AND revision > 0 AND source_version > 0 AND source_revision > 0",
            name="arch_positive_versions",
        ),
        CheckConstraint(
            "(state='draft' AND approved_by IS NULL AND approved_at IS NULL) OR (state IN ('approved','superseded') AND approved_by IS NOT NULL AND approved_at IS NOT NULL)",
            name="arch_approval_metadata",
        ),
        CheckConstraint(
            "generating_run_id IS NULL OR copied_from_id IS NULL", name="arch_single_origin"
        ),
        Index(
            "uq_arch_current_approved",
            "project_id",
            unique=True,
            postgresql_where=text("state='approved'"),
        ),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    source_plan_id: Mapped[UUID]
    source_version: Mapped[int]
    source_revision: Mapped[int]
    source_hash: Mapped[str] = mapped_column(String(64))
    version: Mapped[int] = mapped_column(Integer)
    revision: Mapped[int] = mapped_column(Integer, default=1)
    state: Mapped[str] = mapped_column(String(20), default="draft")
    content: Mapped[dict] = mapped_column(JSONB)
    content_hash: Mapped[str] = mapped_column(String(64))
    hash_version: Mapped[str] = mapped_column(String(64))
    generating_run_id: Mapped[UUID | None]
    copied_from_id: Mapped[UUID | None]
    copy_request_id: Mapped[UUID | None]
    copy_request_hash: Mapped[str | None] = mapped_column(String(64))
    creator_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    editor_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    approved_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approval_dispositions: Mapped[dict | None] = mapped_column(JSONB)


class ArchitectureComponent(Base):
    __tablename__ = "architecture_components"
    __table_args__ = (
        UniqueConstraint("id", "architecture_id", "project_id", name="uq_arch_component_owner"),
        UniqueConstraint("architecture_id", "key", name="uq_arch_component_key"),
        ForeignKeyConstraint(
            ["architecture_id", "project_id"],
            ["architecture_versions.id", "architecture_versions.project_id"],
            name="fk_arch_component_owner",
        ),
        CheckConstraint("display_order >= 0", name="arch_component_order"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    architecture_id: Mapped[UUID] = mapped_column(index=True)
    project_id: Mapped[UUID]
    key: Mapped[str] = mapped_column(String(64))
    content: Mapped[dict] = mapped_column(JSONB)
    display_order: Mapped[int]


class EngineeringTask(Base):
    __tablename__ = "engineering_tasks"
    __table_args__ = (
        UniqueConstraint("id", "architecture_id", "project_id", name="uq_eng_task_owner"),
        UniqueConstraint("architecture_id", "key", name="uq_eng_task_key"),
        ForeignKeyConstraint(
            ["architecture_id", "project_id"],
            ["architecture_versions.id", "architecture_versions.project_id"],
            name="fk_eng_task_owner",
        ),
        CheckConstraint(
            "planning_state IN ('proposed','needs_clarification')", name="eng_task_planning_state"
        ),
        CheckConstraint(
            "priority IN ('P0','P1','P2','P3') AND display_order >= 0",
            name="eng_task_priority_order",
        ),
        CheckConstraint(
            "category IN ('frontend','backend','database','infrastructure','integration','security','testing','documentation')",
            name="eng_task_category",
        ),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    architecture_id: Mapped[UUID] = mapped_column(index=True)
    project_id: Mapped[UUID]
    key: Mapped[str] = mapped_column(String(64))
    planning_state: Mapped[str] = mapped_column(String(24))
    priority: Mapped[str] = mapped_column(String(2))
    category: Mapped[str] = mapped_column(String(24))
    content: Mapped[dict] = mapped_column(JSONB)
    display_order: Mapped[int]


class TaskDependency(Base):
    __tablename__ = "task_dependencies"
    __table_args__ = (
        UniqueConstraint(
            "architecture_id", "prerequisite_id", "dependent_id", name="uq_task_dependency"
        ),
        ForeignKeyConstraint(
            ["prerequisite_id", "architecture_id", "project_id"],
            [
                "engineering_tasks.id",
                "engineering_tasks.architecture_id",
                "engineering_tasks.project_id",
            ],
            name="fk_dependency_prerequisite",
        ),
        ForeignKeyConstraint(
            ["dependent_id", "architecture_id", "project_id"],
            [
                "engineering_tasks.id",
                "engineering_tasks.architecture_id",
                "engineering_tasks.project_id",
            ],
            name="fk_dependency_dependent",
        ),
        CheckConstraint("prerequisite_id != dependent_id", name="dependency_not_self"),
        CheckConstraint("display_order >= 0", name="dependency_order"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    architecture_id: Mapped[UUID] = mapped_column(index=True)
    project_id: Mapped[UUID]
    prerequisite_id: Mapped[UUID]
    dependent_id: Mapped[UUID]
    display_order: Mapped[int]


class RequirementTrace(Base):
    __tablename__ = "requirement_traces"
    __table_args__ = (
        ForeignKeyConstraint(
            ["architecture_id", "project_id", "source_plan_id"],
            [
                "architecture_versions.id",
                "architecture_versions.project_id",
                "architecture_versions.source_plan_id",
            ],
            name="fk_trace_source_owner",
        ),
        ForeignKeyConstraint(
            ["story_id", "source_plan_id"],
            ["product_stories.id", "product_stories.plan_id"],
            name="fk_trace_source_story",
        ),
        ForeignKeyConstraint(
            ["task_id", "architecture_id", "project_id"],
            [
                "engineering_tasks.id",
                "engineering_tasks.architecture_id",
                "engineering_tasks.project_id",
            ],
            name="fk_trace_task",
        ),
        ForeignKeyConstraint(
            ["component_id", "architecture_id", "project_id"],
            [
                "architecture_components.id",
                "architecture_components.architecture_id",
                "architecture_components.project_id",
            ],
            name="fk_trace_component",
        ),
        UniqueConstraint("architecture_id", "story_id", "task_id", name="uq_trace_task_story"),
        UniqueConstraint(
            "architecture_id", "story_id", "component_id", name="uq_trace_component_story"
        ),
        CheckConstraint("(task_id IS NULL) != (component_id IS NULL)", name="trace_one_target"),
        CheckConstraint("display_order >= 0", name="trace_order"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    architecture_id: Mapped[UUID] = mapped_column(index=True)
    project_id: Mapped[UUID]
    source_plan_id: Mapped[UUID]
    story_id: Mapped[UUID]
    task_id: Mapped[UUID | None]
    component_id: Mapped[UUID | None]
    display_order: Mapped[int]

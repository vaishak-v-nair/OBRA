"""PM persistence: one root document, relational backlog, immutable execution inputs."""

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
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from orba.db import Base
from orba.models import Timestamps


class ProductManagerRun(Base):
    __tablename__ = "product_manager_runs"
    __table_args__ = (
        UniqueConstraint("id", "project_id", name="uq_pm_run_project"),
        UniqueConstraint("project_id", "initiator_id", "client_request_id", name="uq_pm_request"),
        ForeignKeyConstraint(
            ["project_id", "workspace_id"],
            ["projects.id", "projects.workspace_id"],
            name="fk_pm_run_project_workspace",
        ),
        CheckConstraint(
            "status IN ('pending','running','succeeded','failed','interrupted')",
            name="pm_run_status",
        ),
        CheckConstraint(
            "(status IN ('pending','running') AND completed_at IS NULL) OR (status IN ('succeeded','failed','interrupted') AND completed_at IS NOT NULL)",
            name="pm_run_completion",
        ),
        CheckConstraint(
            "status != 'succeeded' OR (error_category IS NULL AND started_at IS NOT NULL)",
            name="pm_run_success_metadata",
        ),
        Index(
            "uq_pm_project_active",
            "project_id",
            unique=True,
            postgresql_where=text("status IN ('pending','running')"),
        ),
        Index(
            "ix_pm_active_deadline",
            "deadline_at",
            postgresql_where=text("status IN ('pending','running')"),
        ),
        Index("ix_pm_runs_actor_time", "initiator_id", "created_at"),
        Index("ix_pm_runs_project_time", "project_id", "created_at"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(index=True)
    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id"))
    initiator_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    initiating_session_id: Mapped[UUID] = mapped_column(ForeignKey("sessions.id"))
    executor_id: Mapped[UUID] = mapped_column(default=uuid4)
    client_request_id: Mapped[UUID]
    request_hash: Mapped[str] = mapped_column(String(64))
    snapshot_hash: Mapped[str] = mapped_column(String(64))
    hash_version: Mapped[str] = mapped_column(String(64))
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


class ProductPlan(Timestamps, Base):
    __tablename__ = "product_plans"
    __table_args__ = (
        UniqueConstraint("id", "project_id", name="uq_pm_plan_project"),
        UniqueConstraint("project_id", "version", name="uq_pm_plan_version"),
        UniqueConstraint("generating_run_id", name="uq_pm_plan_run"),
        UniqueConstraint("project_id", "creator_id", "copy_request_id", name="uq_pm_copy_request"),
        ForeignKeyConstraint(
            ["generating_run_id", "project_id"],
            ["product_manager_runs.id", "product_manager_runs.project_id"],
            name="fk_pm_plan_run_project",
        ),
        ForeignKeyConstraint(
            ["source_plan_id", "project_id"],
            ["product_plans.id", "product_plans.project_id"],
            name="fk_pm_plan_source_project",
        ),
        CheckConstraint("state IN ('draft','approved','superseded')", name="pm_plan_state"),
        CheckConstraint("version > 0 AND revision > 0", name="pm_plan_positive_versions"),
        CheckConstraint(
            "(state='draft' AND approved_by IS NULL AND approved_at IS NULL) OR (state IN ('approved','superseded') AND approved_by IS NOT NULL AND approved_at IS NOT NULL)",
            name="pm_plan_approval_metadata",
        ),
        CheckConstraint(
            "generating_run_id IS NULL OR source_plan_id IS NULL", name="pm_plan_single_origin"
        ),
        Index(
            "uq_pm_current_approved",
            "project_id",
            unique=True,
            postgresql_where=text("state='approved'"),
        ),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    version: Mapped[int] = mapped_column(Integer)
    revision: Mapped[int] = mapped_column(Integer, default=1)
    state: Mapped[str] = mapped_column(String(20), default="draft")
    content: Mapped[dict] = mapped_column(JSONB)
    content_hash: Mapped[str] = mapped_column(String(64))
    hash_version: Mapped[str] = mapped_column(String(64))
    generating_run_id: Mapped[UUID | None]
    source_plan_id: Mapped[UUID | None]
    source_revision: Mapped[int | None]
    source_hash: Mapped[str | None] = mapped_column(String(64))
    copy_request_id: Mapped[UUID | None]
    copy_request_hash: Mapped[str | None] = mapped_column(String(64))
    creator_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    editor_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    approved_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ProductEpic(Base):
    __tablename__ = "product_epics"
    __table_args__ = (
        UniqueConstraint("id", "plan_id", name="uq_pm_epic_plan"),
        UniqueConstraint("plan_id", "key", name="uq_pm_epic_key"),
        CheckConstraint(
            "priority IN ('P0','P1','P2','P3') AND display_order >= 0",
            name="pm_epic_order_priority",
        ),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    plan_id: Mapped[UUID] = mapped_column(ForeignKey("product_plans.id"), index=True)
    key: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(200))
    goal: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(2))
    source: Mapped[dict] = mapped_column(JSONB)
    display_order: Mapped[int]


class ProductStory(Base):
    __tablename__ = "product_stories"
    __table_args__ = (
        UniqueConstraint("id", "plan_id", name="uq_pm_story_plan"),
        UniqueConstraint("plan_id", "key", name="uq_pm_story_key"),
        ForeignKeyConstraint(
            ["epic_id", "plan_id"],
            ["product_epics.id", "product_epics.plan_id"],
            name="fk_pm_story_epic_plan",
        ),
        CheckConstraint(
            "priority IN ('P0','P1','P2','P3') AND display_order >= 0",
            name="pm_story_order_priority",
        ),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    plan_id: Mapped[UUID] = mapped_column(ForeignKey("product_plans.id"), index=True)
    epic_id: Mapped[UUID] = mapped_column(index=True)
    key: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(200))
    statement: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(2))
    requirement_refs: Mapped[list] = mapped_column(JSONB)
    dependencies: Mapped[list] = mapped_column(JSONB)
    source: Mapped[dict] = mapped_column(JSONB)
    display_order: Mapped[int]


class ProductCriterion(Base):
    __tablename__ = "product_acceptance_criteria"
    __table_args__ = (
        UniqueConstraint("plan_id", "key", name="uq_pm_criterion_key"),
        ForeignKeyConstraint(
            ["story_id", "plan_id"],
            ["product_stories.id", "product_stories.plan_id"],
            name="fk_pm_criterion_story_plan",
        ),
        CheckConstraint("display_order >= 0", name="pm_criterion_order"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    plan_id: Mapped[UUID] = mapped_column(ForeignKey("product_plans.id"), index=True)
    story_id: Mapped[UUID] = mapped_column(index=True)
    key: Mapped[str] = mapped_column(String(64))
    given: Mapped[str] = mapped_column(Text)
    when: Mapped[str] = mapped_column(Text)
    then: Mapped[str] = mapped_column(Text)
    source: Mapped[dict] = mapped_column(JSONB)
    display_order: Mapped[int]

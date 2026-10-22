"""Independent repeatable-read, read-only SQL evidence; no model or approval writes."""

import argparse
import json
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from orba.architect_models import (
    ArchitectRun,
    ArchitectureVersion,
    EngineeringTask,
    TaskDependency,
)
from orba.db import make_engine
from orba.models import Project, WorkspaceMember
from orba.pm_models import (
    ProductCriterion,
    ProductEpic,
    ProductManagerRun,
    ProductPlan,
    ProductStory,
)
from orba.pm_repository import content_hash, read_document
from scripts.prepare_tests import TEST_URL
from scripts.test_database import guard_test_url


def inspect(project_id, plan_id, actor_id):
    guard_test_url(TEST_URL)
    engine = make_engine(TEST_URL)
    try:
        with Session(engine) as db:
            db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY"))
            project, plan = db.get(Project, project_id), db.get(ProductPlan, plan_id)
            if project is None or plan is None or plan.project_id != project.id:
                raise ValueError("Exact project and source plan do not match.")
            member = db.scalar(
                select(WorkspaceMember).where(
                    WorkspaceMember.workspace_id == project.workspace_id,
                    WorkspaceMember.user_id == actor_id,
                )
            )
            if member is None:
                raise ValueError("Actor is not a member of the source workspace.")
            document = read_document(db, plan)
            if content_hash(document) != plan.content_hash:
                raise ValueError("Stored source hash does not match its relational document.")
            current = db.scalar(
                select(ProductPlan.id).where(
                    ProductPlan.project_id == project.id, ProductPlan.state == "approved"
                )
            )
            return {
                "source": "independent PostgreSQL repeatable-read read-only transaction",
                "project_id": str(project.id),
                "workspace_id": str(project.workspace_id),
                "actor_id": str(actor_id),
                "role": member.role,
                "plan_id": str(plan.id),
                "version": plan.version,
                "revision": plan.revision,
                "state": plan.state,
                "content_hash": plan.content_hash,
                "origin": "human_authored"
                if plan.generating_run_id is None and plan.source_plan_id is None
                else "other",
                "approved_by": str(plan.approved_by) if plan.approved_by else None,
                "approved_at": plan.approved_at.isoformat() if plan.approved_at else None,
                "current_approved_plan_id": str(current) if current else None,
                "document_validated": True,
                "counts": {
                    model.__tablename__: db.scalar(
                        select(func.count()).select_from(model).where(model.plan_id == plan.id)
                    )
                    for model in (ProductEpic, ProductStory, ProductCriterion)
                },
                # These totals concern only the explicitly guarded, isolated test database.
                "generation_records": {
                    model.__tablename__: db.scalar(select(func.count()).select_from(model))
                    for model in (
                        ProductManagerRun,
                        ArchitectRun,
                        ArchitectureVersion,
                        EngineeringTask,
                        TaskDependency,
                    )
                },
            }
    finally:
        engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("project", "plan", "actor"):
        parser.add_argument(f"--{name}", type=UUID, required=True)
    args = parser.parse_args()
    print(json.dumps(inspect(args.project, args.plan, args.actor)))


if __name__ == "__main__":
    main()

"""Read only safe verification metadata from the GUARDED test DB, never dev data."""

import argparse
import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from orba.db import make_engine
from orba.models import Project
from orba.pm_models import (
    ProductCriterion,
    ProductEpic,
    ProductManagerRun,
    ProductPlan,
    ProductStory,
)
from orba.pm_repository import content_hash, read_document
from orba.pm_schemas import validate_generated
from scripts.prepare_tests import TEST_URL
from scripts.test_database import guard_test_url


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=UUID, required=True)
    parser.add_argument("--expect-state", choices=("draft", "approved"))
    args = parser.parse_args()
    guard_test_url(TEST_URL)
    engine = make_engine(TEST_URL)
    with Session(engine) as db:
        run = db.get(ProductManagerRun, args.run)
        if not run:
            raise SystemExit("Run not found in the guarded test database.")
        plans = db.scalars(
            select(ProductPlan).where(ProductPlan.project_id == run.project_id)
        ).all()
        result = {
            "source": "fresh SQLAlchemy session against guarded PostgreSQL",
            "run_id": str(run.id),
            "project_id": str(run.project_id),
            "status": run.status,
            "provider": run.provider,
            "workspace_id": str(run.workspace_id),
            "initiator_id": str(run.initiator_id),
            "provider_response_id": run.provider_response_id,
            "provider_request_id": run.provider_request_id,
            "usage": run.usage,
            "prompt_version": run.prompt_version,
            "prompt_hash": run.prompt_hash,
            "hash_version": run.hash_version,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            "requested_model": run.requested_model,
            "returned_model": run.returned_model,
            "error_category": run.error_category,
            "diagnostic_id": str(run.diagnostic_id) if run.diagnostic_id else None,
            "diagnostic": run.diagnostic,
            "project_plans": [
                {
                    "id": str(p.id),
                    "version": p.version,
                    "state": p.state,
                    "generating_run_id": str(p.generating_run_id) if p.generating_run_id else None,
                    "content_hash": p.content_hash,
                    "approved_at": p.approved_at.isoformat() if p.approved_at else None,
                }
                for p in plans
            ],
        }
        if args.expect_state:
            plan = next((p for p in plans if p.generating_run_id == run.id), None)
            if run.status != "succeeded" or plan is None or plan.state != args.expect_state:
                raise SystemExit("Run/plan has not reached the expected persisted state.")
            project = db.get(Project, run.project_id)
            assert project.workspace_id == run.workspace_id
            document = read_document(db, plan)  # Reconstruct relational graph, then Pydantic.
            assert content_hash(document) == plan.content_hash
            epics = db.scalars(select(ProductEpic).where(ProductEpic.plan_id == plan.id)).all()
            stories = db.scalars(select(ProductStory).where(ProductStory.plan_id == plan.id)).all()
            criteria = db.scalars(
                select(ProductCriterion).where(ProductCriterion.plan_id == plan.id)
            ).all()
            assert all(s.epic_id in {e.id for e in epics} for s in stories)
            assert all(c.story_id in {s.id for s in stories} for c in criteria)
            counts = {"epics": len(epics), "stories": len(stories), "criteria": len(criteria)}
            assert counts == {
                "epics": len(document.epics),
                "stories": sum(len(e.stories) for e in document.epics),
                "criteria": sum(
                    len(s.acceptance_criteria) for e in document.epics for s in e.stories
                ),
            }
            if args.expect_state == "draft":
                assert plan.revision == 1 and plan.approved_by is None and plan.approved_at is None
                validate_generated(document, run.input_snapshot)
            else:
                assert (
                    plan.revision == 2 and plan.approved_by == run.initiator_id and plan.approved_at
                )
                assert not any(
                    c.blocking and c.disposition == "unresolved" for c in document.confirmations
                )
            result |= {
                "graph_validated": True,
                "plan_id": str(plan.id),
                "state": plan.state,
                "version": plan.version,
                "revision": plan.revision,
                "counts": counts,
                "content_hash": content_hash(document),
                "approved_by": str(plan.approved_by) if plan.approved_by else None,
                "approved_at": plan.approved_at.isoformat() if plan.approved_at else None,
            }
    engine.dispose()
    print(json.dumps(result))


if __name__ == "__main__":
    main()

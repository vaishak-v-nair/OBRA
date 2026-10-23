"""Author a draft architecture ONLY in guarded orba_test; never fake a model run/approval."""

import argparse
import json
from uuid import UUID

from sqlalchemy.orm import Session

from orba.architect_repository import create_architecture
from orba.db import make_engine
from orba.pm import safe_document
from orba.pm_models import ProductPlan
from orba.pm_service import lock_project
from scripts.architect_sample import controlled_document
from scripts.prepare_tests import TEST_URL
from scripts.test_database import guard_test_url


def seed(project_id, actor_id, plan_id):
    guard_test_url(TEST_URL)
    engine = make_engine(TEST_URL)
    try:
        with Session(engine) as db, db.begin():
            lock_project(db, project_id, actor_id)
            source = db.get(ProductPlan, plan_id)
            if (
                not source
                or source.project_id != project_id
                or source.state != "approved"
                or not source.approved_by
                or not source.approved_at
            ):
                raise ValueError("An actual approved same-project Product Plan is required.")
            safe_document(db, source)
            document = controlled_document()
            document.overview.title = "Habit journal — human-authored orchestration fixture"
            architecture = create_architecture(db, project_id, actor_id, source, document)
            value = {
                "id": str(architecture.id),
                "version": architecture.version,
                "revision": architecture.revision,
                "state": architecture.state,
                "source_plan_id": str(source.id),
                "origin": "human_authored_test_fixture",
                "model_requests": 0,
            }
        return value
    finally:
        engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=UUID, required=True)
    parser.add_argument("--actor", type=UUID, required=True)
    parser.add_argument("--plan", type=UUID, required=True)
    args = parser.parse_args()
    print(json.dumps(seed(args.project, args.actor, args.plan)))


if __name__ == "__main__":
    main()

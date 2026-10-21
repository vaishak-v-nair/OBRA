"""Seed a HUMAN-authored plan for real editor/browser tests; no fake AI run."""

import argparse
import json
from uuid import UUID

from sqlalchemy.orm import Session

from orba.db import make_engine
from orba.pm_repository import create_plan
from orba.pm_service import lock_project
from scripts.pm_sample import human_document
from scripts.prepare_tests import TEST_URL
from scripts.test_database import guard_test_url


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=UUID, required=True)
    parser.add_argument("--actor", type=UUID, required=True)
    parser.add_argument("--blocking-confirmation", action="store_true")
    args = parser.parse_args()
    guard_test_url(TEST_URL)
    engine = make_engine(TEST_URL)
    with Session(engine) as db, db.begin():
        lock_project(db, args.project, args.actor)
        plan = create_plan(
            db,
            args.project,
            args.actor,
            human_document(args.actor, blocking_confirmation=args.blocking_confirmation),
        )
        value = {
            "plan_id": str(plan.id),
            "version": plan.version,
            "origin": "human_authored",
            "model_call": False,
        }
    engine.dispose()
    print(json.dumps(value))


if __name__ == "__main__":
    main()

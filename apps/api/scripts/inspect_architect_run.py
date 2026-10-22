"""Independent read-only SQL audit of guarded test data. No provider requests."""

import argparse
import json
from uuid import UUID

from sqlalchemy import func, select

from orba.architect_models import (
    ArchitectRun,
    ArchitectureComponent,
    ArchitectureVersion,
    EngineeringTask,
    RequirementTrace,
    TaskDependency,
)
from orba.architect_repository import get_architecture, run_summary, safe_document
from orba.db import make_engine
from orba.pm_service import phase
from scripts.prepare_tests import TEST_URL
from scripts.test_database import guard_test_url


def inspect(run_id):
    guard_test_url(TEST_URL)
    engine = make_engine(TEST_URL)
    try:
        with phase(engine) as db:
            run = db.get(ArchitectRun, run_id)
            if run is None:
                raise ValueError("Test run not found")
            value = run_summary(db, run)
            value.update(
                snapshot_sha256=run.snapshot_hash,
                prompt_sha256=run.prompt_hash,
                diagnostic=run.diagnostic,
            )
            value["project_architectures"] = [
                {
                    "id": str(row.id),
                    "state": row.state,
                    "content_hash": row.content_hash,
                    "version": row.version,
                    "revision": row.revision,
                }
                for row in db.scalars(
                    select(ArchitectureVersion)
                    .where(ArchitectureVersion.project_id == run.project_id)
                    .order_by(ArchitectureVersion.version)
                )
            ]
            if value["architecture_id"]:
                artifact = get_architecture(db, run.project_id, value["architecture_id"])
                document, _, current, report = safe_document(db, artifact)
                value.update(
                    architecture_validated=True,
                    source_current=current,
                    content_hash=artifact.content_hash,
                    state=artifact.state,
                    version=artifact.version,
                    revision=artifact.revision,
                    approved_by=artifact.approved_by,
                    approved_at=artifact.approved_at,
                    counts={
                        model.__tablename__: db.scalar(
                            select(func.count())
                            .select_from(model)
                            .where(model.architecture_id == artifact.id)
                        )
                        for model in (
                            ArchitectureComponent,
                            EngineeringTask,
                            TaskDependency,
                            RequirementTrace,
                        )
                    },
                    coverage_approvable=report["approvable"],
                    task_keys=[task.key for task in document.tasks],
                    graph_valid=True,
                    execution_performed=False,
                )
            return json.loads(json.dumps(value, default=str))
    finally:
        engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=UUID, required=True)
    args = parser.parse_args()
    print(json.dumps(inspect(args.run), default=str))


if __name__ == "__main__":
    main()

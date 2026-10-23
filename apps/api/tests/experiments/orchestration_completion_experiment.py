"""DELIBERATELY INCORRECT. Explicit pytest invocation must exit1, outside discovery."""

from uuid import UUID

from sqlalchemy.orm import Session

from orba.orchestration_models import OrchestrationTask
from tests.orchestration_support import initialize


def test_incorrect_completion_claim(client):
    _, _, _, run = initialize(client)
    with Session(client.app.state.engine) as db:
        task = db.get(OrchestrationTask, UUID(run["tasks"][0]["id"]))
        print(
            f"ACTUAL_EVIDENCE run_id={task.run_id} task_id={task.id} execution_status={task.execution_status} execution_performed=False"
        )
        assert task.execution_status == "verified_complete", (
            "DELIBERATELY INCORRECT: eligibility is not verified execution completion"
        )

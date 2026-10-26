"""Deliberately incorrect assertion. Invoke explicitly; actual pytest exit1 required."""

from uuid import UUID

from sqlalchemy.orm import Session

from orba.orchestration_models import OrchestrationTask
from tests.scheduler_support import acquire, act, ready


def test_acknowledged_handoff_is_not_verified_engineering_completion(client):
    _, run, _, _, headers = ready(client)
    response = acquire(client, run, headers)
    assert response.status_code == 201
    handoff = response.json()
    assert act(client, handoff, headers).status_code == 200
    with Session(client.app.state.engine) as db:
        task = db.get(OrchestrationTask, UUID(handoff["lease"]["task_id"]))
        assert task.execution_status == "verified_complete"

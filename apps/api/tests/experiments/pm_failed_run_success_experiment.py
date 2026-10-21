"""INTENTIONALLY WRONG ASSERTION. Explicit-only invocation must exit 1.

This is not a production failure or part of normal pytest discovery.
"""

from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from orba.config import Settings
from orba.pm_models import ProductManagerRun


def test_incorrectly_expect_configuration_failure_to_be_success(client):
    client.app.state.settings = Settings(
        database_url=client.app.state.settings.database_url, pm_api_key=None, pm_model=None
    )
    project = client.post(
        "/api/v1/projects",
        json={
            "workspace_id": client.workspace_id,
            "title": "Failure experiment",
            "description": "No configured provider",
        },
    ).json()
    response = client.post(
        f"/api/v1/projects/{project['id']}/pm-runs",
        json={"client_request_id": str(uuid4()), "brief": "Track a daily habit"},
    )
    assert response.status_code == 503
    with Session(client.app.state.engine) as db:
        run = db.get(ProductManagerRun, UUID(response.json()["error"]["run_id"]))
        assert run.status == "succeeded", "Intentionally incorrect: the actual saved run is failed."

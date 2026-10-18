"""EXPECTED FAIL: explicit-only experiment. Not discovered by the normal suite."""

from uuid import UUID

from sqlalchemy.orm import Session
from test_auth_workspaces import account

from orba.models import Project


def test_deliberately_wrong_unauthorized_success_expectation(client):
    project = client.post(
        "/api/v1/projects",
        json={
            "title": "Private experiment",
            "description": "Never share",
            "workspace_id": client.workspace_id,
        },
    ).json()
    other, _ = account(client.app, "experiment-outsider@example.com")
    denied = other.get(f"/api/v1/projects/{project['id']}")
    with Session(client.app.state.engine) as db:
        assert db.get(Project, UUID(project["id"])).title == "Private experiment"
    other.close()
    assert denied.status_code == 200, (
        "Deliberately incorrect expectation: unauthorized access must never succeed."
    )

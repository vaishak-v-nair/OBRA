from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from orba.config import Settings
from orba.main import create_app
from orba.models import Project

PAYLOAD = {"title": "ORBA integration project", "description": "A real persisted project."}


def test_creation_persists_in_postgresql(client):
    response = client.post(
        "/api/v1/projects", json={**PAYLOAD, "workspace_id": client.workspace_id}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "created"
    assert data["created_at"] and data["updated_at"]
    with Session(client.app.state.engine) as independent_session:
        saved = independent_session.get(Project, UUID(data["id"]))
        assert saved is not None
        assert saved.title == PAYLOAD["title"]
        assert saved.description == PAYLOAD["description"]


def test_listing_actual_records_and_pagination(client):
    first = client.post(
        "/api/v1/projects", json={**PAYLOAD, "workspace_id": client.workspace_id}
    ).json()
    second = client.post(
        "/api/v1/projects", json={**PAYLOAD, "title": "Second", "workspace_id": client.workspace_id}
    ).json()
    response = client.get(f"/api/v1/projects?workspace_id={client.workspace_id}")
    assert response.status_code == 200
    assert [p["id"] for p in response.json()] == [second["id"], first["id"]]
    assert client.get(
        f"/api/v1/projects?workspace_id={client.workspace_id}&limit=1&offset=1"
    ).json() == [first]


def test_retrieval_correct_data(client):
    created = client.post(
        "/api/v1/projects", json={**PAYLOAD, "workspace_id": client.workspace_id}
    ).json()
    response = client.get(f"/api/v1/projects/{created['id']}")
    assert response.status_code == 200
    assert response.json() == created


@pytest.mark.parametrize(
    "payload",
    [
        {**PAYLOAD, "title": "   "},
        {**PAYLOAD, "description": "\n\t"},
        {**PAYLOAD, "title": "x" * 121},
        {**PAYLOAD, "description": "x" * 10001},
        {"title": "Missing description"},
        {**PAYLOAD, "status": "completed"},
        {**PAYLOAD, "title": None},
    ],
)
def test_validation_rejects_without_persisting(client, payload):
    response = client.post(
        "/api/v1/projects", json={**payload, "workspace_id": client.workspace_id}
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert response.json()["error"]["details"]
    with Session(client.app.state.engine) as session:
        assert session.scalar(select(func.count()).select_from(Project)) == 0


def test_trims_input(client):
    response = client.post(
        "/api/v1/projects",
        json={"title": "  Hello  ", "description": " World ", "workspace_id": client.workspace_id},
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Hello"
    assert response.json()["description"] == "World"


def test_nonexistent_project(client):
    response = client.get(f"/api/v1/projects/{uuid4()}")
    assert response.status_code == 404
    assert response.json() == {"error": {"code": "not_found", "message": "Project not found."}}


def test_malformed_uuid_and_pagination(client):
    for url in [
        "/api/v1/projects/not-a-uuid",
        "/api/v1/projects?limit=101",
        "/api/v1/projects?offset=-1",
    ]:
        response = client.get(url)
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "validation_error"


def test_live_and_ready_with_migrated_database(client):
    assert client.get("/health/live").json() == {"status": "alive"}
    assert client.get("/health/ready").status_code == 200
    assert client.get("/health/ready").json() == {"status": "ready"}


def test_real_unavailable_database_returns_503_and_liveness_survives():
    # Real TCP connection failure, no mock, patch or SQLite substitution.
    app = create_app(
        Settings(
            database_url="postgresql+psycopg://orba_test:orba_test_local@127.0.0.1:1/orba_test"
        )
    )
    with TestClient(app) as client:
        client.cookies.set("orba_session", "unavailable-probe")
        assert client.get("/health/live").status_code == 200
        for method, path, kwargs in [
            ("get", "/health/ready", {}),
            ("get", "/api/v1/projects", {}),
            (
                "post",
                "/api/v1/projects",
                {"json": PAYLOAD, "headers": {"Origin": "http://localhost:3000"}},
            ),
        ]:
            response = getattr(client, method)(path, **kwargs)
            assert response.status_code == 503
            assert response.json()["error"]["code"] == "database_unavailable"
            assert "password" not in response.text

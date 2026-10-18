import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url

from orba.config import Settings
from orba.main import create_app
from scripts.prepare_tests import prepare

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://orba_test:orba_test_local@127.0.0.1:54330/orba_test",
)
# Never truncate an arbitrary database supplied by a developer's environment.
if make_url(TEST_DATABASE_URL).database != "orba_test":
    raise RuntimeError("Integration tests require the isolated orba_test database.")


@pytest.fixture(scope="session")
def migrated_database():
    prepare(reset=False)


@pytest.fixture
def raw_client(migrated_database):
    prepare()
    app = create_app(Settings(database_url=TEST_DATABASE_URL))
    with TestClient(app) as test_client:
        yield test_client


def csrf(client):
    token = client.get("/api/v1/auth/csrf").json()["csrf_token"]
    client.headers.update({"Origin": "http://localhost:3000", "X-CSRF-Token": token})


def register(client, email="owner@example.com"):
    csrf(client)
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "A long test password!", "display_name": "Test Owner"},
    )
    assert response.status_code == 201, response.text
    csrf(client)
    return response.json()


@pytest.fixture
def client(raw_client):
    register(raw_client)
    response = raw_client.post("/api/v1/workspaces", json={"name": "Stage One"})
    assert response.status_code == 201, response.text
    raw_client.workspace_id = response.json()["id"]
    yield raw_client

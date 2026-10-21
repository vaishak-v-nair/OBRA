import os
import socket
import subprocess
import sys
from uuid import UUID, uuid4

import pytest
from alembic import command
from alembic.config import Config
from conftest import TEST_DATABASE_URL, register
from sqlalchemy import text
from sqlalchemy.orm import Session

from orba.db import make_engine
from orba.migration_safety import require_stopped_api
from orba.models import Project
from scripts.claim_legacy import LEGACY_ID


def test_upgrade_guard_requires_actual_api_port_to_be_offline():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        port = listener.getsockname()[1]
        with pytest.raises(RuntimeError, match="Stop the local API"):
            require_stopped_api(port)
    require_stopped_api(port)


def test_stage01_migration_preserves_every_original_field():
    # Fresh schema in the guarded real test DB; never downgrade/drop development data.
    schema = "migration_probe_" + uuid4().hex
    engine = make_engine(TEST_DATABASE_URL)
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        connection.execute(text(f'SET LOCAL search_path TO "{schema}"'))
        config = Config("alembic.ini")
        config.attributes["connection"] = connection
        command.upgrade(config, "0001")
        project_id = uuid4()
        connection.execute(
            text(
                "INSERT INTO projects (id,title,description,status,created_at,updated_at) VALUES (:id,'Legacy title','Original description','created','2025-01-01T00:00:00Z','2025-02-01T00:00:00Z')"
            ),
            {"id": project_id},
        )
        original = connection.execute(text("SELECT * FROM projects")).mappings().one()
        command.upgrade(config, "head")
        migrated = connection.execute(text("SELECT * FROM projects")).mappings().one()
        assert all(migrated[key] == value for key, value in original.items())
        assert migrated["workspace_id"] == LEGACY_ID and migrated["creator_id"] is None
        assert connection.scalar(text("SELECT count(*) FROM workspace_members")) == 0
        command.upgrade(config, "head")
        assert connection.scalar(text("SELECT count(*) FROM projects")) == 1
        connection.execute(text("SET LOCAL search_path TO public"))
        connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
    engine.dispose()


def test_legacy_is_hidden_and_operator_claim_is_explicit(client):
    with Session(client.app.state.engine) as db:
        legacy = Project(
            title="Restricted legacy", description="Preserved body", workspace_id=LEGACY_ID
        )
        db.add(legacy)
        db.commit()
        db.refresh(legacy)
        project_id, created_at, updated_at = legacy.id, legacy.created_at, legacy.updated_at
    assert client.get(f"/api/v1/projects/{project_id}").status_code == 404
    assert client.get(f"/api/v1/projects?workspace_id={LEGACY_ID}").status_code == 404
    assert str(LEGACY_ID) not in client.get("/api/v1/workspaces").text
    owner = client.get("/api/v1/auth/me").json()["id"]
    args = [
        sys.executable,
        "-m",
        "scripts.claim_legacy",
        "--workspace",
        client.workspace_id,
        "--owner",
        owner,
        "--project",
        str(project_id),
    ]
    env = {**os.environ, "DATABASE_URL": TEST_DATABASE_URL}
    mixed = subprocess.run(
        [*args, "--project", str(uuid4()), "--apply"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert mixed.returncode != 0
    assert client.get(f"/api/v1/projects/{project_id}").status_code == 404
    dry_run = subprocess.run(args, env=env, capture_output=True, text=True, check=False)
    assert dry_run.returncode == 0 and '"applied": false' in dry_run.stdout
    assert client.get(f"/api/v1/projects/{project_id}").status_code == 404
    applied = subprocess.run(
        [*args, "--apply"], env=env, capture_output=True, text=True, check=False
    )
    assert applied.returncode == 0 and '"applied": true' in applied.stdout
    assert client.get(f"/api/v1/projects/{project_id}").status_code == 200
    with Session(client.app.state.engine) as db:
        saved = db.get(Project, project_id)
        assert (
            saved.id == project_id
            and saved.title == "Restricted legacy"
            and saved.description == "Preserved body"
        )
        assert saved.created_at == created_at and saved.updated_at == updated_at
        assert saved.workspace_id == UUID(client.workspace_id) and saved.creator_id == UUID(owner)
    second = subprocess.run(
        [*args, "--apply"], env=env, capture_output=True, text=True, check=False
    )
    assert second.returncode != 0  # Already claimed; never silently moves it again.


def test_first_registration_does_not_gain_existing_legacy_projects(raw_client):
    with Session(raw_client.app.state.engine) as db:
        legacy = Project(
            title="Predates all users", description="Existing Stage01 data", workspace_id=LEGACY_ID
        )
        db.add(legacy)
        db.commit()
        project_id = legacy.id
    register(raw_client, "first-new-user@example.com")
    assert raw_client.get("/api/v1/workspaces").json() == []
    assert raw_client.get(f"/api/v1/projects/{project_id}").status_code == 404
    with Session(raw_client.app.state.engine) as db:
        saved = db.get(Project, project_id)
        assert saved.workspace_id == LEGACY_ID and saved.creator_id is None
        assert saved.title == "Predates all users" and saved.description == "Existing Stage01 data"


def test_populated_stage02_schema_and_records_survive_stage03(client):
    """Upgrade a separate guarded-test schema; never downgrade the development DB."""
    import json

    client.post(
        "/api/v1/projects",
        json={
            "title": "Populated Stage02",
            "description": "Preserve this exact record",
            "workspace_id": client.workspace_id,
        },
    ).raise_for_status()
    schema = "stage02_probe_" + uuid4().hex
    tables = (
        "users",
        "workspaces",
        "workspace_members",
        "sessions",
        "login_attempts",
        "workspace_invitations",
        "projects",
    )
    engine = make_engine(TEST_DATABASE_URL)
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        connection.execute(text(f'SET LOCAL search_path TO "{schema}"'))
        config = Config("alembic.ini")
        config.attributes["connection"] = connection
        command.upgrade(config, "0febbe526f54")
        for table in tables:
            connection.execute(
                text(
                    f'INSERT INTO "{schema}".{table} SELECT * FROM public.{table} ON CONFLICT DO NOTHING'
                )
            )

        def snapshot():
            return {
                table: sorted(
                    json.dumps(row, sort_keys=True)
                    for row in connection.scalars(
                        text(f'SELECT to_jsonb(t) FROM "{schema}".{table} t')
                    )
                )
                for table in tables
            }

        before = snapshot()
        assert len(before["users"]) == 1 and len(before["projects"]) == 1
        command.upgrade(config, "head")
        assert snapshot() == before
        command.upgrade(config, "head")
        assert snapshot() == before
        assert connection.scalar(text("SELECT count(*) FROM product_manager_runs")) == 0
        assert connection.scalar(text("SELECT count(*) FROM product_plans")) == 0
        connection.execute(text("SET LOCAL search_path TO public"))
        connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
    engine.dispose()

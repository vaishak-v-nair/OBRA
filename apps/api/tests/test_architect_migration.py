"""Real Alembic upgrade in a fresh schema of the guarded orba_test database only."""

import hashlib
from datetime import UTC, datetime
from uuid import uuid4

from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.orm import Session

from orba.db import make_engine
from orba.models import Project, User, Workspace, WorkspaceMember
from orba.pm_repository import create_plan
from orba.security import passwords
from scripts.pm_sample import human_document
from scripts.test_database import guard_test_url
from tests.conftest import TEST_DATABASE_URL


def test_additive_upgrade_preserves_user_project_and_approved_prd_graph():
    guard_test_url(TEST_DATABASE_URL)
    schema = "architect_migration_" + uuid4().hex
    engine = make_engine(TEST_DATABASE_URL)
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        connection.execute(text(f'SET LOCAL search_path TO "{schema}"'))
        config = Config("alembic.ini")
        config.attributes["connection"] = connection
        command.upgrade(config, "ab3987da8961")
        with Session(bind=connection, join_transaction_mode="create_savepoint") as db, db.begin():
            actor = User(
                email="migration@example.com",
                display_name="Migration fixture",
                password_hash=passwords.hash("Migration passphrase!"),
            )
            db.add(actor)
            db.flush()
            workspace = Workspace(
                name="Preserved workspace", slug="migration-fixture", creator_id=actor.id
            )
            db.add(workspace)
            db.flush()
            db.add(WorkspaceMember(workspace_id=workspace.id, user_id=actor.id, role="owner"))
            project = Project(
                title="Preserved title",
                description="Preserved Stage03 description",
                workspace_id=workspace.id,
                creator_id=actor.id,
            )
            db.add(project)
            db.flush()
            plan = create_plan(db, project.id, actor.id, human_document(actor.id))
            plan.state = "approved"
            plan.approved_by = actor.id
            plan.approved_at = datetime.now(UTC)
            db.flush()
        names = [
            "users",
            "workspaces",
            "workspace_members",
            "projects",
            "product_plans",
            "product_epics",
            "product_stories",
            "product_acceptance_criteria",
        ]

        def snapshot():
            return {
                name: hashlib.sha256(
                    connection.scalar(
                        text(
                            "SELECT coalesce(jsonb_agg(to_jsonb(t) ORDER BY id),'[]'::jsonb)::text FROM "
                            + name
                            + " t"
                        )
                    ).encode()
                ).hexdigest()
                for name in names
            }

        before = snapshot()
        command.upgrade(config, "head")
        assert before == snapshot()
        assert connection.scalar(text("SELECT count(*) FROM architecture_versions")) == 0
        command.upgrade(config, "head")
        assert before == snapshot()
        connection.execute(text("SET LOCAL search_path TO public"))
        connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
    engine.dispose()

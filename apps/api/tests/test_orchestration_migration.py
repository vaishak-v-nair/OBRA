"""Real additive upgrade from Stage04 with unchanged source rows in a guarded test schema."""

import hashlib
from datetime import UTC, datetime
from uuid import uuid4

from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.orm import Session

from orba.architect_repository import create_architecture
from orba.db import make_engine
from orba.models import Project, User, Workspace, WorkspaceMember
from orba.pm_repository import create_plan
from orba.security import passwords
from scripts.architect_sample import controlled_document
from scripts.pm_sample import human_document
from scripts.test_database import guard_test_url
from tests.conftest import TEST_DATABASE_URL


def test_stage04_source_rows_survive_additive_orchestration_migration():
    guard_test_url(TEST_DATABASE_URL)
    schema = "orchestration_migration_" + uuid4().hex
    engine = make_engine(TEST_DATABASE_URL)
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        connection.execute(text(f'SET LOCAL search_path TO "{schema}"'))
        config = Config("alembic.ini")
        config.attributes["connection"] = connection
        command.upgrade(config, "7dd7671f9417")
        with Session(bind=connection, join_transaction_mode="create_savepoint") as db, db.begin():
            actor = User(
                email="migration05a@example.com",
                display_name="Authored fixture",
                password_hash=passwords.hash("Migration preserved password"),
            )
            db.add(actor)
            db.flush()
            workspace = Workspace(name="Preserved05A", slug="migration05a", creator_id=actor.id)
            db.add(workspace)
            db.flush()
            db.add(WorkspaceMember(workspace_id=workspace.id, user_id=actor.id, role="owner"))
            project = Project(
                title="Preserve source",
                description="Original project",
                workspace_id=workspace.id,
                creator_id=actor.id,
            )
            db.add(project)
            db.flush()
            plan = create_plan(db, project.id, actor.id, human_document(actor.id))
            plan.state, plan.approved_by, plan.approved_at = "approved", actor.id, datetime.now(UTC)
            db.flush()
            architecture = create_architecture(
                db, project.id, actor.id, plan, controlled_document()
            )
            (
                architecture.state,
                architecture.approved_by,
                architecture.approved_at,
                architecture.approval_dispositions,
            ) = "approved", actor.id, datetime.now(UTC), {}
            db.flush()
        tables = [
            "users",
            "projects",
            "workspaces",
            "workspace_members",
            "product_plans",
            "product_epics",
            "product_stories",
            "product_acceptance_criteria",
            "architecture_versions",
            "architecture_components",
            "engineering_tasks",
            "task_dependencies",
            "requirement_traces",
        ]

        def hashes():
            return {
                table: hashlib.sha256(
                    connection.scalar(
                        text(
                            f"SELECT coalesce(jsonb_agg(to_jsonb(t) ORDER BY id),'[]'::jsonb)::text FROM {table} t"
                        )
                    ).encode()
                ).hexdigest()
                for table in tables
            }

        before = hashes()
        command.upgrade(config, "head")
        assert hashes() == before
        command.upgrade(config, "head")
        assert hashes() == before
        assert connection.scalar(text("SELECT count(*) FROM orchestration_runs")) == 0
        assert connection.scalar(text("SELECT count(*) FROM orchestration_events")) == 0
        connection.execute(text("SET LOCAL search_path TO public"))
        connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
    engine.dispose()

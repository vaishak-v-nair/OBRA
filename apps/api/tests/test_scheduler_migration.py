"""Forward-only migration preserves actual approved sources and05A snapshot rows."""

import hashlib
from uuid import uuid4

from alembic import command
from alembic.config import Config
from sqlalchemy import text

from orba.db import make_engine
from scripts.test_database import guard_test_url
from tests.conftest import TEST_DATABASE_URL
from tests.orchestration_support import initialize


def test_stage05a_snapshot_and_events_survive_scheduler_migration(client):
    _, _, _, run = initialize(client)
    guard_test_url(TEST_DATABASE_URL)
    schema = "scheduler_migration_" + uuid4().hex
    tables = [
        "users",
        "workspaces",
        "sessions",
        "workspace_members",
        "workspace_invitations",
        "login_attempts",
        "projects",
        "product_manager_runs",
        "product_plans",
        "product_epics",
        "product_stories",
        "product_acceptance_criteria",
        "architect_runs",
        "architecture_versions",
        "architecture_components",
        "engineering_tasks",
        "task_dependencies",
        "requirement_traces",
        "orchestration_runs",
        "orchestration_tasks",
        "orchestration_dependencies",
        "orchestration_events",
    ]
    engine = make_engine(TEST_DATABASE_URL)
    try:
        with engine.connect() as db:
            transaction = db.begin()
            try:
                db.execute(text(f'CREATE SCHEMA "{schema}"'))
                db.execute(text(f'SET LOCAL search_path TO "{schema}"'))
                config = Config("alembic.ini")
                config.attributes["connection"] = db
                command.upgrade(config, "f9e997d59bb4")
                assert db.scalar(text("SELECT current_schema()")) == schema
                db.execute(
                    text("TRUNCATE " + ",".join(f'"{schema}"."{table}"' for table in tables))
                )
                for table in tables:
                    if table == "orchestration_runs":
                        columns = [
                            row[0]
                            for row in db.execute(
                                text(
                                    "SELECT column_name FROM information_schema.columns WHERE table_schema=:schema AND table_name='orchestration_runs' ORDER BY ordinal_position"
                                ),
                                {"schema": schema},
                            )
                        ]
                        projection = ",".join(
                            "'created'" if c == "status" else "1" if c == "revision" else f'"{c}"'
                            for c in columns
                        )
                        db.execute(
                            text(f'INSERT INTO "{table}" SELECT {projection} FROM public."{table}"')
                        )
                    else:
                        db.execute(text(f'INSERT INTO "{table}" SELECT * FROM public."{table}"'))
                db.execute(
                    text("UPDATE orchestration_runs SET status='awaiting_executor',revision=2")
                )

                def hashes():
                    return {
                        table: hashlib.sha256(
                            db.scalar(
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
                assert (
                    db.scalar(
                        text("SELECT count(*) FROM orchestration_tasks WHERE run_id=:id"),
                        {"id": run["id"]},
                    )
                    == 2
                )
                assert db.scalar(text("SELECT count(*) FROM task_leases")) == 0
                assert db.scalar(text("SELECT tick_count FROM scheduler_state WHERE id=1")) == 0
            finally:
                transaction.rollback()  # Entire test schema and its fixture DDL are isolated.
    finally:
        engine.dispose()

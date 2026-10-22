"""Migrate and clear only the fixed isolated test database. Never the dev database."""

import os

from alembic import command
from alembic.config import Config
from sqlalchemy import text

from orba.db import make_engine
from scripts.test_database import guard_test_url

TEST_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://orba_test:orba_test_local@127.0.0.1:54330/orba_test",
)


def prepare(reset: bool = True):
    url = os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://orba_test:orba_test_local@127.0.0.1:54330/orba_test",
    )
    guard_test_url(url)
    previous = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = url
    try:
        command.upgrade(Config("alembic.ini"), "head")
        if reset:
            engine = make_engine(url)
            try:
                with engine.begin() as connection:
                    connection.execute(
                        text(
                            "TRUNCATE TABLE requirement_traces,task_dependencies,engineering_tasks,architecture_components,architecture_versions,architect_runs,product_acceptance_criteria,product_stories,product_epics,product_plans,product_manager_runs,projects,workspace_invitations,workspace_members,sessions,login_attempts,workspaces,users"
                        )
                    )
                    connection.execute(
                        text(
                            "INSERT INTO workspaces (id,name,slug,is_legacy) VALUES ('00000000-0000-0000-0000-000000000001','Legacy projects (operator claim required)','orba-restricted-legacy',true)"
                        )
                    )
            finally:
                engine.dispose()
    finally:
        if previous is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = previous


if __name__ == "__main__":
    prepare()
    print("Isolated orba_test schema migrated and project test data cleared.")

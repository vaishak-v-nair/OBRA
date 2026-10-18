"""Migrate and clear only the fixed isolated test database. Never the dev database."""

import os

from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.engine import make_url

from orba.db import make_engine


def prepare(reset: bool = True):
    url = os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://orba_test:orba_test_local@127.0.0.1:54330/orba_test",
    )
    parsed = make_url(url)
    if parsed.database != "orba_test" or parsed.username != "orba_test":
        raise RuntimeError("Refusing cleanup: expected isolated orba_test database and role.")
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
                            "TRUNCATE TABLE projects,workspace_invitations,workspace_members,sessions,login_attempts,workspaces,users"
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

"""Explicit historical account fixture, confined to guarded orba_test.

This is test setup, never an authentication endpoint or development bypass.
Login still uses the real application, Argon2id, CSRF and session records.
"""

import argparse
import json

from sqlalchemy.orm import Session

from orba.db import make_engine
from orba.models import User
from orba.security import passwords
from scripts.prepare_tests import TEST_URL
from scripts.test_database import guard_test_url

LEGACY_PASSWORD = "oldpassword!"  # Previously permitted12-character test credential.


def seed_legacy_user(email: str, *, database_url=TEST_URL, password_hash=None) -> str:
    guard_test_url(database_url)  # Must precede constructing an engine or hashing.
    engine = make_engine(database_url)
    try:
        with Session(engine) as db:
            user = User(
                email=email,
                display_name="Legacy test account",
                password_hash=password_hash
                if password_hash is not None
                else passwords.hash(LEGACY_PASSWORD),
            )
            db.add(user)
            db.commit()
            return str(user.id)
    finally:
        engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", required=True)
    args = parser.parse_args()
    print(json.dumps({"user_id": seed_legacy_user(args.email)}))


if __name__ == "__main__":
    main()

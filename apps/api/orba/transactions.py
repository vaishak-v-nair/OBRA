"""Existing short PostgreSQL phases, shared without importing model-provider code."""

from contextlib import contextmanager

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session


@contextmanager
def phase(engine):
    with Session(engine) as db, db.begin():
        db.execute(text("SET LOCAL lock_timeout='1s'"))
        db.execute(text("SET LOCAL statement_timeout='2s'"))
        db.execute(text("SET LOCAL transaction_timeout='10s'"))
        yield db


def db_now(db):
    return db.scalar(select(func.clock_timestamp()))

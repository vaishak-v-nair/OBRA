"""Standalone bounded PostgreSQL scheduler; never executes a task."""

import argparse
import json
import signal
import threading
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from orba.config import Settings
from orba.db import make_engine
from orba.pm_errors import PMError
from orba.scheduler_service import tick


def bounded(value):
    number = int(value)
    if not 1 <= number <= 1000:
        raise argparse.ArgumentTypeError("Use a bounded number from1to1000.")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticks", type=bounded, default=1)
    parser.add_argument("--interval", type=int, choices=range(1, 61), default=5)
    args = parser.parse_args()
    stop = threading.Event()
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    config = Settings()
    engine = make_engine(config.database_url)
    process_id = uuid4()
    try:
        for index in range(args.ticks):
            if stop.is_set():
                break
            print(json.dumps(tick(engine, config.scheduler_policy(), process_id)), flush=True)
            if index + 1 < args.ticks and stop.wait(args.interval):
                break
    except (ValueError, OSError, SQLAlchemyError, HTTPException, PMError) as exc:
        print(
            json.dumps(
                {
                    "error": type(exc).__name__,
                    "message": "Scheduler tick failed; no successful decision is certified. Inspect database availability and shared policy.",
                    "execution_performed": False,
                }
            ),
            flush=True,
        )
        return 1
    finally:
        engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

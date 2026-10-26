"""Trusted local operator provisioning. Never prints a worker credential."""

import argparse
import json
import os
import subprocess
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from orba.config import Settings
from orba.db import make_engine
from orba.pm_errors import PMError
from orba.scheduler_models import TaskDispatch, TaskLease, WorkerCredential, WorkerIdentity
from orba.scheduler_schemas import Provision
from orba.scheduler_service import (
    ACTIVE,
    control_event,
    coordination,
    credential_pair,
    end_lease,
    lock_run,
    provision,
)
from orba.transactions import db_now, phase

ROOT = Path(__file__).resolve().parents[3]


def private_file(path, token):
    if str(path).startswith("\\\\"):
        raise ValueError("Use a local private credential file, not a network share.")
    path = path.resolve()
    if path.is_relative_to(ROOT) or not path.parent.is_dir():
        raise ValueError(
            "Use an existing private directory outside the repository for credentials."
        )
    # Restrict the empty file before writing secret bytes; never overwrite a file.
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        if os.name == "nt":
            sid = (
                subprocess.check_output(
                    ["whoami", "/user", "/fo", "csv", "/nh"], text=True, timeout=5
                )
                .strip()
                .split(",")[-1]
                .strip('"')
            )
            subprocess.run(
                ["icacls", str(path), "/inheritance:r", "/grant:r", f"*{sid}:(F)"],
                check=True,
                capture_output=True,
                timeout=5,
            )
        encoded = (token + "\n").encode("ascii")
        if os.write(descriptor, encoded) != len(encoded):
            raise OSError("Credential file write was incomplete.")
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def alter_worker(db, worker_id, action, policy, lifetime=86400):
    coordination(db, policy)
    worker = db.get(WorkerIdentity, worker_id)
    if worker is None:
        raise ValueError("Worker not found.")
    leases = db.scalars(
        select(TaskLease)
        .where(TaskLease.worker_id == worker.id, TaskLease.state.in_(ACTIVE))
        .order_by(TaskLease.run_id, TaskLease.id)
    ).all()
    for lease in leases:
        run = lock_run(db, lease.run_id)
        dispatch = db.get(TaskDispatch, lease.dispatch_id)
        if action == "disable":
            control_event(
                db,
                run,
                "worker_disabled",
                dispatch=dispatch,
                lease=lease,
                reason="operator_disabled",
            )
        end_lease(db, run, dispatch, lease, policy, "revoked", "operator_" + action)
    moment = db_now(db)
    for credential in db.scalars(
        select(WorkerCredential).where(
            WorkerCredential.worker_id == worker.id, WorkerCredential.revoked_at.is_(None)
        )
    ):
        credential.revoked_at = moment
    worker.updated_at = moment
    token = None
    if action == "disable":
        worker.enabled = False
    elif action == "rotate":
        if not worker.enabled:
            raise ValueError(
                "Disabled workers cannot rotate credentials; provision a reviewed replacement."
            )
        worker.credential_version += 1
        credential, token = credential_pair(worker, moment, lifetime)
        db.add(credential)
    return worker, token


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    add = sub.add_parser("provision")
    add.add_argument("--workspace", type=UUID, required=True)
    add.add_argument("--project", type=UUID)
    add.add_argument("--name", required=True)
    add.add_argument("--capability", action="append", required=True)
    add.add_argument("--capacity", type=int, default=1)
    add.add_argument("--credential-file", type=Path, required=True)
    for action in ("rotate", "revoke", "disable"):
        command = sub.add_parser(action)
        command.add_argument("--worker", type=UUID, required=True)
        if action == "rotate":
            command.add_argument("--credential-file", type=Path, required=True)
    args = parser.parse_args()
    config = Settings()
    engine = make_engine(config.database_url)
    try:
        with phase(engine) as db:
            if args.action == "provision":
                worker, token = provision(
                    db,
                    Provision(
                        workspace_id=args.workspace,
                        project_id=args.project,
                        display_name=args.name,
                        capabilities=args.capability,
                        max_leases=args.capacity,
                    ),
                )
            else:
                worker, token = alter_worker(
                    db, args.worker, args.action, config.scheduler_policy()
                )
            if token:
                private_file(args.credential_file, token)
            result = {
                "worker_id": str(worker.id),
                "action": args.action,
                "credential_version": worker.credential_version,
                "credential_written": bool(token),
                "execution_performed": False,
            }
        print(json.dumps(result))
    except (
        ValueError,
        OSError,
        subprocess.SubprocessError,
        SQLAlchemyError,
        HTTPException,
        PMError,
    ) as exc:
        # Do not print validation inputs or SQL parameters containing credential material.
        print(
            json.dumps(
                {
                    "error": type(exc).__name__,
                    "message": "Worker administration failed. Verify scope, database, policy and an unused private credential-file path. No provision success is certified.",
                }
            )
        )
        return 1
    finally:
        engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Validator test INPUTS only; synthetic browser/process attestations are NOT Gate B."""

from copy import deepcopy
from datetime import UTC, datetime
from uuid import UUID, uuid4

from orba.scheduler_service import tick
from scripts.inspect_orchestration import inspect as inspect_source
from scripts.inspect_scheduler import inspect
from tests.orchestration_proof_support import assemble
from tests.orchestration_support import initialize, path
from tests.scheduler_support import acquire, act, worker
from tests.test_scheduler_recovery import FAST, until


def complete_input(client):
    client.app.state.settings = client.app.state.settings.model_copy(update=FAST)
    project, _, _, run = initialize(client)
    initial = inspect_source(UUID(run["id"]))
    foundation = assemble(run, initial)
    _ident, _, headers = worker(client, run)
    registered = client.get("/api/v1/workers/me", headers=headers).json()
    tick(client.app.state.engine, client.app.state.settings.scheduler_policy(), uuid4())
    handoff = acquire(client, run, headers).json()
    ack = act(client, handoff, headers).json()
    until(
        client,
        datetime.fromisoformat(ack["lease"]["acknowledged_at"]).replace(tzinfo=UTC).isoformat(),
        offset=1.05,
    )
    heartbeat = act(client, handoff, headers, "heartbeat", request_id=str(uuid4())).json()
    until(client, heartbeat["lease"]["expires_at"])
    tick(client.app.state.engine, client.app.state.settings.scheduler_policy(), uuid4())
    assert act(client, handoff, headers).status_code == 409
    observed = client.get(path(project, f"/{run['id']}/scheduler")).json()
    sql = inspect(UUID(run["id"]))
    rows = [
        {
            "name": name,
            "receipt_id": str(uuid4()),
            "argv": ["explicit-synthetic-unit-input"],
            "pid": index + 1,
            "exit_code": 1 if name == "scheduler-interrupted" else 0,
            "signal": None,
            "expected_termination": name == "scheduler-interrupted",
            "started_at": "2026-01-01T00:00:00Z",
            "completed_at": "2026-01-01T00:00:01Z",
        }
        for index, name in enumerate(
            (
                "provision",
                "worker-start",
                "scheduler-start",
                "scheduler-interrupted",
                "worker-restart",
                "scheduler-restart",
            )
        )
    ]
    return deepcopy(
        {
            "proof_version": 1,
            "stage": "stage05b-scheduler",
            "result": "PASS",
            "execution_class": "real_local_worker_protocol",
            "started_at": "2000-01-01T00:00:00Z",
            "completed_at": "2100-01-01T00:00:00Z",
            "foundation": foundation,
            "worker": registered,
            "acknowledged_api": ack,
            "heartbeat_api": heartbeat,
            "final_api": observed,
            "independent_sql": sql,
            "process_commands": rows,
            "stale_epoch_status": 409,
            "foreign_worker_status": 404,
            "unauthorized_user_status": 404,
            "revoked_worker_status": 401,
            "model_generation_requests": 0,
            "executed_tasks": 0,
            "browser_rendered": True,
            "reload_persisted": True,
            "protected_ui_hidden": True,
            "incomplete_proof_rejected": True,
        }
    )

"""Authored approved plans; real registry/API/PG, no executor or provider doubles."""

from uuid import UUID, uuid4

from orba.pm_service import phase
from orba.scheduler_schemas import Provision
from orba.scheduler_service import provision, tick
from tests.orchestration_support import initialize
from tests.report_safety import WorkerHeaders


def worker(client, run, *, capabilities=None, project=True, workspace=None, capacity=1):
    with phase(client.app.state.engine) as db:
        row, token = provision(
            db,
            Provision(
                workspace_id=workspace or run["workspace_id"],
                project_id=run["project_id"] if project else None,
                display_name="Protocol verifier",
                capabilities=capabilities or ["backend", "frontend"],
                max_leases=capacity,
            ),
        )
        ident = str(row.id)
    headers = WorkerHeaders(Authorization="Bearer " + token)
    result = client.get("/api/v1/workers/me", headers=headers)
    assert result.status_code == 200, result.text
    return ident, token, headers


def ready(client, *, config=None):
    if config:
        client.app.state.settings = client.app.state.settings.model_copy(update=config)
    project, _source, _request, run = initialize(client)
    ident, token, headers = worker(client, run)
    tick(client.app.state.engine, client.app.state.settings.scheduler_policy(), uuid4())
    return project, run, ident, token, headers


def acquire(client, run, headers, request_id=None):
    return client.post(
        "/api/v1/workers/claim",
        headers=headers,
        json={"request_id": str(request_id or uuid4()), "run_id": run["id"]},
    )


def operation(handoff):
    return {
        "fence_epoch": handoff["lease"]["fence_epoch"],
        "contract_version": 1,
        "manifest_checksum": handoff["manifest"]["checksum"],
    }


def act(client, handoff, headers, action="acknowledge", **changes):
    value = operation(handoff) | changes
    return client.post(
        f"/api/v1/workers/leases/{handoff['lease']['id']}/{action}", headers=headers, json=value
    )


def run_uuid(run):
    return UUID(run["id"])

"""INTENTIONALLY WRONG assertion. Explicit execution must fail; never normal discovery."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from orba.architect_models import ArchitectRun, ArchitectureVersion
from orba.pm_provider import ProviderFailure
from tests.architect_support import ControlledProvider, approved_source, generate


def test_incorrect_success_claim(client):
    project_id, source = approved_source(client)
    response, _ = generate(
        client,
        project_id,
        source,
        ControlledProvider(
            failure=ProviderFailure(
                "provider_unavailable",
                "Clearly labeled controlled HTTP503",
                502,
                diagnostic={"provider_double": True, "provider_http_status": 503},
            )
        ),
    )
    assert response.status_code == 502
    run_id = UUID(response.json()["error"]["run_id"])
    with Session(client.app.state.engine) as db:
        run = db.get(ArchitectRun, run_id)
        assert db.scalar(select(func.count()).select_from(ArchitectureVersion)) == 0
        assert run.completed_at is not None
        print(
            f"ACTUAL_EVIDENCE run_id={run.id} status={run.status} architectures=0 provider_double=True"
        )
        assert run.status == "succeeded", (
            "DELIBERATELY INCORRECT: a failed Architect run must not count as success"
        )

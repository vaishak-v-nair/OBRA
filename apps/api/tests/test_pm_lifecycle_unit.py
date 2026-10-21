"""Isolated lifecycle/error tests using EXPLICIT provider doubles and real PG.

These prove state transitions/validation, NOT a functioning Gemini integration.
No runtime switch can select these doubles. Live API/browser evidence is separate.
"""

from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from pm_support import counts, identity, project, unit_output
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from orba import pm_service
from orba.config import Settings
from orba.models import AuthSession, WorkspaceMember
from orba.pm_errors import PMError
from orba.pm_models import ProductManagerRun, ProductPlan
from orba.pm_provider import ProviderFailure, ProviderResult
from orba.pm_repository import read_document
from orba.pm_schemas import RunCreate
from orba.security import now


class UnitProvider:
    """Only an isolated, counted unit double. Never used by HTTP production routes."""

    def __init__(self, *, malformed=False, failure=None, callback=None):
        self.calls, self.malformed, self.failure, self.callback = 0, malformed, failure, callback

    async def generate(self, snapshot):
        self.calls += 1
        if self.callback:
            self.callback()
        if self.failure:
            raise self.failure
        return ProviderResult(
            '{"not_a_plan":true}' if self.malformed else unit_output().model_dump_json(),
            model="unit-double-not-live",
            response_id="unit-only",
        )


def invoke(client, pid, provider, payload=None):
    actor, session_id = identity(client)
    return pm_service.generate(
        client.app.state.engine,
        client.app.state.settings,
        UUID(pid),
        actor,
        session_id,
        payload or RunCreate(client_request_id=uuid4(), brief="Track daily habits"),
        provider=provider,
    )


def test_unit_valid_lifecycle_persists_graph_and_exact_replay(client):
    pid, provider = project(client), UnitProvider()
    payload = RunCreate(client_request_id=uuid4(), brief="Track daily habits")
    saved, created = invoke(client, pid, provider, payload)
    assert created and saved["status"] == "succeeded" and saved["plan_id"]
    assert provider.calls == 1
    replay, created = invoke(client, pid, provider, payload)
    assert not created and replay["plan_id"] == saved["plan_id"] and provider.calls == 1
    with Session(client.app.state.engine) as db:
        plan = db.get(ProductPlan, saved["plan_id"])
        assert plan.state == "draft" and plan.approved_at is None
        assert read_document(db, plan).epics[0].stories[0].acceptance_criteria
        run = db.get(ProductManagerRun, saved["id"])
        assert (
            run.prompt_hash and run.snapshot_hash and run.input_snapshot["brief"] == payload.brief
        )
    changed = payload.model_copy(update={"brief": "Different input"})
    with pytest.raises(PMError, match="different input"):
        invoke(client, pid, provider, changed)
    assert provider.calls == 1 and counts(client)[:2] == (1, 1)


@pytest.mark.parametrize("case", ["malformed", "timeout", "rate_limit"])
def test_unit_invalid_output_or_provider_failure_never_creates_plan(client, case):
    pid = project(client)
    failure = (
        None
        if case == "malformed"
        else ProviderFailure(
            "provider_timeout" if case == "timeout" else "provider_rate_limited",
            "Controlled unit failure",
            504 if case == "timeout" else 429,
            diagnostic={"exception_type": "UnitDouble"},
        )
    )
    provider = UnitProvider(malformed=case == "malformed", failure=failure)
    with pytest.raises(PMError) as error:
        invoke(client, pid, provider)
    assert error.value.code == (
        "invalid_model_response" if case == "malformed" else failure.category
    )
    with Session(client.app.state.engine) as db:
        run = db.scalar(select(ProductManagerRun))
        assert run.status == "failed" and run.completed_at and run.diagnostic_id
        assert run.diagnostic and run.error_category == error.value.code
    assert counts(client)[:2] == (1, 0) and provider.calls == 1
    if case == "malformed":
        import json

        from scripts.test_evidence import evidence_path

        evidence = {
            "scenario": "Isolated malformed-output provider DOUBLE; not live model evidence",
            "database": "real guarded PostgreSQL",
            "provider_double": True,
            "status": run.status,
            "error_category": run.error_category,
            "run_id": str(run.id),
            "diagnostic_id": str(run.diagnostic_id),
            "diagnostic": run.diagnostic,
            "persisted_plan_count": counts(client)[1],
        }
        evidence_path("invalid-output-double.json").write_text(
            json.dumps(evidence, indent=2) + "\n", encoding="utf8"
        )


def test_real_missing_configuration_endpoint_records_honest_failure(client):
    # Actual config rejection: no provider stub, no network call and no valid key required.
    client.app.state.settings = Settings(
        database_url=client.app.state.settings.database_url, pm_api_key=None, pm_model=None
    )
    pid = project(client)
    response = client.post(
        f"/api/v1/projects/{pid}/pm-runs",
        json={"client_request_id": str(uuid4()), "brief": "Track habits"},
    )
    assert response.status_code == 503, response.text
    error = response.json()["error"]
    assert error["code"] == "pm_not_configured" and error["run_id"]
    detail = client.get(f"/api/v1/projects/{pid}/pm-runs/{error['run_id']}").json()
    assert detail["status"] == "failed" and detail["plan_id"] is None
    with Session(client.app.state.engine) as db:
        assert (
            db.get(ProductManagerRun, UUID(error["run_id"])).error_category == "pm_not_configured"
        )
    assert counts(client) == (1, 0, 1)


@pytest.mark.parametrize(
    "change", ["revoked_session", "expired_session", "membership_removed", "viewer"]
)
def test_unit_authority_changes_during_provider_call_prevent_publication(client, change):
    pid = project(client)
    actor, session_id = identity(client)

    def alter():
        with Session(client.app.state.engine) as db, db.begin():
            if change.endswith("session"):
                saved = db.get(AuthSession, session_id)
                if change == "revoked_session":
                    saved.revoked_at = now()
                else:
                    saved.expires_at = now() - timedelta(seconds=1)
            else:
                member = db.scalar(
                    select(WorkspaceMember).where(
                        WorkspaceMember.user_id == actor,
                        WorkspaceMember.workspace_id == UUID(client.workspace_id),
                    )
                )
                if change == "viewer":
                    member.role = "viewer"
                else:
                    db.delete(member)

    provider = UnitProvider(callback=alter)
    with pytest.raises(PMError) as error:
        invoke(client, pid, provider)
    assert error.value.code == "authorization_changed"
    assert counts(client)[:2] == (1, 0)
    with Session(client.app.state.engine) as db:
        assert db.scalar(select(ProductManagerRun)).status == "failed"


def test_unit_session_expiring_during_graph_write_rolls_back_all_children(client, monkeypatch):
    original = pm_service.create_plan

    def expires_after_graph(db, *args, **kwargs):
        value = original(db, *args, **kwargs)
        run = db.get(ProductManagerRun, kwargs["run_id"])
        db.get(AuthSession, run.initiating_session_id).expires_at = now() - timedelta(seconds=1)
        db.flush()
        return value

    monkeypatch.setattr(pm_service, "create_plan", expires_after_graph)
    with pytest.raises(PMError, match="not published"):
        invoke(client, project(client), UnitProvider())
    assert counts(client)[:2] == (1, 0)


def test_unit_expired_lease_and_late_failure_remain_interrupted(client):
    pid = project(client)
    actor, sid = identity(client)
    payload = RunCreate(client_request_id=uuid4(), brief="Track habits")
    run_id, _, _ = pm_service.reserve(
        client.app.state.engine, client.app.state.settings, UUID(pid), actor, sid, payload
    )
    with Session(client.app.state.engine) as db, db.begin():
        db.get(ProductManagerRun, run_id).deadline_at = now() - timedelta(seconds=1)
    pm_service.record_failure(
        client.app.state.engine, run_id, "provider_timeout", {"exception_type": "UnitDouble"}
    )
    with Session(client.app.state.engine) as db:
        saved = db.get(ProductManagerRun, run_id)
        assert saved.status == "interrupted" and saved.error_category == "provider_timeout"
    provider = UnitProvider()
    replay, _ = invoke(client, pid, provider, payload)
    assert replay["status"] == "interrupted" and provider.calls == 0 and counts(client)[1] == 0


def test_unit_unknown_reservation_commit_never_dispatches_or_resubmits(client, monkeypatch):
    pid, provider = project(client), UnitProvider()
    original = pm_service.reserve
    payload = RunCreate(client_request_id=uuid4(), brief="Track habits")

    def ack_lost(*args):
        original(*args)
        raise OperationalError("unit commit acknowledgment", {}, None)

    monkeypatch.setattr(pm_service, "reserve", ack_lost)
    with pytest.raises(PMError) as error:
        invoke(client, pid, provider, payload)
    assert error.value.code == "run_outcome_unknown" and provider.calls == 0
    assert counts(client)[:2] == (1, 0)
    monkeypatch.setattr(pm_service, "reserve", original)
    replay, _ = invoke(client, pid, provider, payload)
    assert replay["status"] == "pending" and provider.calls == 0


def test_unit_global_admission_and_project_lease_are_enforced(client):
    pid = project(client)
    actor, sid = identity(client)
    payload = RunCreate(client_request_id=uuid4(), brief="Track habits")
    pm_service.reserve(
        client.app.state.engine, client.app.state.settings, UUID(pid), actor, sid, payload
    )
    with pytest.raises(PMError) as error:
        invoke(client, pid, UnitProvider())
    assert error.value.code == "project_generation_active"
    client.app.state.settings.pm_max_concurrent = 1
    with pytest.raises(PMError) as error:
        invoke(client, project(client), UnitProvider())
    assert error.value.status == 429


def test_unit_failures_cannot_overwrite_committed_success(client):
    saved, _ = invoke(client, project(client), UnitProvider())
    pm_service.record_failure(
        client.app.state.engine,
        saved["id"],
        "provider_timeout",
        {"exception_type": "LateUnitDouble"},
    )
    with Session(client.app.state.engine) as db:
        run = db.get(ProductManagerRun, saved["id"])
        assert run.status == "succeeded" and run.error_category is None


def test_isolation_of_run_metadata_uses_real_http_authorization(client):
    from test_auth_workspaces import account

    pid = project(client)
    run, _ = invoke(client, pid, UnitProvider())
    outsider, _ = account(client.app, "unit-outsider@example.com")
    denied = outsider.get(f"/api/v1/projects/{pid}/pm-runs/{run['id']}")
    assert denied.status_code == 404 and "unit-double" not in denied.text
    outsider.close()


def test_unit_router_releases_auth_connection_before_dispatch(client, monkeypatch):
    """A router unit test with a labeled adapter double, not live AI evidence."""
    pid = project(client)
    config = client.app.state.settings
    config.pm_api_key = Settings(pm_api_key="unit-key-never-dispatched").pm_api_key
    config.pm_model = "gemini-unit-double"

    def check_pool():
        assert client.app.state.engine.pool.checkedout() == 0

    provider = UnitProvider(callback=check_pool)
    from orba.pm import model_provider

    client.app.dependency_overrides[model_provider] = lambda: provider
    response = client.post(
        f"/api/v1/projects/{pid}/pm-runs",
        json={"client_request_id": str(uuid4()), "brief": "Track habits"},
    )
    assert response.status_code == 201, response.text
    assert response.json()["status"] == "succeeded" and provider.calls == 1


def test_unit_new_generation_and_failure_preserve_approved_version(client):
    pid = project(client)
    first, _ = invoke(client, pid, UnitProvider())
    base = f"/api/v1/projects/{pid}"
    approved = client.post(
        f"{base}/pm-plans/{first['plan_id']}/approve", json={"version": 1, "expected_revision": 1}
    )
    assert approved.status_code == 200
    snapshot = approved.json()
    second, _ = invoke(client, pid, UnitProvider())
    draft = client.get(f"{base}/pm-plans/{second['plan_id']}").json()
    assert draft["version"] == 2 and draft["state"] == "draft"
    with pytest.raises(PMError):
        invoke(client, pid, UnitProvider(malformed=True))
    original = client.get(f"{base}/pm-plans/{first['plan_id']}").json()
    assert (
        original["state"] == "approved"
        and original["content_hash"] == snapshot["content_hash"]
        and original["approved_at"] == snapshot["approved_at"]
    )


def test_unit_uncertain_final_commit_reconciles_actual_persisted_success(client, monkeypatch):
    from contextlib import contextmanager

    original = pm_service.phase
    acknowledged = False

    @contextmanager
    def lose_success_ack(engine):
        nonlocal acknowledged
        with original(engine) as db:
            yield db
            published = any(
                isinstance(row, ProductManagerRun) and row.status == "succeeded"
                for row in db.identity_map.values()
            )
        if published and not acknowledged:
            acknowledged = True
            raise OperationalError("unit final acknowledgment loss", {}, None)

    monkeypatch.setattr(pm_service, "phase", lose_success_ack)
    provider = UnitProvider()
    run, _ = invoke(client, project(client), provider)
    assert acknowledged and run["status"] == "succeeded" and provider.calls == 1
    assert counts(client)[:2] == (1, 1)


def test_unit_concurrent_generation_reserves_one_provider_call(client):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event

    entered, release = Event(), Event()
    pid = project(client)

    def hold():
        entered.set()
        assert release.wait(10)

    provider = UnitProvider(callback=hold)
    with ThreadPoolExecutor(max_workers=1) as pool:
        first = pool.submit(invoke, client, pid, provider)
        assert entered.wait(10)
        try:
            with pytest.raises(PMError) as error:
                invoke(client, pid, UnitProvider())
            assert error.value.code == "project_generation_active"
        finally:
            release.set()
        run, _ = first.result(timeout=10)
    assert run["status"] == "succeeded" and provider.calls == 1 and counts(client)[:2] == (1, 1)

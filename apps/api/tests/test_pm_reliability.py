"""Labeled provider doubles + real PostgreSQL. No live model certification."""

import logging
from uuid import uuid4

import pytest
from pm_support import counts, project
from sqlalchemy.orm import Session
from test_pm_lifecycle_unit import UnitProvider, invoke

from orba.pm_errors import PMError
from orba.pm_models import ProductManagerRun
from orba.pm_provider import ProviderFailure
from orba.pm_schemas import RunCreate


def test_actual_phase_measurements_and_explicit_failed_retry(client, caplog):
    caplog.set_level(logging.INFO, logger="uvicorn.error.orba.pm_timing")
    pid = project(client)
    private = "Private brief never logged in phase diagnostics"
    provider = UnitProvider(
        failure=ProviderFailure(
            "provider_timeout",
            "Controlled unit timeout",
            504,
            diagnostic={"provider_http_status": 504, "error_origin": "controlled_double"},
        )
    )
    first = RunCreate(client_request_id=uuid4(), brief=private)
    with pytest.raises(PMError) as failure:
        invoke(client, pid, provider, first)
    with Session(client.app.state.engine) as db:
        run = db.get(ProductManagerRun, failure.value.run_id)
        trace = run.diagnostic
        assert run.status == "failed" and trace["attempt"] == 1
        assert trace["timing_boundary"] == "before_terminal_commit"
        assert set(trace["stages_ms"]) == {
            "admission_transaction",
            "running_transaction",
            "provider_call",
        }
        assert all(0 <= value <= trace["elapsed_ms"] for value in trace["stages_ms"].values())
    # Exact replay must not dispatch; only a NEW explicitly submitted UUID retries.
    replay, created = invoke(client, pid, provider, first)
    assert not created and replay["status"] == "failed" and provider.calls == 1
    second = first.model_copy(update={"client_request_id": uuid4()})
    with pytest.raises(PMError) as retried:
        invoke(client, pid, provider, second)
    assert retried.value.run_id != failure.value.run_id and provider.calls == 2
    assert counts(client)[:2] == (2, 0)
    assert "final_state=failed" in caplog.text and "attempt=1" in caplog.text
    assert private not in caplog.text


def test_success_has_precommit_measurements_and_postcommit_log(client, caplog):
    caplog.set_level(logging.INFO, logger="uvicorn.error.orba.pm_timing")
    saved, _ = invoke(client, project(client), UnitProvider())
    with Session(client.app.state.engine) as db:
        trace = db.get(ProductManagerRun, saved["id"]).diagnostic
        assert {"provider_call", "validation", "persistence_flush"} <= trace["stages_ms"].keys()
        assert "persistence_transaction" not in trace["stages_ms"]
        assert trace["timing_boundary"] == "before_terminal_commit"
    assert "stage=publication_commit_acknowledged" in caplog.text
    assert "final_state=succeeded" in caplog.text


def test_controlled_factory_refuses_development_database_before_app_creation(monkeypatch):
    from controlled_app import create_controlled_app

    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://orba:unit@127.0.0.1:54329/orba")
    with pytest.raises(RuntimeError, match="Refusing test mutation"):
        create_controlled_app()


def test_simultaneous_exact_key_http_replay_dispatches_once(client):
    """Independent HTTP clients, real auth/CSRF/PG; explicitly counted model double."""
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    from uuid import UUID

    from fastapi.testclient import TestClient
    from sqlalchemy import func, select

    from orba.pm import model_provider
    from orba.pm_models import ProductPlan
    from orba.pm_repository import read_document

    pid = project(client)
    entered, release = Event(), Event()

    def hold():
        entered.set()
        assert release.wait(10)

    provider = UnitProvider(callback=hold)
    client.app.dependency_overrides[model_provider] = lambda: provider
    first, second = TestClient(client.app), TestClient(client.app)
    for peer in (first, second):
        peer.cookies.update(client.cookies)
        peer.headers.update({name: client.headers[name] for name in ("Origin", "X-CSRF-Token")})
    payload = {"client_request_id": str(uuid4()), "brief": "Track one daily habit"}
    path = f"/api/v1/projects/{pid}/pm-runs"
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            pending = pool.submit(first.post, path, json=payload)
            assert entered.wait(10)
            try:
                replay = second.post(path, json=payload)
                assert replay.status_code == 202 and replay.json()["status"] == "running"
                assert provider.calls == 1 and counts(client)[:2] == (1, 0)
            finally:
                release.set()
            saved = pending.result(timeout=10)
        assert saved.status_code == 201 and saved.json()["status"] == "succeeded"
        assert saved.json()["id"] == replay.json()["id"]
        final = second.post(path, json=payload)
        assert final.status_code == 200 and final.json()["plan_id"] == saved.json()["plan_id"]
        assert provider.calls == 1 and counts(client)[:2] == (1, 1)
        with Session(client.app.state.engine) as db:
            assert db.scalar(select(func.count()).select_from(ProductManagerRun)) == 1
            plan = db.get(ProductPlan, UUID(saved.json()["plan_id"]))
            document = read_document(db, plan)
            assert document.epics and document.epics[0].stories[0].acceptance_criteria
    finally:
        release.set()
        first.close()
        second.close()
        client.app.dependency_overrides.pop(model_provider, None)


def test_sdk_upstream_503_preserves_approval_and_cannot_turn_into_unrelated_success(
    client, monkeypatch
):
    """Synthetic HTTP only at the real SDK boundary; real API, authority and PG."""
    from uuid import UUID

    import httpx

    from orba.config import Settings
    from orba.pm import model_provider
    from orba.pm_provider import GeminiProductManagerProvider

    pid = project(client)
    saved, _ = invoke(client, pid, UnitProvider())
    plan_path = f"/api/v1/projects/{pid}/pm-plans/{saved['plan_id']}"
    approved = client.post(plan_path + "/approve", json={"version": 1, "expected_revision": 1})
    assert approved.status_code == 200
    original = approved.json()
    seen = []

    def upstream(request):
        seen.append(request)
        assert request.method == "POST" and request.url.path.endswith(":generateContent")
        return httpx.Response(
            503,
            json={
                "error": {
                    "code": 503,
                    "status": "UNAVAILABLE",
                    "message": "private-synthetic-provider-marker",
                }
            },
        )

    monkeypatch.setattr("orba.pm_provider.LimitedTransport", lambda: httpx.MockTransport(upstream))
    settings = Settings(
        _env_file=None, pm_api_key="synthetic-no-runtime-key", pm_model="gemini-3.8-flash"
    )
    client.app.dependency_overrides[model_provider] = lambda: GeminiProductManagerProvider(settings)
    payload = {"client_request_id": str(uuid4()), "brief": "Explicit failed regeneration"}
    path = f"/api/v1/projects/{pid}/pm-runs"
    try:
        failed = client.post(path, json=payload)
        assert (
            failed.status_code == 502 and failed.json()["error"]["code"] == "provider_unavailable"
        )
        run_id = UUID(failed.json()["error"]["run_id"])
        assert "private-synthetic-provider-marker" not in failed.text and len(seen) == 1
        assert counts(client)[:2] == (2, 1)  # Prior valid plan only; failed regeneration adds none.
        with Session(client.app.state.engine) as db:
            run = db.get(ProductManagerRun, run_id)
            assert run.status == "failed" and run.usage is None and run.returned_model is None
            assert run.diagnostic["provider_http_status"] == 503
            assert run.diagnostic["error_origin"] == "upstream_http"
        replay = client.post(path, json=payload)
        assert replay.status_code == 409 and len(seen) == 1
        assert replay.json()["error"]["run_id"] == str(run_id)
        assert client.get(plan_path).json() == original
        # A different project/user action cannot convert the failed terminal record.
        later, _ = invoke(client, project(client), UnitProvider())
        assert later["status"] == "succeeded" and later["id"] != run_id
        with Session(client.app.state.engine) as db:
            assert db.get(ProductManagerRun, run_id).status == "failed"
        assert client.get(plan_path).json() == original
    finally:
        client.app.dependency_overrides.pop(model_provider, None)


def test_flushed_partial_graph_is_invisible_and_rollback_never_publishes(client, monkeypatch):
    """Real MVCC observation/fault injection, not mocked database responses."""
    from datetime import timedelta
    from uuid import UUID

    from sqlalchemy import func, select
    from sqlalchemy.exc import OperationalError

    from orba import pm_service
    from orba.pm_models import ProductCriterion, ProductEpic, ProductPlan, ProductStory
    from orba.security import now

    pid = project(client)
    models = (ProductPlan, ProductEpic, ProductStory, ProductCriterion)
    original = pm_service.create_plan
    observed = []

    def flushed_then_fail(db, *args, **kwargs):
        plan = original(db, *args, **kwargs)
        db.flush()  # Actual root and every relational child INSERT reached PostgreSQL.
        assert all(db.scalar(select(func.count()).select_from(model)) > 0 for model in models)
        with Session(client.app.state.engine) as reader:
            assert reader.get(ProductManagerRun, kwargs["run_id"]).status == "running"
            assert all(
                reader.scalar(select(func.count()).select_from(model)) == 0 for model in models
            )
        observed.append(plan.id)
        raise OperationalError("controlled failure after real graph flush", {}, None)

    monkeypatch.setattr(pm_service, "create_plan", flushed_then_fail)
    with pytest.raises(PMError) as outcome:
        invoke(client, pid, UnitProvider())
    assert outcome.value.code == "run_outcome_unknown" and len(observed) == 1
    with Session(client.app.state.engine) as db, db.begin():
        assert all(db.scalar(select(func.count()).select_from(model)) == 0 for model in models)
        run = db.get(ProductManagerRun, outcome.value.run_id)
        assert (
            run.status == "running"
        )  # An uncertain acknowledgement is not invented failure/success.
        run.deadline_at = now() - timedelta(seconds=1)
    history = client.get(f"/api/v1/projects/{pid}/pm-runs").json()["items"]
    assert history[0]["status"] == "interrupted" and history[0]["plan_id"] is None
    with Session(client.app.state.engine) as db:
        assert db.get(ProductPlan, observed[0]) is None
        assert db.get(ProductManagerRun, UUID(history[0]["id"])).status == "interrupted"

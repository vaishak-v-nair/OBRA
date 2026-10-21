"""Real API/auth/PostgreSQL with labeled SDK synthetic HTTP/provider doubles only.

No test in this file establishes live Gemini generation, quality or latency.
"""

import json
from uuid import UUID, uuid4

import httpx
import pytest
from pm_support import counts, project, unit_output
from pydantic import SecretStr
from sqlalchemy.orm import Session
from test_pm_lifecycle_unit import UnitProvider, invoke

from orba.pm import model_provider
from orba.pm_errors import PMError
from orba.pm_models import ProductManagerRun, ProductPlan
from orba.pm_provider import GeminiProductManagerProvider, request_metrics
from orba.pm_repository import read_document
from orba.pm_schemas import RunCreate


def enable_alternative(client):
    settings = client.app.state.settings
    settings.pm_model = "gemini-3.6-flash"
    settings.pm_thinking_level = "minimal"
    settings.pm_api_key = SecretStr("controlled-sdk-not-a-runtime-key")
    client.app.dependency_overrides[model_provider] = lambda: GeminiProductManagerProvider(settings)


def test_api_byte_rejection_precedes_admission_and_preserves_rows(client):
    pid = project(client)
    client.app.state.settings.pm_max_input_bytes = 8192
    provider = UnitProvider()
    client.app.dependency_overrides[model_provider] = lambda: provider
    response = client.post(
        f"/api/v1/projects/{pid}/pm-runs",
        json={"client_request_id": str(uuid4()), "brief": "界" * 3000},
    )
    assert response.status_code == 422 and response.json()["error"]["code"] == "input_too_large"
    assert "No generation was started" in response.json()["error"]["message"]
    assert response.json()["error"]["run_id"] is None and provider.calls == 0
    assert counts(client) == (0, 0, 1)


def test_exact_boundary_and_replay_after_model_cap_change_preserve_approval(client):
    pid = project(client)
    brief = "界" * 3000
    settings = client.app.state.settings
    snapshot = {
        "title": "Habit journal",
        "description": "Track a habit with daily check-ins.",
        "brief": brief,
        "instructions": "",
        "context_nodes": {},
    }
    exact = request_metrics(snapshot)["input_bytes"]
    settings.pm_max_input_bytes = exact
    settings.pm_model = "gemini-3.8-flash"
    provider = UnitProvider()
    payload = RunCreate(client_request_id=uuid4(), brief=brief)
    saved, created = invoke(client, pid, provider, payload)
    assert created and saved["status"] == "succeeded" and provider.calls == 1
    path = f"/api/v1/projects/{pid}/pm-plans/{saved['plan_id']}"
    original = client.post(path + "/approve", json={"version": 1, "expected_revision": 1})
    assert original.status_code == 200
    approved = original.json()
    with Session(client.app.state.engine) as db:
        run = db.get(ProductManagerRun, saved["id"])
        original_config = run.diagnostic["generation_configuration"]
        assert original_config["input_bytes"] == exact
        assert original_config["thinking_level"] == "low"
    settings.pm_model, settings.pm_thinking_level, settings.pm_max_input_bytes = (
        "gemini-3.6-flash",
        "minimal",
        8192,
    )
    replay, created = invoke(client, pid, provider, payload)
    assert not created and replay["id"] == saved["id"] and replay["plan_id"] == saved["plan_id"]
    assert provider.calls == 1 and counts(client) == (1, 1, 1)
    old_run = client.get(f"/api/v1/projects/{pid}/pm-runs/{saved['id']}").json()
    assert old_run["requested_model"] == "gemini-3.8-flash"
    assert old_run["returned_model"] == "unit-double-not-live"
    assert client.get(path).json() == approved
    with Session(client.app.state.engine) as db:
        assert (
            db.get(ProductManagerRun, saved["id"]).diagnostic["generation_configuration"]
            == original_config
        )
    with pytest.raises(PMError) as conflict:
        invoke(client, pid, provider, payload.model_copy(update={"brief": "different brief"}))
    assert conflict.value.code == "idempotency_conflict" and provider.calls == 1


def test_raw_escaped_surrogate_rejected_without_run_or_provider(client):
    pid = project(client)
    provider = UnitProvider()
    client.app.dependency_overrides[model_provider] = lambda: provider
    payload = {"client_request_id": str(uuid4()), "brief": "private-sentinel\ud800"}
    response = client.post(
        f"/api/v1/projects/{pid}/pm-runs",
        content=json.dumps(payload, ensure_ascii=True).encode("ascii"),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422 and "private-sentinel" not in response.text
    assert provider.calls == 0 and counts(client) == (0, 0, 1)
    # Also cover the earlier request-hash guard even if the HTTP parser rejects first.
    raw = RunCreate(client_request_id=uuid4(), brief="valid").model_copy(update={"brief": "\ud800"})
    with pytest.raises(PMError) as failure:
        invoke(client, pid, provider, raw)
    assert failure.value.status == 422 and provider.calls == 0 and counts(client) == (0, 0, 1)


@pytest.mark.parametrize(
    "scenario", ["503", "504", "malformed_json", "invalid_schema", "truncated"]
)
def test_alternative_sdk_failure_never_replaces_approved_plan(client, monkeypatch, scenario):
    pid = project(client)
    saved, _ = invoke(client, pid, UnitProvider())
    plan_path = f"/api/v1/projects/{pid}/pm-plans/{saved['plan_id']}"
    approval = client.post(plan_path + "/approve", json={"version": 1, "expected_revision": 1})
    assert approval.status_code == 200
    before = approval.json()
    enable_alternative(client)
    requests = []

    def respond(request):
        requests.append(request)
        if scenario in {"503", "504"}:
            code = int(scenario)
            return httpx.Response(
                code,
                json={
                    "error": {
                        "code": code,
                        "status": "UNAVAILABLE" if code == 503 else "DEADLINE_EXCEEDED",
                        "message": "Controlled SDK upstream failure, not live evidence",
                    }
                },
            )
        output = '{"broken":' if scenario == "malformed_json" else '{"not_a_plan":true}'
        return httpx.Response(
            200,
            json={
                "modelVersion": "controlled-sdk-not-live",
                "candidates": [
                    {
                        "finishReason": "MAX_TOKENS" if scenario == "truncated" else "STOP",
                        "content": {"parts": [{"text": output}]},
                    }
                ],
            },
        )

    monkeypatch.setattr("orba.pm_provider.LimitedTransport", lambda: httpx.MockTransport(respond))
    response = client.post(
        f"/api/v1/projects/{pid}/pm-runs",
        json={"client_request_id": str(uuid4()), "brief": "Track a daily habit"},
    )
    assert response.status_code == (504 if scenario == "504" else 502)
    error = response.json()["error"]
    expected = (
        "provider_unavailable"
        if scenario == "503"
        else ("provider_timeout" if scenario == "504" else "invalid_model_response")
    )
    assert error["code"] == expected and len(requests) == 1
    assert client.get(plan_path).json() == before and counts(client) == (2, 1, 1)
    with Session(client.app.state.engine) as db:
        run = db.get(ProductManagerRun, UUID(error["run_id"]))
        assert run.status == "failed" and run.error_category == expected
        assert run.diagnostic["generation_configuration"]["thinking_level"] == "minimal"
        if scenario in {"503", "504"}:
            assert run.diagnostic["provider_http_status"] == int(scenario)
            assert run.diagnostic["error_origin"] == "upstream_http"
            assert run.returned_model is None and run.usage is None


def test_real_sdk_synthetic_success_validates_and_persists_relational_draft(client, monkeypatch):
    pid = project(client)
    enable_alternative(client)
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "modelVersion": "controlled-sdk-not-live",
                "responseId": "controlled-sdk-response",
                "candidates": [
                    {
                        "finishReason": "STOP",
                        "content": {
                            "parts": [
                                {"text": unit_output().model_dump_json(exclude_defaults=True)}
                            ]
                        },
                    }
                ],
            },
        )

    monkeypatch.setattr("orba.pm_provider.LimitedTransport", lambda: httpx.MockTransport(respond))
    response = client.post(
        f"/api/v1/projects/{pid}/pm-runs",
        json={"client_request_id": str(uuid4()), "brief": "Track a daily habit"},
    )
    assert response.status_code == 201 and len(requests) == 1
    run = response.json()
    assert run["requested_model"] == "gemini-3.6-flash"
    assert run["returned_model"] == "controlled-sdk-not-live" and run["usage"] is None
    plan = client.get(f"/api/v1/projects/{pid}/pm-plans/{run['plan_id']}").json()
    assert plan["state"] == "draft" and plan["approved_at"] is None
    assert plan["document"]["epics"][0]["stories"][0]["acceptance_criteria"]
    assert counts(client) == (1, 1, 1)
    with Session(client.app.state.engine) as db:
        stored = db.get(ProductPlan, UUID(run["plan_id"]))
        graph = read_document(db, stored)
        assert stored.state == "draft" and stored.generating_run_id == UUID(run["id"])
        assert graph.epics[0].stories[0].acceptance_criteria[0].then

"""Real SDK with labeled synthetic metadata HTTP. NOT live Gemini evidence."""

import asyncio
import json

import httpx
import pytest
from pm_support import counts, project

from orba import pm_readiness as readiness
from orba.config import Settings
from scripts import check_pm_config as cli


def config(**changes):
    return Settings(
        _env_file=None, pm_api_key="unit-readiness-secret", pm_model="gemini-3.8-flash"
    ).model_copy(update=changes)


def metadata(**changes):
    return {
        "name": "models/gemini-3.8-flash",
        "inputTokenLimit": 1048576,
        "outputTokenLimit": 65536,
        "supportedGenerationMethods": ["generateContent", "countTokens"],
        "thinking": True,
    } | changes


@pytest.fixture
def synthetic_metadata(monkeypatch):
    seen = []

    def install(handler):
        def transport(request):
            seen.append(request)
            assert request.method == "GET"
            assert request.url.host == "generativelanguage.googleapis.com"
            assert request.url.path == "/v1beta/models/gemini-3.8-flash"
            assert request.content == b""
            assert request.headers["X-Server-Timeout"] == "10"
            assert request.extensions["timeout"]["read"] == 10
            return handler(request)

        monkeypatch.setattr(readiness, "LimitedTransport", lambda: httpx.MockTransport(transport))
        return seen

    async def forbidden(*_args, **_kwargs):
        raise AssertionError("Metadata must never invoke a generation/token-count operation")

    monkeypatch.setattr("google.genai.models.AsyncModels.generate_content", forbidden)
    monkeypatch.setattr("google.genai.models.AsyncModels.count_tokens", forbidden)
    return install


def test_metadata_sdk_get_limits_cleanup_and_no_generation(synthetic_metadata, monkeypatch):
    seen = synthetic_metadata(lambda _: httpx.Response(200, json=metadata()))
    from google.genai import client as sdk

    closes = []
    sync_close, async_close = sdk.Client.close, sdk.AsyncClient.aclose

    def close(client):
        closes.append("sync")
        return sync_close(client)

    async def aclose(client):
        closes.append("async")
        return await async_close(client)

    monkeypatch.setattr(sdk.Client, "close", close)
    monkeypatch.setattr(sdk.AsyncClient, "aclose", aclose)
    report = asyncio.run(readiness.check_model(config()))
    assert report.status == "ready_for_attempt" and report.provider_http_status == 200
    assert report.metadata_model == "models/gemini-3.8-flash"
    assert (
        report.output_token_limit == 65536 and report.generation_limits["max_output_tokens"] == 6000
    )
    assert report.structured_output_support == "documented"
    assert report.metadata_requests == 1 and len(seen) == 1
    assert report.generation_requests == 0 and report.live_generation_verified is False
    assert "sync" in closes and "async" in closes
    assert "unit-readiness-secret" not in report.model_dump_json()


@pytest.mark.parametrize("model", ["gemini-3.8-flash", "models/gemini-3.8-flash"])
def test_exact_model_prefix_is_canonical_without_switching(synthetic_metadata, model):
    seen = synthetic_metadata(lambda _: httpx.Response(200, json=metadata()))
    settings = config(pm_model=model)
    result = asyncio.run(readiness.check_model(settings))
    assert result.status == "ready_for_attempt" and settings.pm_model == model and len(seen) == 1


@pytest.mark.parametrize(
    "change,expected",
    [
        ({"name": None}, "unknown"),
        ({"name": "models/gemini-other"}, "unknown"),
        ({"supportedGenerationMethods": None}, "unknown"),
        ({"supportedGenerationMethods": []}, "unknown"),
        ({"supportedGenerationMethods": ["embedContent"]}, "model_not_supported"),
        ({"inputTokenLimit": None}, "unknown"),
        ({"outputTokenLimit": 0}, "unknown"),
        ({"outputTokenLimit": 1024}, "invalid_configuration"),
        ({"thinking": False}, "unknown"),
    ],
)
def test_incomplete_or_incompatible_metadata_is_not_ready(synthetic_metadata, change, expected):
    seen = synthetic_metadata(lambda _: httpx.Response(200, json=metadata(**change)))
    report = asyncio.run(readiness.check_model(config()))
    assert report.status == expected and report.live_generation_verified is False and len(seen) == 1


def test_unreviewed_model_metadata_does_not_assert_structured_compatibility(monkeypatch):
    seen = []

    def respond(request):
        seen.append(request)
        return httpx.Response(200, json=metadata(name="models/gemini-other"))

    monkeypatch.setattr(readiness, "LimitedTransport", lambda: httpx.MockTransport(respond))
    result = asyncio.run(readiness.check_model(config(pm_model="gemini-other")))
    # The new reviewed-ID policy is stricter: reject before metadata or reflection.
    assert result.status == "model_not_supported" and result.structured_output_support == "unknown"
    assert len(seen) == 0 and result.requested_model is None


@pytest.mark.parametrize(
    "code,status",
    [
        (400, "credential_error"),
        (401, "credential_error"),
        (403, "credential_error"),
        (404, "model_not_supported"),
        (429, "rate_limited"),
        (500, "provider_unavailable"),
        (502, "provider_unavailable"),
        (503, "provider_unavailable"),
        (504, "timeout"),
        (418, "unknown"),
    ],
)
def test_metadata_http_errors_are_safe_and_not_retried(synthetic_metadata, caplog, code, status):
    seen = synthetic_metadata(
        lambda _: httpx.Response(
            code,
            json={
                "error": {
                    "code": code,
                    "message": "private-provider-body-marker",
                    "status": "UNAVAILABLE",
                    "details": [{"reason": "API_KEY_INVALID"}] if code == 400 else [],
                }
            },
            headers={"x-request-id": "private-header-marker"},
        )
    )
    report = asyncio.run(readiness.check_model(config()))
    assert report.status == status and report.provider_http_status == code and len(seen) == 1
    assert report.error_origin == "upstream_http" and report.generation_requests == 0
    assert "private-provider-body-marker" not in report.model_dump_json() + caplog.text
    assert "private-header-marker" not in report.model_dump_json() + caplog.text
    assert "unit-readiness-secret" not in report.model_dump_json() + caplog.text


@pytest.mark.parametrize(
    "kind,status,origin",
    [
        ("timeout", "timeout", "transport_timeout"),
        ("network", "provider_unavailable", "transport_unavailable"),
        ("malformed", "unknown", "metadata_response"),
    ],
)
def test_metadata_transport_and_decode_errors_are_honest(synthetic_metadata, kind, status, origin):
    def response(request):
        if kind == "timeout":
            raise httpx.ReadTimeout("private-marker", request=request)
        if kind == "network":
            raise httpx.ConnectError("private-marker", request=request)
        return httpx.Response(200, text="private-marker-not-json")

    seen = synthetic_metadata(response)
    report = asyncio.run(readiness.check_model(config()))
    assert report.status == status and report.error_origin == origin and len(seen) == 1
    assert "private-marker" not in report.model_dump_json()


def test_outer_metadata_cancellation_is_bounded_and_safe(monkeypatch):
    async def held(_request):
        await asyncio.sleep(10)

    monkeypatch.setattr(readiness, "METADATA_ENVELOPE_SECONDS", 0)
    monkeypatch.setattr(readiness, "LimitedTransport", lambda: httpx.MockTransport(held))
    report = asyncio.run(readiness.check_model(config()))
    assert report.status == "timeout" and report.error_origin == "local_envelope_timeout"
    assert report.elapsed_ms < 1000 and report.live_generation_verified is False


@pytest.mark.parametrize("compressed", [False, True])
def test_real_bounded_transport_rejects_metadata_envelope(monkeypatch, compressed):
    from orba.pm_provider import MAX_ENVELOPE_BYTES, LimitedTransport

    def transport():
        bounded = LimitedTransport()
        bounded.transport = httpx.MockTransport(
            lambda _: httpx.Response(
                200,
                content=b"x" * (MAX_ENVELOPE_BYTES + 1),
                headers={"content-encoding": "unsupported"} if compressed else {},
            )
        )
        return bounded

    monkeypatch.setattr(readiness, "LimitedTransport", transport)
    result = asyncio.run(readiness.check_model(config()))
    assert result.status == "unknown" and result.error_origin == "metadata_response"


@pytest.mark.parametrize(
    "change,expected",
    [
        ({"pm_api_key": None}, "not_configured"),
        ({"pm_model": None}, "not_configured"),
        (
            {"pm_api_key": Settings(_env_file=None, pm_api_key="  ").pm_api_key},
            "invalid_configuration",
        ),
    ],
)
def test_missing_or_blank_configuration_never_dispatches(monkeypatch, change, expected):
    def tripwire():
        raise AssertionError("No configured provider must mean no HTTP client")

    monkeypatch.setattr(readiness, "LimitedTransport", tripwire)
    report = asyncio.run(readiness.check_model(config(**change)))
    assert report.status == expected and report.metadata_requests == 0


def test_cli_offline_help_and_invalid_args_never_dispatch(monkeypatch, capsys):
    def tripwire(*_args, **_kwargs):
        raise AssertionError("Offline command must not construct network/config during help")

    monkeypatch.setattr(cli, "Settings", tripwire)
    with pytest.raises(SystemExit) as helped:
        cli.main(["--help"])
    assert helped.value.code == 0 and "--check-model" in capsys.readouterr().out
    with pytest.raises(SystemExit) as invalid:
        cli.main(["--unknown-option"])
    assert invalid.value.code == 2
    capsys.readouterr()
    monkeypatch.setattr(cli, "Settings", lambda: config())
    monkeypatch.setattr(cli, "check_model", tripwire)
    assert cli.main([]) == 0
    report = json.loads(capsys.readouterr().out)
    assert (
        report["configured"] and report["status"] == "unknown" and report["metadata_requests"] == 0
    )
    monkeypatch.setattr(cli, "Settings", lambda: config(pm_api_key=None))
    assert cli.main([]) == 1
    assert json.loads(capsys.readouterr().out)["verdict"] == "BLOCKED"
    monkeypatch.setattr(cli, "check_model", readiness.check_model)
    monkeypatch.setattr(readiness, "LimitedTransport", tripwire)
    assert cli.main(["--check-model"]) == 2  # Missing config still never calls the SDK.
    assert json.loads(capsys.readouterr().out)["metadata_requests"] == 0


@pytest.mark.parametrize("args", [[], ["--check-model"]])
def test_cli_invalid_settings_omit_private_input(monkeypatch, capsys, args):
    def invalid():
        return Settings(_env_file=None, pm_model="private-invalid-model-marker")

    monkeypatch.setattr(cli, "Settings", invalid)
    assert cli.main(args) == 2
    captured = capsys.readouterr()
    assert "private-invalid-model-marker" not in captured.out + captured.err
    assert json.loads(captured.out)["status"] == "invalid_configuration"


@pytest.mark.parametrize("code,exit_code", [(200, 0), (503, 2)])
def test_explicit_cli_uses_actual_readiness_result(
    synthetic_metadata, monkeypatch, capsys, code, exit_code
):
    seen = synthetic_metadata(
        lambda _: httpx.Response(
            code,
            json=metadata() if code == 200 else {"error": {"code": 503, "message": "unavailable"}},
        )
    )
    monkeypatch.setattr(cli, "Settings", lambda: config())
    assert cli.main(["--check-model"]) == exit_code
    data = json.loads(capsys.readouterr().out)
    assert data["metadata_requests"] == len(seen) == 1 and data["generation_requests"] == 0


def test_metadata_diagnosis_does_not_create_database_runs_or_plans(client, synthetic_metadata):
    project(client)
    before = counts(client)
    synthetic_metadata(lambda _: httpx.Response(200, json=metadata()))
    assert asyncio.run(readiness.check_model(config())).status == "ready_for_attempt"
    assert counts(client) == before

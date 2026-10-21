"""Deterministic configuration/real-SDK synthetic HTTP tests. NEVER live AI evidence."""

import asyncio
import json
import subprocess
import sys

import httpx
import pytest
from pm_support import unit_output
from pydantic import ValidationError

from orba.config import Settings
from orba.pm_models_policy import APPROVED_MODELS, model_policy
from orba.pm_provider import (
    PROMPT,
    GeminiProductManagerProvider,
    ProviderFailure,
    gemini_output_schema,
    request_metrics,
)
from orba.pm_readiness import check_model
from orba.pm_schemas import ProductDocument, canonical, document_nodes, validate_generated
from scripts.verification import ROOT, deterministic_env


def config(**changes):
    return Settings(
        **{
            "_env_file": None,
            "pm_api_key": "controlled-unit-not-a-runtime-key",
            "pm_model": "gemini-3.8-flash",
            "pm_max_output_tokens": 6000,
        }
        | changes
    )


@pytest.mark.parametrize("prefix", ["", "models/"])
@pytest.mark.parametrize(
    "model,level",
    [(policy.identifier, level) for policy in APPROVED_MODELS for level in policy.thinking_levels],
)
def test_reviewed_model_and_level_reach_real_sdk_once(monkeypatch, prefix, model, level):
    requests = []

    def respond(request):
        requests.append(request)
        assert request.method == "POST" and request.url.path.endswith(f"/{model}:generateContent")
        body = json.loads(request.content)
        generation = body["generationConfig"]
        # google-genai2.31 serializes the nested protobuf field in snake_case.
        # Assert its actual explicit value, not an assumed alternate JSON alias.
        assert generation["thinkingConfig"]["thinking_level"] == level.upper()
        assert generation["maxOutputTokens"] == 6000 and generation["candidateCount"] == 1
        assert generation["responseJsonSchema"] == gemini_output_schema()
        assert generation["responseMimeType"] == "application/json"
        assert body.get("tools", []) == []
        return httpx.Response(
            200,
            json={
                "modelVersion": "controlled-http-returned-model",
                "responseId": "controlled-http-response",
                "candidates": [
                    {"finishReason": "STOP", "content": {"parts": [{"text": '{"unit":true}'}]}}
                ],
            },
        )

    monkeypatch.setattr("orba.pm_provider.LimitedTransport", lambda: httpx.MockTransport(respond))
    settings = config(pm_model=prefix + model, pm_thinking_level=level)
    result = asyncio.run(GeminiProductManagerProvider(settings).generate({"brief": "unit brief"}))
    assert settings.pm_model == prefix + model and len(requests) == 1
    assert result.output == '{"unit":true}' and result.model == "controlled-http-returned-model"
    assert result.response_id == "controlled-http-response" and result.usage is None


@pytest.mark.parametrize(
    "changes",
    [
        {"pm_model": "gemini-other"},
        {"pm_model": "gemini-3.7-flash"},  # Provider-routed aliases are not alternatives.
        {"pm_model": "GEMINI-3.6-FLASH"},
        {"pm_model": "https://example.com/models/gemini-3.6-flash"},
        {"pm_model": "gemini-3.8-flash", "pm_thinking_level": "minimal"},
        {"pm_thinking_level": ""},
        {"pm_thinking_level": "unbounded"},
        {"pm_max_input_bytes": 8191},
        {"pm_max_input_bytes": 96001},
        {"pm_max_output_tokens": 511},
        {"pm_max_output_tokens": 16001},
        {"pm_timeout_seconds": 4},
        {"pm_timeout_seconds": 181},
    ],
)
def test_invalid_configuration_rejects_before_sdk(changes, monkeypatch):
    monkeypatch.setattr(
        "orba.pm_provider.LimitedTransport",
        lambda: pytest.fail("Invalid configuration must not construct an HTTP client"),
    )
    with pytest.raises(ValidationError):
        config(**changes)


def test_explicit_normalization_has_no_model_default_or_silent_switch():
    settings = config(pm_model=" models/gemini-3.6-flash ", pm_thinking_level=" MINIMAL ")
    assert (
        settings.pm_model == "models/gemini-3.6-flash" and settings.pm_thinking_level == "minimal"
    )
    missing = config(pm_api_key=None, pm_model=None)
    assert (
        not missing.pm_configured
        and missing.pm_model is None
        and missing.pm_thinking_level == "low"
    )
    assert model_policy("gemini-3.7-flash") is None


@pytest.mark.parametrize("field", ["ORBA_PM_MODEL", "ORBA_PM_THINKING_LEVEL"])
def test_actual_invalid_api_startup_hides_supplied_values(field):
    marker = "misplaced-private-credential-sentinel"
    env = deterministic_env()
    env.update(ORBA_PM_MODEL="gemini-3.8-flash", ORBA_PM_THINKING_LEVEL="low")
    env[field] = marker
    child = subprocess.run(
        [sys.executable, "-c", "import orba.main"],
        cwd=ROOT / "apps/api",
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=20,
        check=False,
    )
    assert child.returncode == 1 and "ValidationError" in child.stderr
    assert marker not in child.stdout + child.stderr and "input_value=" not in child.stderr


@pytest.mark.parametrize(
    "changes", [{"pm_model": "gemini-unreviewed"}, {"pm_thinking_level": "minimal"}]
)
def test_copied_invalid_settings_cannot_dispatch(changes, monkeypatch):
    monkeypatch.setattr(
        "orba.pm_provider.LimitedTransport",
        lambda: pytest.fail("No client before policy validation"),
    )
    with pytest.raises(ProviderFailure) as error:
        asyncio.run(
            GeminiProductManagerProvider(config().model_copy(update=changes)).generate(
                {"brief": "unit"}
            )
        )
    assert error.value.category == "pm_invalid_configuration"


def test_shared_utf8_content_budget_equality_and_one_byte_over(monkeypatch):
    snapshot = {"brief": "漢" * 1200, "instructions": 'Quote " and slash \\ with\nnewline'}
    metrics = request_metrics(snapshot)
    assert metrics["snapshot_bytes"] == len(canonical(snapshot).encode("utf-8"))
    assert metrics["snapshot_bytes"] > len(canonical(snapshot))
    assert metrics["input_bytes"] == (
        len(PROMPT.encode("utf-8"))
        + len(canonical(gemini_output_schema()).encode("utf-8"))
        + len(canonical(snapshot).encode("utf-8"))
    )
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(
            200,
            json={"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": "{}"}]}}]},
        )

    monkeypatch.setattr("orba.pm_provider.LimitedTransport", lambda: httpx.MockTransport(respond))
    exact = config(pm_max_input_bytes=metrics["input_bytes"])
    assert asyncio.run(GeminiProductManagerProvider(exact).generate(snapshot)).output == "{}"
    assert len(requests) == 1
    with pytest.raises(ProviderFailure) as error:
        asyncio.run(
            GeminiProductManagerProvider(
                config(pm_max_input_bytes=metrics["input_bytes"] - 1)
            ).generate(snapshot)
        )
    assert error.value.category == "input_too_large" and error.value.status == 422
    assert len(requests) == 1  # Rejection was before another client/SDK dispatch.


def test_invalid_unicode_cannot_reach_provider(monkeypatch):
    monkeypatch.setattr(
        "orba.pm_provider.LimitedTransport",
        lambda: pytest.fail("Invalid Unicode must not dispatch"),
    )
    with pytest.raises(ProviderFailure) as error:
        asyncio.run(GeminiProductManagerProvider(config()).generate({"brief": "private\ud800"}))
    assert error.value.category == "validation_error" and "private" not in error.value.message


def test_lean_hint_retains_required_fields_and_full_server_contract():
    full = ProductDocument.model_json_schema()
    hint = gemini_output_schema()
    assert hint["required"] == full["required"]
    assert set(hint["properties"]) == set(full["properties"]) == set(ProductDocument.model_fields)
    assert full["properties"]["epics"]["maxItems"] == 8
    assert "actor_id" in full["$defs"]["Source"]["properties"]
    assert set(hint["$defs"]["Source"]["properties"]) == {"kind", "quote", "context_key"}
    assert set(hint["$defs"]["Confirmation"]["properties"]) == {"key", "text", "source", "blocking"}
    assert "human" in full["$defs"]["Source"]["properties"]["kind"]["enum"]
    assert "human" not in hint["$defs"]["Source"]["properties"]["kind"]["enum"]
    assert ProductDocument.model_json_schema() == full
    document = unit_output()
    for _, node in document_nodes(document):
        assert node.source.actor_id is None and node.source.inherited_kind is None
    assert validate_generated(document, {"brief": "unit"}).epics[0].stories[0].acceptance_criteria
    document.product_name.source.kind = "human"
    with pytest.raises(ValueError, match="human"):
        validate_generated(document, {"brief": "unit"})


@pytest.mark.parametrize(
    "model,level",
    [
        ("gemini-3.8-flash", "low"),
        ("gemini-3.6-flash", "minimal"),
        ("gemini-3.5-flash-lite", "minimal"),
    ],
)
def test_each_reviewed_model_metadata_is_one_get_not_generation(monkeypatch, model, level):
    requests = []

    def respond(request):
        requests.append(request)
        assert request.method == "GET" and request.url.path.endswith("/models/" + model)
        return httpx.Response(
            200,
            json={
                "name": "models/" + model,
                "supportedGenerationMethods": ["generateContent"],
                "inputTokenLimit": 1048576,
                "outputTokenLimit": 65536,
                "thinking": True,
            },
        )

    monkeypatch.setattr("orba.pm_readiness.LimitedTransport", lambda: httpx.MockTransport(respond))
    result = asyncio.run(check_model(config(pm_model=model, pm_thinking_level=level)))
    assert len(requests) == result.metadata_requests == 1 and result.generation_requests == 0
    assert result.status == "ready_for_attempt" and result.live_generation_verified is False
    assert result.structured_output_documentation == model_policy(model).documentation
    assert result.thinking_level == level and result.generation_limits["max_input_bytes"] == 48000

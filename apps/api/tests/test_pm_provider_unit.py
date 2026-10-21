"""Isolated real-SDK transport contracts. Synthetic HTTP is NOT live AI evidence."""

import asyncio
import json
from uuid import uuid4

import httpx
import pytest
from pydantic import ValidationError

from orba.config import Settings
from orba.pm_provider import GeminiProductManagerProvider, ProviderFailure, gemini_output_schema
from orba.pm_schemas import ProductDocument
from scripts.pm_sample import human_document


def unit_settings():
    return Settings(
        _env_file=None,
        pm_api_key="unit-runtime-key",
        pm_model="gemini-3.8-flash",
        pm_max_output_tokens=6000,
        pm_timeout_seconds=60,
    )


@pytest.mark.parametrize("budget", [5, 180])
def test_real_sdk_distinct_server_and_transport_deadlines(monkeypatch, budget):
    """Synthetic HTTP; actual official SDK timeout/header contract, no live call."""
    seen = []

    def transport(request):
        seen.append(request)
        assert request.headers["X-Server-Timeout"] == str(budget)
        assert request.extensions["timeout"]["read"] == budget + 5
        raise httpx.ReadTimeout("synthetic-private-marker", request=request)

    monkeypatch.setattr("orba.pm_provider.LimitedTransport", lambda: httpx.MockTransport(transport))
    config = unit_settings().model_copy(update={"pm_timeout_seconds": budget})
    with pytest.raises(ProviderFailure) as error:
        asyncio.run(GeminiProductManagerProvider(config).generate({"brief": "private-marker"}))
    assert len(seen) == 1 and error.value.category == "provider_timeout"
    assert error.value.diagnostic["error_origin"] == "transport_timeout"
    assert "private-marker" not in str(error.value.diagnostic) + error.value.message


def test_real_sdk_parses_candidate_and_usage_and_makes_one_bounded_request(monkeypatch):
    requests = []

    def transport(request):
        requests.append(request)
        body = json.loads(request.content)
        config = body["generationConfig"]
        assert request.url.host == "generativelanguage.googleapis.com"
        assert config["maxOutputTokens"] == 6000 and config["candidateCount"] == 1
        assert config["responseMimeType"] == "application/json"
        thinking = config["thinkingConfig"]
        assert thinking.get("thinkingLevel", thinking.get("thinking_level")) == "LOW"
        assert config["responseJsonSchema"] == gemini_output_schema()
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {"parts": [{"text": '{"unit_contract":true}'}]},
                        "finishReason": "STOP",
                    }
                ],
                "modelVersion": "unit-model-fixture",
                "responseId": "unit-response-fixture",
                "usageMetadata": {
                    "promptTokenCount": 5,
                    "candidatesTokenCount": 3,
                    "totalTokenCount": 8,
                },
            },
            headers={"x-request-id": "unit-request-fixture"},
        )

    monkeypatch.setattr("orba.pm_provider.LimitedTransport", lambda: httpx.MockTransport(transport))
    result = asyncio.run(GeminiProductManagerProvider(unit_settings()).generate({"brief": "unit"}))
    assert len(requests) == 1
    assert result.output == '{"unit_contract":true}'
    assert result.model == "unit-model-fixture" and result.response_id == "unit-response-fixture"
    assert result.request_id == "unit-request-fixture" and result.usage["total_token_count"] == 8


@pytest.mark.parametrize(
    "code,message,category,hint",
    [
        (
            400,
            "The specified schema has too many states for serving. secret",
            "provider_request_failed",
            "schema_state_limit",
        ),
        (429, "Quota exceeded. secret", "provider_rate_limited", None),
        (504, "Provider deadline exceeded. secret", "provider_timeout", None),
        (500, "Internal provider error. secret", "provider_unavailable", None),
        (503, "Unavailable. secret", "provider_unavailable", None),
    ],
)
def test_real_sdk_rejection_is_safe_and_never_automatically_retried(
    monkeypatch, code, message, category, hint
):
    requests = []

    def transport(request):
        requests.append(request)
        return httpx.Response(
            code,
            json={
                "error": {
                    "code": code,
                    "message": message,
                    "status": {
                        400: "INVALID_ARGUMENT",
                        429: "RESOURCE_EXHAUSTED",
                        504: "DEADLINE_EXCEEDED",
                        500: "INTERNAL",
                        503: "UNAVAILABLE",
                    }[code],
                }
            },
        )

    monkeypatch.setattr("orba.pm_provider.LimitedTransport", lambda: httpx.MockTransport(transport))
    with pytest.raises(ProviderFailure) as failure:
        asyncio.run(GeminiProductManagerProvider(unit_settings()).generate({"brief": "unit"}))
    assert len(requests) == 1 and failure.value.category == category
    assert failure.value.status == (code if code in {429, 504} else 502)
    assert failure.value.diagnostic.get("request_rejection") == hint
    assert failure.value.diagnostic["error_origin"] == "upstream_http"
    assert "secret" not in str(failure.value.diagnostic) and "secret" not in failure.value.message


def test_outer_deadline_cancellation_is_safe_and_not_retried(monkeypatch):
    seen = []

    async def transport(request):
        seen.append(request)
        await asyncio.sleep(0)  # Yield to an actual zero-budget asyncio deadline.
        raise AssertionError("The outer deadline should cancel this request")

    monkeypatch.setattr("orba.pm_provider.ENVELOPE_GRACE_SECONDS", -60)
    monkeypatch.setattr("orba.pm_provider.LimitedTransport", lambda: httpx.MockTransport(transport))
    with pytest.raises(ProviderFailure) as error:
        asyncio.run(GeminiProductManagerProvider(unit_settings()).generate({"brief": "unit"}))
    assert error.value.category == "provider_timeout" and len(seen) == 1
    assert error.value.diagnostic["error_origin"] == "local_envelope_timeout"


def test_provider_projection_keeps_full_pydantic_validation_and_property_names():
    original = ProductDocument.model_json_schema()
    hint = gemini_output_schema()
    assert original["properties"]["epics"]["maxItems"] == 8
    assert "maxItems" not in hint["properties"]["epics"]
    assert "title" in hint["$defs"]["Story"]["properties"]
    assert hint["properties"]["schema_version"]["enum"] == [1]
    assert ProductDocument.model_json_schema() == original
    invalid = human_document(uuid4()).model_dump(mode="json")
    invalid["product_name"]["text"] = "x" * 2001
    with pytest.raises(ValidationError):
        ProductDocument.model_validate(invalid)

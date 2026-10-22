import pytest
from pydantic import SecretStr, ValidationError

from orba.architect_provider import GeminiArchitectProvider, output_schema, request_metrics
from orba.config import Settings


@pytest.mark.parametrize(
    "model,thinking",
    [
        ("gemini-3.6-flash", "minimal"),
        ("models/gemini-3.5-flash-lite", "minimal"),
        ("gemini-3.8-flash", "low"),
    ],
)
def test_explicit_reviewed_architect_selection(model, thinking):
    config = Settings(
        _env_file=None,
        pm_model="gemini-3.8-flash",
        architect_model=model,
        architect_thinking_level=thinking,
    )
    assert config.architect_settings().pm_model == model
    assert config.pm_model == "gemini-3.8-flash"


@pytest.mark.parametrize(
    "model,thinking",
    [("invented-model", "low"), ("gemini-3.8-flash", "minimal"), ("gemini-9-pro", "low")],
)
def test_invalid_selection_rejected_before_dispatch(model, thinking):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, architect_model=model, architect_thinking_level=thinking)


def test_no_implicit_model_fallback_and_credential_precedence():
    config = Settings(
        _env_file=None, pm_model="gemini-3.8-flash", pm_api_key=SecretStr("controlled-not-runtime")
    )
    assert not config.architect_settings().pm_configured
    config.architect_model = "gemini-3.6-flash"
    assert config.architect_settings().pm_configured
    config.architect_api_key = SecretStr("controlled-separate")
    assert config.architect_settings().pm_api_key.get_secret_value() == "controlled-separate"
    config.architect_api_key = SecretStr("")
    assert config.architect_settings().pm_api_key.get_secret_value() == "controlled-not-runtime"


def test_shared_transport_uses_architect_prompt_and_bounded_schema():
    config = Settings(_env_file=None)
    provider = GeminiArchitectProvider(config)
    metrics = request_metrics(config, {"approved_product_plan": {}})
    assert (
        metrics["input_bytes"]
        == metrics["prompt_bytes"] + metrics["provider_schema_bytes"] + metrics["snapshot_bytes"]
    )
    assert metrics["provider_schema_bytes"] > 0 and len(metrics["provider_schema_sha256"]) == 64
    assert provider.schema_factory() == output_schema()
    assert "cannot execute" in provider.prompt


@pytest.mark.parametrize("status", [200, 503, 504])
def test_actual_sdk_architect_contract_using_labeled_synthetic_http(monkeypatch, status):
    import asyncio
    import json

    import httpx

    from orba.architect_provider import PROMPT
    from orba.pm_provider import ProviderFailure

    calls = []

    def transport(request):
        calls.append(request)
        body = json.loads(request.content)
        configuration = body["generationConfig"]
        assert configuration["responseJsonSchema"] == output_schema()
        assert configuration["maxOutputTokens"] == 6000
        thinking = configuration["thinkingConfig"]
        assert thinking.get("thinkingLevel", thinking.get("thinking_level")) == "MINIMAL"
        assert body["systemInstruction"]["parts"][0]["text"] == PROMPT
        assert request.headers["X-Server-Timeout"] == "90"
        assert request.extensions["timeout"]["read"] == 95
        if status != 200:
            return httpx.Response(
                status,
                json={
                    "error": {
                        "code": status,
                        "status": "UNAVAILABLE" if status == 503 else "DEADLINE_EXCEEDED",
                        "message": "Controlled HTTP, not live evidence",
                    }
                },
            )
        return httpx.Response(
            200,
            json={
                "candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": "{}"}]}}],
                "modelVersion": "controlled-sdk-not-live",
                "usageMetadata": {
                    "promptTokenCount": 2,
                    "candidatesTokenCount": 1,
                    "totalTokenCount": 3,
                },
            },
        )

    monkeypatch.setattr("orba.pm_provider.LimitedTransport", lambda: httpx.MockTransport(transport))
    config = Settings(
        _env_file=None,
        architect_api_key="controlled-not-runtime",
        architect_model="gemini-3.6-flash",
        architect_thinking_level="minimal",
    )
    if status == 200:
        result = asyncio.run(
            GeminiArchitectProvider(config).generate({"approved_product_plan": {}})
        )
        assert result.model == "controlled-sdk-not-live" and result.usage["total_token_count"] == 3
    else:
        with pytest.raises(ProviderFailure) as failure:
            asyncio.run(GeminiArchitectProvider(config).generate({"approved_product_plan": {}}))
        assert failure.value.diagnostic["provider_http_status"] == status
        assert "No new architecture" in failure.value.message
    assert len(calls) == 1

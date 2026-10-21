"""Explicit, read-only provider diagnosis. Metadata is never generation evidence.

offline Settings -> explicit models.get (one GET) -> safe point-in-time report
No database, generation, tools, fallback, pagination, polling or automatic retry.
"""

import asyncio
from datetime import UTC, datetime
from importlib.metadata import version
from time import monotonic
from typing import Literal

import httpx
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, ConfigDict, Field

from orba.config import Settings
from orba.pm_models_policy import (
    MODEL_CONFIGURATION_HELP,
    ThinkingLevel,
    model_policy,
    validate_model_configuration,
)
from orba.pm_provider import (
    ENVELOPE_GRACE_SECONDS,
    PROVIDER,
    TRANSPORT_GRACE_SECONDS,
    LimitedTransport,
    ProviderFailure,
    error_metadata,
    safe_identifier,
)

METADATA_TIMEOUT_SECONDS = 10
METADATA_ENVELOPE_SECONDS = 12

ReadinessStatus = Literal[
    "not_configured",
    "invalid_configuration",
    "model_not_supported",
    "credential_error",
    "provider_unavailable",
    "rate_limited",
    "timeout",
    "ready_for_attempt",
    "unknown",
]


class ProviderReadiness(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)

    version: Literal[1] = 1
    operation: Literal["configuration", "model_metadata"] = "configuration"
    status: ReadinessStatus
    message: str
    checked_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    provider: Literal["google-gemini"] = PROVIDER
    sdk_version: str = Field(default_factory=lambda: version("google-genai"))
    configured: bool = False
    requested_model: str | None = Field(default=None, max_length=160)
    thinking_level: ThinkingLevel | None = None
    metadata_model: str | None = Field(default=None, max_length=200)
    supported_actions: list[str] = Field(default_factory=list, max_length=16)
    input_token_limit: int | None = Field(default=None, ge=1)
    output_token_limit: int | None = Field(default=None, ge=1)
    structured_output_support: Literal["documented", "unknown"] = "unknown"
    structured_output_documentation: str | None = None
    generation_limits: dict[str, int] = Field(default_factory=dict)
    metadata_timeout_seconds: int = METADATA_TIMEOUT_SECONDS
    metadata_envelope_seconds: int = METADATA_ENVELOPE_SECONDS
    metadata_requests: Literal[0, 1] = 0
    generation_requests: Literal[0] = 0
    live_generation_verified: Literal[False] = False
    provider_http_status: int | None = Field(default=None, ge=100, le=599)
    error_origin: (
        Literal[
            "upstream_http",
            "transport_timeout",
            "local_envelope_timeout",
            "transport_unavailable",
            "metadata_response",
        ]
        | None
    ) = None
    elapsed_ms: float = Field(default=0, ge=0)


def configuration_readiness(config: Settings) -> ProviderReadiness:
    # Guard copied/mutated Settings too, before echoing any unreviewed value or
    # constructing a network client. Ordinary Settings validation is fail-closed.
    if config.pm_model and model_policy(config.pm_model) is None:
        return ProviderReadiness(status="model_not_supported", message=MODEL_CONFIGURATION_HELP)
    try:
        validate_model_configuration(config.pm_model, config.pm_thinking_level)
    except ValueError:
        return ProviderReadiness(status="invalid_configuration", message=MODEL_CONFIGURATION_HELP)
    report = ProviderReadiness(
        status="unknown" if config.pm_configured else "not_configured",
        message=(
            "Configuration is present. Use --check-model for one read-only metadata check; "
            "generation and provider availability remain unverified."
            if config.pm_configured
            else "Set GEMINI_API_KEY (or ORBA_PM_API_KEY) and an explicit ORBA_PM_MODEL "
            "server-side, then restart the API. No provider request was sent."
        ),
        configured=config.pm_configured,
        requested_model=config.pm_model,
        thinking_level=config.pm_thinking_level,
        generation_limits={
            "server_timeout_seconds": config.pm_timeout_seconds,
            "transport_timeout_seconds": config.pm_timeout_seconds + TRANSPORT_GRACE_SECONDS,
            "envelope_timeout_seconds": config.pm_timeout_seconds + ENVELOPE_GRACE_SECONDS,
            "max_output_tokens": config.pm_max_output_tokens,
            "max_input_bytes": config.pm_max_input_bytes,
            "max_concurrent": config.pm_max_concurrent,
            "account_attempts_per_hour": config.pm_account_attempts,
            "global_attempts_per_hour": config.pm_global_attempts,
        },
    )
    if config.pm_api_key and not config.pm_api_key.get_secret_value().strip():
        return report.model_copy(
            update={
                "status": "invalid_configuration",
                "message": "The runtime credential is blank. Correct local configuration; "
                "no provider request was sent.",
            }
        )
    return report


def _observed(report, started, **fields):
    return ProviderReadiness(
        **(report.model_dump() | fields | {"elapsed_ms": round((monotonic() - started) * 1000, 3)})
    )


def _model_metadata(report, model, configured_output):
    """Allowlist public scalar metadata. Never retain descriptions/headers/bodies."""
    name = safe_identifier(model.name)
    actions = [
        action
        for action in (model.supported_actions or [])[:16]
        if isinstance(action, str)
        and action
        in {
            "generateContent",
            "countTokens",
            "createCachedContent",
            "batchGenerateContent",
            "embedContent",
            "batchEmbedContents",
        }
    ]
    limits = {
        key: value if isinstance(value, int) and value > 0 else None
        for key, value in {
            "input_token_limit": model.input_token_limit,
            "output_token_limit": model.output_token_limit,
        }.items()
    }
    fields = {"metadata_model": name, "supported_actions": actions, **limits}
    expected = "models/" + report.requested_model.removeprefix("models/")
    if name != expected or not model.supported_actions or not all(limits.values()):
        return fields | {
            "status": "unknown",
            "message": "Provider metadata is incomplete or does not identify the exact requested "
            "model. Review configuration and official model documentation; generation is unverified.",
        }
    if "generateContent" not in model.supported_actions:
        return fields | {
            "status": "model_not_supported",
            "message": "This model's metadata does not advertise generateContent. Review the "
            "configured model and account access; ORBA did not switch models or generate content.",
        }
    if configured_output > model.output_token_limit:
        return fields | {
            "status": "invalid_configuration",
            "message": "ORBA_PM_MAX_OUTPUT_TOKENS exceeds the advertised model limit. Correct "
            "the local limit before requesting generation. No generation was sent.",
        }
    policy = model_policy(report.requested_model)
    if policy is None or model.thinking is False:
        return fields | {
            "status": "unknown",
            "message": "Model metadata is accessible, but this configuration's structured-output "
            "compatibility has not been established by the reviewed model documentation. "
            "Review the model before authorizing generation; ORBA did not switch models.",
        }
    return fields | {
        "status": "ready_for_attempt",
        "structured_output_support": "documented",
        "structured_output_documentation": policy.documentation,
        "message": "The exact model advertises generateContent and compatible token limits; "
        "structured output is documented. Ready for a separately authorized live attempt only. "
        "Metadata does not prove generation, schema acceptance, available quota or persistence.",
    }


async def check_model(config: Settings) -> ProviderReadiness:
    started = monotonic()
    report = configuration_readiness(config).model_copy(update={"operation": "model_metadata"})
    if report.status != "unknown" or not report.configured:
        return report
    report = report.model_copy(update={"metadata_requests": 1})
    try:
        async with asyncio.timeout(METADATA_ENVELOPE_SECONDS):
            async with httpx.AsyncClient(
                transport=LimitedTransport(),
                trust_env=False,
                follow_redirects=False,
                timeout=METADATA_TIMEOUT_SECONDS,
            ) as http:
                client = genai.Client(
                    api_key=config.pm_api_key.get_secret_value(),
                    vertexai=False,
                    http_options=types.HttpOptions(
                        base_url="https://generativelanguage.googleapis.com/",
                        api_version="v1beta",
                        headers={"X-Server-Timeout": str(METADATA_TIMEOUT_SECONDS)},
                        timeout=METADATA_TIMEOUT_SECONDS * 1000,
                        retry_options=types.HttpRetryOptions(attempts=1),
                        httpx_async_client=http,
                        client_args={"trust_env": False},
                    ),
                )
                try:
                    model = await client.aio.models.get(model=config.pm_model)
                finally:
                    await client.aio.aclose()
                    client.close()
        return _observed(
            report,
            started,
            provider_http_status=200,
            **_model_metadata(report, model, config.pm_max_output_tokens),
        )
    except errors.APIError as exc:
        status = exc.code
        category, message = {
            401: (
                "credential_error",
                "The provider rejected the credential. Check local key/account access.",
            ),
            403: (
                "credential_error",
                "The provider denied metadata access. Check local key/account access.",
            ),
            404: (
                "model_not_supported",
                "Metadata for this model was not found for this credential. Check the model identifier and account access; no model was switched.",
            ),
            429: (
                "rate_limited",
                "The provider rate limited the metadata check. Wait before an explicit read-only recheck; no generation was sent.",
            ),
            504: (
                "timeout",
                "The provider returned a metadata deadline error. No generation was sent; recheck explicitly later.",
            ),
        }.get(
            status,
            (
                "provider_unavailable" if status in {500, 502, 503} else "unknown",
                (
                    "The provider could not establish metadata readiness. No generation was sent. "
                    "Check provider availability/configuration before an explicit recheck."
                ),
            ),
        )
        if error_metadata(exc).get("provider_reason") == "API_KEY_INVALID":
            category, message = (
                "credential_error",
                "The provider rejected the runtime credential. Check local key/account access; no generation was sent.",
            )
        return _observed(
            report,
            started,
            status=category,
            message=message,
            provider_http_status=status
            if isinstance(status, int) and 100 <= status <= 599
            else None,
            error_origin="upstream_http",
        )
    except (TimeoutError, httpx.TimeoutException) as exc:
        return _observed(
            report,
            started,
            status="timeout",
            message="The metadata check timed out. No generation was sent. Recheck explicitly later; this does not establish generation availability.",
            error_origin="transport_timeout"
            if isinstance(exc, httpx.TimeoutException)
            else "local_envelope_timeout",
        )
    except (httpx.HTTPError, OSError):
        return _observed(
            report,
            started,
            status="provider_unavailable",
            message="The provider could not be reached for metadata. Check connectivity before an explicit read-only recheck; no generation was sent.",
            error_origin="transport_unavailable",
        )
    except (ProviderFailure, ValueError, TypeError):
        return _observed(
            report,
            started,
            status="unknown",
            message="The SDK could not safely decode usable model metadata. Review the pinned SDK/model configuration; generation remains unverified.",
            error_origin="metadata_response",
        )

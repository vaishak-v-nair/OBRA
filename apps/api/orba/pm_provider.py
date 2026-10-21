"""One real official Gemini SDK adapter. No runtime fake or automatic continuation."""

import asyncio
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import httpx
from google import genai
from google.genai import errors, types

from orba.config import Settings
from orba.pm_models_policy import validate_model_configuration
from orba.pm_schemas import ProductDocument, canonical

PROMPT_VERSION = "pm-v2"
PROMPT = (Path(__file__).parent / "prompts" / "product_manager_v2.txt").read_text(encoding="utf-8")
PROMPT_HASH = hashlib.sha256(PROMPT.encode()).hexdigest()
PROVIDER = "google-gemini"
MAX_ENVELOPE_BYTES = 1024 * 1024
TRANSPORT_GRACE_SECONDS = 5
ENVELOPE_GRACE_SECONDS = 10
TIMEOUT_MESSAGE = (
    "Plan generation could not finish because the AI provider timed out. "
    "No new plan was saved. Your project and existing plans are safe. "
    "Usage may have been incurred; check status before explicitly retrying."
)


def gemini_output_schema():
    """Provider grammar hint only; ProductDocument remains the full server contract.

    Gemini supports a JSON Schema subset. Nested large maxItems bounds can also
    exceed its grammar state budget. Omit those generation hints, never the
    independent Pydantic validation, graph checks or persistence limits.
    """

    def project(node):
        if isinstance(node, list):
            return [project(item) for item in node]
        if not isinstance(node, dict):
            return node
        result = {}
        for key, value in node.items():
            if key in {"properties", "$defs"}:
                result[key] = {name: project(item) for name, item in value.items()}
            elif key not in {
                "default",
                "title",
                "maxItems",
                "minLength",
                "maxLength",
                "pattern",
                "const",
            }:
                result[key] = project(value)
        if "const" in node:
            result["enum"] = [node["const"]]
        return result

    schema = project(ProductDocument.model_json_schema())
    # These optional fields describe human decisions, not model output. Their
    # normal Pydantic defaults and validate_generated checks remain authoritative.
    for definition, fields in {
        "Source": ("actor_id", "inherited_kind"),
        "Confirmation": ("active", "disposition", "reason", "actor_id", "decided_at"),
    }.items():
        for field in fields:
            schema["$defs"][definition]["properties"].pop(field)
    kinds = schema["$defs"]["Source"]["properties"]["kind"]["enum"]
    kinds.remove("human")
    return schema


def request_metrics(snapshot: dict) -> dict:
    """Local content bytes, NOT SDK wire bytes, provider tokens or a price quote."""
    schema = canonical(gemini_output_schema()).encode("utf-8")
    snapshot_bytes = len(canonical(snapshot).encode("utf-8"))
    prompt_bytes = len(PROMPT.encode("utf-8"))
    return {
        "prompt_bytes": prompt_bytes,
        "provider_schema_bytes": len(schema),
        "snapshot_bytes": snapshot_bytes,
        "input_bytes": prompt_bytes + len(schema) + snapshot_bytes,
        "provider_schema_sha256": hashlib.sha256(schema).hexdigest(),
    }


INPUT_LIMIT_MESSAGE = (
    "The planning input exceeds the configured size limit. No generation was started. "
    "Shorten the brief or instructions, or exclude the saved plan as context."
)
INVALID_UNICODE_MESSAGE = (
    "Planning input must contain valid Unicode text. No generation was started."
)


def safe_identifier(value):
    return (
        value
        if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9._:/+=-]{1,200}", value)
        else None
    )


def error_metadata(exc):
    diagnostic = {
        "exception_type": type(exc).__name__,
        "provider_http_status": exc.code,
        "dispatch_phase": "provider_response",
        "error_origin": "upstream_http",
    }
    status = getattr(exc, "status", None)
    if isinstance(status, str) and re.fullmatch(r"[A-Z_]{1,80}", status):
        diagnostic["provider_status"] = status
    # Classify known compatibility failures without retaining arbitrary provider
    # messages/bodies, which could contain credentials or private input.
    message = getattr(exc, "message", "") or ""
    if isinstance(message, str):
        lowered = message.lower()
        if "too many states" in lowered:
            diagnostic["request_rejection"] = "schema_state_limit"
        elif "schema" in lowered and ("nest" in lowered or "depth" in lowered):
            diagnostic["request_rejection"] = "schema_nesting_limit"
        elif "unknown name" in lowered:
            diagnostic["request_rejection"] = "unsupported_request_field"
    body = getattr(exc, "details", None)
    error = body.get("error", body) if isinstance(body, dict) else {}
    details = error.get("details", []) if isinstance(error, dict) else []
    for item in details[:5] if isinstance(details, list) else []:
        reason = item.get("reason") if isinstance(item, dict) else None
        if isinstance(reason, str) and re.fullmatch(r"[A-Z_]{1,80}", reason):
            diagnostic["provider_reason"] = reason
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", {}) or {}
    request_id = safe_identifier(headers.get("x-request-id") or headers.get("x-goog-request-id"))
    if request_id:
        diagnostic["provider_request_id"] = request_id
    retry = headers.get("retry-after", "")
    if isinstance(retry, str) and retry.isdigit() and len(retry) <= 8:
        diagnostic["retry_after_seconds"] = min(int(retry), 3600)
    return diagnostic


@dataclass(frozen=True)
class ProviderResult:
    output: str
    model: str | None = None
    response_id: str | None = None
    request_id: str | None = None
    usage: dict | None = None


class ProviderFailure(Exception):
    def __init__(
        self, category: str, message: str, status: int = 502, *, diagnostic=None, result=None
    ):
        super().__init__(message)
        self.category, self.message, self.status = category, message, status
        self.diagnostic = diagnostic or {}
        self.result: ProviderResult | None = result


class ProductManagerModelProvider(Protocol):
    async def generate(self, snapshot: dict) -> ProviderResult: ...


class LimitedStream(httpx.AsyncByteStream):
    """Count bytes BEFORE HTTPX/SDK buffering; request uncompressed official JSON."""

    def __init__(self, stream):
        self.stream = stream

    async def __aiter__(self):
        size = 0
        async for chunk in self.stream:
            size += len(chunk)
            if size > MAX_ENVELOPE_BYTES:
                raise ProviderFailure(
                    "invalid_model_response", "The provider response exceeded its size limit."
                )
            yield chunk

    async def aclose(self):
        await self.stream.aclose()


class LimitedTransport(httpx.AsyncBaseTransport):
    def __init__(self):
        self.transport = httpx.AsyncHTTPTransport(retries=0)

    async def handle_async_request(self, request):
        request.headers["Accept-Encoding"] = "identity"
        response = await self.transport.handle_async_request(request)
        # Avoid a decompression bomb before the envelope bound. The official endpoint
        # accepts identity; unexpected compression is an honest provider failure.
        if response.headers.get("content-encoding", "identity").lower() not in {"identity", ""}:
            await response.aclose()
            raise ProviderFailure(
                "invalid_model_response", "The provider returned an unsupported response encoding."
            )
        return httpx.Response(
            response.status_code,
            headers=response.headers,
            stream=LimitedStream(response.stream),
            extensions=response.extensions,
        )

    async def aclose(self):
        await self.transport.aclose()


class GeminiProductManagerProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def generate(self, snapshot: dict) -> ProviderResult:
        config = self.settings
        if not config.pm_configured:
            raise ProviderFailure(
                "pm_not_configured",
                "Set GEMINI_API_KEY and ORBA_PM_MODEL in the root .env, then restart the API.",
                503,
            )
        try:
            validate_model_configuration(config.pm_model, config.pm_thinking_level)
        except ValueError:
            raise ProviderFailure(
                "pm_invalid_configuration",
                "The configured model or thinking level is unsupported. Check server configuration before retrying.",
                503,
                diagnostic={"dispatch_phase": "before_provider_call"},
            ) from None
        try:
            metrics = request_metrics(snapshot)
        except UnicodeEncodeError:
            raise ProviderFailure("validation_error", INVALID_UNICODE_MESSAGE, 422) from None
        if metrics["input_bytes"] > config.pm_max_input_bytes:
            raise ProviderFailure("input_too_large", INPUT_LIMIT_MESSAGE, 422)
        try:
            async with asyncio.timeout(config.pm_timeout_seconds + ENVELOPE_GRACE_SECONDS):
                async with httpx.AsyncClient(
                    transport=LimitedTransport(),
                    trust_env=False,
                    follow_redirects=False,
                    timeout=config.pm_timeout_seconds + TRANSPORT_GRACE_SECONDS,
                ) as http:
                    client = genai.Client(
                        api_key=config.pm_api_key.get_secret_value(),
                        vertexai=False,
                        http_options=types.HttpOptions(
                            base_url="https://generativelanguage.googleapis.com/",
                            api_version="v1beta",
                            # The SDK otherwise derives the server header from its
                            # transport timeout. Keep these distinct and explicit.
                            headers={"X-Server-Timeout": str(config.pm_timeout_seconds)},
                            timeout=(config.pm_timeout_seconds + TRANSPORT_GRACE_SECONDS) * 1000,
                            retry_options=types.HttpRetryOptions(attempts=1),
                            httpx_async_client=http,
                            client_args={"trust_env": False},
                        ),
                    )
                    try:
                        response = await client.aio.models.generate_content(
                            model=config.pm_model,
                            contents=canonical(snapshot),
                            config=types.GenerateContentConfig(
                                system_instruction=PROMPT,
                                response_mime_type="application/json",
                                response_json_schema=gemini_output_schema(),
                                max_output_tokens=config.pm_max_output_tokens,
                                candidate_count=1,
                                tools=[],
                                automatic_continuation=False,
                                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                                    disable=True
                                ),
                                thinking_config=types.ThinkingConfig(
                                    thinking_level=types.ThinkingLevel(
                                        config.pm_thinking_level.upper()
                                    )
                                ),
                            ),
                        )
                    finally:
                        await client.aio.aclose()
                        client.close()
        except ProviderFailure:
            raise
        except (TimeoutError, httpx.TimeoutException) as exc:
            raise ProviderFailure(
                "provider_timeout",
                TIMEOUT_MESSAGE,
                504,
                diagnostic={
                    "exception_type": type(exc).__name__,
                    "dispatch_phase": "provider_call",
                    "error_origin": "transport_timeout"
                    if isinstance(exc, httpx.TimeoutException)
                    else "local_envelope_timeout",
                },
            ) from None
        except errors.APIError as exc:
            code = exc.code
            diagnostic = error_metadata(exc)
            category = {
                429: "provider_rate_limited",
                401: "provider_access_denied",
                403: "provider_access_denied",
                404: "provider_model_unavailable",
                504: "provider_timeout",
                500: "provider_unavailable",
                502: "provider_unavailable",
                503: "provider_unavailable",
            }.get(code, "provider_request_failed")
            if diagnostic.get("provider_reason") == "API_KEY_INVALID":
                category = "provider_access_denied"
            message = {
                429: "The model provider rate limit was reached. Wait before explicitly starting another request.",
                401: "The provider rejected the runtime credential. Check local configuration.",
                403: "The provider denied the request. Check runtime credential and model access.",
                404: "The configured model is unavailable. Check ORBA_PM_MODEL and account access.",
                504: TIMEOUT_MESSAGE,
                500: "The AI provider is temporarily unavailable. No new plan was saved.",
                502: "The AI provider is temporarily unavailable. No new plan was saved.",
                503: "The AI provider is temporarily unavailable. No new plan was saved.",
            }.get(
                code,
                "The provider rejected the request. Check configuration and the run reference.",
            )
            if category == "provider_access_denied":
                message = "The provider rejected the runtime credential or model access. Check local configuration."
            raise ProviderFailure(
                category,
                message,
                code if code in {429, 504} else 502,
                diagnostic=diagnostic,
            ) from None
        except (httpx.HTTPError, OSError) as exc:
            raise ProviderFailure(
                "provider_unavailable",
                "The model provider could not be reached. No plan was created.",
                502,
                diagnostic={
                    "exception_type": type(exc).__name__,
                    "dispatch_phase": "provider_call",
                    "error_origin": "transport_unavailable",
                },
            ) from None
        except (ValueError, TypeError) as exc:
            raise ProviderFailure(
                "provider_response_or_configuration_error",
                "The SDK could not validate configuration or decode a valid provider response. Dispatch outcome is uncertain; check the run reference before trying again.",
                502,
                diagnostic={"exception_type": type(exc).__name__, "dispatch_phase": "unknown"},
            ) from None

        headers = response.sdk_http_response.headers if response.sdk_http_response else {}
        metadata = ProviderResult(
            output="",
            model=safe_identifier(response.model_version),
            response_id=safe_identifier(response.response_id),
            request_id=safe_identifier(
                (headers or {}).get("x-request-id") or (headers or {}).get("x-goog-request-id")
            ),
            usage=response.usage_metadata.model_dump(mode="json", exclude_none=True)
            if response.usage_metadata
            else None,
        )
        candidates = response.candidates or []
        if len(candidates) != 1 or str(candidates[0].finish_reason) not in {
            "STOP",
            "FinishReason.STOP",
        }:
            raise ProviderFailure(
                "invalid_model_response",
                "The model did not return a complete plan. No draft was saved.",
                result=metadata,
                diagnostic={
                    "finish_reason": str(candidates[0].finish_reason)
                    if candidates
                    else "no_candidate"
                },
            )
        parts = candidates[0].content.parts if candidates[0].content else []
        output = []
        for part in parts or []:
            if part.thought:
                continue  # Never expose/persist private reasoning text.
            if part.text is None or part.function_call or part.executable_code:
                raise ProviderFailure(
                    "invalid_model_response",
                    "The model returned unsupported content instead of a product document.",
                    result=metadata,
                )
            output.append(part.text)
        if not output:
            raise ProviderFailure(
                "invalid_model_response", "The model returned no product document.", result=metadata
            )
        return ProviderResult(
            "".join(output),
            metadata.model,
            metadata.response_id,
            metadata.request_id,
            metadata.usage,
        )

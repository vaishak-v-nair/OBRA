"""Isolated transport/body contract tests, not provider integration evidence."""

import asyncio
from types import SimpleNamespace

import pytest

from orba.pm_middleware import PMBodyLimitMiddleware
from orba.pm_provider import MAX_ENVELOPE_BYTES, LimitedStream, ProviderFailure, error_metadata


@pytest.mark.parametrize("method,cap", [("POST", 256 * 1024), ("PUT", 512 * 1024)])
def test_chunked_body_limit_applies_without_content_length(method, cap):
    sent = []
    called = False
    received = 0

    async def app(*_):
        nonlocal called
        called = True

    async def receive():
        nonlocal received
        received += 17000
        return {"type": "http.request", "body": b"x" * 17000, "more_body": True}

    async def send(message):
        sent.append(message)

    asyncio.run(
        PMBodyLimitMiddleware(app)(
            {
                "type": "http",
                "method": method,
                "path": "/api/v1/projects/id/pm-plans/id",
                "headers": [],
            },
            receive,
            send,
        )
    )
    assert not called and sent[0]["status"] == 413
    assert cap < received <= cap + 17000


def test_raw_provider_envelope_capped_before_buffering():
    class UnitStream:
        async def __aiter__(self):
            yield b"x" * (MAX_ENVELOPE_BYTES // 2)
            yield b"x" * (MAX_ENVELOPE_BYTES // 2 + 1)

    async def consume():
        async for _ in LimitedStream(UnitStream()):
            pass

    with pytest.raises(ProviderFailure, match="size limit"):
        asyncio.run(consume())


def test_failure_metadata_allowlist_excludes_body_and_secret_headers():
    exc = SimpleNamespace(
        code=403,
        status="PERMISSION_DENIED",
        details={
            "error": {
                "status": "PERMISSION_DENIED",
                "message": "secret body",
                "details": [
                    {"reason": "API_KEY_INVALID", "metadata": {"secret": "never log this"}}
                ],
            }
        },
        response=SimpleNamespace(
            headers={
                "x-request-id": "real-header-id",
                "retry-after": "9999999",
                "authorization": "secret header",
            }
        ),
    )
    result = error_metadata(exc)
    assert (
        result["provider_status"] == "PERMISSION_DENIED"
        and result["provider_request_id"] == "real-header-id"
    )
    assert result["retry_after_seconds"] == 3600 and "secret" not in str(result)
    assert result["provider_reason"] == "API_KEY_INVALID"

"""Bound PM request bodies before JSON parsing, including chunked requests."""

import asyncio
from time import monotonic

from starlette.responses import JSONResponse


class PMBodyLimitMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        path = scope.get("path", "")
        if (
            scope["type"] != "http"
            or scope.get("method") not in {"POST", "PUT"}
            or not (
                path.startswith("/api/v1/projects/") and ("/pm-runs" in path or "/pm-plans" in path)
            )
        ):
            return await self.app(scope, receive, send)
        start = monotonic()
        scope.setdefault("state", {})["pm_started_at"] = start
        limit = 512 * 1024 if scope["method"] == "PUT" else 256 * 1024
        body = bytearray()
        try:
            async with asyncio.timeout(5):
                while True:
                    message = await receive()
                    if message["type"] == "http.disconnect":
                        return
                    body.extend(message.get("body", b""))
                    if len(body) > limit:
                        return await self.reject(
                            scope,
                            receive,
                            send,
                            413,
                            "request_too_large",
                            "The planning request exceeds its size limit.",
                        )
                    if not message.get("more_body", False):
                        break
        except TimeoutError:
            return await self.reject(
                scope,
                receive,
                send,
                408,
                "request_body_timeout",
                "The planning request body did not arrive within five seconds.",
            )
        consumed = False

        async def replay():
            nonlocal consumed
            if consumed:
                return await receive()
            consumed = True
            return {"type": "http.request", "body": bytes(body), "more_body": False}

        return await self.app(scope, replay, send)

    @staticmethod
    async def reject(scope, receive, send, status, code, message):
        response = JSONResponse(
            status_code=status,
            content={"error": {"code": code, "message": message}},
            headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
        )
        await response(scope, receive, send)

"""TEST ONLY: real auth/API/PostgreSQL, ONLY Architect model dependency doubled."""

import asyncio
import os

from orba.architect import model_provider
from orba.config import Settings
from orba.main import create_app
from orba.pm_provider import ProviderFailure, ProviderResult
from scripts.architect_sample import controlled_document
from scripts.test_database import guard_test_url


class ControlledArchitectProvider:
    async def generate(self, snapshot):
        await asyncio.sleep(1)
        scenario = snapshot["constraints"]
        if "DOUBLE: invalid" in scenario:
            return ProviderResult('{"malformed":true}', model="controlled-double-not-live")
        if "DOUBLE: cycle" in scenario:
            value = controlled_document().model_dump()
            value["tasks"][0]["dependencies"] = ["screen"]
            import json

            return ProviderResult(json.dumps(value), model="controlled-double-not-live")
        for keyword, category, code, message in (
            (
                "unavailable",
                "provider_unavailable",
                503,
                "The AI provider is temporarily unavailable. No new architecture was saved.",
            ),
            (
                "timeout",
                "provider_timeout",
                504,
                "Architecture generation could not finish because the AI provider timed out. No new architecture was saved. Your project and existing plans are safe.",
            ),
            (
                "rate limited",
                "provider_rate_limited",
                429,
                "The AI provider rate limit was reached. No new architecture was saved.",
            ),
        ):
            if f"DOUBLE: {keyword}" in scenario:
                raise ProviderFailure(
                    category,
                    message,
                    code if code in {429, 504} else 502,
                    diagnostic={
                        "provider_double": True,
                        "provider_http_status": code,
                        "error_origin": "controlled_double",
                    },
                )
        return ProviderResult(
            controlled_document().model_dump_json(), model="controlled-double-not-live"
        )


def create_controlled_app():
    target = os.environ.get("DATABASE_URL", "")
    guard_test_url(target)
    app = create_app(
        Settings(
            _env_file=None,
            database_url=target,
            web_origin="http://localhost:3001",
            pm_api_key=None,
            pm_model=None,
            architect_api_key="controlled-not-runtime",
            architect_model="gemini-3.6-flash",
            architect_thinking_level="minimal",
            pm_account_attempts=20,
            pm_global_attempts=100,
            pm_max_concurrent=1,
        )
    )
    app.dependency_overrides[model_provider] = ControlledArchitectProvider
    return app

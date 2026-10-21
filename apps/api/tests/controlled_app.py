"""TEST-ONLY FastAPI factory. Real auth/routes/PG; labeled provider DOUBLE.

No production flag selects this provider. It never contacts an external model.
"""

import asyncio
import os

from orba.config import Settings
from orba.main import create_app
from orba.pm import model_provider
from orba.pm_provider import TIMEOUT_MESSAGE, ProviderFailure, ProviderResult
from scripts.test_database import guard_test_url


class ControlledTimeoutProvider:
    async def generate(self, snapshot):
        await asyncio.sleep(
            4 if snapshot["instructions"] == "Controlled provider DOUBLE: hold admission" else 1.5
        )  # Bounded windows for real admission/transport races, never a paid call.
        if snapshot["instructions"] == "Controlled provider DOUBLE: valid response":
            from tests.pm_support import unit_output

            return ProviderResult(
                unit_output().model_dump_json(), model="controlled-double-not-live"
            )
        if snapshot["instructions"] == "Controlled provider DOUBLE: invalid response":
            return ProviderResult(
                '{"not_a_product_document":true}', model="controlled-double-not-live"
            )
        if snapshot["instructions"] in {
            "Controlled provider DOUBLE: unavailable",
            "Controlled provider DOUBLE: rate limited",
        }:
            unavailable = snapshot["instructions"] == "Controlled provider DOUBLE: unavailable"
            raise ProviderFailure(
                "provider_unavailable" if unavailable else "provider_rate_limited",
                "The AI provider is temporarily unavailable. No new plan was saved."
                if unavailable
                else "The model provider rate limit was reached. Wait before explicitly starting another request.",
                502 if unavailable else 429,
                diagnostic={
                    "provider_double": True,
                    "exception_type": "ControlledProviderFailure",
                    "provider_http_status": 503 if unavailable else 429,
                    "error_origin": "controlled_double",
                    "dispatch_phase": "provider_response",
                },
            )
        raise ProviderFailure(
            "provider_timeout",
            TIMEOUT_MESSAGE,
            504,
            diagnostic={
                "provider_double": True,
                "exception_type": "ControlledProviderTimeout",
                "error_origin": "controlled_double",
                "dispatch_phase": "provider_call",
            },
        )


def create_controlled_app():
    target = os.environ.get("DATABASE_URL", "")
    guard_test_url(target)
    config = Settings(
        _env_file=None,
        database_url=target,
        web_origin="http://localhost:3001",
        pm_api_key="controlled-double-never-a-runtime-credential",
        # Valid configuration; ONLY the explicit dependency override below is fake.
        pm_model="gemini-3.8-flash",
        pm_timeout_seconds=5,
        pm_account_attempts=10,
        pm_global_attempts=60,
    )
    app = create_app(config)
    app.dependency_overrides[model_provider] = lambda: ControlledTimeoutProvider()
    return app

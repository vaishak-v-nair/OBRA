"""UNPAID browser setup only: real application, auth and PostgreSQL; no AI dispatch.

This factory is not imported by production. A non-credential sentinel lets tests
inspect the enabled generation control; it is NOT provider readiness evidence.
Both generation endpoints are denied before FastAPI dependencies, with a second
tripwire preventing construction of either provider if routing changes.
"""

import os
import re

from fastapi import Request
from fastapi.responses import JSONResponse

from orba.architect import model_provider as architect_provider
from orba.config import Settings
from orba.main import create_app
from orba.pm import model_provider as pm_provider
from scripts.test_database import guard_test_url

GENERATION_PATH = re.compile(r"/api/v1/projects/[^/]+/(?:pm-runs|architect-runs)/?")


def create_no_generation_app():
    target = os.environ.get("DATABASE_URL", "")
    guard_test_url(target)
    if os.environ.get("ORBA_ARCHITECT_LIVE_OPT_IN") == "1":
        raise RuntimeError("Unpaid test factory refuses live generation opt-in.")
    app = create_app(
        Settings(
            _env_file=None,
            database_url=target,
            web_origin="http://localhost:3001",
            cookie_secure=False,  # Isolated loopback HTTP; production cookie policy is unchanged.
            pm_api_key=None,
            pm_model=None,
            architect_api_key="test-only-no-generation-not-a-credential",
            architect_model="gemini-3.6-flash",
            architect_thinking_level="minimal",
        )
    )
    counts = {"blocked_generation_posts": 0, "provider_dependency_entries": 0}
    app.state.no_generation_counts = counts

    def provider_tripwire():
        counts["provider_dependency_entries"] += 1
        raise RuntimeError("UNPAID PREFLIGHT: provider construction forbidden.")

    app.dependency_overrides[pm_provider] = provider_tripwire
    app.dependency_overrides[architect_provider] = provider_tripwire

    @app.middleware("http")
    async def generation_denied(request: Request, call_next):
        if request.method == "POST" and GENERATION_PATH.fullmatch(request.url.path):
            counts["blocked_generation_posts"] += 1
            return JSONResponse(
                status_code=409,
                content={
                    "error": {
                        "code": "unpaid_generation_boundary",
                        "message": "Unpaid preflight cannot dispatch model generation.",
                    }
                },
            )
        return await call_next(request)

    @app.get("/__test/no-generation")
    def boundary_counts():
        return {
            "execution_class": "no_generation_test_boundary",
            "provider_readiness_verified": False,
            **counts,
        }

    return app

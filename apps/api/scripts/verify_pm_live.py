"""Bounded, actual Gemini -> API -> PostgreSQL verification. No mocks/skips.

Exit nonzero = BLOCKED configuration or actual failure; 0 = real verified flow.
Only the guarded isolated test DB may be reset. Never prints credentials/PRD text.
"""

import json
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from orba.config import Settings
from orba.main import create_app
from orba.pm_models import ProductManagerRun, ProductPlan
from orba.pm_repository import read_document
from scripts.prepare_tests import TEST_URL, prepare
from scripts.test_database import guard_test_url

BRIEF = "Build a simple personal habit tracker with daily check-ins, a streak counter, and a weekly summary. The first version is for one user and does not require social features."
ROOT = Path(__file__).resolve().parents[3]


def csrf(client):
    value = client.get("/api/v1/auth/csrf")
    value.raise_for_status()
    client.headers.update(
        {"Origin": "http://localhost:3000", "X-CSRF-Token": value.json()["csrf_token"]}
    )


def main():
    from scripts.verification import EvidenceError, require_live_opt_in

    try:
        require_live_opt_in()
    except (EvidenceError, OSError, ValueError, KeyError):
        print(
            "BLOCKED: explicit live opt-in and current passing Gate A are required. No call dispatched."
        )
        return 2
    config = Settings(database_url=TEST_URL, web_origin="http://localhost:3000")
    evidence = {
        "test": "live_api",
        "provider": "google-gemini",
        "requested_model": config.pm_model,
        "mocks": False,
    }
    if not config.pm_configured:
        evidence |= {
            "verdict": "BLOCKED",
            "missing": [
                name
                for name, present in [
                    (
                        "GEMINI_API_KEY or ORBA_PM_API_KEY",
                        bool(config.pm_api_key and config.pm_api_key.get_secret_value()),
                    ),
                    ("ORBA_PM_MODEL", bool(config.pm_model)),
                ]
                if not present
            ],
        }
        write_evidence(evidence)
        return 1
    guard_test_url(TEST_URL)
    prepare()
    with TestClient(create_app(config)) as client:
        csrf(client)
        registered = client.post(
            "/api/v1/auth/register",
            json={
                "email": f"live-{uuid4().hex}@example.com",
                "password": "A long live verification password!",
                "display_name": "Live verification",
            },
        )
        registered.raise_for_status()
        csrf(client)
        workspace = client.post(
            "/api/v1/workspaces", json={"name": "Isolated live PM verification"}
        )
        workspace.raise_for_status()
        project = client.post(
            "/api/v1/projects",
            json={
                "title": "Live habit tracker plan",
                "description": BRIEF,
                "workspace_id": workspace.json()["id"],
            },
        )
        project.raise_for_status()
        project_id = project.json()["id"]
        response = client.post(
            f"/api/v1/projects/{project_id}/pm-runs",
            json={
                "client_request_id": str(uuid4()),
                "brief": BRIEF,
                "instructions": "Keep this first version small: 1 epic, at most 3 stories and 6 acceptance criteria in total. Use concise text. Flag unknown targets rather than inventing facts.",
            },
        )
        evidence["http_status"] = response.status_code
        if response.status_code != 201:
            error = response.json().get("error", {})
            evidence |= {"verdict": "FAIL", "error": error}
            write_evidence(evidence)
            return 1
        run = response.json()
        saved = client.get(f"/api/v1/projects/{project_id}/pm-plans/{run['plan_id']}")
        saved.raise_for_status()
        plan = saved.json()
        assert (
            run["status"] == "succeeded"
            and plan["state"] == "draft"
            and plan["approved_by"] is None
        )
        from uuid import UUID

        with Session(client.app.state.engine) as db:
            record = db.get(ProductPlan, UUID(plan["id"]))
            document = read_document(db, record)
            actual_run = db.scalar(
                select(ProductManagerRun).where(ProductManagerRun.id == UUID(run["id"]))
            )
            assert document.epics and all(e.stories for e in document.epics)
            assert all(s.acceptance_criteria for e in document.epics for s in e.stories)
            assert actual_run.status == "succeeded" and record.generating_run_id == actual_run.id
        evidence |= {
            "verdict": "PASS",
            "run_id": run["id"],
            "project_id": project_id,
            "plan_id": plan["id"],
            "model": run["returned_model"],
            "provider_response_id": run["provider_response_id"],
            "provider_request_id": run["provider_request_id"],
            "usage": run["usage"],
            "prompt_version": run["prompt_version"],
            "state": plan["state"],
            "content_hash": plan["content_hash"],
            "epics": len(document.epics),
            "stories": sum(len(e.stories) for e in document.epics),
            "criteria": sum(len(s.acceptance_criteria) for e in document.epics for s in e.stories),
            "persistence": "retrieved via authenticated API and fresh SQLAlchemy session",
        }
        write_evidence(evidence)
    return 0


def write_evidence(value):
    from scripts.test_evidence import evidence_path

    path = evidence_path("live-api-diagnostic.json")
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(value, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())

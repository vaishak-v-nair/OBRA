"""Real PostgreSQL boundary/audit tests; verifier subprocess doubles are unit-only."""

import json
import sys
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from orba.db import make_engine
from orba.models import Project, User
from orba.pm_models import ProductPlan
from orba.pm_repository import create_plan
from scripts import architect_preflight as preflight
from scripts import architect_verification as stage
from scripts import verification as base
from scripts.inspect_architect_preflight import inspect
from scripts.pm_sample import human_document
from tests.conftest import TEST_DATABASE_URL
from tests.no_generation_app import create_no_generation_app


@pytest.mark.parametrize("endpoint", ["pm-runs", "architect-runs", "pm-runs/", "architect-runs/"])
def test_unpaid_server_denies_generation_before_provider_or_auth_dependencies(
    migrated_database, monkeypatch, endpoint
):
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
    monkeypatch.delenv("ORBA_ARCHITECT_LIVE_OPT_IN", raising=False)
    app = create_no_generation_app()
    with TestClient(app) as client:
        response = client.post(f"/api/v1/projects/{uuid4()}/{endpoint}", json={})
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "unpaid_generation_boundary"
        assert app.state.no_generation_counts == {
            "blocked_generation_posts": 1,
            "provider_dependency_entries": 0,
        }
        assert client.get("/__test/no-generation").json()["provider_readiness_verified"] is False
        # No runtime dotenv/key or success response is substituted in this test-only factory.
        assert app.state.settings.pm_api_key is None
        assert app.state.settings.architect_api_key.get_secret_value().startswith("test-only-")


def test_unpaid_factory_refuses_development_database(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://orba:local@127.0.0.1:54329/orba")
    with pytest.raises(RuntimeError, match="Refusing test mutation"):
        create_no_generation_app()


def test_unpaid_factory_refuses_live_opt_in(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
    monkeypatch.setenv("ORBA_ARCHITECT_LIVE_OPT_IN", "1")
    with pytest.raises(RuntimeError, match="refuses live generation"):
        create_no_generation_app()


def authored(client):
    response = client.post(
        "/api/v1/projects",
        json={
            "title": "Preflight source",
            "description": "Read-only source audit",
            "workspace_id": client.workspace_id,
        },
    )
    assert response.status_code == 201
    project_id = UUID(response.json()["id"])
    actor_id = UUID(client.get("/api/v1/auth/me").json()["id"])
    engine = make_engine(TEST_DATABASE_URL)
    try:
        with Session(engine) as db, db.begin():
            plan = create_plan(db, project_id, actor_id, human_document(actor_id))
            plan_id = plan.id
    finally:
        engine.dispose()
    return project_id, plan_id, actor_id


def test_fresh_read_only_sql_reconstructs_actual_draft_then_exact_api_approval(client):
    project_id, plan_id, actor_id = authored(client)
    draft = inspect(project_id, plan_id, actor_id)
    assert draft["state"] == "draft" and draft["approved_at"] is None
    assert draft["counts"] == {
        "product_epics": 1,
        "product_stories": 1,
        "product_acceptance_criteria": 1,
    }
    assert all(count == 0 for count in draft["generation_records"].values())
    response = client.post(
        f"/api/v1/projects/{project_id}/pm-plans/{plan_id}/approve",
        json={"expected_revision": draft["revision"], "version": draft["version"]},
    )
    assert response.status_code == 200
    approved = inspect(
        project_id, plan_id, actor_id
    )  # Independent engine/session after API commit.
    assert approved["state"] == "approved" and approved["approved_at"]
    assert approved["approved_by"] == str(actor_id)
    # Existing approval binds the exact saved revision; it does not perform an edit.
    assert approved["version"] == 1 and approved["revision"] == draft["revision"] == 1
    assert approved["current_approved_plan_id"] == str(plan_id)
    assert approved["content_hash"] == response.json()["content_hash"]


def test_sql_audit_rejects_wrong_project_and_unrelated_actor(client):
    project_id, plan_id, actor_id = authored(client)
    with pytest.raises(ValueError, match="do not match"):
        inspect(uuid4(), plan_id, actor_id)
    with pytest.raises(ValueError, match="not a member"):
        inspect(project_id, plan_id, uuid4())


def test_sql_audit_does_not_change_persisted_source_or_project(client):
    project_id, plan_id, actor_id = authored(client)
    first = inspect(project_id, plan_id, actor_id)
    second = inspect(project_id, plan_id, actor_id)
    assert first == second
    engine = make_engine(TEST_DATABASE_URL)
    try:
        with Session(engine) as db:
            assert db.get(ProductPlan, plan_id).revision == 1
            assert db.get(Project, project_id).workspace_id == UUID(client.workspace_id)
            assert db.scalar(select(User.id).where(User.id == actor_id)) == actor_id
    finally:
        engine.dispose()


def test_unpaid_runner_preserves_child_failure_and_never_runs_next_command(tmp_path, monkeypatch):
    # Unit-only child double; never model/browser evidence. Exit status must propagate.
    monkeypatch.setattr(preflight.stage, "EVIDENCE", tmp_path)
    monkeypatch.setattr(base, "ports_available", lambda: None)
    calls = []

    def failed(name, argv, cwd, env, logfile, timeout):
        calls.append(name)
        assert env["ORBA_ARCHITECT_API_KEY"] == env["GEMINI_API_KEY"] == ""
        assert "ORBA_ARCHITECT_LIVE_OPT_IN" not in env
        logfile.write_text("unit-only prerequisite failure\n", encoding="utf-8")
        return {"name": name, "argv": argv, "exit_code": 37}

    monkeypatch.setattr(base, "run_command", failed)
    assert preflight.execute() == 37
    receipt = json.loads(next(tmp_path.glob("*/receipt.json")).read_text(encoding="utf-8"))
    assert calls == ["database"]
    assert receipt["result"] == "FAIL" and receipt["paid_authorized"] is False
    assert receipt["exit_code"] == 37


def test_unpaid_runner_failure_is_a_real_nonzero_subprocess_exit(tmp_path):
    # Actual assertion failure, isolated verifier-unit child; no external service double.
    row = base.run_command(
        "unit-only-required-failure",
        [sys.executable, "-c", "assert False, 'unpaid prerequisite did not pass'"],
        base.ROOT,
        base.deterministic_env(),
        tmp_path / "failed.log",
        10,
    )
    assert row["exit_code"] == 1
    assert "unpaid prerequisite did not pass" in (tmp_path / "failed.log").read_text()


@pytest.mark.parametrize(
    "missing", ["result", "generation_budget", "server_boundary", "final_sql", "milestones"]
)
def test_preflight_cannot_pass_from_incomplete_or_controlled_success_labels(missing):
    proof = parser_proof()
    preflight.validate_preflight(proof)
    proof.pop(missing, None)
    with pytest.raises(base.EvidenceError):
        preflight.validate_preflight(proof)


def parser_proof():
    """Unit-only parser fixture, never generation/browser verification evidence."""
    sql = {
        "project_id": "unit-project",
        "workspace_id": "unit-workspace",
        "plan_id": "unit-plan",
        "version": 1,
        "revision": 1,
        "content_hash": "a" * 64,
        "approved_by": "unit-actor",
        "approved_at": "2026-01-01T00:00:00+00:00",
        "current_approved_plan_id": "unit-plan",
        "state": "approved",
        "document_validated": True,
        "generation_records": {
            "product_manager_runs": 0,
            "architect_runs": 0,
            "architecture_versions": 0,
            "engineering_tasks": 0,
            "task_dependencies": 0,
        },
    }
    return {
        "execution_class": "no_generation_preflight",
        "result": "PASS",
        "approved_source_reloaded": True,
        "provider_readiness_verified": False,
        "project_id": "unit-project",
        "workspace_id": "unit-workspace",
        "actor_id": "unit-actor",
        "source_plan_id": "unit-plan",
        "source_version": 1,
        "source_revision": 1,
        "source_hash": "a" * 64,
        "generation_budget": {"attempted": 0, "forwarded": 0, "blocked": 0},
        "server_boundary": {
            "execution_class": "no_generation_test_boundary",
            "provider_readiness_verified": False,
            "blocked_generation_posts": 0,
            "provider_dependency_entries": 0,
        },
        "final_sql": sql,
        "milestones": [
            {"event": event}
            for event in (
                "project_post_received",
                "exact_project_loaded",
                "authored_draft_persisted",
                "exact_draft_visible",
                "approval_http_response",
                "approval_independently_verified",
                "architect_entry_reached_without_generation",
            )
        ],
    }


@pytest.mark.parametrize(
    "field,sql_field",
    [
        ("project_id", "project_id"),
        ("workspace_id", "workspace_id"),
        ("actor_id", "approved_by"),
        ("source_plan_id", "plan_id"),
        ("source_version", "version"),
        ("source_revision", "revision"),
        ("source_hash", "content_hash"),
    ],
)
def test_unpaid_proof_rejects_identity_absent_on_both_sides_unit_only(field, sql_field):
    proof = parser_proof()
    preflight.validate_preflight(proof)  # Parser acceptance only; no gate/live claim.
    proof.pop(field)
    proof["final_sql"].pop(sql_field)
    with pytest.raises(base.EvidenceError, match="nonempty source identity"):
        preflight.validate_preflight(proof)


@pytest.mark.parametrize("invalid", [0, -1, True, None])
def test_unpaid_proof_rejects_invalid_matching_versions_unit_only(invalid):
    proof = parser_proof()
    proof["source_version"] = proof["final_sql"]["version"] = invalid
    with pytest.raises(base.EvidenceError, match="nonempty source identity"):
        preflight.validate_preflight(proof)


@pytest.mark.parametrize(
    "failure",
    [
        "no_setup",
        "draft",
        "wrong_revision",
        "missing_sql",
        "early_dispatch",
        "unrelated_dispatch",
        "phase_order",
    ],
)
def test_live_verdict_rejects_missing_or_inconsistent_preflight_unit_only(failure):
    # Synthetic parser input only: this does not establish browser or provider success.
    sql = {
        "project_id": "unit-project",
        "workspace_id": "unit-workspace",
        "plan_id": "unit-plan",
        "version": 1,
        "revision": 1,
        "content_hash": "unit-hash",
        "approved_by": "unit-actor",
        "current_approved_plan_id": "unit-plan",
        "state": "approved",
        "document_validated": True,
        "approved_at": "unit-only",
        "generation_records": {
            "product_manager_runs": 0,
            "architect_runs": 0,
            "architecture_versions": 0,
            "engineering_tasks": 0,
            "task_dependencies": 0,
        },
    }
    value = {
        "project_id": "unit-project",
        "source_plan_id": "unit-plan",
        "source_version": 1,
        "source_revision": 1,
        "source_hash": "unit-hash",
        "initiator_id": "unit-actor",
        "preflight": {
            "result": "PASS",
            "approved_source_reloaded": True,
            "step": "architect_entry_reached_without_generation",
            "workspace_id": "unit-workspace",
            "final_sql": sql,
        },
        "preflight_generation_budget": {"attempted": 0, "forwarded": 0, "blocked": 0},
        "unrelated_generation_budget": {"attempted": 0, "forwarded": 0, "blocked": 0},
        "phases": [{"phase": phase} for phase in ("preflight", "generation", "post_generation")],
    }
    stage.require_live_setup(value)  # Parser contract only; never a live receipt.
    if failure == "no_setup":
        value.pop("preflight")
    elif failure == "draft":
        sql["state"] = "draft"
    elif failure == "wrong_revision":
        sql["revision"] = 2
    elif failure == "missing_sql":
        value["preflight"].pop("final_sql")
    elif failure == "early_dispatch":
        value["preflight_generation_budget"]["forwarded"] = 1
    elif failure == "unrelated_dispatch":
        value["unrelated_generation_budget"]["forwarded"] = 1
    else:
        value["phases"].reverse()
    with pytest.raises(base.EvidenceError, match="exact approved-source"):
        stage.require_live_setup(value)

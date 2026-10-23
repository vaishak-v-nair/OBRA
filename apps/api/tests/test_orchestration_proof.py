"""Adversarial inputs exercise the actual verifier. Unit fixtures are not live evidence."""

import json
import subprocess
import sys
from copy import deepcopy
from types import SimpleNamespace
from uuid import UUID

import pytest
from sqlalchemy.orm import Session

from orba.orchestration_models import OrchestrationTask
from scripts import orchestration_verification as gates
from scripts import verification as base
from scripts.inspect_orchestration import inspect
from scripts.orchestration_proof import SQL, Dependency, Event, LocalProof, SQLTask, validate_proof
from tests.orchestration_proof_support import assemble, ident, synthetic_proof
from tests.orchestration_support import initialize


@pytest.mark.parametrize("independent", [False, True])
def test_complete_proof_and_legitimate_zero_edge_graph_are_accepted(independent):
    proof = synthetic_proof(independent_tasks=independent)
    assert validate_proof(proof) is proof
    assert proof["initial_sql"]["counts"]["dependencies"] == (0 if independent else 1)
    assert len(proof["initial_sql"]["tasks"]) == 2


@pytest.mark.parametrize("field", list(LocalProof.model_fields))
@pytest.mark.parametrize("operation", ["missing", "null"])
def test_every_required_proof_field_rejects_omission_and_null(field, operation):
    proof = synthetic_proof()
    if operation == "missing":
        del proof[field]
    else:
        proof[field] = None
    with pytest.raises(base.EvidenceError, match="required field"):
        validate_proof(proof)


@pytest.mark.parametrize(
    "field",
    [
        "run_id",
        "project_id",
        "workspace_id",
        "architecture_id",
        "architecture_version",
        "architecture_revision",
        "architecture_hash",
        "source_plan_id",
        "source_version",
        "source_revision",
        "source_hash",
        "snapshot_hash",
        "graph",
        "tasks",
        "dependencies",
        "events",
    ],
)
@pytest.mark.parametrize("operation", ["missing", "null"])
def test_equally_absent_sql_and_api_fields_cannot_agree(field, operation):
    proof = synthetic_proof()
    for target in (proof["initial_sql"], proof["reloaded_sql"], proof["run_api"]):
        name = "id" if target is proof["run_api"] and field == "run_id" else field
        if operation == "missing":
            target.pop(name, None)
        else:
            target[name] = None
    with pytest.raises(base.EvidenceError, match="required field"):
        validate_proof(proof)


MUTATIONS = {
    "empty-proof": lambda p: p.clear(),
    "empty-api": lambda p: p.update(run_api={}),
    "invalid-uuid": lambda p: p.update(run_id="not-a-uuid"),
    "empty-uuid": lambda p: p.update(run_id=""),
    "integer-uuid": lambda p: p.update(run_id=1),
    "empty-sql-tasks": lambda p: p["initial_sql"].update(tasks=[]),
    "wrong-task-count": lambda p: p["initial_sql"]["counts"].update(tasks=3),
    "boolean-count": lambda p: p["initial_sql"]["counts"].update(tasks=True),
    "string-count": lambda p: p["initial_sql"]["counts"].update(tasks="2"),
    "boolean-version": lambda p: p["run_api"].update(architecture_version=True),
    "string-revision": lambda p: p["run_api"].update(source_revision="1"),
    "zero-revision": lambda p: p["run_api"].update(source_revision=0),
    "short-checksum": lambda p: p["run_api"].update(snapshot_hash="a" * 63),
    "nonhex-checksum": lambda p: p["run_api"].update(snapshot_hash="x" * 64),
    "wrong-checksum": lambda p: p["run_api"].update(snapshot_hash="a" * 64),
    "wrong-project": lambda p: p.update(project_id=ident("foreign-project")),
    "wrong-workspace": lambda p: p["run_api"].update(workspace_id=ident("foreign-workspace")),
    "wrong-architecture": lambda p: p["run_api"].update(
        architecture_id=ident("foreign-architecture")
    ),
    "wrong-source": lambda p: p["run_api"].update(source_plan_id=ident("foreign-source")),
    "wrong-api-task-id": lambda p: p["run_api"]["tasks"][0].update(id=ident("foreign-task")),
    "duplicate-task-id": lambda p: p["initial_sql"]["tasks"][1].update(
        id=p["initial_sql"]["tasks"][0]["id"]
    ),
    "duplicate-source-task": lambda p: p["initial_sql"]["tasks"][1].update(
        source_task_id=p["initial_sql"]["tasks"][0]["source_task_id"]
    ),
    "duplicate-task-key": lambda p: p["initial_sql"]["tasks"][1].update(key="storage"),
    "missing-api-task": lambda p: p["run_api"]["tasks"].pop(),
    "missing-graph-node": lambda p: p["initial_sql"]["graph"]["nodes"].pop(),
    "foreign-graph-node": lambda p: p["initial_sql"]["graph"]["nodes"][0].update(key="foreign"),
    "invalid-dependency": lambda p: p["initial_sql"]["dependencies"][0].update(
        prerequisite_id=ident("absent-task")
    ),
    "foreign-edge-run": lambda p: p["initial_sql"]["dependencies"][0].update(
        run_id=ident("foreign-run")
    ),
    "foreign-edge-project": lambda p: p["initial_sql"]["dependencies"][0].update(
        project_id=ident("foreign-project")
    ),
    "missing-edge": lambda p: p["initial_sql"].update(dependencies=[]),
    "duplicate-edge": lambda p: p["initial_sql"]["dependencies"].append(
        deepcopy(p["initial_sql"]["dependencies"][0])
    ),
    "modified-snapshot": lambda p: p["initial_sql"]["source_snapshot"].update(
        project_id=ident("foreign-project")
    ),
    "missing-snapshot": lambda p: p["initial_sql"].pop("source_snapshot"),
    "missing-events": lambda p: p["initial_sql"].update(events=[]),
    "missing-event-fields": lambda p: p["initial_sql"].update(
        events=[{"sequence": 1}, {"sequence": 2}]
    ),
    "wrong-event-actor": lambda p: p["initial_sql"]["events"][0].update(
        actor_id=ident("foreign-actor")
    ),
    "false-event-success": lambda p: p["initial_sql"]["events"][1].update(
        new_state="verified_complete"
    ),
    "duplicate-event": lambda p: p["initial_sql"]["events"][1].update(
        id=p["initial_sql"]["events"][0]["id"]
    ),
    "boolean-event-sequence": lambda p: p["initial_sql"]["events"][0].update(sequence=True),
    "forged-completion": lambda p: p["run_api"]["tasks"][0].update(
        execution_status="verified_complete"
    ),
    "false-no-execution": lambda p: p["run_api"].update(execution_performed=0),
    "false-graph-valid": lambda p: p["initial_sql"]["graph"].update(valid=1),
    "false-zero-generation": lambda p: p.update(model_generation_requests=False),
    "false-one-post": lambda p: p.update(browser_create_posts=True),
    "false-flag": lambda p: p.update(protected_ui_hidden=1),
    "malformed-task": lambda p: p["initial_sql"]["tasks"][0].update(definition={}),
    "extra-secret-field": lambda p: p.update(unexpected_private_value="unit-sensitive-marker"),
    "boolean-document-version": lambda p: p["initial_sql"]["source_snapshot"]["architecture"][
        "document"
    ].update(schema_version=True),
    "float-document-version": lambda p: p["initial_sql"]["source_snapshot"]["product_plan"][
        "document"
    ].update(schema_version=1.0),
    "normalized-sql-text": lambda p: p["initial_sql"]["tasks"][0]["definition"].update(
        title=" Persist daily check-ins "
    ),
    "normalized-api-text": lambda p: p["run_api"]["tasks"][0]["definition"].update(
        title=" Persist daily check-ins "
    ),
    "noncontiguous-edge-order": lambda p: p["initial_sql"]["dependencies"][0].update(
        display_order=3
    ),
    "self-edge": lambda p: p["initial_sql"]["dependencies"][0].update(
        dependent_id=p["initial_sql"]["dependencies"][0]["prerequisite_id"]
    ),
}


def invalid_proof(case):
    proof = synthetic_proof()
    MUTATIONS[case](proof)
    # Reconcile reload envelope deliberately, so independent relational/typed checks must reject.
    proof["reloaded_sql"] = deepcopy(proof.get("initial_sql"))
    return proof


@pytest.mark.parametrize("case", list(MUTATIONS))
def test_malformed_contradictory_and_forged_proof_is_rejected(case):
    with pytest.raises(base.EvidenceError, match="Local B proof") as error:
        validate_proof(invalid_proof(case))
    assert "unit-sensitive-marker" not in str(error.value)


@pytest.mark.parametrize("case", list(MUTATIONS))
def test_full_receipt_validator_rejects_bound_but_invalid_proof(tmp_path, monkeypatch, case):
    # Only the browser REPORT PARSER is unit-isolated. Production receipt/artifact/proof
    # checks execute, with a self-consistent invalid proof/hash/results envelope.
    # No receipt produced here is actual command or live-control-plane evidence.
    proof = invalid_proof(case)
    current = base.source_manifest()
    report = {"unit_fixture_not_execution_evidence": True}
    monkeypatch.setattr(base, "playwright_report", lambda *a, **kw: report)
    artifacts = {"local-proof.json": proof, "local-browser.json": {}, "local-browser.log": None}
    for name, value in artifacts.items():
        (tmp_path / name).write_text(
            "unit log" if value is None else json.dumps(value), encoding="utf-8"
        )
    command, argv, _ = gates.commands("B", tmp_path)[0]
    receipt = {
        "stage": gates.STAGE,
        "gate": "B",
        "result": "PASS",
        "exit_code": 0,
        "execution_class": "real_local_control_plane",
        "verification_contract": gates.contract(),
        "source_start": current,
        "source_end": current,
        "commands": [{"name": command, "argv": argv, "exit_code": 0}],
        "artifacts": {name: base.digest(tmp_path / name) for name in artifacts},
        "results": {"local-browser": report, "local-proof": proof},
    }
    path = tmp_path / "synthetic-invalid-receipt.json"
    path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(base.EvidenceError, match="Local B proof"):
        gates.validate(path, "B", current)


def test_independent_postgresql_rows_form_complete_proof_and_empty_sql_is_rejected(client):
    project, _, _, api = initialize(client)
    audit = inspect(UUID(api["id"]))  # Actual separate engine/connection and SQL queries.
    assert audit == inspect(UUID(api["id"]))
    proof = assemble(api, audit)
    assert validate_proof(proof) is proof
    assert audit["project_id"] == project
    assert len(audit["tasks"]) == 2 and len(audit["dependencies"]) == 1
    for task, api_task in zip(audit["tasks"], api["tasks"], strict=True):
        assert task["id"] == api_task["id"] and task["definition"] == api_task["definition"]
    for sql in (proof["initial_sql"], proof["reloaded_sql"]):
        sql["tasks"] = []
    with pytest.raises(base.EvidenceError, match="required field"):
        validate_proof(proof)


def test_independent_sql_missing_run_is_rejected(client):
    with pytest.raises(ValueError, match="Saved test run not found"):
        inspect(UUID(ident("nonexistent-run")))


@pytest.mark.parametrize(
    "path,fields",
    [
        ([], list(SQL.model_fields)),
        (["tasks", 0], list(SQLTask.model_fields)),
        (["dependencies", 0], list(Dependency.model_fields)),
        (["events", 0], list(Event.model_fields)),
    ],
)
def test_every_sql_record_field_is_required(path, fields):
    for field in fields:
        proof = synthetic_proof()
        for audit in (proof["initial_sql"], proof["reloaded_sql"]):
            target = audit
            for part in path:
                target = target[part]
            del target[field]
        with pytest.raises(base.EvidenceError, match="required field"):
            validate_proof(proof)


@pytest.mark.parametrize(
    "field,value",
    [
        ("snapshot_hash", "b" * 64),
        ("project_id", ident("foreign-project")),
        ("workspace_id", ident("foreign-workspace")),
        ("architecture_id", ident("foreign-source")),
        ("source_plan_id", ident("foreign-plan")),
    ],
)
def test_equal_but_contradictory_sql_api_bindings_do_not_validate_source(field, value):
    proof = synthetic_proof()
    for target in (proof, proof["run_api"], proof["initial_sql"], proof["reloaded_sql"]):
        if field in target:
            target[field] = value
    with pytest.raises(base.EvidenceError, match="Local B proof"):
        validate_proof(proof)


def test_native_sql_empty_task_query_fails_closed(client, monkeypatch):
    _, _, _, api = initialize(client)
    original = Session.scalars

    def empty_task_query(session, statement, *args, **kwargs):
        # Explicit narrow SQL-result double only. Real run/engine/other queries remain.
        if statement.column_descriptions[0].get("entity") is OrchestrationTask:
            return SimpleNamespace(all=list)
        return original(session, statement, *args, **kwargs)

    monkeypatch.setattr(Session, "scalars", empty_task_query)
    with pytest.raises(ValueError, match="no persisted task records"):
        inspect(UUID(api["id"]))


def test_native_sql_integrity_guard_survives_python_optimization():
    result = subprocess.run(
        [
            sys.executable,
            "-O",
            "-c",
            "from scripts.inspect_orchestration import require; require(False, 'unit-invalid-records')",
        ],
        capture_output=True,
        check=False,
        text=True,
        timeout=30,
    )
    assert result.returncode == 1
    assert "Independent SQL audit: unit-invalid-records" in result.stderr


def test_reload_cannot_hide_raw_sql_differences_through_normalization():
    proof = synthetic_proof()
    proof["reloaded_sql"]["tasks"][0]["definition"]["title"] = " Persist daily check-ins "
    with pytest.raises(base.EvidenceError, match="reload"):
        validate_proof(proof)


@pytest.mark.parametrize(
    "field,value",
    [
        ("workers", True),
        ("model_generation_requests", False),
        ("proof_version", 2.0),
    ],
)
def test_receipt_contract_uses_type_sensitive_comparison(tmp_path, field, value):
    current = base.source_manifest()
    contract = gates.contract()
    contract[field] = value
    path = tmp_path / "synthetic-malformed-contract.json"
    path.write_text(
        json.dumps(
            {
                "stage": gates.STAGE,
                "gate": "B",
                "result": "PASS",
                "exit_code": 0,
                "verification_contract": contract,
                "execution_class": "real_local_control_plane",
                "source_start": current,
                "source_end": current,
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(base.EvidenceError, match="passing receipt"):
        gates.validate(path, "B", current)

"""Verifier-unit tests. Synthetic receipts/child processes are NEVER live evidence."""

import json
import sys

import pytest

from scripts import architect_verification as stage
from scripts import verification as base


def test_architect_gate_a_blanks_every_runtime_alias():
    env = base.deterministic_env(
        {
            "ORBA_ARCHITECT_API_KEY": "unit-secret",
            "ORBA_ARCHITECT_MODEL": "gemini-3.6-flash",
            "GEMINI_API_KEY": "unit-secret",
            "ORBA_PM_MODEL": "gemini-3.8-flash",
            "ORBA_ARCHITECT_LIVE_OPT_IN": "1",
        }
    )
    for key in (
        "ORBA_ARCHITECT_API_KEY",
        "ORBA_ARCHITECT_MODEL",
        "GEMINI_API_KEY",
        "ORBA_PM_API_KEY",
        "ORBA_PM_MODEL",
    ):
        assert env[key] == ""
    assert "orba_test" in env["DATABASE_URL"]
    assert "ORBA_ARCHITECT_LIVE_OPT_IN" not in env


def test_stage04_runner_propagates_actual_required_child_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(stage, "EVIDENCE", tmp_path)
    monkeypatch.setattr(base, "source_manifest", lambda: {"sha256": "unit-only-source"})
    monkeypatch.setattr(base, "ports_available", lambda: None)
    monkeypatch.setattr(
        stage,
        "commands",
        lambda gate, attempt: [
            (
                "required-unit-failure",
                [
                    sys.executable,
                    "-c",
                    "assert False, 'required Architect verification child failed'",
                ],
                5,
            ),
            ("never-dispatch", [sys.executable, "-c", "raise SystemExit(99)"], 5),
        ],
    )
    assert stage.execute("A") == 1
    receipt = json.loads(stage.latest("A").read_text())
    assert receipt["stage"] == stage.STAGE and receipt["result"] == "FAIL"
    assert len(receipt["commands"]) == 1 and receipt["commands"][0]["exit_code"] == 1


def test_live_runner_propagates_failed_child_without_retry_unit_only(tmp_path, monkeypatch):
    monkeypatch.setattr(stage, "EVIDENCE", tmp_path)
    monkeypatch.setattr(base, "source_manifest", lambda: {"sha256": "unit-only-source"})
    monkeypatch.setattr(base, "ports_available", lambda: None)
    monkeypatch.setattr(stage, "require_live_opt_in", lambda **kwargs: None)
    monkeypatch.setattr(stage, "profile", lambda: {"unit_only": True})
    # Base runner binds A receipt hashes before dispatch; this file is synthetic UNIT input.
    a = tmp_path / "unit-A.json"
    a.write_text("{}")
    (tmp_path / "latest-A.json").write_text(
        json.dumps({"receipt": a.name, "sha256": base.digest(a)})
    )
    monkeypatch.setattr(
        stage,
        "commands",
        lambda gate, attempt: [("live-browser", [sys.executable, "-c", "raise SystemExit(37)"], 5)],
    )
    assert stage.execute("B", allow_paid=True) == 37
    receipt = json.loads(stage.latest("B").read_text())
    assert receipt["result"] == "FAIL" and receipt["commands"][0]["exit_code"] == 37


def test_missing_optin_never_reads_runtime_profile_or_dispatches(tmp_path, monkeypatch):
    monkeypatch.setattr(stage, "EVIDENCE", tmp_path)
    monkeypatch.setattr(base, "source_manifest", lambda: {"sha256": "unit-only-source"})

    def tripwire(*args, **kwargs):
        raise AssertionError("Missing opt-in must not inspect credentials or dispatch")

    monkeypatch.setattr(stage, "profile", tripwire)
    monkeypatch.setattr(stage, "commands", tripwire)
    assert stage.execute("B") == 2
    receipt = json.loads(stage.latest("B").read_text())
    assert receipt["commands"] == [] and receipt["result"] == "BLOCKED"


@pytest.mark.parametrize("mutation", ["old_stage", "double", "failed", "missing_exit", "stale"])
def test_architect_receipt_rejects_false_certification(tmp_path, mutation):
    value = {
        "stage": stage.STAGE,
        "gate": "B",
        "verification_contract": stage.contract(),
        "execution_class": "real_gemini_browser",
        "result": "PASS",
        "exit_code": 0,
        "source_start": {"sha256": "unit"},
        "source_end": {"sha256": "unit"},
        "commands": [],
        "artifacts": {},
    }
    if mutation == "old_stage":
        value["stage"] = "stage03"
    elif mutation == "double":
        value["execution_class"] = "controlled_provider_double"
    elif mutation == "failed":
        value["result"] = "FAIL"
    elif mutation == "missing_exit":
        value.pop("exit_code")
    else:
        value["source_end"] = {"sha256": "stale"}
    path = tmp_path / "receipt.json"
    path.write_text(json.dumps(value))
    with pytest.raises(base.EvidenceError):
        stage.validate(path, "B", {"sha256": "unit"})


def test_stage04_c_is_partial_without_its_own_real_gate_b(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(stage, "EVIDENCE", tmp_path)
    assert stage.summary() == 2
    assert json.loads(capsys.readouterr().out)["stage04_verdict"] == "PARTIAL"


@pytest.mark.parametrize("returned", [None, "", "controlled-double-not-live", "fixture", 123])
def test_live_identity_rejects_missing_or_controlled_model_labels(returned):
    with pytest.raises(base.EvidenceError):
        stage.require_live_identity(
            {"requested_model": "gemini-3.6-flash", "returned_model": returned},
            {"model": "gemini-3.6-flash"},
        )


@pytest.mark.parametrize("returned", ["gemini-3.6-flash-001", "models/gemini-3.6-flash"])
def test_live_identity_accepts_versioned_labels_but_never_a_flagged_double(returned):
    audit = {"requested_model": "gemini-3.6-flash", "returned_model": returned}
    selected = {"model": "gemini-3.6-flash"}
    # A metadata shape check is not evidence of generation or real provider access.
    stage.require_live_identity(audit, selected)
    audit["diagnostic"] = {"provider_double": True}
    with pytest.raises(base.EvidenceError):
        stage.require_live_identity(audit, selected)
    audit.pop("diagnostic")
    audit["requested_model"] = "gemini-3.8-flash"
    with pytest.raises(base.EvidenceError):
        stage.require_live_identity(audit, selected)

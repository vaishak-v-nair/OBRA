"""Isolated verifier unit tests. Synthetic INVALID receipts are never live evidence."""

import json
import subprocess
import sys

import pytest

from scripts import orchestration_verification as gates
from scripts import verification as base


def test_gate_a_retains_every_previous_command_and_adds_orchestration(tmp_path):
    existing = gates.prior.commands("A", tmp_path)
    current = gates.commands("A", tmp_path)
    assert current[:-1] == existing
    assert [row[0] for row in current][-1] == "orchestration-browser"
    assert len(current) == 17
    assert all("live" not in row[0] for row in current)
    assert gates.commands("B", tmp_path) == [
        ("local-browser", base.NPM + ["test:e2e:orchestration:local"], 600)
    ]


@pytest.mark.parametrize("gate,exit_code", [("A", 7), ("B", 9)])
def test_actual_failed_required_command_cannot_become_passing_gate(
    tmp_path, monkeypatch, gate, exit_code
):
    # Only prerequisites are unit-isolated. The required command genuinely exits nonzero.
    monkeypatch.setattr(gates, "EVIDENCE", tmp_path)
    monkeypatch.setattr(base, "ports_available", lambda: None)
    if gate == "B":
        a = tmp_path / "synthetic-a-unit-fixture.json"
        a.write_text("{}", encoding="utf-8")
        monkeypatch.setattr(gates, "latest", lambda _: a)
        monkeypatch.setattr(gates, "validate", lambda *args: None)
    monkeypatch.setattr(
        gates,
        "commands",
        lambda *args: [
            (
                "deliberately-failed-required-command",
                [sys.executable, "-c", f"raise SystemExit({exit_code})"],
                15,
            )
        ],
    )
    assert gates.execute(gate) == exit_code
    receipt = json.loads(
        next(tmp_path.glob(f"*-{gate}-*/receipt.json")).read_text(encoding="utf-8")
    )
    assert receipt["result"] == "FAIL" and receipt["exit_code"] == exit_code
    assert receipt["commands"][0]["exit_code"] == exit_code
    assert "results" not in receipt


def test_local_b_without_matching_gate_a_dispatches_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(gates, "EVIDENCE", tmp_path)
    assert gates.execute("B") == 2
    receipt = json.loads(next(tmp_path.glob("*-B-*/receipt.json")).read_text(encoding="utf-8"))
    assert receipt["result"] == "BLOCKED" and receipt["commands"] == []


@pytest.mark.parametrize("child_exit", [0, 7])
def test_final_fingerprint_failure_preserves_native_exit_and_cannot_pass(
    tmp_path, monkeypatch, child_exit
):
    # Unit-isolate only source discovery/report parsing. The child really executes.
    current = base.source_manifest()
    calls = 0

    def source():
        nonlocal calls
        calls += 1
        if calls == (3 if child_exit == 0 else 2):
            raise subprocess.CalledProcessError(3221226091, ["git", "ls-files"])
        return current

    monkeypatch.setattr(gates, "EVIDENCE", tmp_path)
    monkeypatch.setattr(base, "ports_available", lambda: None)
    monkeypatch.setattr(base, "source_manifest", source)
    monkeypatch.setattr(gates, "results_for", lambda *args: {})
    monkeypatch.setattr(
        gates,
        "commands",
        lambda *args: [
            ("native-child", [sys.executable, "-c", f"raise SystemExit({child_exit})"], 15)
        ],
    )
    assert gates.execute("A") == (child_exit or 1)
    receipt_path = next(tmp_path.glob("*-A-*/receipt.json"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    journal = json.loads(
        (receipt_path.parent / "native-child-command.json").read_text(encoding="utf-8")
    )
    assert receipt["result"] == "FAIL" and receipt["source_end"] is None
    assert receipt["source_end_error"] == {
        "category": "CalledProcessError",
        "exit_code": 3221226091,
    }
    assert journal == receipt["commands"][0]
    assert journal["exit_code"] == child_exit
    with pytest.raises(base.EvidenceError):
        gates.validate(receipt_path, "A", current)


@pytest.mark.parametrize(
    "case", ["controlled", "stale", "missing_commands", "failed", "wrong_stage"]
)
def test_receipt_contract_rejects_fake_stale_incomplete_and_failed_evidence(tmp_path, case):
    current = base.source_manifest()
    value = {
        "stage": gates.STAGE,
        "gate": "B",
        "result": "PASS",
        "exit_code": 0,
        "execution_class": "real_local_control_plane",
        "verification_contract": gates.contract(),
        "source_start": current,
        "source_end": current,
        "commands": [],
    }
    if case == "controlled":
        value["execution_class"] = "controlled_provider_double"
    elif case == "stale":
        value["source_end"] = {"sha256": "0" * 64}
    elif case == "failed":
        value.update(result="FAIL", exit_code=1)
    elif case == "wrong_stage":
        value["stage"] = "stage04-architect"
    path = tmp_path / "synthetic-invalid-receipt-unit-fixture.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(base.EvidenceError):
        gates.validate(path, "B", current)


def test_gate_c_cannot_certify_missing_local_or_controlled_evidence(tmp_path, monkeypatch):
    monkeypatch.setattr(gates, "EVIDENCE", tmp_path)
    assert gates.summary() == 1
    value = json.loads(next(tmp_path.glob("summary-*.json")).read_text(encoding="utf-8"))
    assert value["verdict"] == "PARTIAL" and value["overall_stage05"] == "IN PROGRESS"
    assert all(gate["result"] != "PASS" for gate in value["gates"].values())


def test_orchestration_gate_environment_cannot_inherit_runtime_credentials():
    env = base.deterministic_env(
        {
            "ORBA_PM_API_KEY": "unit-not-a-real-key",
            "GEMINI_API_KEY": "unit-not-a-real-key",
            "ORBA_ARCHITECT_API_KEY": "unit-not-a-real-key",
            "ORBA_ARCHITECT_LIVE_OPT_IN": "1",
        }
    )
    assert all(
        env[key] == "" for key in ("ORBA_PM_API_KEY", "GEMINI_API_KEY", "ORBA_ARCHITECT_API_KEY")
    )
    assert env.get("ORBA_ARCHITECT_LIVE_OPT_IN") != "1"

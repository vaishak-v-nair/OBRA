"""Isolated gate tests: actual nonzero native children cannot become PASS receipts."""

import json
import sys

import pytest

from scripts import scheduler_verification as gates
from scripts import verification as base


def test_stage05b_retains_all_previous_commands_and_browser_baselines(tmp_path):
    previous = gates.foundation.commands("A", tmp_path)
    assert len(previous) == 17
    assert [(name, argv) for name, argv, _ in gates.commands("A", tmp_path)[:-1]] == [
        (name, argv) for name, argv, _ in previous
    ]
    assert (
        next(timeout for name, _, timeout in gates.commands("A", tmp_path) if name == "backend")
        == 1800
    )
    assert (
        next(
            timeout
            for name, _, timeout in gates.commands("A", tmp_path)
            if name == "orchestration-browser"
        )
        == 3990
    )
    assert len(gates.commands("A", tmp_path)) == 18
    assert gates.commands("A", tmp_path)[-1][0] == "scheduler-browser"
    assert gates.commands("B", tmp_path) == [
        ("local-browser", base.NPM + ["test:e2e:scheduler:local"], 600)
    ]
    assert gates.contract()["execution_performed"] is False


@pytest.mark.parametrize("gate,exit_code", [("A", 7), ("B", 9)])
def test_required_native_command_failure_preserves_real_exit(
    tmp_path, monkeypatch, gate, exit_code
):
    monkeypatch.setattr(gates, "EVIDENCE", tmp_path)
    monkeypatch.setattr(base, "ports_available", lambda: None)
    if gate == "B":
        a = tmp_path / "isolated-unit-a.json"
        a.write_text("{}", encoding="utf-8")
        monkeypatch.setattr(gates, "latest", lambda _: a)
        monkeypatch.setattr(gates, "validate", lambda *args: None)
    monkeypatch.setattr(
        gates,
        "commands",
        lambda *args: [
            (
                "intentionally-failing-native-command",
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


def test_local_gate_b_requires_applicable_gate_a_before_starting_processes(tmp_path, monkeypatch):
    monkeypatch.setattr(gates, "EVIDENCE", tmp_path)
    assert gates.execute("B") == 2
    receipt = json.loads(next(tmp_path.glob("*-B-*/receipt.json")).read_text(encoding="utf-8"))
    assert receipt["result"] == "BLOCKED" and receipt["commands"] == []


def test_controlled_or_empty_proof_cannot_verify_stage05b(tmp_path, monkeypatch):
    monkeypatch.setattr(gates, "EVIDENCE", tmp_path)
    with pytest.raises(base.EvidenceError):
        gates.live_local_proof(tmp_path)
    (tmp_path / "scheduler-proof.json").write_text(
        '{"result":"PASS","provider_double":true}', encoding="utf-8"
    )
    with pytest.raises(base.EvidenceError):
        gates.live_local_proof(tmp_path)

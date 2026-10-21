"""Verifier contract UNIT tests. Authored reports are NOT gate/live evidence."""

import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest

from orba.config import Settings
from scripts import verification as v


def json_file(path, value):
    path.write_text(json.dumps(value))
    return path


def browser_fixture(project="chromium"):
    return {
        "config": {"projects": [{"name": project, "retries": 0}]},
        "errors": [],
        "stats": {"expected": 1, "skipped": 0, "unexpected": 0, "flaky": 0},
        "suites": [
            {
                "specs": [
                    {
                        "file": "fixture.spec.ts",
                        "title": "authored unit report",
                        "tests": [
                            {
                                "projectName": project,
                                "expectedStatus": "passed",
                                "status": "expected",
                                "results": [{"status": "passed", "retry": 0}],
                            }
                        ],
                    }
                ]
            }
        ],
    }


@pytest.mark.parametrize("kind", ["skipped", "failure", "error", "empty", "missing_case"])
def test_junit_rejects_incomplete_or_nonpassing_reports(tmp_path, kind):
    report = ET.Element("testsuites")
    suite = ET.SubElement(report, "testsuite")
    if kind != "empty":
        case = ET.SubElement(suite, "testcase", classname="tests.test_fixture", name="test_case")
        if kind in {"skipped", "failure", "error"}:
            ET.SubElement(case, kind)
    path = tmp_path / "report.xml"
    ET.ElementTree(report).write(path)
    with pytest.raises(v.EvidenceError):
        v.junit_report(
            path,
            [
                "tests/test_fixture.py::test_missing"
                if kind == "missing_case"
                else "tests/test_fixture.py::test_case"
            ],
        )


@pytest.mark.parametrize(
    "kind", ["skip", "xfail", "retry", "flaky", "missing", "duplicate", "zero", "missing_project"]
)
def test_browser_report_rejects_false_success(tmp_path, kind):
    report = browser_fixture()
    test = report["suites"][0]["specs"][0]["tests"][0]
    if kind == "skip":
        report["stats"]["skipped"] = 1
    elif kind == "xfail":
        test["expectedStatus"] = "failed"
    elif kind == "retry":
        test["results"][0]["retry"] = 1
    elif kind == "flaky":
        report["stats"]["flaky"] = 1
    elif kind == "missing":
        test["results"] = []
    elif kind == "duplicate":
        report["suites"].append(report["suites"][0])
    elif kind == "zero":
        report["suites"] = []
    with pytest.raises(v.EvidenceError):
        v.playwright_report(
            json_file(tmp_path / "report.json", report),
            projects={"mobile": 1} if kind == "missing_project" else None,
        )


def test_actual_passed_reports_are_validated_not_stdout(tmp_path):
    path = tmp_path / "backend.xml"
    path.write_text(
        '<testsuites><testsuite><testcase classname="tests.test_real" name="test_case"/></testsuite></testsuites>'
    )
    assert v.junit_report(path, ["tests/test_real.py::test_case"])["passed"] == 1
    assert (
        v.playwright_report(json_file(tmp_path / "browser.json", browser_fixture()))["passed"] == 1
    )
    path.write_text("PASS")
    with pytest.raises(ET.ParseError):
        v.junit_report(path)


@pytest.mark.parametrize(
    "parameter", ["models/gemini-3.8-flash", "models.gemini-3.8-flash", "docs/a.py::section/b"]
)
def test_junit_preserves_literal_parameters_and_rejects_changed_names(tmp_path, parameter):
    # Authored UNIT report: module path separators normalize; parameter text must not.
    name = f"test_model[{parameter}]"
    report = ET.Element("testsuites")
    suite = ET.SubElement(report, "testsuite")
    ET.SubElement(suite, "testcase", classname="tests.test_metadata", name=name)
    path = tmp_path / "literal.xml"
    ET.ElementTree(report).write(path)
    result = v.junit_report(path, [f"tests/test_metadata.py::{name}"])
    assert result["passed"] == 1
    assert result["identities"] == [f"tests.test_metadata::{name}"]
    different_name = name.replace("/", ".") if "/" in name else name + "-missing"
    with pytest.raises(v.EvidenceError, match="Missing 1 mandatory backend baseline cases"):
        v.junit_report(path, [f"tests/test_metadata.py::{different_name}"])


def test_gate_a_empty_overrides_defeat_dotenv_and_selection_filters(tmp_path, monkeypatch):
    dotenv = tmp_path / ".env"
    dotenv.write_text("GEMINI_API_KEY=synthetic-unit-marker\nORBA_PM_MODEL=gemini-unit\n")
    env = v.deterministic_env(
        {
            "GEMINI_API_KEY": "unit",
            "PYTEST_ADDOPTS": "-k only_happy",
            "ORBA_LIVE_OPT_IN": "1",
            "PLAYWRIGHT_GREP": "only_happy",
        }
    )
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    config = Settings(_env_file=dotenv)
    assert not config.pm_configured and config.pm_model is None
    assert env["ORBA_PM_API_KEY"] == env["GEMINI_API_KEY"] == ""
    assert (
        "PYTEST_ADDOPTS" not in env
        and "PLAYWRIGHT_GREP" not in env
        and "ORBA_LIVE_OPT_IN" not in env
    )
    assert "orba_test" in env["DATABASE_URL"]


def test_manifest_detects_uncommitted_add_change_delete_but_excludes_secrets(tmp_path):
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
    (tmp_path / "apps").mkdir()
    code = tmp_path / "apps/source.py"
    code.write_text("version = 1\n")
    (tmp_path / ".gitignore").write_text(".env\n")
    (tmp_path / ".env").write_text("synthetic-unit-secret")
    original = v.source_manifest(tmp_path)
    assert ".env" not in original["files"] and "apps/source.py" in original["files"]
    code.write_text("version = 2\n")
    assert v.source_manifest(tmp_path) != original
    code.unlink()
    assert v.source_manifest(tmp_path) != original


def test_native_failure_launch_error_and_timeout_preserve_nonzero(tmp_path):
    failure = v.run_command(
        "assertion",
        [sys.executable, "-c", "assert False, 'intentional verifier unit failure'"],
        tmp_path,
        dict(os.environ),
        tmp_path / "failure.log",
        5,
    )
    assert failure["exit_code"] == 1 and "AssertionError" in (tmp_path / "failure.log").read_text()
    missing = v.run_command(
        "missing", ["orba-binary-does-not-exist"], tmp_path, {}, tmp_path / "missing.log", 1
    )
    assert missing["exit_code"] == 127 and missing["failure"] == "launch_error"
    timeout = v.run_command(
        "timeout",
        [sys.executable, "-c", "import time; time.sleep(10)"],
        tmp_path,
        dict(os.environ),
        tmp_path / "timeout.log",
        0.1,
    )
    assert timeout["exit_code"] == 124 and timeout["failure"] == "command_deadline"


def test_gate_a_runner_stops_after_real_child_assertion_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(v, "EVIDENCE", tmp_path)
    monkeypatch.setattr(v, "source_manifest", lambda: {"sha256": "synthetic-unit-source"})
    monkeypatch.setattr(v, "ports_available", lambda: None)
    monkeypatch.setattr(
        v,
        "commands",
        lambda gate, attempt: [
            (
                "required-test-unit-experiment",
                [sys.executable, "-c", "assert False, 'required controlled test fails'"],
                5,
            ),
            ("must-not-run", [sys.executable, "-c", "raise SystemExit(99)"], 5),
        ],
    )
    assert v.execute_gate("A") == 1
    receipt = json.loads(v.latest("A").read_text())
    assert receipt["result"] == "FAIL" and len(receipt["commands"]) == 1
    assert receipt["commands"][0]["exit_code"] == 1


def test_missing_paid_optin_never_reaches_config_or_commands(tmp_path, monkeypatch):
    monkeypatch.setattr(v, "EVIDENCE", tmp_path)
    monkeypatch.setattr(v, "source_manifest", lambda: {"sha256": "synthetic-unit-source"})

    def dispatch_tripwire(*args, **kwargs):
        raise AssertionError("Missing opt-in must never dispatch or inspect a credential")

    monkeypatch.setattr(v, "execution_profile", dispatch_tripwire)
    monkeypatch.setattr(v, "commands", dispatch_tripwire)
    monkeypatch.delenv("ORBA_LIVE_OPT_IN", raising=False)
    assert v.execute_gate("B") == 2
    receipt = json.loads(v.latest("B").read_text())
    assert receipt["result"] == "BLOCKED" and receipt["commands"] == []


@pytest.mark.parametrize(
    "change",
    [
        "double",
        "failed",
        "stale",
        "missing_command",
        "native_failure",
        "missing_exit",
        "mutated_artifact",
    ],
)
def test_receipts_fail_closed_before_any_live_certification(tmp_path, monkeypatch, change):
    current = {"sha256": "unit-source"}
    value = {
        "version": 1,
        "gate": "B",
        "execution_class": "real_gemini_browser",
        "result": "PASS",
        "exit_code": 0,
        "source_start": current,
        "source_end": current,
        "commands": [{"name": "live-browser", "argv": v.NPM + ["test:e2e:live"], "exit_code": 0}],
        "artifacts": {},
    }
    if change == "double":
        value["execution_class"] = "controlled_provider_double"
    elif change == "failed":
        value["result"] = "FAIL"
    elif change == "stale":
        value["source_end"] = {"sha256": "old"}
    elif change == "missing_command":
        value["commands"] = []
    elif change == "native_failure":
        value["commands"][0]["exit_code"] = 1
    elif change == "missing_exit":
        del value["commands"][0]["exit_code"]
    else:
        value["artifacts"] = {"artifact.log": "incorrect-hash"}
        (tmp_path / "artifact.log").write_text("changed")
    with pytest.raises(v.EvidenceError):
        v.validate_receipt(json_file(tmp_path / "receipt.json", value), "B", current)


def test_controlled_or_missing_gate_b_cannot_make_stage_verified(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(v, "EVIDENCE", tmp_path)
    monkeypatch.setattr(v, "source_manifest", lambda: {"sha256": "unit-source"})
    assert v.stage_summary() == 2
    assert json.loads(capsys.readouterr().out)["stage03_verdict"] == "PARTIAL"


def test_controlled_provider_proof_is_never_live_evidence(tmp_path):
    json_file(tmp_path / "live-browser.json", browser_fixture())
    json_file(
        tmp_path / "live-proof.json",
        {
            "execution_class": "controlled_provider_double",
            "provider_double": True,
            "generation_posts": 1,
            "result": "PASS",
        },
    )
    with pytest.raises(v.EvidenceError, match="genuine"):
        v.results_for("B", tmp_path)


def test_receipts_are_create_once_and_local_gate_lock_is_exclusive(tmp_path):
    path = tmp_path / "receipt.json"
    v.write_new(path, {"result": "FAIL"})
    with pytest.raises(FileExistsError):
        v.write_new(path, {"result": "PASS"})
    with v.gate_lock(tmp_path), pytest.raises(v.EvidenceError), v.gate_lock(tmp_path):
        raise AssertionError("Second gate must not enter")

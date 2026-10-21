"""Authored validator fixtures/native failure experiments, NEVER live evidence."""

import json
import sys
from datetime import UTC, datetime

import pytest

from orba.pm_models_policy import model_policy
from orba.pm_readiness import ProviderReadiness
from scripts import verification as v


def fixture_report(profile):
    return ProviderReadiness(
        status="ready_for_attempt",
        message="Authored unit fixture; not provider evidence",
        operation="model_metadata",
        configured=True,
        requested_model=profile["model"],
        metadata_model="models/" + profile["model"].removeprefix("models/"),
        thinking_level=profile["thinking_level"],
        supported_actions=["generateContent"],
        input_token_limit=1048576,
        output_token_limit=65536,
        metadata_requests=1,
        provider_http_status=200,
        structured_output_support="documented",
        structured_output_documentation=model_policy(profile["model"]).documentation,
        checked_at=datetime(2026, 10, 19, 0, 0, 2, tzinfo=UTC),
        elapsed_ms=500,
        generation_limits={
            k: profile[k]
            for k in (
                "server_timeout_seconds",
                "transport_timeout_seconds",
                "envelope_timeout_seconds",
                "max_output_tokens",
                "max_input_bytes",
                "max_concurrent",
                "account_attempts_per_hour",
                "global_attempts_per_hour",
            )
        },
    )


@pytest.fixture
def authored_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(v, "EVIDENCE", tmp_path)
    source = {"sha256": "authored-unit-source"}
    profile = v.execution_profile() | {
        "model": "gemini-3.8-flash",
        "thinking_level": "low",
        "credential_configured": True,
    }
    monkeypatch.setattr(v, "source_manifest", lambda: source)
    monkeypatch.setattr(v, "execution_profile", lambda: profile)
    attempt = tmp_path / "authored-B"
    attempt.mkdir()
    v.write_new(attempt / "attempt.json", {"started_at": "2026-10-19T00:00:00+00:00"})
    a_path = tmp_path / "authored-A" / "receipt.json"
    v.write_new(a_path, {"authored": "Not actual Gate A evidence"})

    def validate_a(path, gate, current):
        assert path == a_path and gate == "A" and current == source
        return {"unit_validation_only": True}

    monkeypatch.setattr(v, "validate_receipt", validate_a)
    name, argv, _ = v.commands("B", attempt)[0]
    report = fixture_report(profile).model_dump(mode="json")
    artifact = {
        "version": 1,
        "execution_class": "real_read_only_model_metadata",
        "provider_double": False,
        "attempt_id": attempt.name,
        "source_sha256": source["sha256"],
        "execution_profile": profile,
        "gate_a_receipt": str(a_path.relative_to(tmp_path)),
        "gate_a_receipt_sha256": v.digest(a_path),
        "command": {
            "name": name,
            "argv": argv,
            "exit_code": 0,
            "started_at": "2026-10-19T00:00:01+00:00",
            "completed_at": "2026-10-19T00:00:03+00:00",
        },
        "report": report,
    }

    def save():
        (attempt / "model-readiness.json").write_text(json.dumps(artifact), encoding="utf-8")
        (attempt / "provider-readiness.log").write_text(
            json.dumps(artifact["report"] | {"model": artifact["report"]["requested_model"]}),
            encoding="utf-8",
        )

    save()
    return attempt, artifact, save


def test_metadata_validator_accepts_complete_fixture_but_never_calls_provider(authored_metadata):
    attempt, artifact, _ = authored_metadata
    assert v.validate_model_readiness(attempt, before="2026-10-19T00:00:04+00:00") == artifact


@pytest.mark.parametrize("model", ["gemini-3.6-flash", "gemini-3.5-flash-lite"])
def test_alternative_metadata_artifact_binds_exact_policy_and_profile(
    authored_metadata, monkeypatch, model
):
    attempt, artifact, save = authored_metadata
    profile = artifact["execution_profile"] | {"model": model, "thinking_level": "minimal"}
    monkeypatch.setattr(v, "execution_profile", lambda: profile)
    artifact["execution_profile"] = profile
    artifact["report"] = fixture_report(profile).model_dump(mode="json")
    save()
    assert v.validate_model_readiness(attempt, before="2026-10-19T00:00:04+00:00") == artifact


@pytest.mark.parametrize("change", ["thinking", "input_limit", "hint_hash", "wrong_docs"])
def test_new_generation_policy_cannot_use_mismatched_readiness(authored_metadata, change):
    attempt, artifact, save = authored_metadata
    if change == "thinking":
        artifact["report"]["thinking_level"] = "high"
    elif change == "input_limit":
        artifact["report"]["generation_limits"]["max_input_bytes"] += 1
    elif change == "hint_hash":
        artifact["execution_profile"] = artifact["execution_profile"] | {
            "provider_schema_sha256": "old-provider-schema"
        }
    else:
        artifact["report"]["structured_output_documentation"] = model_policy(
            "gemini-3.6-flash"
        ).documentation
    save()
    with pytest.raises(v.EvidenceError):
        v.validate_model_readiness(attempt, before="2026-10-19T00:00:04+00:00")


@pytest.mark.parametrize(
    "change",
    [
        "missing",
        "controlled",
        "source",
        "profile",
        "a_hash",
        "attempt",
        "not_ready",
        "wrong_model",
        "no_actions",
        "no_limits",
        "excess_output",
        "fake_generation",
        "no_get",
        "old_time",
        "naive_time",
        "nonzero_exit",
        "wrong_command",
        "too_late",
        "duration",
        "mutated_cli",
    ],
)
def test_metadata_validator_rejects_stale_incomplete_or_false_proof(authored_metadata, change):
    attempt, artifact, save = authored_metadata
    if change == "missing":
        (attempt / "model-readiness.json").unlink()
    elif change == "controlled":
        artifact["provider_double"] = True
    elif change == "source":
        artifact["source_sha256"] = "old-source"
    elif change == "profile":
        artifact["execution_profile"] = {"model": "different"}
    elif change == "a_hash":
        artifact["gate_a_receipt_sha256"] = "wrong"
    elif change == "attempt":
        artifact["attempt_id"] = "another-B"
    elif change == "not_ready":
        artifact["report"]["status"] = "provider_unavailable"
    elif change == "wrong_model":
        artifact["report"]["metadata_model"] = "models/gemini-other"
    elif change == "no_actions":
        artifact["report"]["supported_actions"] = []
    elif change == "no_limits":
        artifact["report"]["generation_limits"] = {}
    elif change == "excess_output":
        artifact["report"]["output_token_limit"] = 1
    elif change == "fake_generation":
        artifact["report"]["live_generation_verified"] = True
    elif change == "no_get":
        artifact["report"]["metadata_requests"] = 0
    elif change == "old_time":
        artifact["report"]["checked_at"] = "2026-10-18T00:00:02+00:00"
    elif change == "naive_time":
        artifact["report"]["checked_at"] = "2026-10-19T00:00:02"
    elif change == "nonzero_exit":
        artifact["command"]["exit_code"] = 1
    elif change == "wrong_command":
        artifact["command"]["argv"] = ["fake-success"]
    elif change == "too_late":
        artifact["command"]["completed_at"] = "2026-10-19T00:00:05+00:00"
    elif change == "duration":
        artifact["report"]["elapsed_ms"] = 10000
    if change != "missing":
        save()
    if change == "mutated_cli":
        (attempt / "provider-readiness.log").write_text("{}", encoding="utf-8")
    with pytest.raises((ValueError, OSError, KeyError)):
        v.validate_model_readiness(attempt, before="2026-10-19T00:00:04+00:00")


def test_gate_b_nonready_metadata_stops_before_browser_with_actual_native_exit(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(v, "EVIDENCE", tmp_path)
    monkeypatch.setattr(v, "source_manifest", lambda: {"sha256": "unit-source"})
    monkeypatch.setattr(v, "require_live_opt_in", lambda **kwargs: None)
    monkeypatch.setattr(v, "ports_available", lambda: None)
    profile = v.execution_profile() | {"model": "gemini-3.8-flash", "credential_configured": True}
    monkeypatch.setattr(v, "execution_profile", lambda: profile)
    a_path = tmp_path / "authored-A.json"
    v.write_new(a_path, {"unit": True})
    monkeypatch.setattr(v, "latest", lambda gate: a_path)
    report = fixture_report(profile).model_dump(mode="json") | {"status": "provider_unavailable"}
    program = tmp_path / "nonready.py"
    program.write_text(
        "import json\nprint("
        + repr(json.dumps(report | {"model": report["requested_model"]}))
        + ")\nraise SystemExit(2)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        v,
        "commands",
        lambda gate, attempt: [
            ("provider-readiness", [sys.executable, str(program)], 5),
            ("must-not-run", [sys.executable, "-c", "raise SystemExit(99)"], 5),
        ],
    )
    assert (
        v.execute_gate("B", allow_paid=True) == 2
    )  # Unit-only preflight override; no provider call.
    receipts = list(tmp_path.glob("*-B-*/receipt.json"))
    assert len(receipts) == 1
    receipt = json.loads(receipts[0].read_text())
    assert receipt["result"] == "BLOCKED" and receipt["commands"][0]["exit_code"] == 2
    assert len(receipt["commands"]) == 1 and not (receipts[0].parent / "must-not-run.log").exists()


def test_gate_b_preserves_real_native_failure_without_running_followup(tmp_path, monkeypatch):
    """Temporary controlled runner experiment, not a live-model receipt."""
    monkeypatch.setattr(v, "EVIDENCE", tmp_path)
    monkeypatch.setattr(v, "source_manifest", lambda: {"sha256": "unit-source"})
    monkeypatch.setattr(v, "require_live_opt_in", lambda **kwargs: None)
    monkeypatch.setattr(v, "ports_available", lambda: None)
    a_path = tmp_path / "authored-A.json"
    v.write_new(a_path, {"unit": True})
    monkeypatch.setattr(v, "latest", lambda gate: a_path)
    monkeypatch.setattr(
        v,
        "commands",
        lambda gate, attempt: [
            (
                "controlled-browser-failure",
                [sys.executable, "-c", "assert False, 'controlled required B failure'"],
                5,
            ),
            ("must-not-run", [sys.executable, "-c", "raise SystemExit(99)"], 5),
        ],
    )
    assert v.execute_gate("B", allow_paid=True) == 1
    receipt = json.loads(next(tmp_path.glob("*-B-*/receipt.json")).read_text())
    assert receipt["result"] == "FAIL" and receipt["commands"][0]["exit_code"] == 1
    assert len(receipt["commands"]) == 1

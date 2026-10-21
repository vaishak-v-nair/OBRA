"""Explicit-only real PostgreSQL wrong-success assertion. Expected native exit1.

Never part of normal test discovery and never eligible as Gate A/B evidence.
"""

from datetime import UTC, datetime
from uuid import uuid4

from scripts.verification import (
    EVIDENCE,
    ROOT,
    UV,
    deterministic_env,
    digest,
    gate_lock,
    run_command,
    source_manifest,
    write_new,
)


def main():
    attempt = EVIDENCE / (
        datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-wrong-success-" + uuid4().hex[:8]
    )
    attempt.mkdir(parents=True)
    env = deterministic_env()
    env["ORBA_TEST_EVIDENCE_DIR"] = str(attempt)
    log = attempt / "wrong-success.log"
    with gate_lock():
        result = run_command(
            "real-pg-wrong-success-assertion",
            UV + ["pytest", "-q", "tests/experiments/pm_failed_run_success_experiment.py"],
            ROOT,
            env,
            log,
            120,
        )
    output = log.read_text(encoding="utf-8", errors="replace")
    detected = (
        result["exit_code"] == 1
        and "assert 'failed' == 'succeeded'" in output
        and "1 failed" in output
    )
    receipt = {
        "version": 1,
        "execution_class": "expected_failure_experiment",
        "scenario": "Deliberately incorrect assertion expects persisted failed run to succeed",
        "provider_call": False,
        "database": "real guarded orba_test PostgreSQL",
        "source": source_manifest(),
        "command": result,
        "expected_native_exit_code": 1,
        "false_success_assertion_detected": detected,
        "log_sha256": digest(log),
    }
    write_new(attempt / "experiment.json", receipt)
    print(f"Expected-failure detection={detected}; native exit={result['exit_code']}; {attempt}")
    # Preserve native1. An unexpected native0 is a failed experiment, not success.
    return result["exit_code"] or 2


if __name__ == "__main__":
    raise SystemExit(main())

"""Record the genuinely failing assertion separately from mandatory green tests."""

import json
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from uuid import uuid4

from scripts import orchestration_verification as gates
from scripts import verification as base


def main():
    attempt = gates.EVIDENCE / (
        datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-expected-failure-" + uuid4().hex[:8]
    )
    attempt.mkdir(parents=True)
    argv = base.UV + [
        "pytest",
        "tests/experiments/orchestration_completion_experiment.py",
        "-q",
        "-s",
        f"--junitxml={attempt / 'experiment.xml'}",
    ]
    with base.gate_lock(gates.EVIDENCE):
        row = base.run_command(
            "isolated-incorrect-completion",
            argv,
            base.ROOT,
            base.deterministic_env(),
            attempt / "experiment.log",
            120,
        )
    cases = ET.parse(attempt / "experiment.xml").getroot().findall(".//testcase")
    output = (attempt / "experiment.log").read_text(encoding="utf-8")
    expected = (
        row["exit_code"] == 1
        and len(cases) == 1
        and cases[0].find("failure") is not None
        and "ACTUAL_EVIDENCE" in output
        and "execution_status=awaiting_executor execution_performed=False" in output
        and "DELIBERATELY INCORRECT" in output
    )
    receipt = {
        "stage": gates.STAGE,
        "recorded_at": base.utc(),
        "execution_class": "isolated_expected_failure_no_executor",
        "source": base.source_manifest(),
        "command": row,
        "expected_child_exit_code": 1,
        "expected_failure_observed": expected,
        "production_test_pass": False,
        "artifacts": {file.name: base.digest(file) for file in attempt.iterdir() if file.is_file()},
    }
    base.write_new(attempt / "receipt.json", receipt)
    print(
        json.dumps(
            {
                "actual_pytest_exit_code": row["exit_code"],
                "expected_failure_observed": expected,
                "receipt": str(attempt / "receipt.json"),
            }
        )
    )
    return 0 if expected else 1


if __name__ == "__main__":
    raise SystemExit(main())

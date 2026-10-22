"""Run the isolated wrong-success assertion; preserve its genuine nonzero exit."""

import json
import re
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from uuid import uuid4

from scripts import verification as base


def main():
    attempt = (
        base.ROOT
        / "docs/evidence/stage04"
        / (datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-expected-failure-" + uuid4().hex[:8])
    )
    attempt.mkdir(parents=True)
    argv = base.UV + [
        "pytest",
        "tests/experiments/architect_failed_run_success_experiment.py",
        "-q",
        "-s",
        f"--junitxml={attempt / 'experiment.xml'}",
    ]
    with base.gate_lock():
        row = base.run_command(
            "isolated-incorrect-success",
            argv,
            base.ROOT,
            base.deterministic_env(),
            attempt / "experiment.log",
            120,
        )
    tests = ET.parse(attempt / "experiment.xml").getroot().findall(".//testcase")
    output = (attempt / "experiment.log").read_text(encoding="utf-8")
    expected = (
        row["exit_code"] == 1
        and len(tests) == 1
        and tests[0].find("failure") is not None
        and "DELIBERATELY INCORRECT" in output
        and re.search(
            r"ACTUAL_EVIDENCE run_id=[a-f0-9-]+ status=failed architectures=0 provider_double=True",
            output,
        )
        is not None
    )
    receipt = {
        "stage": "stage04-architect",
        "execution_class": "isolated_expected_failure_controlled_provider",
        "recorded_at": base.utc(),
        "source": base.source_manifest(),
        "command": row,
        "expected_child_exit_code": 1,
        "expected_failure_observed": expected,
        "production_test_pass": False,
        "artifacts": {p.name: base.digest(p) for p in attempt.iterdir() if p.is_file()},
    }
    base.write_new(attempt / "receipt.json", receipt)
    print(
        json.dumps(
            {
                "actual_child_exit_code": row["exit_code"],
                "expected_failure_observed": expected,
                "receipt": str(attempt / "receipt.json"),
            }
        )
    )
    return 0 if expected else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Independent Stage05B gates: real local scheduler and protocol client, zero models."""

import argparse
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from uuid import uuid4

from scripts import orchestration_verification as foundation
from scripts import verification as base

EVIDENCE = base.ROOT / "docs/evidence/stage05b"
BASELINE = base.ROOT / "apps/api/scripts/scheduler_verification_baseline.json"
STAGE = "stage05b-scheduler"
CREDENTIAL_RACE_FILES = (
    "workspace-race.json",
    "task_fk-race.json",
    "worker-race.json",
    "credential-race.json",
    "revoke-race.json",
    "disable-race.json",
    "rotate-race.json",
    "replay-race.json",
    "recovery-race.json",
    "acknowledge-race.json",
    "release-race.json",
    "heartbeat-race.json",
)


def contract():
    from orba.scheduler_schemas import HandoffManifest, SchedulerPolicy
    from scripts.scheduler_proof import SchedulerProof

    return {
        "stage": STAGE,
        "proof_version": 1,
        "proof_schema_sha256": hashlib.sha256(
            json.dumps(SchedulerProof.model_json_schema(), sort_keys=True).encode()
        ).hexdigest(),
        "handoff_schema_sha256": hashlib.sha256(
            json.dumps(HandoffManifest.model_json_schema(), sort_keys=True).encode()
        ).hexdigest(),
        "policy": SchedulerPolicy().model_dump(mode="json"),
        "source_contract": foundation.contract(),
        "model_generation_requests": 0,
        "executor_available": False,
        "execution_performed": False,
        "automatic_retries": 0,
        "backend_diagnostics": {"durations": 25, "stall_dump_seconds": 60},
        "credential_publication_guard": "post-lock-and-final-db-clock-v1",
        "credential_race_artifacts": list(CREDENTIAL_RACE_FILES),
        "workers": 1,
        "database": "guarded local orba_test",
    }


def deterministic_env():
    env = base.deterministic_env()
    env["PYTEST_ADDOPTS"] = "--durations=25 -o faulthandler_timeout=60"
    policy = contract()["policy"]
    for suffix, field in {
        "ACK_SECONDS": "acknowledge_seconds",
        "LEASE_SECONDS": "lease_seconds",
        "MAX_LEASE_SECONDS": "max_lease_seconds",
        "HEARTBEAT_SECONDS": "heartbeat_seconds",
        "LIVENESS_SECONDS": "worker_liveness_seconds",
        "GLOBAL_CAPACITY": "global_capacity",
        "RUN_CAPACITY": "run_capacity",
        "MAX_ATTEMPTS": "max_attempts",
        "BATCH_SIZE": "batch_size",
    }.items():
        env["ORBA_SCHEDULER_" + suffix] = str(policy[field])
    return env


def commands(gate, attempt):
    if gate == "A":
        # All prior commands remain. Additional PG protocol/race/deadline tests
        # need a bounded larger suite envelope; application lease limits do not change.
        # The measured cold ESLint scan also exceeds the old180s envelope here.
        # Core reached only46/60 cases before its old900s command deadline on this
        # host. Its full two-account journey also exceeded the old30s case budget.
        # Bound the full core command at1500s; keep its locator/HTTP limits intact.
        # Rules/assertions/retries are unchanged; only bounded command supervision differs.
        # A later full backend command reached1200s without an assertion failure.
        # Its isolated93scheduler cases completed normally in315s (previous217s),
        # including the suspected cutoff case in4.17s. Allow the aggregate suite
        # 1800s while retaining actual per-test durations and a60s stall dump.
        # The21 orchestration journeys each build and approve real PRD/architecture
        # sources. The measured first12 cases took almost900s; a later90s case
        # deadline expired even with the expected real ledger visible. Their total
        # is now180s, with explicit30s actions/navigation and unchanged5s assertions.
        # Allow21*180s plus210s startup/reporting for the finite full command.
        previous = [
            (
                name,
                argv,
                {
                    "backend": 1800,
                    "eslint": 600,
                    "core-browser": 1500,
                    "orchestration-browser": 3990,
                }.get(name, timeout),
            )
            for name, argv, timeout in foundation.commands("A", attempt)
        ]
        return previous + [("scheduler-browser", base.NPM + ["test:e2e:scheduler"], 1800)]
    return [("local-browser", base.NPM + ["test:e2e:scheduler:local"], 600)]


def live_local_proof(attempt):
    from scripts.scheduler_proof import validate_proof

    try:
        proof = json.loads((attempt / "scheduler-proof.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise base.EvidenceError("Local B proof JSON is missing or malformed.") from None
    return validate_proof(proof)


def results_for(gate, attempt):
    if gate == "B":
        from scripts.scheduler_proof import ProcessCommand

        proof = live_local_proof(attempt)
        if proof["final_api"]["policy"] != contract()["policy"]:
            raise base.EvidenceError(
                "Gate B runtime policy differs from the Gate A-bound contract."
            )
        for row in proof["process_commands"]:
            receipt = attempt / (row["receipt_id"] + "-process.json")
            log = attempt / (row["receipt_id"] + "-process.log")
            if not log.is_file() or ProcessCommand.model_validate_json(
                receipt.read_text(encoding="utf-8")
            ) != ProcessCommand.model_validate_json(json.dumps(row)):
                raise base.EvidenceError("Native process journal differs from worker proof.")
        return {
            "local-browser": base.playwright_report(
                attempt / "local-browser.json",
                minimum=1,
                projects={"chromium-scheduler-control-plane": 1},
            ),
            "local-proof": proof,
        }
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    result = foundation.results_for("A", attempt)
    result["backend"] = base.junit_report(attempt / "backend.xml", baseline["backend"])
    result["scheduler-browser"] = base.playwright_report(
        attempt / "scheduler-browser.json",
        required=baseline["scheduler_browser"],
        minimum=len(baseline["scheduler_browser"]),
        projects={device: 1 for device in ("chromium", "mobile", "tablet")},
    )
    if any(not (attempt / name).is_file() for name in CREDENTIAL_RACE_FILES):
        raise base.EvidenceError(
            "Required real PostgreSQL credential race diagnostics are missing."
        )
    return result


def latest(gate):
    pointer = json.loads((EVIDENCE / f"latest-{gate}.json").read_text(encoding="utf-8"))
    path = (EVIDENCE / pointer["receipt"]).resolve()
    if not path.is_relative_to(EVIDENCE.resolve()) or base.digest(path) != pointer["sha256"]:
        raise base.EvidenceError(
            "Stage05B receipt pointer changed or escaped its evidence directory."
        )
    return path


def validate(path, gate, current=None):
    path = path.resolve()
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        value.get("stage") != STAGE
        or value.get("gate") != gate
        or value.get("result") != "PASS"
        or type(value.get("exit_code")) is not int
        or value["exit_code"] != 0
        or json.dumps(value.get("verification_contract"), sort_keys=True)
        != json.dumps(contract(), sort_keys=True)
        or value.get("execution_class")
        != ("deterministic" if gate == "A" else "real_local_worker_protocol")
    ):
        raise base.EvidenceError("Stage05B requires an applicable passing receipt for this gate.")
    if json.dumps(value.get("source_start"), sort_keys=True) != json.dumps(
        value.get("source_end"), sort_keys=True
    ) or json.dumps(value["source_end"], sort_keys=True) != json.dumps(
        current or base.source_manifest(), sort_keys=True
    ):
        raise base.EvidenceError("Stage05B receipt source fingerprint is stale.")
    expected, actual = commands(gate, path.parent), value["commands"]
    if len(expected) != len(actual) or any(
        row.get("name") != name
        or row.get("argv") != argv
        or type(row.get("exit_code")) is not int
        or row["exit_code"] != 0
        for row, (name, argv, _) in zip(actual, expected, strict=True)
    ):
        raise base.EvidenceError("Required commands or their actual zero exits are missing.")
    required = {row["name"] + ".log" for row in actual} | (
        {
            "backend.xml",
            "core-browser.json",
            "controlled-browser.json",
            "architect-browser.json",
            "navigation-browser.json",
            "orchestration-browser.json",
            "scheduler-browser.json",
        }
        if gate == "A"
        else {"local-browser.json", "scheduler-proof.json"}
    )
    if gate == "A":
        required |= set(CREDENTIAL_RACE_FILES)
    if gate == "B":
        proof = live_local_proof(path.parent)
        required |= {
            row["receipt_id"] + suffix
            for row in proof["process_commands"]
            for suffix in ("-process.json", "-process.log")
        }
    if not required <= value["artifacts"].keys():
        raise base.EvidenceError("Required verification artifacts are missing.")
    for name, digest in value["artifacts"].items():
        artifact = (path.parent / name).resolve()
        if (
            not artifact.is_relative_to(path.parent)
            or not artifact.is_file()
            or base.digest(artifact) != digest
        ):
            raise base.EvidenceError("A receipt-bound artifact changed or is missing.")
    if json.dumps(value.get("results"), sort_keys=True) != json.dumps(
        results_for(gate, path.parent), sort_keys=True
    ):
        raise base.EvidenceError("Parsed real test evidence differs from its receipt.")
    if gate == "B":
        a = latest("A")
        validate(a, "A", current)
        if value.get("gate_a_receipt") != str(a.relative_to(EVIDENCE)) or value.get(
            "gate_a_receipt_sha256"
        ) != base.digest(a):
            raise base.EvidenceError("Local B is not bound to the applicable Gate A receipt.")
        times = [
            value["started_at"],
            actual[0]["started_at"],
            value["results"]["local-proof"]["started_at"],
            value["results"]["local-proof"]["foundation"]["initial_sql"]["created_at"],
            value["results"]["local-proof"]["completed_at"],
            actual[0]["completed_at"],
            value["completed_at"],
        ]
        moments = [datetime.fromisoformat(time) for time in times]
        if any(time.tzinfo is None for time in moments) or moments != sorted(moments):
            raise base.EvidenceError(
                "Local B proof does not belong to its actual command interval."
            )
    return value


def execute(gate):
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    attempt = EVIDENCE / (
        datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + f"-{gate}-" + uuid4().hex[:8]
    )
    attempt.mkdir()
    value = {
        "stage": STAGE,
        "gate": gate,
        "execution_class": "deterministic" if gate == "A" else "real_local_worker_protocol",
        "verification_contract": contract(),
        "started_at": base.utc(),
        "commands": [],
        "result": "BLOCKED",
        "exit_code": 2,
    }
    base.write_new(attempt / "attempt.json", value)
    try:
        with base.gate_lock(EVIDENCE):
            value["source_start"] = base.source_manifest()
            value["git_head"] = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=base.ROOT, text=True
            ).strip()
            if gate == "B":
                a = latest("A")
                validate(a, "A")
                value.update(
                    gate_a_receipt=str(a.relative_to(EVIDENCE)),
                    gate_a_receipt_sha256=base.digest(a),
                )
            env = deterministic_env()
            env.update(
                ORBA_TEST_EVIDENCE_DIR=str(attempt),
                ORBA_ARCHITECT_LIVE_OPT_IN="",
                ORBA_LIVE_OPT_IN="",
            )
            base.ports_available()
            value["result"] = "FAIL"
            for name, argv, timeout in commands(gate, attempt):
                child_env = dict(env)
                if name == "backend":
                    child_env["ORBA_CREDENTIAL_RACE_EVIDENCE_DIR"] = str(attempt)
                if name.endswith("browser"):
                    child_env["PLAYWRIGHT_JSON_OUTPUT_NAME"] = str(attempt / f"{name}.json")
                row = base.run_command(
                    name, argv, base.ROOT, child_env, attempt / f"{name}.log", timeout
                )
                value["commands"].append(row)
                value["exit_code"] = row["exit_code"]
                # Preserve each native result even if a later process/host interruption
                # prevents final receipt publication. A journal is not a passing gate.
                base.write_new(attempt / f"{name}-command.json", row)
                if row["exit_code"]:
                    break
            else:
                value["results"] = results_for(gate, attempt)
                if value["source_start"] != base.source_manifest():
                    raise base.EvidenceError("Implementation changed during verification.")
                value.update(result="PASS", exit_code=0)
    except KeyboardInterrupt:
        value.update(result="FAIL", exit_code=130, reason="interrupted")
    except (
        base.EvidenceError,
        OSError,
        ValueError,
        KeyError,
        TypeError,
        ET.ParseError,
        subprocess.SubprocessError,
    ) as exc:
        value.update(
            exit_code=value["exit_code"] or 1,
            reason=str(exc) if isinstance(exc, base.EvidenceError) else type(exc).__name__,
        )
    finally:
        value["completed_at"] = base.utc()
        try:
            value["source_end"] = base.source_manifest()
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            # An unavailable final fingerprint must fail closed without erasing
            # native command failures already observed and journaled.
            value.update(
                result="FAIL",
                exit_code=value["exit_code"] or 1,
                source_end=None,
                source_end_error={
                    "category": type(exc).__name__,
                    "exit_code": getattr(exc, "returncode", None),
                },
            )
        value["artifacts"] = {
            str(file.relative_to(attempt)): base.digest(file)
            for file in sorted(attempt.rglob("*"))
            if file.is_file()
        }
        path = attempt / "receipt.json"
        base.write_new(path, value)
        temporary = EVIDENCE / f"latest-{gate}-{uuid4().hex}.tmp"
        temporary.write_text(
            json.dumps({"receipt": str(path.relative_to(EVIDENCE)), "sha256": base.digest(path)})
            + "\n",
            encoding="utf-8",
        )
        temporary.replace(EVIDENCE / f"latest-{gate}.json")
    print(
        json.dumps(
            {
                "gate": gate,
                "result": value["result"],
                "exit_code": value["exit_code"],
                "reason": value.get("reason"),
                "receipt": str(path),
            }
        )
    )
    return value["exit_code"]


def summary():
    current, gates = base.source_manifest(), {}
    for gate in ("A", "B"):
        try:
            path = latest(gate)
            validate(path, gate, current)
            gates[gate] = {
                "result": "PASS",
                "receipt": str(path.relative_to(EVIDENCE)),
                "sha256": base.digest(path),
            }
        except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as exc:
            gates[gate] = {
                "result": "NOT VERIFIED",
                "reason": str(exc) if isinstance(exc, base.EvidenceError) else type(exc).__name__,
            }
    verdict = "VERIFIED" if all(gate["result"] == "PASS" for gate in gates.values()) else "PARTIAL"
    result = {
        "stage": STAGE,
        "recorded_at": base.utc(),
        "source": current,
        "gates": gates,
        "verdict": verdict,
        "overall_stage05": "IN PROGRESS",
        "execution_performed": False,
        "model_generation_requests": 0,
    }
    base.write_new(EVIDENCE / f"summary-{uuid4().hex}.json", result)
    print(json.dumps(result | {"source": current["sha256"]}, indent=2))
    return 0 if verdict == "VERIFIED" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gate", choices=["A", "B", "C"])
    args = parser.parse_args()
    return summary() if args.gate == "C" else execute(args.gate)


if __name__ == "__main__":
    raise SystemExit(main())

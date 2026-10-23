"""Independent Stage05A A/B/C gates. Both gates are local and dispatch zero models."""

import argparse
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from uuid import uuid4

from scripts import architect_verification as prior
from scripts import verification as base

EVIDENCE = base.ROOT / "docs/evidence/stage05a"
BASELINE = base.ROOT / "apps/api/scripts/orchestration_verification_baseline.json"
STAGE = "stage05a-orchestration"


def contract():
    from orba.orchestration_schemas import GraphRead, RunCreate, RunDetail
    from orba.orchestration_service import HASH_VERSION, TRANSITIONS
    from scripts.orchestration_proof import PROOF_VERSION, LocalProof

    return {
        "stage": STAGE,
        "proof_version": PROOF_VERSION,
        "proof_schema_sha256": hashlib.sha256(
            json.dumps(LocalProof.model_json_schema(), sort_keys=True).encode()
        ).hexdigest(),
        "hash_version": HASH_VERSION,
        "edge_convention": "prerequisite -> dependent",
        "transitions": {key: sorted(value) for key, value in TRANSITIONS.items()},
        "schema_sha256": hashlib.sha256(
            json.dumps(
                [schema.model_json_schema() for schema in (RunCreate, RunDetail, GraphRead)],
                sort_keys=True,
            ).encode()
        ).hexdigest(),
        "model_generation_requests": 0,
        "executor_available": False,
        "execution_performed": False,
        "database": "guarded local orba_test",
        "workers": 1,
        "automatic_retries": 0,
    }


def commands(gate, attempt):
    if gate == "A":
        return prior.commands("A", attempt) + [
            ("orchestration-browser", base.NPM + ["test:e2e:orchestration"], 900)
        ]
    return [("local-browser", base.NPM + ["test:e2e:orchestration:local"], 600)]


def live_local_proof(attempt):
    from scripts.orchestration_proof import validate_proof

    try:
        proof = json.loads((attempt / "local-proof.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise base.EvidenceError("Local B proof JSON is missing or malformed.") from None
    return validate_proof(proof)


def results_for(gate, attempt):
    if gate == "B":
        return {
            "local-browser": base.playwright_report(
                attempt / "local-browser.json",
                minimum=1,
                projects={"chromium-local-control-plane": 1},
            ),
            "local-proof": live_local_proof(attempt),
        }
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    result = {"backend": base.junit_report(attempt / "backend.xml", baseline["backend"])}
    for name, key in (
        ("core-browser", "core_browser"),
        ("controlled-browser", "controlled_browser"),
        ("architect-browser", "architect_browser"),
        ("navigation-browser", "navigation_browser"),
        ("orchestration-browser", "orchestration_browser"),
    ):
        result[name] = base.playwright_report(
            attempt / f"{name}.json",
            required=baseline[key],
            minimum=len(baseline[key]),
            projects={device: 1 for device in ("chromium", "mobile", "tablet")},
        )
    return result


def latest(gate):
    pointer = json.loads((EVIDENCE / f"latest-{gate}.json").read_text(encoding="utf-8"))
    path = (EVIDENCE / pointer["receipt"]).resolve()
    if not path.is_relative_to(EVIDENCE.resolve()) or base.digest(path) != pointer["sha256"]:
        raise base.EvidenceError(
            "Stage05A receipt pointer changed or escaped its evidence directory."
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
        != ("deterministic" if gate == "A" else "real_local_control_plane")
    ):
        raise base.EvidenceError("Stage05A requires an applicable passing receipt for this gate.")
    if json.dumps(value.get("source_start"), sort_keys=True) != json.dumps(
        value.get("source_end"), sort_keys=True
    ) or json.dumps(value["source_end"], sort_keys=True) != json.dumps(
        current or base.source_manifest(), sort_keys=True
    ):
        raise base.EvidenceError("Stage05A receipt source fingerprint is stale.")
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
        }
        if gate == "A"
        else {"local-browser.json", "local-proof.json"}
    )
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
            value["results"]["local-proof"]["initial_sql"]["created_at"],
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
        "execution_class": "deterministic" if gate == "A" else "real_local_control_plane",
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
            env = base.deterministic_env()
            env.update(
                ORBA_TEST_EVIDENCE_DIR=str(attempt),
                ORBA_ARCHITECT_LIVE_OPT_IN="",
                ORBA_LIVE_OPT_IN="",
            )
            base.ports_available()
            value["result"] = "FAIL"
            for name, argv, timeout in commands(gate, attempt):
                child_env = dict(env)
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

"""Unpaid Phase1/navigation verification with immutable receipts and no live opt-in."""

import argparse
import json
import re
from datetime import UTC, datetime
from uuid import uuid4

from scripts import architect_verification as stage
from scripts import verification as base


def preflight_result(attempt):
    report = base.playwright_report(
        attempt / "preflight-browser.json",
        minimum=1,
        projects={"chromium-architect-preflight": 1},
    )
    proof = json.loads((attempt / "preflight-proof.json").read_text(encoding="utf-8"))
    validate_preflight(proof)
    return {"browser": report, "preflight": proof}


def validate_preflight(proof):
    sql = proof.get("final_sql", {})
    validate_source_identity(proof, sql)
    if (
        proof.get("execution_class") != "no_generation_preflight"
        or proof.get("result") != "PASS"
        or proof.get("approved_source_reloaded") is not True
        or proof.get("provider_readiness_verified") is not False
        or proof.get("generation_budget") != {"attempted": 0, "forwarded": 0, "blocked": 0}
        or proof.get("server_boundary")
        != {
            "execution_class": "no_generation_test_boundary",
            "provider_readiness_verified": False,
            "blocked_generation_posts": 0,
            "provider_dependency_entries": 0,
        }
        or sql.get("state") != "approved"
        or sql.get("document_validated") is not True
        or not sql.get("approved_at")
        or sql.get("approved_by") != proof.get("actor_id")
        or sql.get("plan_id") != proof.get("source_plan_id")
        or sql.get("project_id") != proof.get("project_id")
        or sql.get("workspace_id") != proof.get("workspace_id")
        or sql.get("version") != proof.get("source_version")
        or sql.get("revision") != proof.get("source_revision")
        or sql.get("content_hash") != proof.get("source_hash")
        or sql.get("current_approved_plan_id") != proof.get("source_plan_id")
        or sql.get("generation_records")
        != {
            "product_manager_runs": 0,
            "architect_runs": 0,
            "architecture_versions": 0,
            "engineering_tasks": 0,
            "task_dependencies": 0,
        }
    ):
        raise base.EvidenceError(
            "Unpaid preflight source, approval or zero-generation proof failed."
        )
    required = [
        "project_post_received",
        "exact_project_loaded",
        "authored_draft_persisted",
        "exact_draft_visible",
        "approval_http_response",
        "approval_independently_verified",
        "architect_entry_reached_without_generation",
    ]
    events = [row.get("event") for row in proof.get("milestones", [])]
    if any(event not in events for event in required) or [
        events.index(e) for e in required
    ] != sorted(events.index(e) for e in required):
        raise base.EvidenceError("Unpaid preflight milestones are incomplete or out of order.")


def validate_source_identity(proof, sql):
    """Missing values must never compare equal and certify an unidentified artifact."""
    identities = ("project_id", "workspace_id", "actor_id", "source_plan_id")
    if (
        any(not isinstance(proof.get(key), str) or not proof[key] for key in identities)
        or any(
            type(proof.get(key)) is not int or proof[key] < 1
            for key in ("source_version", "source_revision")
        )
        or not isinstance(proof.get("source_hash"), str)
        or re.fullmatch(r"[a-f0-9]{64}", proof["source_hash"]) is None
        or any(
            sql.get(target) != proof[key]
            for key, target in (
                ("project_id", "project_id"),
                ("workspace_id", "workspace_id"),
                ("actor_id", "approved_by"),
                ("source_plan_id", "plan_id"),
                ("source_version", "version"),
                ("source_revision", "revision"),
                ("source_hash", "content_hash"),
            )
        )
    ):
        raise base.EvidenceError(
            "Exact nonempty source identity/version/revision/hash is required."
        )


def navigation_result(attempt):
    baseline = json.loads(stage.BASELINE.read_text(encoding="utf-8"))
    report = base.playwright_report(
        attempt / "navigation-browser.json",
        required=baseline["navigation_browser"],
        minimum=len(baseline["navigation_browser"]),
        projects={key: 13 for key in ("chromium", "mobile", "tablet")},
    )
    proofs = list(attempt.glob("navigation-*.json"))
    proofs = [p for p in proofs if p.name != "navigation-browser.json"]
    if len(proofs) != report["passed"]:
        raise base.EvidenceError("Each navigation case needs its own safe milestone evidence.")
    for path in proofs:
        proof = json.loads(path.read_text(encoding="utf-8"))
        server = proof.get("server_boundary", {})
        if (
            proof.get("case_result") != "PASS"
            or proof.get("generation_budget") != {"attempted": 0, "forwarded": 0, "blocked": 0}
            or server.get("provider_dependency_entries") != 0
            or server.get("provider_readiness_verified") is not False
        ):
            raise base.EvidenceError("Navigation case did not pass with zero generation dispatch.")
    return report


def execute(mode="preflight"):
    attempt = stage.EVIDENCE / (
        datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + f"-unpaid-{mode}-" + uuid4().hex[:8]
    )
    attempt.mkdir(parents=True)
    value = {
        "stage": stage.STAGE,
        "execution_class": "no_generation_preflight"
        if mode == "preflight"
        else "no_generation_navigation_regression",
        "started_at": base.utc(),
        "commands": [],
        "result": "FAIL",
        "exit_code": 1,
        "paid_authorized": False,
        "live_generation_verified": False,
    }
    try:
        with base.gate_lock(stage.EVIDENCE):
            value["source_start"] = base.source_manifest()
            env = base.deterministic_env()
            env["ORBA_TEST_EVIDENCE_DIR"] = str(attempt)
            base.ports_available()
            name = "preflight-browser" if mode == "preflight" else "navigation-browser"
            script = (
                "test:e2e:architect:preflight" if mode == "preflight" else "test:e2e:navigation"
            )
            env["PLAYWRIGHT_JSON_OUTPUT_NAME"] = str(attempt / f"{name}.json")
            commands = [
                (
                    "database",
                    [
                        "docker",
                        "compose",
                        "-f",
                        "infra/compose.yaml",
                        "--profile",
                        "test",
                        "up",
                        "-d",
                        "--wait",
                        "test-postgres",
                    ],
                    180,
                ),
                (name, base.NPM + [script], 900 if mode == "navigation" else 180),
            ]
            for name, argv, timeout in commands:
                row = base.run_command(name, argv, base.ROOT, env, attempt / f"{name}.log", timeout)
                value["commands"].append(row)
                value["exit_code"] = row["exit_code"]
                if row["exit_code"]:
                    break
            else:
                value["results"] = (
                    preflight_result(attempt) if mode == "preflight" else navigation_result(attempt)
                )
                value["source_end"] = base.source_manifest()
                if value["source_start"] != value["source_end"]:
                    raise base.EvidenceError("Source changed during unpaid verification.")
                value.update(result="PASS", exit_code=0)
    except KeyboardInterrupt:
        value.update(result="FAIL", exit_code=130, reason="interrupted")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        value.update(
            result="FAIL",
            exit_code=value["exit_code"] or 1,
            reason=str(exc) if isinstance(exc, base.EvidenceError) else type(exc).__name__,
        )
    finally:
        value["completed_at"] = base.utc()
        value.setdefault("source_end", base.source_manifest())
        value["artifacts"] = {
            str(p.relative_to(attempt)): base.digest(p) for p in attempt.rglob("*") if p.is_file()
        }
        base.write_new(attempt / "receipt.json", value)
    print(
        json.dumps(
            {
                "mode": mode,
                "result": value["result"],
                "exit_code": value["exit_code"],
                "receipt": str(attempt / "receipt.json"),
                "reason": value.get("reason"),
                "live_generation_verified": False,
            }
        )
    )
    return value["exit_code"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("preflight", "navigation"), default="preflight")
    return execute(parser.parse_args().mode)


if __name__ == "__main__":
    raise SystemExit(main())

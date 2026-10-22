"""Stage04 gates reuse the existing command runner; no paid dispatch without opt-in."""

import argparse
import hashlib
import json
import os
import re
from contextlib import contextmanager
from uuid import uuid4

from scripts import verification as base

EVIDENCE = base.ROOT / "docs/evidence/stage04"
BASELINE = base.ROOT / "apps/api/scripts/architect_verification_baseline.json"
ORIGINAL_COMMANDS, ORIGINAL_RESULTS = base.commands, base.results_for
STAGE = "stage04-architect"


def contract():
    from orba.architect_provider import PROMPT_HASH, PROMPT_VERSION, output_schema
    from orba.architect_schemas import ArchitectureDocument
    from orba.pm_models_policy import APPROVED_MODELS
    from orba.pm_schemas import canonical

    return {
        "stage": STAGE,
        "prompt_version": PROMPT_VERSION,
        "prompt_sha256": PROMPT_HASH,
        "schema_sha256": hashlib.sha256(
            canonical(ArchitectureDocument.model_json_schema()).encode()
        ).hexdigest(),
        "provider_schema_sha256": hashlib.sha256(canonical(output_schema()).encode()).hexdigest(),
        "edge_convention": "prerequisite -> dependent",
        "execution_performed": False,
        "reviewed_model_policy": {
            item.identifier: list(item.thinking_levels) for item in APPROVED_MODELS
        },
    }


def profile():
    import importlib.metadata

    from orba.config import Settings

    config = Settings()
    selected = config.architect_settings()
    return contract() | {
        "provider": "google-gemini",
        "model": selected.pm_model,
        "thinking_level": selected.pm_thinking_level,
        "max_output_tokens": selected.pm_max_output_tokens,
        "max_input_bytes": selected.pm_max_input_bytes,
        "server_timeout_seconds": selected.pm_timeout_seconds,
        "transport_timeout_seconds": selected.pm_timeout_seconds + 5,
        "envelope_timeout_seconds": selected.pm_timeout_seconds + 10,
        "max_concurrent": config.pm_max_concurrent,
        "sdk_version": importlib.metadata.version("google-genai"),
        "credential_configured": selected.pm_configured,
        "workers": 1,
        "generation_request_limit": 1,
        "automatic_retries": 0,
    }


def commands(gate, attempt):
    if gate == "A":
        return ORIGINAL_COMMANDS("A", attempt) + [
            ("architect-browser", base.NPM + ["test:e2e:architect"], 900),
            ("navigation-browser", base.NPM + ["test:e2e:navigation"], 900),
        ]
    return [
        (
            "architect-readiness",
            base.UV + ["python", "-m", "scripts.check_architect_config", "--check-model"],
            45,
        ),
        ("live-browser", base.NPM + ["test:e2e:architect:live"], 600),
    ]


def require_live_identity(audit, selected):
    returned = audit.get("returned_model")
    if (
        audit.get("requested_model") != selected["model"]
        or not isinstance(returned, str)
        or not re.fullmatch(r"(?:models/)?gemini-[A-Za-z0-9][A-Za-z0-9._-]*", returned)
        or (audit.get("diagnostic") or {}).get("provider_double")
    ):
        raise base.EvidenceError("Live provider identity is missing or controlled.")


def require_live_setup(proof):
    """Phase1 success never substitutes for generation; it must precede its one dispatch."""
    setup = proof.get("preflight", {})
    sql = setup.get("final_sql", {})
    expected = {
        "project_id": proof.get("project_id"),
        "workspace_id": setup.get("workspace_id"),
        "plan_id": proof.get("source_plan_id"),
        "version": proof.get("source_version"),
        "revision": proof.get("source_revision"),
        "content_hash": proof.get("source_hash"),
        "approved_by": proof.get("initiator_id"),
        "current_approved_plan_id": proof.get("source_plan_id"),
    }
    if (
        setup.get("result") != "PASS"
        or setup.get("approved_source_reloaded") is not True
        or setup.get("step") != "architect_entry_reached_without_generation"
        or proof.get("preflight_generation_budget")
        != {"attempted": 0, "forwarded": 0, "blocked": 0}
        or proof.get("unrelated_generation_budget")
        != {"attempted": 0, "forwarded": 0, "blocked": 0}
        or [p.get("phase") for p in proof.get("phases", [])]
        != ["preflight", "generation", "post_generation"]
        or sql.get("state") != "approved"
        or sql.get("document_validated") is not True
        or not sql.get("approved_at")
        or any(not value or sql.get(key) != value for key, value in expected.items())
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
            "Live Architect phases lack exact approved-source/zero-dispatch setup."
        )


def live_results(attempt):
    browser = base.playwright_report(
        attempt / "live-browser.json", minimum=1, projects={"chromium-architect-live": 1}
    )
    proof = json.loads((attempt / "live-proof.json").read_text())
    if (
        proof.get("stage") != STAGE
        or proof.get("execution_class") != "real_gemini_browser"
        or proof.get("provider_double") is not False
        or proof.get("result") != "PASS"
        or proof.get("generation_budget") != {"attempted": 1, "forwarded": 1, "blocked": 0}
        or proof.get("pm_generation_posts") != 0
    ):
        raise base.EvidenceError(
            "Architect B requires exactly one genuine successful Architect browser flow; no PM generation or controlled response."
        )
    require_live_setup(proof)
    selected = profile()
    for key, state, revision in (("draft_sql", "draft", 1), ("approved_sql", "approved", 2)):
        audit = proof[key]
        counts = audit.get("counts", {})
        config = (audit.get("diagnostic") or {}).get("generation_configuration", {})
        if (
            audit.get("status") != "succeeded"
            or audit.get("architecture_validated") is not True
            or audit.get("graph_valid") is not True
            or audit.get("coverage_approvable") is not True
            or audit.get("execution_performed") is not False
            or audit.get("state") != state
            or audit.get("revision") != revision
        ):
            raise base.EvidenceError(
                "Independent architecture SQL validation/state evidence is incomplete."
            )
        if (
            any(
                audit.get(k) != proof.get(k)
                for k in (
                    "project_id",
                    "initiator_id",
                    "source_plan_id",
                    "source_version",
                    "source_revision",
                    "source_hash",
                    "requested_model",
                    "returned_model",
                    "provider_response_id",
                    "usage",
                )
            )
            or audit.get("id") != proof.get("run_id")
            or audit.get("architecture_id") != proof.get("architecture_id")
        ):
            raise base.EvidenceError("API, source, run and independent SQL metadata differ.")
        require_live_identity(audit, selected)
        if (
            any(
                config.get(k) != selected[k]
                for k in (
                    "thinking_level",
                    "max_input_bytes",
                    "max_output_tokens",
                    "provider_schema_sha256",
                )
            )
            or not 0 < config.get("input_bytes", 0) <= selected["max_input_bytes"]
        ):
            raise base.EvidenceError("Live request configuration differs from its receipt.")
        # Edgeless DAGs are valid. Require nodes/traces, never min(all counts)>0.
        if (
            counts.get("engineering_tasks", 0) < 1
            or counts.get("architecture_components", 0) < 1
            or counts.get("requirement_traces", 0) < 1
            or counts.get("task_dependencies", -1) < 0
        ):
            raise base.EvidenceError("Independent relational records are missing.")
        if audit.get("content_hash") != proof.get(
            "draft_api_hash" if state == "draft" else "approved_api_hash"
        ):
            raise base.EvidenceError("API and independently assembled SQL hashes differ.")
    approved = proof["approved_sql"]
    if (
        approved.get("approved_by") != proof["initiator_id"]
        or not approved.get("approved_at")
        or proof.get("unrelated_http_status") != 404
        or proof.get("edited_criterion_persisted") is not True
        or proof.get("browser_graph_rendered") is not True
    ):
        raise base.EvidenceError("Human edit, exact approval or isolation evidence is incomplete.")
    readiness = json.loads((attempt / "architect-readiness.log").read_text(encoding="utf-8"))
    if (
        readiness.get("status") != "ready_for_attempt"
        or readiness.get("model") != selected["model"]
        or readiness.get("generation_verified") is not False
    ):
        raise base.EvidenceError(
            "Actual bounded read-only readiness command did not establish metadata readiness."
        )
    return {"live-browser": browser, "live-proof": proof, "architect-readiness": readiness}


def results_for(gate, attempt):
    if gate == "B":
        return live_results(attempt)
    value = ORIGINAL_RESULTS("A", attempt)
    baseline = json.loads(BASELINE.read_text())
    value["architect-browser"] = base.playwright_report(
        attempt / "architect-browser.json",
        baseline["architect_browser"],
        minimum=len(baseline["architect_browser"]),
        projects={key: 8 for key in ("chromium", "mobile", "tablet")},
    )
    from scripts.architect_preflight import navigation_result

    value["navigation-browser"] = navigation_result(attempt)
    return value


def latest(gate):
    pointer = json.loads((EVIDENCE / f"latest-{gate}.json").read_text())
    path = (EVIDENCE / pointer["receipt"]).resolve()
    if not path.is_relative_to(EVIDENCE.resolve()) or base.digest(path) != pointer["sha256"]:
        raise base.EvidenceError("Stage04 receipt pointer is invalid.")
    return path


def validate(path, gate, current=None):
    value = json.loads(path.read_text())
    if (
        value.get("stage") != STAGE
        or value.get("verification_contract") != contract()
        or value.get("gate") != gate
        or value.get("result") != "PASS"
        or value.get("exit_code") != 0
        or value.get("execution_class")
        != ("deterministic" if gate == "A" else "real_gemini_browser")
    ):
        raise base.EvidenceError("Stage04 has no applicable complete passing receipt.")
    if value.get("source_start") != value.get("source_end") or value["source_end"] != (
        current or base.source_manifest()
    ):
        raise base.EvidenceError("Stage04 source evidence is stale.")
    expected, rows = commands(gate, path.parent), value["commands"]
    if len(rows) != len(expected) or any(
        row.get("name") != name or row.get("argv") != argv or row.get("exit_code") != 0
        for row, (name, argv, _) in zip(rows, expected, strict=True)
    ):
        raise base.EvidenceError(
            "Stage04 required commands or actual successful exits are missing."
        )
    required = {row["name"] + ".log" for row in rows} | (
        {
            "backend.xml",
            "core-browser.json",
            "controlled-browser.json",
            "architect-browser.json",
            "navigation-browser.json",
        }
        if gate == "A"
        else {"live-browser.json", "live-proof.json"}
    )
    if not required <= value["artifacts"].keys():
        raise base.EvidenceError("Stage04 artifact manifest is incomplete.")
    for name, sha in value["artifacts"].items():
        artifact = (path.parent / name).resolve()
        if (
            not artifact.is_relative_to(path.parent.resolve())
            or not artifact.is_file()
            or base.digest(artifact) != sha
        ):
            raise base.EvidenceError("Stage04 evidence artifact changed or is missing.")
    with stage_context():
        if value["results"] != results_for(gate, path.parent):
            raise base.EvidenceError("Stage04 executed reports differ from the receipt.")
    if gate == "B":
        if value["execution_profile"] != profile():
            raise base.EvidenceError("Live Architect profile changed.")
        a = latest("A")
        validate(a, "A", current)
        if value["gate_a_receipt"] != str(a.relative_to(EVIDENCE)) or value[
            "gate_a_receipt_sha256"
        ] != base.digest(a):
            raise base.EvidenceError("Live Architect proof is not bound to the passing A receipt.")
        from datetime import datetime

        proof = value["results"]["live-proof"]
        readiness = value["results"]["architect-readiness"]
        times = [
            value["started_at"],
            rows[0]["started_at"],
            readiness["checked_at"],
            rows[0]["completed_at"],
            rows[1]["started_at"],
            proof["started_at"],
            proof["draft_sql"]["created_at"],
            proof["draft_sql"]["completed_at"],
            proof["approved_sql"]["approved_at"],
            proof["completed_at"],
            rows[1]["completed_at"],
            value["completed_at"],
        ]
        moments = [datetime.fromisoformat(item) for item in times]
        if any(item.tzinfo is None for item in moments) or moments != sorted(moments):
            raise base.EvidenceError(
                "Live proof timestamps do not belong to this attempt's actual command boundaries."
            )
    return value


def require_live_opt_in(*, allow_paid=False, require_a=True):
    if not allow_paid and os.environ.get("ORBA_ARCHITECT_LIVE_OPT_IN") != "1":
        raise base.EvidenceError(
            "BLOCKED: fresh Architect paid opt-in required; no request dispatched."
        )
    if require_a:
        validate(latest("A"), "A")
    selected = profile()
    if not selected["credential_configured"]:
        raise base.EvidenceError(
            "BLOCKED: explicit ORBA_ARCHITECT_MODEL and valid runtime credential required."
        )
    if selected["max_concurrent"] != 1 or selected["max_output_tokens"] > 6000:
        raise base.EvidenceError(
            "BLOCKED: Architect live verification requires concurrency1 and at most6000 output/thinking tokens."
        )


@contextmanager
def stage_context():
    """Scoped runner configuration in this CLI process; historical PM parser stays intact."""
    replacements = {
        "EVIDENCE": EVIDENCE,
        "BASELINE": BASELINE,
        "commands": commands,
        "results_for": results_for,
        "execution_profile": profile,
        "require_live_opt_in": require_live_opt_in,
    }
    old = {key: getattr(base, key) for key in replacements}
    try:
        for key, value in replacements.items():
            setattr(base, key, value)
        yield
    finally:
        for key, value in old.items():
            setattr(base, key, value)


def execute(gate, *, allow_paid=False):
    # No external command is allowed in the missing-opt-in branch of the base runner.
    old = os.environ.get("ORBA_ARCHITECT_LIVE_OPT_IN")
    try:
        if gate == "B" and allow_paid:
            os.environ["ORBA_ARCHITECT_LIVE_OPT_IN"] = "1"
        with stage_context():
            return base.execute_gate(
                gate,
                allow_paid=allow_paid,
                context={"stage": STAGE, "agent": "architect", "verification_contract": contract()},
            )
    finally:
        if old is None:
            os.environ.pop("ORBA_ARCHITECT_LIVE_OPT_IN", None)
        else:
            os.environ["ORBA_ARCHITECT_LIVE_OPT_IN"] = old


def summary():
    current, gates = base.source_manifest(), {}
    for gate in ("A", "B"):
        recorded = None
        try:
            path = latest(gate)
            recorded = json.loads(path.read_text(encoding="utf-8"))
            validate(path, gate, current)
            gates[gate] = {
                "result": "PASS",
                "receipt": str(path.relative_to(EVIDENCE)),
                "sha256": base.digest(path),
            }
        except (OSError, ValueError, KeyError) as exc:
            gates[gate] = {
                "result": recorded["result"]
                if recorded and recorded.get("result") in {"FAIL", "BLOCKED"}
                else "NOT RUN"
                if isinstance(exc, FileNotFoundError)
                else "INVALID",
                "reason": str(exc) if isinstance(exc, base.EvidenceError) else type(exc).__name__,
            }
    verdict = "VERIFIED" if all(item["result"] == "PASS" for item in gates.values()) else "PARTIAL"
    value = {
        "stage": STAGE,
        "recorded_at": base.utc(),
        "source_sha256": current["sha256"],
        "gates": gates,
        "stage04_verdict": verdict,
    }
    base.write_new(EVIDENCE / f"summary-{uuid4().hex}.json", value)
    print(json.dumps(value, indent=2))
    return 0 if verdict == "VERIFIED" else 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gate", choices=("A", "B", "summary", "live-preflight"))
    parser.add_argument("--allow-paid", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.gate == "summary":
            return summary()
        if args.gate == "live-preflight":
            require_live_opt_in()
            attempt = os.environ.get("ORBA_GATE_ATTEMPT", "")
            if not attempt or not (
                EVIDENCE.resolve() in __import__("pathlib").Path(attempt).resolve().parents
            ):
                raise base.EvidenceError("BLOCKED: an owned Stage04 Gate B attempt is required.")
            return 0
        return execute(args.gate, allow_paid=args.allow_paid)
    except (OSError, ValueError, KeyError) as exc:
        print(
            json.dumps(
                {
                    "result": "BLOCKED",
                    "reason": str(exc)
                    if isinstance(exc, base.EvidenceError)
                    else type(exc).__name__,
                }
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

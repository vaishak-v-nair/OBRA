"""Independent, fail-closed Stage03 gates. Only explicit Gate B may call Gemini."""

import argparse
import hashlib
import importlib.metadata
import json
import os
import shutil
import socket
import subprocess
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "docs/evidence/stage031"
BASELINE = Path(__file__).with_name("verification_baseline.json")
VERSION = 1
NPM = ["npm", "exec", "--yes", "--package=pnpm@12.14.0", "--", "pnpm"]
UV = ["uv", "run", "--directory", "apps/api"]


class EvidenceError(ValueError):
    pass


def utc():
    return datetime.now(UTC).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def source_manifest(root=ROOT):
    paths = (
        subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root
        )
        .decode()
        .split("\0")
    )
    files = {}
    for name in sorted(set(paths)):
        if not name or not (
            name.startswith(("apps/", "scripts/", "infra/"))
            or name
            in {
                ".gitignore",
                "package.json",
                "pnpm-lock.yaml",
                "pnpm-workspace.yaml",
            }
        ):
            continue
        path = root / name
        if (
            (path.name.startswith(".env") and not path.name.endswith(".example"))
            or path.name == "next-env.d.ts"
            or any(
                part
                in {
                    "node_modules",
                    ".next",
                    ".venv",
                    "__pycache__",
                    "test-results",
                    "playwright-report",
                }
                for part in path.parts
            )
        ):
            continue
        if path.is_file():
            files[name] = digest(path)
    identity = hashlib.sha256(
        json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "version": VERSION,
        "policy": "git-relevant-source-v1",
        "sha256": identity,
        "files": files,
    }


def deterministic_env(inherited=None):
    env = dict(os.environ if inherited is None else inherited)
    for name in list(env):
        if name.startswith(("PYTEST_", "PLAYWRIGHT_")) or name in {
            "ORBA_LIVE_OPT_IN",
            "ORBA_GATE_ATTEMPT",
            "ORBA_GATE_A_RECEIPT",
            "ORBA_TEST_EVIDENCE_DIR",
        }:
            env.pop(name, None)
    # Deletion would reactivate root/API dotenv credentials. Empty overrides win.
    env.update(
        ORBA_PM_API_KEY="",
        GEMINI_API_KEY="",
        ORBA_PM_MODEL="",
        ORBA_PM_THINKING_LEVEL="low",
        ORBA_PM_MAX_INPUT_BYTES="48000",
        PYTHONIOENCODING="utf-8",
    )
    from scripts.prepare_tests import TEST_URL
    from scripts.test_database import guard_test_url

    guard_test_url(TEST_URL)
    env.update(DATABASE_URL=TEST_URL, TEST_DATABASE_URL=TEST_URL)
    return env


def execution_profile():
    from orba.config import Settings
    from orba.pm_provider import (
        ENVELOPE_GRACE_SECONDS,
        PROMPT_HASH,
        PROMPT_VERSION,
        PROVIDER,
        TRANSPORT_GRACE_SECONDS,
        gemini_output_schema,
    )
    from orba.pm_schemas import HASH_VERSION, ProductDocument, canonical

    config = Settings()
    return {
        "provider": PROVIDER,
        "model": config.pm_model,
        "prompt_version": PROMPT_VERSION,
        "prompt_sha256": PROMPT_HASH,
        "hash_version": HASH_VERSION,
        "schema_sha256": hashlib.sha256(
            json.dumps(ProductDocument.model_json_schema(), sort_keys=True).encode()
        ).hexdigest(),
        "provider_schema_sha256": hashlib.sha256(
            canonical(gemini_output_schema()).encode("utf-8")
        ).hexdigest(),
        "sdk_version": importlib.metadata.version("google-genai"),
        "server_timeout_seconds": config.pm_timeout_seconds,
        "transport_timeout_seconds": config.pm_timeout_seconds + TRANSPORT_GRACE_SECONDS,
        "envelope_timeout_seconds": config.pm_timeout_seconds + ENVELOPE_GRACE_SECONDS,
        "max_output_tokens": config.pm_max_output_tokens,
        "thinking_level": config.pm_thinking_level,
        "max_input_bytes": config.pm_max_input_bytes,
        "max_concurrent": config.pm_max_concurrent,
        "account_attempts_per_hour": config.pm_account_attempts,
        "global_attempts_per_hour": config.pm_global_attempts,
        "credential_configured": config.pm_configured,
    }


def commands(gate, attempt):
    if gate == "B":
        return [
            (
                "provider-readiness",
                UV + ["python", "-m", "scripts.check_pm_config", "--check-model"],
                30,
            ),
            ("live-browser", NPM + ["test:e2e:live"], 900),
        ]
    return [
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
        ("python-lock", ["uv", "sync", "--locked", "--directory", "apps/api"], 300),
        ("frontend-lock", NPM + ["install", "--frozen-lockfile"], 300),
        ("peers", NPM + ["peers", "check"], 120),
        ("migration", UV + ["alembic", "upgrade", "head"], 120),
        ("schema-drift", UV + ["alembic", "check"], 120),
        ("backend", UV + ["pytest", "-q", f"--junitxml={attempt / 'backend.xml'}"], 600),
        ("ruff", UV + ["ruff", "check", "."], 120),
        ("format", UV + ["ruff", "format", "--check", "."], 120),
        ("typecheck", NPM + ["typecheck"], 180),
        ("eslint", NPM + ["lint"], 180),
        ("build", NPM + ["build"], 300),
        ("core-browser", NPM + ["test:e2e"], 900),
        ("controlled-browser", NPM + ["test:e2e:controlled"], 600),
    ]


def junit_report(path, required=()):
    root = ET.parse(path).getroot()
    cases = root.findall(".//testcase")
    if not cases:
        raise EvidenceError("Backend report contains no executed tests.")
    found = set()
    for case in cases:
        if any(case.find(kind) is not None for kind in ("skipped", "failure", "error")):
            raise EvidenceError("Backend failure/error/skip/xfail cannot pass Gate A.")
        key = case.attrib.get("classname", "") + "::" + case.attrib.get("name", "")
        if key in found:
            raise EvidenceError("Duplicate backend result identity.")
        found.add(key)
    # Normalize only the module path; parameter IDs are literal test identities.
    expected = {
        module.removesuffix(".py").replace("/", ".").replace("\\", ".") + "::" + selector
        for module, selector in (node.split("::", 1) for node in required)
    }
    if not expected <= found:
        raise EvidenceError(f"Missing {len(expected - found)} mandatory backend baseline cases.")
    return {"passed": len(cases), "skipped": 0, "identities": sorted(found)}


def playwright_report(path, required=(), minimum=1, projects=None):
    report = json.loads(path.read_text())
    stats = report["stats"]
    if report.get("errors") or any(stats.get(k, 0) for k in ("skipped", "unexpected", "flaky")):
        raise EvidenceError("Browser errors/skips/flaky results cannot pass a gate.")
    identities = []

    def walk(suites):
        for suite in suites:
            for spec in suite.get("specs", []):
                for test in spec.get("tests", []):
                    results = test.get("results", [])
                    if (
                        test.get("expectedStatus") != "passed"
                        or test.get("status") != "expected"
                        or len(results) != 1
                        or results[0].get("status") != "passed"
                        or results[0].get("retry") != 0
                    ):
                        raise EvidenceError(
                            "Each browser case must actually pass once without retry."
                        )
                    identities.append((spec["file"], spec["title"], test["projectName"]))
            walk(suite.get("suites", []))

    walk(report["suites"])
    if (
        len(identities) < minimum
        or len(set(identities)) != len(identities)
        or stats["expected"] != len(identities)
    ):
        raise EvidenceError("Incomplete or duplicate browser results.")
    if not {tuple(x) for x in required} <= set(identities):
        raise EvidenceError("Mandatory browser baseline identities are missing.")
    if projects and any(
        sum(x[2] == project for x in identities) < count for project, count in projects.items()
    ):
        raise EvidenceError("Required viewport coverage is incomplete.")
    if any(project["retries"] != 0 for project in report["config"]["projects"]):
        raise EvidenceError("Browser retry configuration must be zero.")
    return {
        "passed": len(identities),
        "skipped": 0,
        "identities": [list(x) for x in sorted(identities)],
    }


def results_for(gate, attempt):
    baseline = json.loads(BASELINE.read_text())
    if gate == "A":
        return {
            "backend": junit_report(
                attempt / "backend.xml",
                baseline.get(
                    "stage033_backend", baseline.get("stage031_backend", baseline["backend"])
                ),
            ),
            "core-browser": playwright_report(
                attempt / "core-browser.json",
                baseline["core_browser"],
                51,
                {p: 17 for p in ("chromium", "mobile", "tablet")},
            ),
            "controlled-browser": playwright_report(
                attempt / "controlled-browser.json",
                required=baseline.get(
                    "stage033_controlled_browser", baseline.get("controlled_browser", ())
                ),
                minimum=18,
                projects={p: 6 for p in ("chromium", "mobile", "tablet")},
            ),
        }
    browser = playwright_report(attempt / "live-browser.json")
    proof = json.loads((attempt / "live-proof.json").read_text())
    if (
        proof.get("execution_class") != "real_gemini_browser"
        or proof.get("provider_double") is not False
        or proof.get("generation_posts") != 1
        or proof.get("generation_dispatches") != 1
        or proof.get("blocked_generation_posts") != 0
        or proof.get("result") != "PASS"
    ):
        raise EvidenceError("Gate B requires exactly one genuine successful model browser flow.")
    draft, approved = proof["draft_sql"], proof["approved_sql"]
    for audit, state in ((draft, "draft"), (approved, "approved")):
        if (
            audit["status"] != "succeeded"
            or audit["graph_validated"] is not True
            or audit["state"] != state
            or audit["run_id"] != proof["run_id"]
            or audit["plan_id"] != proof["plan_id"]
            or audit["provider"] != "google-gemini"
            or not audit["returned_model"]
            or min(audit["counts"].values()) < 1
        ):
            raise EvidenceError("Independent SQL/model evidence is incomplete.")
    if (
        draft["revision"] != 1
        or draft["approved_at"] is not None
        or approved["revision"] != 2
        or approved["version"] != draft["version"]
        or approved["approved_by"] != proof["actor_id"]
        or not approved["approved_at"]
        or proof["unrelated_http_status"] != 404
    ):
        raise EvidenceError("Exact draft/edit/approval/isolation evidence is incomplete.")
    profile = execution_profile()
    for audit in (draft, approved):
        configuration = (audit.get("diagnostic") or {}).get("generation_configuration", {})
        if (
            audit["project_id"] != proof["project_id"]
            or audit["initiator_id"] != proof["actor_id"]
            or audit["requested_model"] != profile["model"]
            or audit["prompt_hash"] != profile["prompt_sha256"]
            or audit["prompt_version"] != profile["prompt_version"]
            or any(
                configuration.get(field) != profile[field]
                for field in (
                    "thinking_level",
                    "max_input_bytes",
                    "max_output_tokens",
                    "provider_schema_sha256",
                )
            )
            or not isinstance(configuration.get("input_bytes"), int)
            or not 0 < configuration["input_bytes"] <= profile["max_input_bytes"]
        ):
            raise EvidenceError("Live source/profile/actor linkage is inconsistent.")
        if (
            audit["returned_model"] != proof["model"]
            or audit["provider_response_id"] != proof["provider_response_id"]
            or audit["usage"] != proof["usage"]
        ):
            raise EvidenceError("Actual API and SQL provider metadata differ.")
    if (
        draft["content_hash"] != proof["draft_api_hash"]
        or approved["content_hash"] != proof["approved_api_hash"]
    ):
        raise EvidenceError("Actual API and SQL document hashes differ.")
    readiness = validate_model_readiness(attempt, before=proof["started_at"])
    return {"live-browser": browser, "live-proof": proof, "provider-readiness": readiness}


def _readiness_output(attempt):
    from orba.pm_readiness import ProviderReadiness

    raw = json.loads((attempt / "provider-readiness.log").read_text(encoding="utf-8"))
    alias = raw.pop("model", None)
    # CLI compatibility keys occur only for a blocked missing-configuration check.
    raw.pop("verdict", None)
    raw.pop("missing", None)
    report = ProviderReadiness.model_validate_json(json.dumps(raw))
    if alias != report.requested_model:
        raise EvidenceError("Readiness CLI model identity is inconsistent.")
    return report


def record_model_readiness(attempt, value, command):
    """Record the actual read-only child command, never a synthetic native exit."""
    report = _readiness_output(attempt)
    artifact = {
        "version": 1,
        "execution_class": "real_read_only_model_metadata",
        "provider_double": False,
        "attempt_id": attempt.name,
        "source_sha256": value["source_start"]["sha256"],
        "execution_profile": value["execution_profile"],
        "gate_a_receipt": value["gate_a_receipt"],
        "gate_a_receipt_sha256": value["gate_a_receipt_sha256"],
        "command": command,
        "report": report.model_dump(mode="json"),
    }
    write_new(attempt / "model-readiness.json", artifact)
    if report.status != "ready_for_attempt":
        value.update(result="BLOCKED", reason=f"Provider metadata readiness: {report.status}")
        if command["exit_code"] == 0:
            raise EvidenceError("Non-ready metadata cannot authorize browser generation.")
    elif command["exit_code"] != 0:
        raise EvidenceError("Ready metadata cannot suppress a nonzero native command exit.")
    else:
        validate_model_readiness(attempt)


def validate_model_readiness(attempt, *, before=None):
    """Network-free validation; nested live-preflight must not issue another GET."""
    from orba.pm_models_policy import model_policy
    from orba.pm_readiness import (
        METADATA_ENVELOPE_SECONDS,
        METADATA_TIMEOUT_SECONDS,
        ProviderReadiness,
    )

    artifact = json.loads((attempt / "model-readiness.json").read_text(encoding="utf-8"))
    report = ProviderReadiness.model_validate_json(json.dumps(artifact["report"]))
    profile, source = execution_profile(), source_manifest()
    policy = model_policy(profile.get("model"))
    a_path = (EVIDENCE / artifact["gate_a_receipt"]).resolve()
    if (
        not a_path.is_relative_to(EVIDENCE.resolve())
        or digest(a_path) != artifact["gate_a_receipt_sha256"]
    ):
        raise EvidenceError("Readiness Gate A receipt identity is invalid.")
    validate_receipt(a_path, "A", source)
    if (
        artifact.get("version") != VERSION
        or artifact.get("execution_class") != "real_read_only_model_metadata"
        or artifact.get("provider_double") is not False
        or artifact.get("attempt_id") != attempt.name
        or artifact.get("source_sha256") != source["sha256"]
        or artifact.get("execution_profile") != profile
        or report.status != "ready_for_attempt"
        or report.operation != "model_metadata"
        or not profile["credential_configured"]
        or not profile["model"]
        or policy is None
        or profile["thinking_level"] not in policy.thinking_levels
        or not report.configured
        or report.metadata_requests != 1
        or report.generation_requests != 0
        or report.live_generation_verified is not False
        or report.provider_http_status != 200
        or report.error_origin is not None
        or report.requested_model != profile["model"]
        or report.thinking_level != profile["thinking_level"]
        or report.metadata_model != "models/" + profile["model"].removeprefix("models/")
        or "generateContent" not in report.supported_actions
        or report.structured_output_support != "documented"
        or report.structured_output_documentation != policy.documentation
        or report.metadata_timeout_seconds != METADATA_TIMEOUT_SECONDS
        or report.metadata_envelope_seconds != METADATA_ENVELOPE_SECONDS
        or report.sdk_version != profile["sdk_version"]
        or report.generation_limits != {k: profile.get(k) for k in report.generation_limits}
        or set(report.generation_limits)
        != {
            "server_timeout_seconds",
            "transport_timeout_seconds",
            "envelope_timeout_seconds",
            "max_output_tokens",
            "max_input_bytes",
            "max_concurrent",
            "account_attempts_per_hour",
            "global_attempts_per_hour",
        }
        or not report.input_token_limit
        or not report.output_token_limit
        or profile["max_output_tokens"] > report.output_token_limit
        or report.model_dump(mode="json") != _readiness_output(attempt).model_dump(mode="json")
    ):
        raise EvidenceError("Readiness evidence is incomplete, controlled, stale or not ready.")
    command = artifact["command"]
    name, argv, _ = commands("B", attempt)[0]
    if command["name"] != name or command["argv"] != argv or command.get("exit_code") != 0:
        raise EvidenceError("Readiness requires its actual successful native command.")
    initial = json.loads((attempt / "attempt.json").read_text(encoding="utf-8"))
    times = [
        datetime.fromisoformat(t)
        for t in (
            initial["started_at"],
            command["started_at"],
            report.checked_at.isoformat(),
            command["completed_at"],
            before or utc(),
        )
    ]
    if any(t.tzinfo is None for t in times) or times != sorted(times):
        raise EvidenceError("Readiness timestamps do not belong before dispatch in this attempt.")
    if report.elapsed_ms > (times[3] - times[1]).total_seconds() * 1000:
        raise EvidenceError("Readiness duration exceeds its actual command boundary.")
    return artifact


def terminate_owned(process):
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    else:
        import signal

        os.killpg(process.pid, signal.SIGTERM)
    process.wait(timeout=15)


def run_command(name, argv, cwd, env, logfile, timeout):
    from scripts.owned_process import ProcessTree

    start = monotonic()
    result = {"name": name, "argv": argv, "started_at": utc(), "exit_code": None}
    actual = list(argv)
    actual[0] = shutil.which(actual[0]) or actual[0]
    process = None
    tree = None
    try:
        tree = ProcessTree()
        with logfile.open("xb") as output:
            process = subprocess.Popen(
                actual,
                cwd=cwd,
                env=env,
                stdout=output,
                stderr=subprocess.STDOUT,
                start_new_session=os.name != "nt",
            )
            result["pid"] = process.pid
            tree.assign(process)
            try:
                result["exit_code"] = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                terminate_owned(process)
                result.update(
                    exit_code=124, failure="command_deadline", native_exit_code=process.returncode
                )
            except KeyboardInterrupt:
                terminate_owned(process)
                result.update(
                    exit_code=130, failure="interrupted", native_exit_code=process.returncode
                )
    except OSError as exc:
        result.update(exit_code=127, failure="launch_error", exception_type=type(exc).__name__)
    finally:
        if process is not None and process.poll() is None:
            terminate_owned(process)
        if tree is not None:
            tree.close()  # Also closes lingering descendants after a parent exits.
        result["duration_seconds"] = round(monotonic() - start, 3)
        result["completed_at"] = utc()
    print(
        f"{name}: exit {result['exit_code']} ({result['duration_seconds']}s); {logfile}", flush=True
    )
    return result


@contextmanager
def gate_lock(directory=None):
    directory = directory or EVIDENCE
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / "gate.lock").open("a+b") as lock:
        lock.seek(0)
        lock.write(b"0")
        lock.flush()
        lock.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise EvidenceError("Another verification gate owns the isolated database.") from None
        try:
            yield
        finally:
            lock.seek(0)
            if os.name == "nt":
                msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(lock, fcntl.LOCK_UN)


def validate_receipt(path, gate, current=None):
    value = json.loads(path.read_text())
    if (
        value.get("version") != VERSION
        or value.get("gate") != gate
        or value.get("execution_class") != {"A": "deterministic", "B": "real_gemini_browser"}[gate]
        or value.get("result") != "PASS"
        or value.get("exit_code") != 0
    ):
        raise EvidenceError(f"Gate {gate} has no passing complete receipt.")
    if value["source_start"] != value["source_end"] or value["source_end"] != (
        current or source_manifest()
    ):
        raise EvidenceError(f"Gate {gate} source evidence is stale.")
    expected = commands(gate, path.parent)
    rows = value["commands"]
    if len(rows) != len(expected) or any(
        row["name"] != name or row["argv"] != argv or row.get("exit_code") != 0
        for row, (name, argv, _) in zip(rows, expected, strict=True)
    ):
        raise EvidenceError("Required commands or successful native exits are missing.")
    for name, sha in value["artifacts"].items():
        artifact = path.parent / name
        if not artifact.is_file() or digest(artifact) != sha:
            raise EvidenceError("A required evidence artifact is missing or changed.")
    required = {row["name"] + ".log" for row in rows} | (
        {"backend.xml", "core-browser.json", "controlled-browser.json"}
        if gate == "A"
        else {"live-browser.json", "live-proof.json", "model-readiness.json"}
    )
    if not required <= value["artifacts"].keys():
        raise EvidenceError("Evidence artifact manifest is incomplete.")
    if value["results"] != results_for(gate, path.parent):
        raise EvidenceError("Structured result evidence changed.")
    if gate == "B" and value["execution_profile"] != execution_profile():
        raise EvidenceError("Live nonsecret execution configuration changed.")
    if gate == "B":
        readiness = value["results"]["provider-readiness"]
        if any(value[k] != readiness[k] for k in ("gate_a_receipt", "gate_a_receipt_sha256")):
            raise EvidenceError("Live/readiness Gate A receipt linkage differs.")
        if readiness["command"] != rows[0] or rows[0]["completed_at"] > rows[1]["started_at"]:
            raise EvidenceError("Readiness command order/evidence differs from actual dispatch.")
    return value


def latest(gate):
    pointer = json.loads((EVIDENCE / f"latest-{gate}.json").read_text())
    path = (EVIDENCE / pointer["receipt"]).resolve()
    if not path.is_relative_to(EVIDENCE) or digest(path) != pointer["sha256"]:
        raise EvidenceError("Latest receipt identity is invalid.")
    return path


def require_live_opt_in(*, allow_paid=False, require_a=True):
    if not allow_paid and os.environ.get("ORBA_LIVE_OPT_IN") != "1":
        raise EvidenceError(
            "BLOCKED: explicit paid opt-in required; use scripts/verify-live.ps1 -AllowPaid after Gate A."
        )
    if require_a:
        validate_receipt(latest("A"), "A")
    if not execution_profile()["credential_configured"]:
        raise EvidenceError(
            "BLOCKED: configure GEMINI_API_KEY (or ORBA_PM_API_KEY) and ORBA_PM_MODEL server-side."
        )


def ports_available():
    for port in (3001, 8001):
        with socket.socket() as sock:
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                raise EvidenceError(
                    f"BLOCKED: loopback test port {port} is occupied; stop its owner before verification."
                )
    if (ROOT / "apps/web/.next/dev/lock").exists():
        raise EvidenceError(
            "BLOCKED: Next development lock exists; stop the development server before verification."
        )


def execute_gate(gate, *, allow_paid=False):
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    attempt = EVIDENCE / (
        datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + f"-{gate}-" + uuid4().hex[:8]
    )
    attempt.mkdir()
    value = {
        "version": VERSION,
        "gate": gate,
        "execution_class": "deterministic" if gate == "A" else "real_gemini_browser",
        "started_at": utc(),
        "commands": [],
        "result": "BLOCKED",
        "exit_code": 2,
    }
    write_new(attempt / "attempt.json", value)
    try:
        with gate_lock():
            value["source_start"] = source_manifest()
            value["git_head"] = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip()
            if gate == "B":
                if not allow_paid:
                    raise EvidenceError(
                        "BLOCKED: verify-live requires the explicit -AllowPaid switch for this attempt."
                    )
                require_live_opt_in(allow_paid=allow_paid)
                value["gate_a_receipt"] = str(latest("A").relative_to(EVIDENCE))
                value["gate_a_receipt_sha256"] = digest(latest("A"))
                value["execution_profile"] = execution_profile()
                env = dict(os.environ)
                for name in list(env):
                    if name.startswith(("PYTEST_", "PLAYWRIGHT_")):
                        env.pop(name, None)
                env.update(ORBA_LIVE_OPT_IN="1", ORBA_GATE_ATTEMPT=str(attempt))
            else:
                env = deterministic_env()
            ports_available()
            env.update(ORBA_TEST_EVIDENCE_DIR=str(attempt), PYTHONIOENCODING="utf-8")
            value["result"] = "FAIL"
            for name, argv, timeout in commands(gate, attempt):
                child_env = dict(env)
                if name.endswith("browser"):
                    child_env["PLAYWRIGHT_JSON_OUTPUT_NAME"] = str(attempt / f"{name}.json")
                result = run_command(name, argv, ROOT, child_env, attempt / f"{name}.log", timeout)
                value["commands"].append(result)
                value["exit_code"] = result["exit_code"]
                if gate == "B" and name == "provider-readiness":
                    record_model_readiness(attempt, value, result)
                if result["exit_code"]:
                    break
            else:
                value["results"] = results_for(gate, attempt)
                value["source_end"] = source_manifest()
                if value["source_start"] != value["source_end"]:
                    raise EvidenceError("Application source changed during verification.")
                value.update(result="PASS", exit_code=0)
    except KeyboardInterrupt:
        value.update(result="FAIL", exit_code=130, reason="interrupted")
    except (EvidenceError, OSError, ValueError, KeyError, ET.ParseError) as exc:
        value.update(
            result="BLOCKED" if value["result"] == "BLOCKED" else "FAIL",
            exit_code=value["exit_code"] or 1,
            reason=str(exc) if isinstance(exc, EvidenceError) else type(exc).__name__,
        )
    finally:
        value["completed_at"] = utc()
        value.setdefault("source_end", source_manifest())
        value["artifacts"] = {
            str(file.relative_to(attempt)): digest(file)
            for file in sorted(attempt.rglob("*"))
            if file.is_file()
        }
        path = attempt / "receipt.json"
        write_new(path, value)
        pointer = EVIDENCE / f"latest-{gate}.json"
        temporary = pointer.with_suffix(".tmp")
        temporary.write_text(
            json.dumps({"receipt": str(path.relative_to(EVIDENCE)), "sha256": digest(path)}) + "\n"
        )
        temporary.replace(pointer)
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


def stage_summary():
    current = source_manifest()
    gates = {}
    for gate in ("A", "B"):
        recorded = None
        try:
            path = latest(gate)
            recorded = json.loads(path.read_text())
            validate_receipt(path, gate, current)
            gates[gate] = {"result": "PASS", "receipt": str(path.relative_to(EVIDENCE))}
        except (OSError, ValueError, KeyError, ET.ParseError) as exc:
            gates[gate] = {
                "result": recorded["result"]
                if recorded and recorded.get("result") in {"FAIL", "BLOCKED"}
                else ("STALE" if recorded else "NOT RUN"),
                "reason": str(exc) if isinstance(exc, EvidenceError) else type(exc).__name__,
            }
    verdict = "VERIFIED" if all(gate["result"] == "PASS" for gate in gates.values()) else "PARTIAL"
    result = {
        "version": VERSION,
        "recorded_at": utc(),
        "source_sha256": current["sha256"],
        "gates": gates,
        "stage03_verdict": verdict,
    }
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    write_new(EVIDENCE / f"summary-{uuid4().hex}.json", result)
    print(json.dumps(result, indent=2))
    return 0 if verdict == "VERIFIED" else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gate", choices=("A", "B", "summary", "live-preflight"))
    parser.add_argument("--allow-paid", action="store_true")
    args = parser.parse_args()
    if args.gate == "summary":
        return stage_summary()
    if args.gate == "live-preflight":
        try:
            require_live_opt_in()
            if os.environ.get("ORBA_GATE_ATTEMPT"):
                validate_model_readiness(Path(os.environ["ORBA_GATE_ATTEMPT"]))
        except (EvidenceError, OSError, ValueError, KeyError) as exc:
            print(
                str(exc)
                if isinstance(exc, EvidenceError)
                else "BLOCKED: current passing Gate A evidence is unavailable."
            )
            return 2
        return 0
    return execute_gate(args.gate, allow_paid=args.allow_paid)


if __name__ == "__main__":
    raise SystemExit(main())

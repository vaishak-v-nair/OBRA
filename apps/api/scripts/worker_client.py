"""Real protocol-only client. No AI, files from a task, shell execution or completion."""

import argparse
import json
import signal
import threading
from pathlib import Path
from urllib.parse import urlsplit
from uuid import UUID, uuid4

import httpx

from orba.scheduler_schemas import HandoffRead
from orba.snapshot_checksum import checksum


class ProtocolError(ValueError):
    pass


def validate_handoff(value, worker):
    parsed = HandoffRead.model_validate(value)
    manifest = parsed.manifest.model_dump(mode="json")
    if manifest["checksum"] != checksum(
        {key: item for key, item in manifest.items() if key != "checksum"}
    ):
        raise ProtocolError("Manifest checksum does not match its canonical content.")
    lease = parsed.lease
    if (
        str(parsed.manifest.worker_id) != worker["id"]
        or parsed.manifest.lease_id != lease.id
        or parsed.manifest.fence_epoch != lease.fence_epoch
        or parsed.manifest.task_id != lease.task_id
        or parsed.manifest.run_id != lease.run_id
        or parsed.manifest.project_id != lease.project_id
        or parsed.manifest.workspace_id != lease.workspace_id
    ):
        raise ProtocolError("Manifest identity contradicts authenticated ownership.")
    if (
        str(parsed.manifest.workspace_id) != worker["workspace_id"]
        or (worker["project_id"] and str(lease.project_id) != worker["project_id"])
        or parsed.manifest.required_capability not in worker["capabilities"]
    ):
        raise ProtocolError("Manifest exceeds the worker's registered scope or capability.")
    return parsed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", default="http://127.0.0.1:8000")
    parser.add_argument("--credential-file", type=Path, required=True)
    parser.add_argument("--state-file", type=Path, required=True)
    parser.add_argument("--run", type=UUID)
    parser.add_argument("--cycles", type=int, choices=range(1, 1001), default=1)
    parser.add_argument("--interval", type=int, choices=range(1, 61), default=10)
    parser.add_argument(
        "--retry-claim",
        action="store_true",
        help="Explicitly repeat the saved same-key claim only after GET found no receipt.",
    )
    parser.add_argument(
        "--release",
        action="store_true",
        help="Release saved ownership; acknowledged releases require reconciliation.",
    )
    args = parser.parse_args()
    url = urlsplit(args.api_url)
    if (
        url.scheme != "http"
        or url.hostname not in {"127.0.0.1", "localhost", "::1"}
        or url.path not in {"", "/"}
        or url.username
        or url.password
        or url.query
        or url.fragment
    ):
        parser.error(
            "Stage05B client requires a loopback HTTP API origin without credentials or path."
        )
    stop = threading.Event()
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    try:
        token = args.credential_file.read_text(encoding="ascii").strip()
        with httpx.Client(
            base_url=args.api_url.rstrip("/"),
            headers={"Authorization": "Bearer " + token},
            timeout=10,
            trust_env=False,
            follow_redirects=False,
        ) as client:

            def request(method, path, data=None):
                response = client.request(method, path, json=data)
                if response.is_error:
                    raise ProtocolError(
                        f"Protocol request rejected with HTTP{response.status_code}; inspect saved ownership before retrying."
                    )
                return response

            worker = request("GET", "/api/v1/workers/me").json()
            print(
                json.dumps(
                    {
                        "event": "worker_authenticated",
                        "worker_id": worker["id"],
                        "execution_performed": False,
                    }
                ),
                flush=True,
            )
            state = (
                json.loads(args.state_file.read_text(encoding="utf-8"))
                if args.state_file.exists()
                else {}
            )
            binding = {
                "worker_id": worker["id"],
                "api_url": args.api_url,
                "run_id": str(args.run) if args.run else None,
            }
            if state and any(state.get(key) != item for key, item in binding.items()):
                raise ProtocolError(
                    "Saved claim belongs to another worker, API or run; use a separate nonsecret state file."
                )
            if args.release and not state.get("request_id"):
                raise ProtocolError(
                    "Release requires an existing saved claim; no new ownership was requested."
                )

            def save(value):
                temporary = args.state_file.with_suffix(".tmp")
                temporary.write_text(json.dumps(value) + "\n", encoding="utf-8")
                temporary.replace(args.state_file)

            handoff = None
            for index in range(args.cycles):
                if stop.is_set():
                    break
                if state.get("request_id"):
                    recovery = client.get("/api/v1/workers/claims/" + state["request_id"])
                    if recovery.status_code == 404 and args.retry_claim:
                        recovery = request(
                            "POST",
                            "/api/v1/workers/claim",
                            {"request_id": state["request_id"], "run_id": binding["run_id"]},
                        )
                    elif recovery.status_code == 404:
                        raise ProtocolError(
                            "Claim outcome is unknown. GET found no committed receipt; use --retry-claim only for an explicit same-key retry."
                        )
                    elif recovery.is_error:
                        raise ProtocolError(
                            f"Claim recovery rejected with HTTP{recovery.status_code}."
                        )
                    if recovery.status_code == 204:
                        state = {}
                    else:
                        handoff = validate_handoff(recovery.json(), worker)
                else:
                    state = binding | {"request_id": str(uuid4())}
                    save(
                        state
                    )  # Persist before dispatch; an unknown response never mints a new key.
                    response = request(
                        "POST",
                        "/api/v1/workers/claim",
                        {"request_id": state["request_id"], "run_id": binding["run_id"]},
                    )
                    if response.status_code == 204:
                        state = {}
                        save(state)
                        print(
                            json.dumps({"event": "no_work", "execution_performed": False}),
                            flush=True,
                        )
                    else:
                        handoff = validate_handoff(response.json(), worker)
                if handoff:
                    lease = handoff.lease
                    payload = {
                        "fence_epoch": lease.fence_epoch,
                        "contract_version": 1,
                        "manifest_checksum": handoff.manifest.checksum,
                    }
                    if lease.state not in {"claimed", "acknowledged"}:
                        raise ProtocolError(
                            "Saved ownership ended. Manual review is required; no new claim was attempted."
                        )
                    if args.release:
                        request("POST", f"/api/v1/workers/leases/{lease.id}/release", payload)
                        print(
                            json.dumps(
                                {
                                    "event": "lease_released",
                                    "lease_id": str(lease.id),
                                    "execution_performed": False,
                                }
                            ),
                            flush=True,
                        )
                        break
                    if lease.state == "claimed":
                        handoff = validate_handoff(
                            request(
                                "POST", f"/api/v1/workers/leases/{lease.id}/acknowledge", payload
                            ).json(),
                            worker,
                        )
                        print(
                            json.dumps(
                                {
                                    "event": "handoff_acknowledged",
                                    "lease_id": str(lease.id),
                                    "fence_epoch": lease.fence_epoch,
                                    "execution_performed": False,
                                }
                            ),
                            flush=True,
                        )
                    else:
                        handoff = validate_handoff(
                            request(
                                "POST",
                                f"/api/v1/workers/leases/{lease.id}/heartbeat",
                                payload | {"request_id": str(uuid4())},
                            ).json(),
                            worker,
                        )
                        print(
                            json.dumps(
                                {
                                    "event": "heartbeat_accepted",
                                    "lease_id": str(lease.id),
                                    "fence_epoch": lease.fence_epoch,
                                    "expires_at": handoff.lease.expires_at.isoformat(),
                                    "execution_performed": False,
                                }
                            ),
                            flush=True,
                        )
                    save(
                        state
                        | {
                            "lease_id": str(lease.id),
                            "fence_epoch": lease.fence_epoch,
                            "manifest_checksum": handoff.manifest.checksum,
                        }
                    )
                if index + 1 < args.cycles and stop.wait(args.interval):
                    break
    except (ValueError, OSError, KeyError, TypeError, httpx.HTTPError) as exc:
        message = (
            str(exc)
            if isinstance(exc, ProtocolError)
            else "Client failed; claim outcome may be unknown. Preserve state and inspect GET recovery before an explicit retry."
        )
        print(
            json.dumps(
                {"error": type(exc).__name__, "message": message, "execution_performed": False}
            ),
            flush=True,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

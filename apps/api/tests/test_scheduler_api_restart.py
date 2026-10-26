"""Actual separate API process restarts preserve PG ownership; no worker execution."""

import socket
import subprocess
import sys
import threading
from contextlib import contextmanager
from time import monotonic
from uuid import uuid4

import httpx

from scripts.owned_process import ProcessTree
from scripts.verification import deterministic_env
from tests.scheduler_support import ready


@contextmanager
def api_process(port, logfile):
    tree = ProcessTree()
    with logfile.open("xb") as output:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "tests.no_generation_app:create_no_generation_app",
                "--factory",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--no-proxy-headers",
                "--no-access-log",
                "--log-level",
                "warning",
            ],
            env=deterministic_env(),
            stdout=output,
            stderr=subprocess.STDOUT,
        )
        try:
            tree.assign(process)
            deadline = monotonic() + 30
            with httpx.Client(
                base_url=f"http://127.0.0.1:{port}", timeout=2, trust_env=False
            ) as probe:
                while True:
                    assert process.poll() is None, "API process exited before readiness"
                    try:
                        if probe.get("/health/ready").status_code == 200:
                            break
                    except httpx.TransportError:
                        pass  # Bounded actual service-readiness polling, never POST retry.
                    assert monotonic() < deadline, "API process did not become ready within30s"
                    threading.Event().wait(0.1)
            yield process
        finally:
            if process.poll() is None:
                process.terminate()
            process.wait(timeout=10)
            tree.close()


def test_actual_api_process_restart_preserves_claim_and_acknowledgment(client, tmp_path):
    _, run, _, _, headers = ready(client)
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    key = str(uuid4())
    url = f"http://127.0.0.1:{port}"
    with (
        api_process(port, tmp_path / "first-api.log") as first,
        httpx.Client(base_url=url, headers=headers, timeout=10, trust_env=False) as network,
    ):
        response = network.post(
            "/api/v1/workers/claim", json={"request_id": key, "run_id": run["id"]}
        )
        assert response.status_code == 201, response.text
        original = response.json()
        lease = original["lease"]
        ack = network.post(
            f"/api/v1/workers/leases/{lease['id']}/acknowledge",
            json={
                "fence_epoch": lease["fence_epoch"],
                "contract_version": 1,
                "manifest_checksum": original["manifest"]["checksum"],
            },
        )
        assert ack.status_code == 200
        acknowledged = ack.json()
        first_pid = first.pid
    assert first.returncode is not None
    with (
        api_process(port, tmp_path / "second-api.log") as second,
        httpx.Client(base_url=url, headers=headers, timeout=10, trust_env=False) as network,
    ):
        assert second.pid != first_pid
        recovered = network.get(f"/api/v1/workers/claims/{key}")
        assert recovered.status_code == 200
        assert recovered.json() == acknowledged
        assert recovered.json()["execution_performed"] is False
        assert network.get("/__test/no-generation").json()["provider_dependency_entries"] == 0

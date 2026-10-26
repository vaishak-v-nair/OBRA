"""Actual standalone imports must not initialize a planning model SDK."""

import json
import subprocess
import sys


def test_scheduler_and_protocol_client_do_not_load_model_sdk():
    code = "import sys,json; import orba.scheduler_service,scripts.worker_admin,scripts.worker_client; print(json.dumps([name for name in sys.modules if name.startswith('google.genai')]))"
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=30, check=False
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == []

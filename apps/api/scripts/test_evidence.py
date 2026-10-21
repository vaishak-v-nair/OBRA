"""New test attempts never overwrite historical acceptance records."""

import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

_manual = (
    Path(__file__).resolve().parents[3]
    / "docs/evidence/manual"
    / (datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8])
)


def evidence_path(name):
    directory = Path(os.environ.get("ORBA_TEST_EVIDENCE_DIR", str(_manual)))
    directory.mkdir(parents=True, exist_ok=True)
    return directory / name

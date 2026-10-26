"""Offline strict evidence validation; never dispatches a task, worker or model."""

import argparse
import json
from pathlib import Path

from scripts.scheduler_proof import validate_proof
from scripts.verification import EvidenceError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path)
    parser.add_argument("--reject-empty", action="store_true")
    args = parser.parse_args()
    if args.reject_empty:
        try:
            validate_proof({})
        except EvidenceError:
            print(json.dumps({"incomplete_proof_rejected": True, "execution_performed": False}))
            return 0
        return 1
    if not args.file:
        parser.error("Use --file or --reject-empty.")
    try:
        validate_proof(json.loads(args.file.read_text(encoding="utf-8")))
    except (EvidenceError, OSError, ValueError):
        print(json.dumps({"result": "FAIL", "reason": "Incomplete or contradictory proof."}))
        return 1
    print(json.dumps({"result": "PASS", "execution_performed": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

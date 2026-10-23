"""Negative-input process experiment. Rejection must produce native exit1, not PASS."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))  # uv --directory apps/api
from scripts.orchestration_proof import validate_proof

print('NEGATIVE INPUT EXPERIMENT: empty proof; no DB or model operation.', flush=True)
validate_proof({})
print('INCORRECT ACCEPTANCE: invalid proof was accepted.', flush=True)

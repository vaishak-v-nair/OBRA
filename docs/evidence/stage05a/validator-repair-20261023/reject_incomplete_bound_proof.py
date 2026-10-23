"""ISOLATED in-memory invalid proof, not real Gate B. Disk artifacts stay untouched."""
import copy
import hashlib
import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path.cwd()))  # uv --directory apps/api
from scripts import orchestration_verification as gates
from scripts import verification as base

receipt_path = gates.latest('B')
proof_path = receipt_path.parent / 'local-proof.json'
actual = gates.validate(receipt_path, 'B')
tracked = [receipt_path, proof_path, gates.latest('A')]
before = {path: base.digest(path) for path in tracked}
incomplete = copy.deepcopy(actual['results']['local-proof'])
incomplete['run_api'] = {}
for name in ('run_id', 'project_id', 'workspace_id'):
    incomplete.pop(name)
for audit in (incomplete['initial_sql'], incomplete['reloaded_sql']):
    for name in ('run_id', 'project_id', 'workspace_id', 'graph', 'snapshot_hash',
                 'tasks', 'dependencies', 'events', 'source_snapshot'):
        audit.pop(name)
proof_text = json.dumps(incomplete)
proof_hash = hashlib.sha256(proof_text.encode()).hexdigest()
synthetic = copy.deepcopy(actual)
synthetic['results']['local-proof'] = incomplete
synthetic['artifacts']['local-proof.json'] = proof_hash
receipt_text = json.dumps(synthetic)
original_read, original_digest = Path.read_text, base.digest

def read(path, *args, **kwargs):
    if path.resolve() == proof_path.resolve(): return proof_text
    if path.resolve() == receipt_path.resolve(): return receipt_text
    return original_read(path, *args, **kwargs)

def digest(path):
    return proof_hash if Path(path).resolve() == proof_path.resolve() else original_digest(path)

print(json.dumps({'experiment':'isolated bound invalid proof, not actual Gate B',
                  'complete_saved_B_accepted_first':True, 'disk_mutations':0,
                  'database_operations':0,'model_requests':0}), flush=True)
try:
    with patch.object(Path, 'read_text', read), patch.object(base, 'digest', digest):
        gates.validate(receipt_path, 'B')  # Must raise EvidenceError and native exit1.
finally:
    if not all(base.digest(path) == value for path, value in before.items()):
        raise RuntimeError('Historical artifact changed during isolated experiment')
print('INCORRECT ACCEPTANCE: incomplete proof was accepted.', flush=True)

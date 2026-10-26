"""Adversarial production validator tests; synthetic attestations are never live proof."""

from copy import deepcopy

import pytest

from orba.orchestration_service import checksum
from scripts.scheduler_proof import SchedulerProof, validate_proof
from scripts.verification import EvidenceError
from tests.scheduler_proof_support import complete_input


def test_complete_sql_backed_protocol_proof_and_adversarial_changes(client):
    proof = complete_input(client)
    assert validate_proof(proof)["result"] == "PASS"
    mutations = [
        lambda x: x.clear(),
        lambda x: x.pop("worker"),
        lambda x: x.update(worker=None),
        lambda x: x["independent_sql"].update(dispatches=[]),
        lambda x: x["independent_sql"]["orchestration"].update(tasks=[]),
        lambda x: x["independent_sql"]["orchestration"].update(graph=None),
        lambda x: x["independent_sql"]["orchestration"].update(snapshot_hash=None),
        lambda x: x["independent_sql"]["orchestration"].update(snapshot_hash="0" * 64),
        lambda x: x["independent_sql"]["orchestration"].update(project_id="not-a-uuid"),
        lambda x: x["independent_sql"]["orchestration"].update(workspace_id=x["worker"]["id"]),
        lambda x: x["independent_sql"]["orchestration"]["counts"].update(tasks=99),
        lambda x: x["independent_sql"]["orchestration"]["tasks"].append(
            deepcopy(x["independent_sql"]["orchestration"]["tasks"][0])
        ),
        lambda x: x["independent_sql"]["orchestration"]["graph"]["nodes"].clear(),
        lambda x: x["independent_sql"]["orchestration"]["dependencies"][0].update(
            prerequisite_id=x["worker"]["id"]
        ),
        lambda x: x["independent_sql"]["dispatches"][0].update(task_id=x["worker"]["id"]),
        lambda x: x["independent_sql"]["dispatches"][0]["leases"][0].update(fence_epoch=True),
        lambda x: x["independent_sql"].update(heartbeats=[]),
        lambda x: x["independent_sql"]["credentials"][0].update(revoked_at="2020-01-01T00:00:00Z"),
        lambda x: x["independent_sql"]["handoffs"][0].update(checksum="a" * 64),
        lambda x: x["independent_sql"]["handoffs"][0]["manifest"].update(architecture=None),
        lambda x: x["acknowledged_api"]["lease"].update(state="verified_complete"),
        lambda x: x["heartbeat_api"]["lease"].update(worker_id=x["foundation"]["run_id"]),
        lambda x: x["process_commands"][0].update(exit_code=1),
        lambda x: x["process_commands"][0].update(exit_code=False),
        lambda x: x["independent_sql"]["orchestration"]["events"][-1]["details"].update(
            execution_performed=0
        ),
        lambda x: x.update(executed_tasks=True),
        lambda x: x.update(reload_persisted=False),
        lambda x: x.update(model_generation_requests=1),
        lambda x: x["final_api"].update(snapshot_hash="0" * 64),
        lambda x: x["independent_sql"]["workers"][0].update(enabled=False),
        lambda x: x["independent_sql"]["heartbeats"][0].update(request_hash="0" * 64),
        lambda x: x["independent_sql"]["heartbeats"][0].update(accepted_at="2090-01-01T00:00:00Z"),
        lambda x: x["independent_sql"]["orchestration"]["events"][-1]["details"].update(
            lease_id=x["worker"]["id"]
        ),
        lambda x: x["independent_sql"]["orchestration"]["events"][-1]["details"].update(
            fence_epoch=999
        ),
        forge_coherent_trace,
    ]
    for mutation in mutations:
        broken = deepcopy(proof)
        mutation(broken)
        with pytest.raises(EvidenceError):
            validate_proof(broken)


def forge_coherent_trace(proof):
    """Even consistently rehashed forged manifests cannot replace source traceability."""
    record = proof["independent_sql"]["handoffs"][0]
    manifests = [
        record["manifest"],
        proof["acknowledged_api"]["manifest"],
        proof["heartbeat_api"]["manifest"],
    ]
    for manifest in manifests:
        manifest["requirement_traces"][0]["story_id"] = proof["worker"]["id"]
        manifest["checksum"] = checksum({k: v for k, v in manifest.items() if k != "checksum"})
    record["checksum"] = manifests[0]["checksum"]
    lease = proof["heartbeat_api"]["lease"]
    for heartbeat in proof["independent_sql"]["heartbeats"]:
        heartbeat["request_hash"] = checksum(
            {
                "fence_epoch": lease["fence_epoch"],
                "contract_version": 1,
                "manifest_checksum": record["checksum"],
                "request_id": heartbeat["request_id"],
            }
        )


@pytest.mark.parametrize("field", list(SchedulerProof.model_fields))
def test_missing_mandatory_protocol_proof_cannot_pass(field):
    # Missing-vs-missing used to compare equal. Required types reject it directly.
    with pytest.raises(EvidenceError):
        validate_proof({key: None for key in SchedulerProof.model_fields if key != field})


@pytest.mark.parametrize("value", [{}, None, [], {"result": "PASS"}, {"proof_version": True}])
def test_empty_and_forged_proofs_fail_closed(value):
    with pytest.raises(EvidenceError):
        validate_proof(value)

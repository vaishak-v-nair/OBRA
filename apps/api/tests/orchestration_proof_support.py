"""Synthetic evidence INPUTS for isolated validator tests, never actual Gate B evidence."""

from copy import deepcopy
from uuid import NAMESPACE_URL, uuid5

from orba.architect_repository import document_hash
from orba.orchestration_graph import evaluate
from orba.orchestration_service import HASH_VERSION, checksum
from orba.pm_repository import content_hash
from scripts.architect_sample import controlled_document
from scripts.pm_sample import human_document


def ident(name):
    return str(uuid5(NAMESPACE_URL, "orba-unit-proof:" + name))


def assemble(api, sql):
    """Unit input builder. The caller must never publish this as executed browser proof."""
    return {
        "proof_version": 2,
        "stage": "stage05a-orchestration",
        "result": "PASS",
        "execution_class": "real_local_control_plane",
        "source_origin": "human_authored_test_fixture_approved_through_real_UI",
        "provider_double": False,
        "executor_available": False,
        "started_at": "2020-01-01T00:00:00Z",
        "completed_at": "2099-01-01T00:00:00Z",
        "run_id": api["id"],
        "project_id": api["project_id"],
        "workspace_id": api["workspace_id"],
        "model_generation_budget": {"attempted": 0, "forwarded": 0, "blocked": 0},
        "server_boundary": {
            "execution_class": "no_generation_test_boundary",
            "provider_readiness_verified": False,
            "blocked_generation_posts": 0,
            "provider_dependency_entries": 0,
        },
        "model_generation_requests": 0,
        "browser_create_posts": 1,
        "explicit_idempotency_replay_status": 200,
        "forged_completion_status": 404,
        "unauthorized_status": 404,
        "protected_ui_hidden": True,
        "reload_persisted": True,
        "run_api": deepcopy(api),
        "initial_sql": deepcopy(sql),
        "reloaded_sql": deepcopy(sql),
    }


def synthetic_proof(*, independent_tasks=False):
    architecture, plan = controlled_document(), human_document(ident("creator"))
    if independent_tasks:
        for task in architecture.tasks:
            task.dependencies = []
    moment = "2026-10-23T00:00:01Z"
    snapshot_tasks = [
        {
            "source_task_id": ident("source-" + task.key),
            "display_order": order,
            "definition": task.model_dump(mode="json"),
        }
        for order, task in enumerate(architecture.tasks)
    ]
    snapshot_edges = [
        {
            "source_dependency_id": ident("source-edge-" + task.key + "-" + dependency),
            "prerequisite": dependency,
            "dependent": task.key,
            "display_order": order,
        }
        for task in architecture.tasks
        for order, dependency in enumerate(task.dependencies)
    ]
    snapshot = {
        "hash_version": HASH_VERSION,
        "project_id": ident("project"),
        "workspace_id": ident("workspace"),
        "architecture": {
            "id": ident("architecture"),
            "version": 1,
            "revision": 1,
            "hash": document_hash(architecture),
            "approved_by": ident("creator"),
            "approved_at": moment,
            "approval_dispositions": {},
            "document": architecture.model_dump(mode="json"),
        },
        "product_plan": {
            "id": ident("plan"),
            "version": 1,
            "revision": 1,
            "hash": content_hash(plan),
            "approved_by": ident("creator"),
            "approved_at": moment,
            "document": plan.model_dump(mode="json"),
        },
        "tasks": snapshot_tasks,
        "dependencies": snapshot_edges,
        "traces": [
            {
                "source_trace_id": ident("trace"),
                "story_id": ident("story"),
                "task_key": "storage",
                "component_key": None,
            }
        ],
    }
    api = {
        "id": ident("run"),
        "project_id": ident("project"),
        "workspace_id": ident("workspace"),
        "architecture_id": ident("architecture"),
        "architecture_version": 1,
        "architecture_revision": 1,
        "architecture_hash": document_hash(architecture),
        "source_plan_id": ident("plan"),
        "source_version": 1,
        "source_revision": 1,
        "source_hash": content_hash(plan),
        "creator_id": ident("creator"),
        "client_request_id": ident("request"),
        "snapshot_hash": checksum(snapshot),
        "hash_version": HASH_VERSION,
        "status": "awaiting_executor",
        "revision": 2,
        "last_event_sequence": 2,
        "created_at": moment,
        "updated_at": moment,
        "cancelled_at": None,
        "execution_performed": False,
        "source_current": True,
        "graph": evaluate(architecture.tasks),
        "tasks": [
            {
                "id": ident("task-" + task["definition"]["key"]),
                "run_id": ident("run"),
                "source_task_id": task["source_task_id"],
                "key": task["definition"]["key"],
                "definition": task["definition"],
                "display_order": order,
                "eligibility": "eligible"
                if not task["definition"]["dependencies"]
                else "waiting_prerequisites",
                "execution_status": "awaiting_executor",
                "created_at": moment,
                "updated_at": moment,
            }
            for order, task in enumerate(snapshot_tasks)
        ],
    }
    sql = {
        key: deepcopy(value)
        for key, value in api.items()
        if key not in {"id", "last_event_sequence", "updated_at", "hash_version", "source_current"}
    }
    sql.update(
        run_id=api["id"],
        source_approved_by=ident("creator"),
        source_approved_at=moment,
        source_snapshot=snapshot,
        hash_valid=True,
        relational_snapshot_valid=True,
        execution_class="real_local_control_plane",
        audit_model_requests=0,
        generation_records={"product_manager_runs": 0, "architect_runs": 0},
        counts={
            "tasks": len(api["tasks"]),
            "dependencies": len(snapshot_edges),
            "traces": 1,
            "events": 2,
        },
        tasks=[
            task | {"project_id": api["project_id"], "architecture_id": api["architecture_id"]}
            for task in api["tasks"]
        ],
        dependencies=[
            {
                "id": ident("edge-" + edge["dependent"]),
                "run_id": api["id"],
                "project_id": api["project_id"],
                "source_dependency_id": edge["source_dependency_id"],
                "prerequisite_id": ident("task-" + edge["prerequisite"]),
                "dependent_id": ident("task-" + edge["dependent"]),
                "display_order": edge["display_order"],
            }
            for edge in snapshot_edges
        ],
        events=[
            {
                "id": ident("event-" + str(order)),
                "run_id": api["id"],
                "project_id": api["project_id"],
                "task_id": None,
                "sequence": order,
                "run_revision": order,
                "event_type": event,
                "actor_type": "user" if order == 1 else "system",
                "actor_id": ident("creator") if order == 1 else None,
                "occurred_at": moment,
                "previous_state": None if order == 1 else "created",
                "new_state": "created" if order == 1 else "awaiting_executor",
                "details": {"execution_performed": False},
            }
            for order, event in enumerate(["run_created", "run_awaiting_executor"], 1)
        ],
    )
    return assemble(api, sql)

"""Strict local verification inputs, never an executor or a source of execution facts."""

import hashlib
import json
from typing import Annotated, Literal
from uuid import UUID

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    ValidationError,
)

from orba.architect_repository import document_hash
from orba.architect_schemas import ArchitectureDocument, Task
from orba.orchestration_graph import evaluate
from orba.orchestration_schemas import EventRead, GraphNode, GraphRead, RunDetail, TaskRead
from orba.orchestration_service import HASH_VERSION
from orba.pm_repository import content_hash
from orba.pm_schemas import ProductDocument, canonical
from orba.task_graph import GraphError
from scripts.verification import EvidenceError

PROOF_VERSION = 2
Positive = Annotated[int, Field(strict=True, ge=1)]
Count = Annotated[int, Field(strict=True, ge=0)]
Key = Annotated[str, Field(min_length=1, pattern=r"\S")]
SHA256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class EvidenceModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")


class Edge(EvidenceModel):
    prerequisite: Key
    dependent: Key


class Node(GraphNode, EvidenceModel):
    key: Key
    prerequisites: list[Key]
    dependents: list[Key]
    ancestors: list[Key]
    impact: list[Key]


class Graph(GraphRead, EvidenceModel):
    valid: StrictBool
    execution_performed: StrictBool
    topological_order: list[Key]
    roots: list[Key]
    eligible: list[Key]
    blocked: list[Key]
    nodes: Annotated[list[Node], Field(min_length=1, max_length=40)]
    edges: list[Edge]


class Binding(EvidenceModel):
    project_id: UUID
    workspace_id: UUID
    architecture_id: UUID
    architecture_version: Positive
    architecture_revision: Positive
    architecture_hash: SHA256
    source_plan_id: UUID
    source_version: Positive
    source_revision: Positive
    source_hash: SHA256
    creator_id: UUID
    client_request_id: UUID
    snapshot_hash: SHA256


class APITask(TaskRead, EvidenceModel):
    key: Key
    display_order: Count
    created_at: AwareDatetime
    updated_at: AwareDatetime


class API(Binding, RunDetail):
    model_config = ConfigDict(strict=True, extra="forbid")
    revision: Positive
    last_event_sequence: Positive
    created_at: AwareDatetime
    updated_at: AwareDatetime
    execution_performed: StrictBool
    source_current: StrictBool
    graph: Graph
    tasks: Annotated[list[APITask], Field(min_length=1, max_length=40)]


class SQLTask(APITask):
    project_id: UUID
    architecture_id: UUID


class Dependency(EvidenceModel):
    id: UUID
    run_id: UUID
    project_id: UUID
    source_dependency_id: UUID
    prerequisite_id: UUID
    dependent_id: UUID
    display_order: Count


class NoExecution(EvidenceModel):
    execution_performed: StrictBool


class Event(EventRead, EvidenceModel):
    project_id: UUID
    sequence: Positive
    run_revision: Positive
    occurred_at: AwareDatetime
    details: NoExecution


class SnapshotTask(EvidenceModel):
    source_task_id: UUID
    display_order: Count
    definition: Task


class SnapshotEdge(Edge):
    source_dependency_id: UUID
    display_order: Count


class Trace(EvidenceModel):
    source_trace_id: UUID
    story_id: UUID
    task_key: Key | None
    component_key: Key | None


class Artifact(EvidenceModel):
    id: UUID
    version: Positive
    revision: Positive
    hash: SHA256
    approved_by: UUID
    approved_at: AwareDatetime


class Architecture(Artifact):
    document: ArchitectureDocument
    approval_dispositions: dict


class ProductPlan(Artifact):
    document: ProductDocument


class Snapshot(EvidenceModel):
    hash_version: Literal["orba-orchestration-canonical-json-v1"]
    project_id: UUID
    workspace_id: UUID
    architecture: Architecture
    product_plan: ProductPlan
    tasks: Annotated[list[SnapshotTask], Field(min_length=1, max_length=40)]
    dependencies: list[SnapshotEdge]
    traces: Annotated[list[Trace], Field(min_length=1)]


class Counts(EvidenceModel):
    tasks: Positive
    dependencies: Count
    events: Positive
    traces: Positive


class GenerationRecords(EvidenceModel):
    product_manager_runs: Count
    architect_runs: Count


class SQL(Binding):
    run_id: UUID
    source_approved_by: UUID
    source_approved_at: AwareDatetime
    source_snapshot: Snapshot
    snapshot_hash: SHA256
    hash_valid: StrictBool
    relational_snapshot_valid: StrictBool
    status: Literal["awaiting_executor"]
    revision: Positive
    created_at: AwareDatetime
    cancelled_at: None
    counts: Counts
    graph: Graph
    tasks: Annotated[list[SQLTask], Field(min_length=1, max_length=40)]
    dependencies: list[Dependency]
    events: list[Event]
    generation_records: GenerationRecords
    audit_model_requests: Count
    execution_performed: StrictBool
    execution_class: Literal["real_local_control_plane"]


class Budget(EvidenceModel):
    attempted: Count
    forwarded: Count
    blocked: Count


class Boundary(EvidenceModel):
    execution_class: Literal["no_generation_test_boundary"]
    provider_readiness_verified: StrictBool
    blocked_generation_posts: Count
    provider_dependency_entries: Count


class LocalProof(EvidenceModel):
    proof_version: Positive
    stage: Literal["stage05a-orchestration"]
    result: Literal["PASS"]
    execution_class: Literal["real_local_control_plane"]
    source_origin: Literal["human_authored_test_fixture_approved_through_real_UI"]
    provider_double: StrictBool
    executor_available: StrictBool
    started_at: AwareDatetime
    completed_at: AwareDatetime
    run_id: UUID
    project_id: UUID
    workspace_id: UUID
    model_generation_budget: Budget
    server_boundary: Boundary
    model_generation_requests: Count
    browser_create_posts: Positive
    explicit_idempotency_replay_status: Positive
    forged_completion_status: Positive
    unauthorized_status: Positive
    protected_ui_hidden: StrictBool
    reload_persisted: StrictBool
    run_api: API
    initial_sql: SQL
    reloaded_sql: SQL


def require(condition, message):
    if not condition:
        raise EvidenceError(
            "Local B proof: " + message + " Recreate complete local Gate B evidence."
        )


def unique(items, field, label):
    values = [getattr(item, field) for item in items]
    require(len(values) == len(set(values)), label + " contains duplicate " + field + ".")


def validate_rows(sql, api, raw):
    for label, tasks in (("initial_sql", sql.tasks), ("run_api", api.tasks)):
        require(
            all(
                canonical(before["definition"])
                == canonical(task.definition.model_dump(mode="json"))
                for before, task in zip(raw[label]["tasks"], tasks, strict=True)
            ),
            "Task definitions require exact types and text without normalization.",
        )
    for field in ("id", "key", "source_task_id", "display_order"):
        unique(sql.tasks, field, "SQL tasks")
        unique(api.tasks, field, "API tasks")
    expected = sql.counts.tasks
    require(
        expected == len(sql.tasks) == len(api.tasks) == len(sql.graph.nodes), "Task counts differ."
    )
    require(
        [task.display_order for task in sql.tasks] == list(range(expected)), "Task order differs."
    )
    require(
        [task.model_dump(exclude={"project_id", "architecture_id"}) for task in sql.tasks]
        == [task.model_dump() for task in api.tasks],
        "SQL and API task records differ.",
    )
    require(
        all(
            task.run_id == sql.run_id
            and task.project_id == sql.project_id
            and task.architecture_id == sql.architecture_id
            and task.key == task.definition.key
            and task.execution_status == "awaiting_executor"
            and task.created_at == sql.created_at == task.updated_at
            for task in sql.tasks
        ),
        "Task identity, ownership, timestamps or unexecuted state differ.",
    )
    try:
        graph = evaluate([task.definition for task in sql.tasks])
    except GraphError:
        raise EvidenceError(
            "Local B proof: persisted task definitions contain an invalid DAG."
        ) from None
    require(
        sql.graph.model_dump() == api.graph.model_dump() == graph, "Computed task graph differs."
    )
    states = {node.key: node for node in sql.graph.nodes}
    require(
        all(task.eligibility == states[task.key].eligibility for task in sql.tasks),
        "Task eligibility differs from graph.",
    )
    keys = {task.id: task.key for task in sql.tasks}
    for field in ("id", "source_dependency_id", "display_order"):
        unique(sql.dependencies, field, "SQL dependencies")
    require(sql.counts.dependencies == len(sql.dependencies), "Dependency counts differ.")
    require(
        [edge.display_order for edge in sql.dependencies] == list(range(len(sql.dependencies))),
        "Dependency order differs.",
    )
    require(
        all(
            edge.run_id == sql.run_id
            and edge.project_id == sql.project_id
            and edge.prerequisite_id in keys
            and edge.dependent_id in keys
            and edge.prerequisite_id != edge.dependent_id
            for edge in sql.dependencies
        ),
        "Dependency ownership or task reference is invalid.",
    )
    pairs = [(keys[edge.prerequisite_id], keys[edge.dependent_id]) for edge in sql.dependencies]
    require(len(set(pairs)) == len(pairs), "Duplicate dependency endpoints.")
    require(
        set(pairs) == {(edge.prerequisite, edge.dependent) for edge in sql.graph.edges},
        "SQL dependency edges differ from graph.",
    )


def validate_snapshot(sql, api, raw):
    snapshot = sql.source_snapshot
    for label, artifact in (
        ("architecture", snapshot.architecture),
        ("product_plan", snapshot.product_plan),
    ):
        require(
            canonical(raw[label]["document"])
            == canonical(artifact.document.model_dump(mode="json")),
            "Approved documents require exact types and text without normalization.",
        )
    require(
        all(
            canonical(before["definition"]) == canonical(task.definition.model_dump(mode="json"))
            for before, task in zip(raw["tasks"], snapshot.tasks, strict=True)
        ),
        "Snapshot task definitions were normalized.",
    )
    require(
        hashlib.sha256(canonical(raw).encode("utf-8")).hexdigest() == sql.snapshot_hash,
        "Canonical SQL snapshot checksum differs.",
    )
    require(
        snapshot.hash_version == api.hash_version == HASH_VERSION, "Snapshot hash version differs."
    )
    require(
        (snapshot.project_id, snapshot.workspace_id) == (sql.project_id, sql.workspace_id),
        "Snapshot project/workspace differs.",
    )
    for artifact, prefix, ident in (
        (snapshot.architecture, "architecture", sql.architecture_id),
        (snapshot.product_plan, "source", sql.source_plan_id),
    ):
        require(
            artifact.id == ident
            and artifact.version == getattr(sql, prefix + "_version")
            and artifact.revision == getattr(sql, prefix + "_revision")
            and artifact.hash == getattr(sql, prefix + "_hash")
            and artifact.approved_at <= sql.created_at,
            "Approved source identity/version/revision/hash differs.",
        )
    require(
        snapshot.architecture.approved_by == sql.source_approved_by
        and snapshot.architecture.approved_at == sql.source_approved_at
        and document_hash(snapshot.architecture.document) == sql.architecture_hash
        and content_hash(snapshot.product_plan.document) == sql.source_hash,
        "Approved source document hash or approval differs.",
    )
    require(
        [task.model_dump(mode="json") for task in snapshot.tasks]
        == [
            {
                "source_task_id": str(task.source_task_id),
                "display_order": task.display_order,
                "definition": task.definition.model_dump(mode="json"),
            }
            for task in sql.tasks
        ]
        and [task.definition for task in snapshot.tasks] == snapshot.architecture.document.tasks,
        "SQL tasks differ from immutable source definitions.",
    )
    keys = {task.id: task.key for task in sql.tasks}
    require(
        [edge.model_dump(mode="json") for edge in snapshot.dependencies]
        == [
            {
                "source_dependency_id": str(edge.source_dependency_id),
                "prerequisite": keys[edge.prerequisite_id],
                "dependent": keys[edge.dependent_id],
                "display_order": edge.display_order,
            }
            for edge in sql.dependencies
        ],
        "SQL dependencies differ from immutable source.",
    )
    unique(snapshot.traces, "source_trace_id", "Snapshot traces")
    components = {component.key for component in snapshot.architecture.document.components}
    require(
        sql.counts.traces == len(snapshot.traces)
        and all(
            (trace.task_key in keys.values() and trace.component_key is None)
            or (trace.task_key is None and trace.component_key in components)
            for trace in snapshot.traces
        ),
        "Snapshot trace count or reference differs.",
    )


def validate_events(sql, api):
    unique(sql.events, "id", "SQL events")
    require(
        sql.counts.events == len(sql.events) == api.last_event_sequence == 2, "Event count differs."
    )
    expected = [
        (1, 1, "run_created", "user", sql.creator_id, None, "created"),
        (2, 2, "run_awaiting_executor", "system", None, "created", "awaiting_executor"),
    ]
    require(
        [
            (
                e.sequence,
                e.run_revision,
                e.event_type,
                e.actor_type,
                e.actor_id,
                e.previous_state,
                e.new_state,
            )
            for e in sql.events
        ]
        == expected
        and all(
            e.run_id == sql.run_id
            and e.project_id == sql.project_id
            and e.task_id is None
            and e.occurred_at == sql.created_at
            and e.details.execution_performed is False
            for e in sql.events
        ),
        "Lifecycle ledger identities, states, actors or times differ.",
    )


def validate_proof(raw):
    """Validate JSON without coercion and reconcile independent SQL/API/snapshot facts."""
    try:
        proof = LocalProof.model_validate_json(json.dumps(raw), strict=True)
    except (ValidationError, TypeError, ValueError) as exc:
        location = "JSON"
        if isinstance(exc, ValidationError):
            schema = LocalProof.model_json_schema()
            names = set(schema["properties"])
            for definition in schema["$defs"].values():
                names.update(definition.get("properties", {}))
            location = ".".join(
                str(part) if isinstance(part, int) or part in names else "<unknown-field>"
                for part in exc.errors(include_input=False)[0]["loc"]
            )
        raise EvidenceError(
            f"Local B proof has a missing or invalid required field at {location}. "
            "Recreate complete local Gate B evidence; see docs/VERIFICATION_STAGE05A.md."
        ) from None
    sql, api = proof.initial_sql, proof.run_api
    require(proof.proof_version == PROOF_VERSION, "Proof version differs.")
    require(
        not proof.provider_double
        and not proof.executor_available
        and proof.model_generation_requests == 0
        and proof.model_generation_budget.model_dump()
        == {"attempted": 0, "forwarded": 0, "blocked": 0}
        and proof.server_boundary.blocked_generation_posts == 0
        and proof.server_boundary.provider_dependency_entries == 0
        and proof.server_boundary.provider_readiness_verified is False
        and proof.browser_create_posts == 1
        and proof.explicit_idempotency_replay_status == 200
        and proof.forged_completion_status in {404, 405}
        and proof.unauthorized_status == 404
        and proof.protected_ui_hidden
        and proof.reload_persisted,
        "Real local browser, authorization or zero-generation boundary evidence differs.",
    )
    require(
        canonical(raw["initial_sql"]) == canonical(raw["reloaded_sql"])
        and sql.run_id == proof.run_id == api.id
        and sql.project_id == proof.project_id
        and sql.workspace_id == proof.workspace_id
        and sql.model_dump(include=set(Binding.model_fields))
        == api.model_dump(include=set(Binding.model_fields)),
        "API/SQL/reload run, project, workspace or source bindings differ.",
    )
    require(
        sql.hash_valid
        and sql.relational_snapshot_valid
        and not sql.execution_performed
        and not api.execution_performed
        and api.source_current
        and api.cancelled_at is None
        and sql.status == api.status == "awaiting_executor"
        and sql.revision == api.revision == 2
        and sql.created_at == api.created_at == api.updated_at
        and proof.started_at <= sql.created_at <= proof.completed_at
        and sql.generation_records.model_dump() == {"product_manager_runs": 0, "architect_runs": 0}
        and sql.audit_model_requests == 0,
        "SQL run state, timestamps, hash checks or no-execution evidence differs.",
    )
    validate_rows(sql, api, raw)
    validate_snapshot(sql, api, raw["initial_sql"]["source_snapshot"])
    validate_events(sql, api)
    return raw

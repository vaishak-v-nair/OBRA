"""Architect v1 output contract: proposals only, with strict bounded references."""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from orba.pm_schemas import Key, Label, Priority, Prose, RequestModel, StrictModel
from orba.task_graph import analyze

Texts = Annotated[list[Prose], Field(max_length=20)]
Refs = Annotated[list[Key], Field(max_length=40)]


class Overview(StrictModel):
    title: Label
    summary: Prose
    architectural_style: Label
    design_goals: Annotated[list[Prose], Field(min_length=1, max_length=12)]
    constraints: Texts
    assumptions: Texts
    non_goals: Texts


class Technology(StrictModel):
    technology: Label
    responsibility: Prose
    reason: Prose
    alternatives: Texts
    tradeoffs: Texts
    constraints: Texts
    basis: Literal["requirement", "recommendation"]


class Component(StrictModel):
    key: Key
    name: Label
    responsibility: Prose
    inputs: Texts
    outputs: Texts
    dependencies: Refs
    story_refs: Refs
    security_considerations: Texts


class EntityField(StrictModel):
    name: Key
    logical_type: Label
    constraints: Texts


class Entity(StrictModel):
    key: Key
    name: Label
    fields: Annotated[list[EntityField], Field(min_length=1, max_length=30)]
    constraints: Texts
    indexes: Texts
    data_ownership: Prose
    privacy_considerations: Texts


class Relationship(StrictModel):
    source: Key
    target: Key
    description: Prose


class DatabaseDesign(StrictModel):
    notes: Prose
    entities: Annotated[list[Entity], Field(max_length=16)]
    relationships: Annotated[list[Relationship], Field(max_length=30)]


class Endpoint(StrictModel):
    key: Key
    status: Literal["proposed"]
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
    route: Annotated[str, Field(min_length=1, max_length=200, pattern=r"^/[^\s]*$")]
    purpose: Prose
    request_contract: Prose
    response_contract: Prose
    authentication: Prose
    authorization: Prose
    error_behavior: Texts


class APIDesign(StrictModel):
    notes: Prose
    endpoints: Annotated[list[Endpoint], Field(max_length=24)]


class Threat(StrictModel):
    threat: Prose
    mitigation: Prose


class SecurityDesign(StrictModel):
    trust_boundaries: Annotated[list[Prose], Field(min_length=1, max_length=12)]
    authentication_assumptions: Prose
    authorization_model: Prose
    sensitive_data: Texts
    external_integrations: Texts
    secret_management: Prose
    threats: Annotated[list[Threat], Field(min_length=1, max_length=12)]


class Deployment(StrictModel):
    topology: Prose
    infrastructure_requirements: Texts
    operational_considerations: Texts
    uncertain_choices: Texts


class Decision(StrictModel):
    key: Key
    question: Prose
    blocking: bool


class Task(StrictModel):
    key: Key
    title: Label
    description: Prose
    scope: Prose
    deliverables: Annotated[list[Prose], Field(min_length=1, max_length=12)]
    acceptance_criteria: Annotated[list[Prose], Field(min_length=1, max_length=16)]
    priority: Priority
    category: Literal[
        "frontend",
        "backend",
        "database",
        "infrastructure",
        "integration",
        "security",
        "testing",
        "documentation",
    ]
    complexity_estimate: Literal["small", "medium", "large"] | None
    planning_state: Literal["proposed", "needs_clarification"]
    story_refs: Refs
    requirement_refs: Refs
    criterion_refs: Refs
    component_refs: Annotated[list[Key], Field(min_length=1, max_length=12)]
    dependencies: Refs


class CoverageException(StrictModel):
    kind: Literal["story", "requirement", "criterion", "source_dependency"]
    reference: Annotated[str, Field(min_length=1, max_length=200)]
    reason: Prose


class ArchitectureDocument(StrictModel):
    schema_version: Literal[1]
    overview: Overview
    technologies: Annotated[list[Technology], Field(min_length=1, max_length=12)]
    components: Annotated[list[Component], Field(min_length=1, max_length=12)]
    database_design: DatabaseDesign
    api_design: APIDesign
    security: SecurityDesign
    deployment: Deployment
    risks: Texts
    open_decisions: Annotated[list[Decision], Field(max_length=20)]
    tasks: Annotated[list[Task], Field(min_length=1, max_length=40)]
    coverage_exceptions: Annotated[list[CoverageException], Field(max_length=80)]

    @model_validator(mode="after")
    def integrity(self):
        for label, items in (
            ("component", self.components),
            ("entity", self.database_design.entities),
            ("endpoint", self.api_design.endpoints),
            ("decision", self.open_decisions),
        ):
            keys = [item.key for item in items]
            if len(keys) != len(set(keys)):
                raise ValueError(f"Duplicate {label} key.")
        components = {item.key for item in self.components}
        for component in self.components:
            if (
                component.key in component.dependencies
                or not set(component.dependencies) <= components
            ):
                raise ValueError(f"Invalid component dependency in {component.key}.")
            if len(set(component.dependencies)) != len(component.dependencies):
                raise ValueError(f"Duplicate component dependency in {component.key}.")
        for entity in self.database_design.entities:
            names = [field.name for field in entity.fields]
            if len(set(names)) != len(names):
                raise ValueError(f"Duplicate field in entity {entity.key}.")
        entities = {item.key for item in self.database_design.entities}
        for relation in self.database_design.relationships:
            if relation.source not in entities or relation.target not in entities:
                raise ValueError("Database relationship references an unknown entity.")
        for item in [*self.components, *self.tasks]:
            for name in ("story_refs", "requirement_refs", "criterion_refs", "component_refs"):
                refs = getattr(item, name, [])
                if len(refs) != len(set(refs)):
                    raise ValueError(f"Duplicate {name} in {item.key}.")
            if hasattr(item, "component_refs") and not set(item.component_refs) <= components:
                raise ValueError(f"Unknown component reference in {item.key}.")
        analyze(self.tasks)
        try:
            encoded = self.model_dump_json().encode("utf-8")
        except UnicodeEncodeError:
            raise ValueError("Architecture text must contain valid Unicode.") from None
        if len(encoded) > 512 * 1024 or len(encoded.decode()) > 100000:
            raise ValueError("Architecture exceeds the complete document limit.")
        return self


class ArchitectRunCreate(RequestModel):
    client_request_id: UUID
    source_plan_id: UUID
    source_version: Annotated[int, Field(ge=1)]
    source_revision: Annotated[int, Field(ge=1)]
    constraints: Annotated[str, Field(max_length=4000)] = ""


class ArchitectureUpdate(RequestModel):
    expected_revision: Annotated[int, Field(ge=1)]
    document: ArchitectureDocument


class ArchitectureApprove(RequestModel):
    version: Annotated[int, Field(ge=1)]
    expected_revision: Annotated[int, Field(ge=1)]
    acknowledgments: dict[str, Prose] = Field(default_factory=dict, max_length=100)


class ArchitectureCopy(RequestModel):
    version: Annotated[int, Field(ge=1)]
    expected_revision: Annotated[int, Field(ge=1)]
    client_request_id: UUID


class ArchitectRunRead(BaseModel):
    id: UUID
    project_id: UUID
    workspace_id: UUID
    initiator_id: UUID
    client_request_id: UUID
    source_plan_id: UUID
    source_version: int
    source_revision: int
    source_hash: str
    status: Literal["pending", "running", "succeeded", "failed", "interrupted"]
    provider: str
    requested_model: str | None
    returned_model: str | None
    prompt_version: str
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    deadline_at: datetime
    provider_response_id: str | None
    provider_request_id: str | None
    usage: dict | None
    error_category: str | None
    diagnostic_id: UUID | None
    architecture_id: UUID | None


class ArchitectRunDetail(ArchitectRunRead):
    input_snapshot: dict


class ArchitectureSummary(BaseModel):
    id: UUID
    project_id: UUID
    source_plan_id: UUID
    source_version: int
    source_revision: int
    source_hash: str
    version: int
    revision: int
    state: Literal["draft", "approved", "superseded"]
    content_hash: str
    hash_version: str
    creator_id: UUID
    editor_id: UUID
    approved_by: UUID | None
    approved_at: datetime | None
    created_at: datetime
    updated_at: datetime
    generating_run_id: UUID | None
    copied_from_id: UUID | None
    copy_request_id: UUID | None
    approval_dispositions: dict | None


class ArchitectureRead(ArchitectureSummary):
    document: ArchitectureDocument
    source_document: dict
    source_current: bool
    graph: dict
    coverage: dict
    generation: ArchitectRunRead | None


class ArchitectureView(BaseModel):
    architecture_id: UUID
    version: int
    revision: int
    content_hash: str
    source_current: bool


class ArchitectureTasksRead(ArchitectureView):
    tasks: list[Task]


class ArchitectureGraphRead(ArchitectureView):
    graph: dict


class ArchitectureCoverageRead(ArchitectureView):
    coverage: dict

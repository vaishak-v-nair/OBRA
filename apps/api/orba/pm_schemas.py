"""The authoritative PM document contract, graph integrity and source traceability."""

import json
import re
from collections.abc import Iterator
from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

Key = Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[a-zA-Z][a-zA-Z0-9_-]*$")]
Label = Annotated[str, Field(min_length=1, max_length=200)]
Prose = Annotated[str, Field(min_length=1, max_length=2000)]
Priority = Literal["P0", "P1", "P2", "P3"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)


class Source(StrictModel):
    kind: Literal[
        "brief",
        "title",
        "description",
        "instructions",
        "context",
        "suggested",
        "assumption",
        "human",
    ]
    quote: Annotated[str, Field(min_length=1, max_length=1000)] | None = None
    context_key: Key | None = None
    actor_id: str | None = None
    inherited_kind: str | None = None


class Statement(StrictModel):
    key: Key
    text: Prose
    source: Source


class Confirmation(Statement):
    blocking: bool
    active: bool = True
    disposition: Literal["unresolved", "resolved", "deferred"] = "unresolved"
    reason: Annotated[str, Field(min_length=1, max_length=2000)] | None = None
    actor_id: str | None = None
    decided_at: str | None = None

    @model_validator(mode="after")
    def disposition_integrity(self):
        if self.disposition != "unresolved" and not self.reason:
            raise ValueError("Resolved or deferred confirmations need a reason.")
        if not self.active and self.disposition == "unresolved":
            raise ValueError("Retired confirmations need an explicit disposition.")
        return self


class Criterion(StrictModel):
    key: Key
    given: Annotated[str, Field(min_length=1, max_length=500)]
    when: Annotated[str, Field(min_length=1, max_length=500)]
    then: Annotated[str, Field(min_length=1, max_length=500)]
    source: Source


class Story(StrictModel):
    key: Key
    title: Label
    statement: Annotated[str, Field(min_length=1, max_length=1000)]
    description: Prose
    priority: Priority
    requirement_refs: Annotated[list[Key], Field(min_length=1, max_length=10)]
    dependencies: Annotated[list[Key], Field(max_length=10)]
    source: Source
    acceptance_criteria: Annotated[list[Criterion], Field(min_length=1, max_length=40)]

    @model_validator(mode="after")
    def statement_format(self):
        if not re.fullmatch(r"As an? .+, I want .+, so that .+", self.statement, re.DOTALL):
            raise ValueError("Use 'As a [user], I want [capability], so that [benefit]'.")
        return self


class Epic(StrictModel):
    key: Key
    title: Label
    goal: Prose
    priority: Priority
    source: Source
    stories: Annotated[list[Story], Field(min_length=1, max_length=40)]


class ProductDocument(StrictModel):
    schema_version: Literal[1]
    product_name: Statement
    summary: Statement
    problem_statement: Statement
    proposed_solution: Statement
    target_users: Annotated[list[Statement], Field(min_length=1, max_length=10)]
    user_goals: Annotated[list[Statement], Field(min_length=1, max_length=10)]
    in_scope: Annotated[list[Statement], Field(min_length=1, max_length=20)]
    out_of_scope: Annotated[list[Statement], Field(max_length=20)]
    functional_requirements: Annotated[list[Statement], Field(min_length=1, max_length=40)]
    nonfunctional_requirements: Annotated[list[Statement], Field(max_length=20)]
    prerequisites: Annotated[list[Statement], Field(max_length=20)]
    assumptions: Annotated[list[Statement], Field(max_length=20)]
    risks: Annotated[list[Statement], Field(max_length=20)]
    open_questions: Annotated[list[Statement], Field(max_length=20)]
    confirmations: Annotated[list[Confirmation], Field(max_length=20)]
    epics: Annotated[list[Epic], Field(min_length=1, max_length=8)]

    @model_validator(mode="after")
    def integrity(self):
        nodes = list(document_nodes(self))
        keys = [node.key for _, node in nodes]
        if len(set(keys)) != len(keys):
            raise ValueError("Every document node needs a unique stable key.")
        stories = [story for epic in self.epics for story in epic.stories]
        criteria = [criterion for story in stories for criterion in story.acceptance_criteria]
        if len(stories) > 40 or len(criteria) > 160:
            raise ValueError("A plan supports at most 40 stories and 160 criteria.")
        requirements = {
            s.key for s in self.functional_requirements + self.nonfunctional_requirements
        }
        graph = {story.key: story.dependencies for story in stories}
        for story in stories:
            if len(set(story.requirement_refs)) != len(story.requirement_refs):
                raise ValueError(f"Duplicate requirement reference in {story.key}.")
            if not set(story.requirement_refs) <= requirements:
                raise ValueError(f"Unknown requirement reference in {story.key}.")
            if len(set(story.dependencies)) != len(story.dependencies):
                raise ValueError(f"Duplicate dependency in {story.key}.")
            if not set(story.dependencies) <= graph.keys() or story.key in story.dependencies:
                raise ValueError(f"Unknown or self dependency in {story.key}.")
        visiting, visited = set(), set()

        def visit(key):
            if key in visiting:
                raise ValueError("Story dependencies must not contain cycles.")
            if key in visited:
                return
            visiting.add(key)
            for dependency in graph[key]:
                visit(dependency)
            visiting.remove(key)
            visited.add(key)

        for key in graph:
            visit(key)
        encoded = self.model_dump_json().encode("utf-8")
        if len(encoded) > 512 * 1024 or len(encoded.decode()) > 80000:
            raise ValueError("The complete document exceeds its size limit.")
        return self


def document_nodes(
    document: ProductDocument,
) -> Iterator[tuple[str, Statement | Epic | Story | Criterion]]:
    """Yield every attributed node with its semantic parent; order alone is not an edit."""
    for field in ProductDocument.model_fields:
        value = getattr(document, field)
        if field == "epics":
            for epic in value:
                yield "epics", epic
                for story in epic.stories:
                    yield epic.key, story
                    for criterion in story.acceptance_criteria:
                        yield story.key, criterion
        elif isinstance(value, Statement):
            yield field, value
        elif isinstance(value, list):
            for node in value:
                yield field, node


def node_text(node) -> str:
    if isinstance(node, Statement):
        return node.text
    if isinstance(node, Epic):
        return f"{node.title}\n{node.goal}"
    if isinstance(node, Story):
        return f"{node.title}\n{node.statement}\n{node.description}"
    return f"{node.given}\n{node.when}\n{node.then}"


def validate_generated(document: ProductDocument, snapshot: dict) -> ProductDocument:
    """Verify textual sources and reject model-created human authority."""
    sources = {
        name: snapshot.get(name, "") for name in ("brief", "title", "description", "instructions")
    }
    context = snapshot.get("context_nodes", {})
    for _, node in document_nodes(document):
        source = node.source
        if (
            source.kind == "human"
            or source.actor_id is not None
            or source.inherited_kind is not None
        ):
            raise ValueError("A model cannot assert human editing or inherited authority.")
        if source.kind in sources:
            if not source.quote or source.quote not in sources[source.kind]:
                raise ValueError(f"Source quotation does not match supplied {source.kind}.")
        elif source.kind == "context":
            original = context.get(source.context_key)
            if not original or not source.quote or source.quote not in original["text"]:
                raise ValueError("Context quotation does not match the selected plan node.")
            source.inherited_kind = original["origin"]
        elif source.quote is not None or source.context_key is not None:
            raise ValueError("Suggestions and assumptions cannot claim supplied-source quotations.")
    for confirmation in document.confirmations:
        if (
            confirmation.disposition != "unresolved"
            or confirmation.reason is not None
            or confirmation.actor_id is not None
            or confirmation.decided_at is not None
            or not confirmation.active
        ):
            raise ValueError("A model cannot resolve, defer or retire human confirmations.")
    # A model cannot erase a selected plan's unresolved human obligation by
    # omitting it, rewording it, or downgrading its blocking flag. Inherit that
    # evidence on the server, including across repeated context generations.
    for key, original in context.items():
        if original.get("blocking") and original.get("disposition") == "unresolved":
            occupied = {node.key: node for _, node in document_nodes(document)}
            if key in occupied and not isinstance(occupied[key], Confirmation):
                raise ValueError("An inherited confirmation key collides with another node.")
            document.confirmations = [c for c in document.confirmations if c.key != key]
            document.confirmations.append(
                Confirmation(
                    key=key,
                    text=original["text"],
                    blocking=True,
                    source=Source(
                        kind="context",
                        context_key=key,
                        quote=original["text"][:1000],
                        inherited_kind=original["origin"],
                    ),
                )
            )
    return ProductDocument.model_validate_json(document.model_dump_json())


def node_content(parent: str, node) -> dict:
    return {
        "parent": parent,
        **node.model_dump(
            exclude={
                "source",
                "stories",
                "acceptance_criteria",
                "disposition",
                "reason",
                "actor_id",
                "decided_at",
                "active",
            }
        ),
    }


def attribute_edits(old: ProductDocument, incoming: ProductDocument, actor: UUID, timestamp: str):
    """Ignore client provenance claims and retain persisted blocking-item evidence."""
    previous = {node.key: (parent, node) for parent, node in document_nodes(old)}
    new_nodes = {node.key: node for _, node in document_nodes(incoming)}
    for confirmation in old.confirmations:
        proposed = new_nodes.get(confirmation.key)
        if confirmation.blocking:
            if proposed is None:
                if confirmation.disposition == "unresolved":
                    raise ValueError(
                        f"Resolve or defer blocking item {confirmation.key} before retirement."
                    )
                retired = confirmation.model_copy(deep=True)
                retired.active = False
                incoming.confirmations.append(retired)
            elif not isinstance(proposed, Confirmation) or (
                proposed.text != confirmation.text or not proposed.blocking
            ):
                raise ValueError(
                    f"Retain original blocking item {confirmation.key}; dispose it explicitly."
                )
    for parent, node in document_nodes(incoming):
        prior = previous.get(node.key)
        if prior and node_content(parent, node) == node_content(*prior):
            node.source = prior[1].source.model_copy(deep=True)
        else:
            node.source = Source(kind="human", actor_id=str(actor))
        if isinstance(node, Confirmation):
            original = prior[1] if prior and isinstance(prior[1], Confirmation) else None
            if node.disposition != "unresolved":
                if not node.reason:
                    raise ValueError(f"Confirmation {node.key} needs a disposition reason.")
                if original and (node.disposition, node.reason) == (
                    original.disposition,
                    original.reason,
                ):
                    node.actor_id, node.decided_at = original.actor_id, original.decided_at
                else:
                    node.actor_id, node.decided_at = str(actor), timestamp
            else:
                node.actor_id = node.decided_at = node.reason = None
    return ProductDocument.model_validate_json(incoming.model_dump_json())


class RequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class RunCreate(RequestModel):
    client_request_id: UUID
    brief: Annotated[str, Field(min_length=1, max_length=10000)]
    instructions: Annotated[str, Field(max_length=4000)] = ""
    context_plan_id: UUID | None = None
    context_revision: Annotated[int, Field(ge=1)] | None = None

    @model_validator(mode="after")
    def context_pair(self):
        if (self.context_plan_id is None) != (self.context_revision is None):
            raise ValueError("Choose an exact context plan and revision together.")
        return self


class PlanUpdate(RequestModel):
    expected_revision: Annotated[int, Field(ge=1)]
    document: ProductDocument


class PlanApprove(RequestModel):
    version: Annotated[int, Field(ge=1)]
    expected_revision: Annotated[int, Field(ge=1)]


class PlanCopy(PlanApprove):
    client_request_id: UUID


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


HASH_VERSION = "orba-pm-canonical-json-v1"


class CapabilityRead(BaseModel):
    provider: str
    configured: bool
    model: str | None
    timeout_seconds: int
    max_output_tokens: int
    setup_message: str | None


class RunRead(BaseModel):
    id: UUID
    project_id: UUID
    workspace_id: UUID
    initiator_id: UUID
    client_request_id: UUID
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
    plan_id: UUID | None


class RunDetail(RunRead):
    input_snapshot: dict


class PlanSummary(BaseModel):
    id: UUID
    project_id: UUID
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
    source_plan_id: UUID | None
    source_revision: int | None
    copy_request_id: UUID | None
    origin: Literal["generated", "human_copy", "human_authored"]


class PlanRead(PlanSummary):
    document: ProductDocument
    generation: RunRead | None
    inputs: dict | None


class Page[Item](BaseModel):
    items: list[Item]
    limit: int
    offset: int
    next_offset: int | None
    capability: CapabilityRead | None = None

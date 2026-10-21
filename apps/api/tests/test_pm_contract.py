"""Pure contract tests. Synthetic documents are explicitly unit inputs."""

from uuid import uuid4

import pytest
from pm_support import unit_output
from pydantic import ValidationError

from orba.pm_schemas import (
    Confirmation,
    ProductDocument,
    Source,
    attribute_edits,
    validate_generated,
)


def test_valid_contract_and_exact_source_quote():
    doc = unit_output()
    doc.summary.source = Source(kind="brief", quote="daily check-ins")
    assert (
        validate_generated(doc, {"brief": "Track daily check-ins"}).summary.source.kind == "brief"
    )
    doc.summary.source.quote = "nonexistent quote"
    with pytest.raises(ValueError, match="quotation"):
        validate_generated(doc, {"brief": "Track daily check-ins"})


def test_additional_instructions_have_exact_source_traceability():
    doc = unit_output()
    doc.summary.source = Source(kind="instructions", quote="single user")
    assert (
        validate_generated(doc, {"instructions": "Keep this for a single user"}).summary.source.kind
        == "instructions"
    )


@pytest.mark.parametrize(
    "change",
    [
        "empty_epics",
        "empty_criteria",
        "duplicate_key",
        "unknown_ref",
        "dependency",
        "story_format",
        "unknown_field",
        "wrong_type",
    ],
)
def test_rejects_incomplete_or_invalid_graph(change):
    value = unit_output().model_dump(mode="json")
    story = value["epics"][0]["stories"][0]
    if change == "empty_epics":
        value["epics"] = []
    if change == "empty_criteria":
        story["acceptance_criteria"] = []
    if change == "duplicate_key":
        value["summary"]["key"] = value["product_name"]["key"]
    if change == "unknown_ref":
        story["requirement_refs"] = ["unknown"]
    if change == "dependency":
        story["dependencies"] = [story["key"]]
    if change == "story_format":
        story["statement"] = "It should work perfectly"
    if change == "unknown_field":
        value["fake_success"] = True
    if change == "wrong_type":
        value["schema_version"] = "1"
    with pytest.raises(ValidationError):
        ProductDocument.model_validate(value)


def test_dependency_cycle_is_rejected():
    value = unit_output().model_dump(mode="json")
    a = value["epics"][0]["stories"][0]
    b = {
        **a,
        "key": "story_second",
        "acceptance_criteria": [{**a["acceptance_criteria"][0], "key": "criterion_second"}],
        "dependencies": [a["key"]],
    }
    a["dependencies"] = [b["key"]]
    value["epics"][0]["stories"].append(b)
    with pytest.raises(ValidationError, match="cycles"):
        ProductDocument.model_validate(value)


@pytest.mark.parametrize("kind", ["human", "spoof_actor", "spoof_inheritance", "resolved"])
def test_model_cannot_assert_human_authority(kind):
    doc = unit_output()
    if kind == "human":
        doc.summary.source = Source(kind="human")
    if kind == "spoof_actor":
        doc.summary.source.actor_id = "owner"
    if kind == "spoof_inheritance":
        doc.summary.source.inherited_kind = "brief"
    if kind == "resolved":
        doc.confirmations = [
            Confirmation(
                key="confirm",
                text="Confirm timezone",
                source=Source(kind="suggested"),
                blocking=True,
                disposition="resolved",
                reason="Model decided",
            )
        ]
    with pytest.raises(ValueError):
        validate_generated(doc, {})


def test_unresolved_context_blocker_survives_two_generations_and_omission():
    context = {
        "blocker": {
            "text": "Confirm the reporting timezone",
            "origin": "assumption",
            "blocking": True,
            "active": True,
            "disposition": "unresolved",
        }
    }
    first = validate_generated(unit_output(), {"context_nodes": context})
    inherited = first.confirmations[0]
    assert inherited.key == "blocker" and inherited.source.inherited_kind == "assumption"
    second = validate_generated(
        unit_output(),
        {
            "context_nodes": {
                "blocker": {**context["blocker"], "origin": inherited.source.inherited_kind}
            }
        },
    )
    assert second.confirmations[0].blocking and second.confirmations[0].disposition == "unresolved"


def test_human_edit_provenance_and_blocker_disposition_are_server_owned():
    original = unit_output()
    original.confirmations = [
        Confirmation(
            key="confirm", text="Confirm timezone", source=Source(kind="assumption"), blocking=True
        )
    ]
    edited = original.model_copy(deep=True)
    edited.summary.text = "A corrected summary"
    edited.summary.source = Source(kind="brief", quote="forged")
    actor = uuid4()
    edited.confirmations[0].disposition = "deferred"
    edited.confirmations[0].reason = "The owner will choose a timezone before implementation."
    result = attribute_edits(original, edited, actor, "2026-10-19T00:00:00Z")
    assert result.summary.source.kind == "human" and result.summary.source.actor_id == str(actor)
    assert result.confirmations[0].actor_id == str(actor)
    assert result.product_name.source.kind == "suggested"
    retired = result.model_copy(deep=True)
    retired.confirmations = []
    assert (
        not attribute_edits(result, retired, actor, "2026-10-19T00:00:00Z").confirmations[0].active
    )
    removed = original.model_copy(deep=True)
    removed.confirmations = []
    with pytest.raises(ValueError, match="Resolve or defer"):
        attribute_edits(original, removed, actor, "2026-10-19T00:00:00Z")

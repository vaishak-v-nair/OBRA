import pytest
from pydantic import ValidationError

from orba.architect_schemas import ArchitectureDocument
from orba.architect_traceability import coverage
from scripts.architect_sample import controlled_document
from scripts.pm_sample import human_document


def test_complete_contract_and_source_coverage():
    document = controlled_document()
    report = coverage(document, human_document("fixture"))
    assert report["approvable"] and report["covered_stories"] == ["story_checkin"]
    assert report["covered_criteria"] == ["criterion_checkin"]


def test_source_component_task_trace_chain_cannot_be_omitted():
    document = controlled_document()
    document.components[0].story_refs = []
    report = coverage(document, human_document("fixture"))
    assert not report["approvable"] and report["component_gaps"] == [
        "storage:story_checkin",
        "screen:story_checkin",
    ]
    value = controlled_document().model_dump()
    value["tasks"][0]["component_refs"] = []
    with pytest.raises(ValidationError):
        ArchitectureDocument.model_validate(value)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda d: d.update(schema_version=2),
        lambda d: d.update(execution_status="completed"),
        lambda d: d["tasks"][0].update(planning_state="tests_passed"),
        lambda d: d["tasks"][0].update(acceptance_criteria=[]),
        lambda d: d["tasks"][0].update(dependencies=["screen"]),
        lambda d: d["tasks"][0].update(component_refs=["missing"]),
        lambda d: d["api_design"]["endpoints"][0].update(status="implemented"),
        lambda d: d["database_design"]["relationships"].append(
            {"source": "checkin", "target": "missing", "description": "Invalid"}
        ),
    ],
)
def test_invalid_contract_rejected(mutation):
    value = controlled_document().model_dump()
    mutation(value)
    with pytest.raises(ValidationError):
        ArchitectureDocument.model_validate(value)


@pytest.mark.parametrize("field", ["story_refs", "requirement_refs", "criterion_refs"])
def test_source_references_are_authoritative(field):
    document = controlled_document()
    setattr(document.tasks[0], field, ["forged"])
    with pytest.raises(ValueError):
        coverage(document, human_document("fixture"))


def test_criterion_must_belong_to_referenced_story():
    document = controlled_document()
    document.tasks[0].story_refs = []
    with pytest.raises(ValueError, match="belong"):
        coverage(document, human_document("fixture"))


def test_missing_links_and_clarification_block_approval():
    document = controlled_document()
    for task in document.tasks:
        task.criterion_refs = []
    document.tasks[0].planning_state = "needs_clarification"
    result = coverage(document, human_document("fixture"))
    assert not result["approvable"] and result["unaccounted_gaps"][0]["kind"] == "criterion"


def test_exception_requires_exact_current_gap_and_human_review():
    value = controlled_document().model_dump()
    for task in value["tasks"]:
        task["criterion_refs"] = []
    value["coverage_exceptions"] = [
        {
            "kind": "criterion",
            "reference": "criterion_checkin",
            "reason": "Review deferred with operator",
        }
    ]
    report = coverage(ArchitectureDocument.model_validate(value), human_document("fixture"))
    assert (
        report["approvable"]
        and report["review_obligations"][0]["id"] == "exception:criterion:criterion_checkin"
    )
    value["coverage_exceptions"][0]["reference"] = "forged"
    with pytest.raises(ValueError, match="current"):
        coverage(ArchitectureDocument.model_validate(value), human_document("fixture"))


def test_inherited_confirmation_cannot_be_erased_by_model():
    source = human_document("fixture", blocking_confirmation=True)
    source.confirmations[0].disposition = "deferred"
    source.confirmations[0].reason = "Human will decide platform later"
    report = coverage(controlled_document(), source)
    assert report["review_obligations"][0]["id"] == "source_confirmation:confirmation_platform"


def test_all_prerequisite_contributors_are_required():
    source = human_document("fixture")
    story = source.epics[0].stories[0].model_copy(deep=True)
    story.key = "story_review"
    story.dependencies = ["story_checkin"]
    story.acceptance_criteria[0].key = "criterion_review"
    source.epics[0].stories.append(story)
    doc = controlled_document()
    task = doc.tasks[0].model_copy(deep=True)
    task.key = "review"
    task.story_refs = ["story_review"]
    task.criterion_refs = []
    task.dependencies = ["storage"]
    doc.tasks.append(task)
    assert any(g["kind"] == "source_dependency" for g in coverage(doc, source)["gaps"])
    task.dependencies = ["screen"]
    assert not any(g["kind"] == "source_dependency" for g in coverage(doc, source)["gaps"])

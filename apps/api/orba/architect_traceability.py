"""Structural source linkage, never semantic completeness or implementation proof."""

from orba.task_graph import analyze


def coverage(document, source):
    stories = {story.key: story for epic in source.epics for story in epic.stories}
    requirements = {
        item.key for item in source.functional_requirements + source.nonfunctional_requirements
    }
    criteria = {
        criterion.key: story.key
        for story in stories.values()
        for criterion in story.acceptance_criteria
    }
    for component in document.components:
        if not set(component.story_refs) <= stories.keys():
            raise ValueError(f"Unknown source story in component {component.key}.")
    for task in document.tasks:
        if not set(task.story_refs) <= stories.keys():
            raise ValueError(f"Unknown source story in task {task.key}.")
        if not set(task.requirement_refs) <= requirements:
            raise ValueError(f"Unknown source requirement in task {task.key}.")
        if any(criteria.get(key) not in task.story_refs for key in task.criterion_refs):
            raise ValueError(
                f"Criterion references must belong to referenced stories in task {task.key}."
            )
    graph = analyze(document.tasks)
    covered_stories = {key for task in document.tasks for key in task.story_refs}
    covered_requirements = {key for task in document.tasks for key in task.requirement_refs}
    covered_criteria = {key for task in document.tasks for key in task.criterion_refs}
    gaps = []
    for kind, missing in (
        ("story", stories.keys() - covered_stories),
        ("requirement", requirements - covered_requirements),
        ("criterion", criteria.keys() - covered_criteria),
    ):
        gaps.extend(
            {"id": f"{kind}:{key}", "kind": kind, "reference": key} for key in sorted(missing)
        )
    ancestors = {node["key"]: set(node["ancestors"]) for node in graph["nodes"]}
    for task in document.tasks:
        for story_key in task.story_refs:
            for prerequisite in stories[story_key].dependencies:
                required_tasks = {
                    item.key for item in document.tasks if prerequisite in item.story_refs
                } - {task.key}
                if not required_tasks or not required_tasks <= ancestors[task.key]:
                    # A combined task covers both stories itself; other contributors still count.
                    if prerequisite in task.story_refs and required_tasks <= ancestors[task.key]:
                        continue
                    reference = f"{story_key}:{prerequisite}:{task.key}"
                    gaps.append(
                        {
                            "id": f"source_dependency:{reference}",
                            "kind": "source_dependency",
                            "reference": reference,
                        }
                    )
    gap_by_id = {item["id"]: item for item in gaps}
    exceptions = {}
    for item in document.coverage_exceptions:
        key = f"{item.kind}:{item.reference}"
        if key not in gap_by_id or key in exceptions:
            raise ValueError("Coverage exceptions must identify distinct current source gaps.")
        exceptions[key] = item.reason
    component_stories = {item.key: set(item.story_refs) for item in document.components}
    component_gaps = [
        f"{task.key}:{story}"
        for task in document.tasks
        for story in task.story_refs
        if not any(story in component_stories[key] for key in task.component_refs)
    ]
    orphan_tasks = [
        task.key for task in document.tasks if not task.story_refs or not task.requirement_refs
    ]
    clarification = [
        task.key for task in document.tasks if task.planning_state == "needs_clarification"
    ]
    obligations = [
        {"id": f"exception:{key}", "reason": reason} for key, reason in sorted(exceptions.items())
    ]
    obligations += [
        {"id": f"decision:{item.key}", "reason": item.question}
        for item in document.open_decisions
        if item.blocking
    ]
    obligations += [
        {
            "id": f"source_confirmation:{item.key}",
            "reason": item.text + " — " + (item.reason or "Unresolved source uncertainty"),
        }
        for item in source.confirmations
        if item.blocking and item.disposition != "resolved"
    ]
    uncovered = [item for item in gaps if item["id"] not in exceptions]
    return {
        "meaning": "Structural linkage only; no semantic completeness or implementation is certified.",
        "covered_stories": sorted(covered_stories),
        "covered_requirements": sorted(covered_requirements),
        "covered_criteria": sorted(covered_criteria),
        "gaps": gaps,
        "unaccounted_gaps": uncovered,
        "orphan_tasks": orphan_tasks,
        "component_gaps": component_gaps,
        "needs_clarification": clarification,
        "open_decisions": [item.model_dump() for item in document.open_decisions],
        "review_obligations": obligations,
        "approvable": not uncovered
        and not orphan_tasks
        and not clarification
        and not component_gaps,
    }

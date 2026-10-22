"""Pure bounded planning graph. A -> B means B depends on A; no task executes here."""

import heapq


class GraphError(ValueError):
    def __init__(self, message, *, task=None, path=None):
        super().__init__(message)
        self.task, self.path = task, path or []


def analyze(tasks):
    """Deterministic Kahn order, prerequisite closure and transitive impact."""
    keys = [task.key for task in tasks]
    if len(keys) > 40 or len(set(keys)) != len(keys):
        raise GraphError("Use at most40 tasks with unique stable keys.")
    nodes = {task.key: task for task in tasks}
    position = {key: index for index, key in enumerate(keys)}
    dependencies, dependents = {}, {key: [] for key in keys}
    for task in tasks:
        deps = task.dependencies
        if len(set(deps)) != len(deps):
            raise GraphError(f"Duplicate prerequisite in {task.key}.", task=task.key)
        if task.key in deps:
            raise GraphError(f"Task {task.key} cannot depend on itself.", task=task.key)
        missing = sorted(set(deps) - nodes.keys())
        if missing:
            raise GraphError(
                f"Task {task.key} references missing prerequisite {missing[0]}.", task=task.key
            )
        dependencies[task.key] = list(deps)
        for prerequisite in deps:
            dependents[prerequisite].append(task.key)
    remaining = {key: len(value) for key, value in dependencies.items()}
    ready = [(position[key], key) for key in keys if not remaining[key]]
    heapq.heapify(ready)
    ordered = []
    while ready:
        _, key = heapq.heappop(ready)
        ordered.append(key)
        for child in dependents[key]:
            remaining[child] -= 1
            if remaining[child] == 0:
                heapq.heappush(ready, (position[child], child))
    if len(ordered) != len(keys):
        visiting, visited, path = set(), set(), []

        def visit(key):
            if key in visiting:
                cycle = path[path.index(key) :] + [key]
                raise GraphError("Dependency cycle: " + " -> ".join(cycle), task=key, path=cycle)
            if key in visited:
                return
            visiting.add(key)
            path.append(key)
            for child in dependents[key]:
                visit(child)
            visiting.remove(key)
            path.pop()
            visited.add(key)

        for key in keys:
            visit(key)
        raise GraphError("Dependency graph contains a cycle.")
    ancestors = {}
    for key in ordered:
        parents = set(dependencies[key])
        for parent in dependencies[key]:
            parents.update(ancestors[parent])
        ancestors[key] = parents
    impacts = {key: [child for child in ordered if key in ancestors[child]] for key in keys}
    states = []
    for key in ordered:
        clarification = getattr(nodes[key], "planning_state", "proposed") == "needs_clarification"
        states.append(
            {
                "key": key,
                "state": "needs_clarification"
                if clarification
                else "blocked"
                if dependencies[key]
                else "ready",
                "explanation": "Needs clarification before future execution."
                if clarification
                else "Blocked by unexecuted planning prerequisites: " + ", ".join(dependencies[key])
                if dependencies[key]
                else "No prerequisites in this planning graph; not executed.",
                "prerequisites": dependencies[key],
                "dependents": dependents[key],
                "ancestors": [parent for parent in ordered if parent in ancestors[key]],
                "impact": impacts[key],
            }
        )
    return {
        "valid": True,
        "edge_convention": "prerequisite -> dependent",
        "topological_order": ordered,
        "edges": [
            {"prerequisite": parent, "dependent": child}
            for child in keys
            for parent in dependencies[child]
        ],
        "nodes": states,
        "ready": [item["key"] for item in states if item["state"] == "ready"],
        "blocked": [item["key"] for item in states if item["state"] == "blocked"],
        "execution_performed": False,
    }

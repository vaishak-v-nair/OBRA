"""Pure dependency eligibility, not a scheduler and never an execution assertion."""

from orba.task_graph import GraphError, analyze


def evaluate(tasks, *, cancelled=False):
    graph = analyze(tasks)
    if not tasks or any(task.planning_state != "proposed" for task in tasks):
        raise GraphError(
            "An approved execution plan must contain proposed tasks without clarification gaps."
        )
    nodes = []
    for node in graph["nodes"]:
        parents = node["prerequisites"]
        eligibility = "waiting_prerequisites" if parents else "eligible"
        nodes.append(
            {
                **{
                    key: node[key]
                    for key in ("key", "prerequisites", "dependents", "ancestors", "impact")
                },
                "eligibility": eligibility,
                "execution_status": "cancelled" if cancelled else "awaiting_executor",
                "explanation": "This run is cancelled. No task was executed or completed."
                if cancelled
                else "Waiting for " + ", ".join(parents) + " to complete with verified evidence."
                if parents
                else "No unmet prerequisites. Eligible for future dispatch; awaiting an execution agent. No code has been run.",
            }
        )
    roots = [node["key"] for node in nodes if not node["prerequisites"]]
    return {
        "valid": True,
        "edge_convention": graph["edge_convention"],
        "topological_order": graph["topological_order"],
        "roots": roots,
        "eligible": [] if cancelled else roots,
        "blocked": [node["key"] for node in nodes if node["prerequisites"]],
        "nodes": nodes,
        "edges": graph["edges"],
        "execution_performed": False,
    }

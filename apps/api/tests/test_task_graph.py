from types import SimpleNamespace

import pytest

from orba.task_graph import GraphError, analyze


def tasks(edges):
    return [
        SimpleNamespace(key=key, dependencies=deps, planning_state="proposed")
        for key, deps in edges
    ]


def test_diamond_order_readiness_and_impact():
    graph = analyze(tasks([("a", []), ("b", ["a"]), ("c", ["a"]), ("d", ["b", "c"])]))
    assert graph["topological_order"] == ["a", "b", "c", "d"]
    assert graph["ready"] == ["a"] and graph["blocked"] == ["b", "c", "d"]
    assert graph["nodes"][0]["impact"] == ["b", "c", "d"]
    assert graph["nodes"][-1]["ancestors"] == ["a", "b", "c"]
    assert graph["execution_performed"] is False
    assert "not executed" in graph["nodes"][0]["explanation"]


@pytest.mark.parametrize(
    "edges,match",
    [
        ([("a", ["b"]), ("b", ["a"])], "cycle"),
        ([("a", ["c"]), ("b", ["a"]), ("c", ["b"])], "cycle"),
        ([("a", ["a"])], "itself"),
        ([("a", ["missing"])], "missing"),
        ([("a", []), ("b", ["a", "a"])], "Duplicate"),
        ([("a", []), ("a", [])], "unique"),
    ],
)
def test_invalid_graphs(edges, match):
    with pytest.raises(GraphError, match=match):
        analyze(tasks(edges))


def test_independent_order_is_explicit_display_order_not_priority():
    assert analyze(tasks([("z", []), ("a", [])]))["topological_order"] == ["z", "a"]
    assert analyze([])["topological_order"] == []


def test_clarification_is_not_execution_ready():
    node = SimpleNamespace(key="a", dependencies=[], planning_state="needs_clarification")
    graph = analyze([node])
    assert graph["ready"] == [] and graph["nodes"][0]["state"] == "needs_clarification"

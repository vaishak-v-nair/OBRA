"""Forced real PostgreSQL schedules with human-authored plan fixtures."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import UUID

from pm_support import project, seed
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from orba.pm_models import ProductPlan


def test_two_editors_same_revision_only_one_save_commits(client):
    pid = project(client)
    plan_id = seed(client, pid)
    path = f"/api/v1/projects/{pid}/pm-plans/{plan_id}"
    document = client.get(path).json()["document"]
    barrier = Barrier(2)

    def save(text):
        import copy

        body = copy.deepcopy(document)
        body["summary"]["text"] = text
        barrier.wait(timeout=10)
        return client.put(path, json={"expected_revision": 1, "document": body}).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(save, ["Editor one", "Editor two"]))
    assert sorted(results) == [200, 409]
    saved = client.get(path).json()
    assert saved["revision"] == 2 and saved["document"]["summary"]["text"] in {
        "Editor one",
        "Editor two",
    }


def test_racing_approvals_leave_one_current_highest_version(client):
    pid = project(client)
    first, second = seed(client, pid), seed(client, pid)
    barrier = Barrier(2)

    def approve(pair):
        plan_id, version = pair
        barrier.wait(timeout=10)
        return client.post(
            f"/api/v1/projects/{pid}/pm-plans/{plan_id}/approve",
            json={"version": version, "expected_revision": 1},
        ).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(approve, [(first, 1), (second, 2)]))
    assert outcomes[1] == 200 and outcomes[0] in {200, 409}
    with Session(client.app.state.engine) as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(ProductPlan)
                .where(ProductPlan.project_id == UUID(pid), ProductPlan.state == "approved")
            )
            == 1
        )
        assert db.get(ProductPlan, second).state == "approved"


def test_plan_get_holds_one_coherent_revision_during_concurrent_save(client):
    """Instrument real SQL scheduling only; no API/data/provider response doubles."""
    from concurrent.futures import TimeoutError as FutureTimeout
    from threading import Event

    import pytest
    from sqlalchemy import event

    pid = project(client)
    plan_id = seed(client, pid)
    path = f"/api/v1/projects/{pid}/pm-plans/{plan_id}"
    original = client.get(path).json()
    document = original["document"]
    document["epics"][0]["stories"][0]["acceptance_criteria"][0]["then"] = (
        "A concurrently saved criterion"
    )
    read_locked, write_attempt, release = Event(), Event(), Event()
    engine = client.app.state.engine

    def before(_connection, _cursor, statement, *_args):
        if "FROM product_plans" in statement and "FOR UPDATE" in statement:
            write_attempt.set()

    def after(_connection, _cursor, statement, *_args):
        if "FROM product_plans" in statement and "FOR SHARE" in statement:
            read_locked.set()
            assert release.wait(5)

    event.listen(engine, "before_cursor_execute", before)
    event.listen(engine, "after_cursor_execute", after)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            reader = pool.submit(client.get, path)
            assert read_locked.wait(5)
            writer = pool.submit(
                client.put, path, json={"expected_revision": 1, "document": document}
            )
            try:
                assert write_attempt.wait(5)
                with pytest.raises(FutureTimeout):
                    writer.result(timeout=0.1)
            finally:
                release.set()
            response = reader.result(timeout=5)
            assert response.status_code == 200
            assert response.json()["revision"] == 1
            assert (
                response.json()["document"]["epics"][0]["stories"][0]["acceptance_criteria"][0][
                    "then"
                ]
                != "A concurrently saved criterion"
            )
            assert writer.result(timeout=5).status_code == 200
    finally:
        release.set()
        event.remove(engine, "before_cursor_execute", before)
        event.remove(engine, "after_cursor_execute", after)
    assert client.get(path).json()["revision"] == 2

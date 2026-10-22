from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from orba.architect_models import ArchitectRun, ArchitectureVersion
from orba.pm import model_provider as pm_provider
from orba.pm_provider import ProviderResult
from tests.architect_support import ControlledProvider, approved_source, artifact, generate, payload
from tests.pm_support import unit_output


def test_simultaneous_same_request_has_one_provider_call(client):
    project_id, source = approved_source(client)
    started, release = Event(), Event()

    def hold(snapshot):
        started.set()
        assert release.wait(5)

    provider = ControlledProvider(callback=hold)
    body = payload(source)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(generate, client, project_id, source, provider, body)
        try:
            assert started.wait(5)
            second, _ = generate(client, project_id, source, provider, body)
            assert second.status_code == 202 and second.json()["status"] == "running"
            assert provider.calls == 1
        finally:
            release.set()
        result, _ = first.result(timeout=5)
        assert result.status_code == 201
    with Session(client.app.state.engine) as db:
        assert db.scalar(select(func.count()).select_from(ArchitectRun)) == 1
        assert db.scalar(select(func.count()).select_from(ArchitectureVersion)) == 1


def test_architect_blocks_pm_when_combined_concurrency_is_one(client):
    project_id, source = approved_source(client)
    client.app.state.settings.pm_max_concurrent = 1
    started, release = Event(), Event()

    def hold(snapshot):
        started.set()
        assert release.wait(5)

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(generate, client, project_id, source, ControlledProvider(callback=hold))
        try:
            assert started.wait(5)
            from uuid import uuid4

            response = client.post(
                f"/api/v1/projects/{project_id}/pm-runs",
                json={"client_request_id": str(uuid4()), "brief": "A daily journal"},
            )
            assert (
                response.status_code == 429
                and response.json()["error"]["code"] == "generation_admission_limited"
            )
        finally:
            release.set()
        assert first.result(timeout=5)[0].status_code == 201


def test_pm_blocks_architect_when_combined_concurrency_is_one(client):
    project_id, source = approved_source(client)
    client.app.state.settings.pm_max_concurrent = 1
    started, release = Event(), Event()

    class PMDouble:
        async def generate(self, snapshot):
            started.set()
            assert release.wait(5)
            return ProviderResult(unit_output().model_dump_json())

    client.app.dependency_overrides[pm_provider] = PMDouble
    with ThreadPoolExecutor(max_workers=2) as pool:
        from uuid import uuid4

        first = pool.submit(
            client.post,
            f"/api/v1/projects/{project_id}/pm-runs",
            json={"client_request_id": str(uuid4()), "brief": "Daily check-ins"},
        )
        try:
            assert started.wait(5)
            response, provider = generate(client, project_id, source)
            assert response.status_code == 429 and provider.calls == 0
        finally:
            release.set()
        assert first.result(timeout=5).status_code == 201


def test_two_architecture_editors_only_one_revision_commits(client):
    import copy

    project_id, source = approved_source(client)
    result, _ = generate(client, project_id, source)
    saved = artifact(client, project_id, result.json())
    barrier = Barrier(2)

    def edit(title):
        document = copy.deepcopy(saved["document"])
        document["overview"]["title"] = title
        barrier.wait(timeout=5)
        return client.put(
            f"/api/v1/projects/{project_id}/architectures/{saved['id']}",
            json={"expected_revision": 1, "document": document},
        ).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(edit, ["Editor A", "Editor B"])) == [200, 409]
    with Session(client.app.state.engine) as db:
        assert db.get(ArchitectureVersion, UUID(saved["id"])).revision == 2


def test_shared_root_lock_prevents_torn_graph_reads(client):
    from concurrent.futures import TimeoutError as FutureTimeout

    import pytest
    from sqlalchemy import event

    project_id, source = approved_source(client)
    result, _ = generate(client, project_id, source)
    saved = artifact(client, project_id, result.json())
    path = f"/api/v1/projects/{project_id}/architectures/{saved['id']}"
    document = saved["document"]
    document["tasks"][0]["acceptance_criteria"] = ["A concurrently saved criterion"]
    locked, writing, release = Event(), Event(), Event()
    engine = client.app.state.engine

    def after(connection, cursor, statement, *args):
        if "FROM architecture_versions" in statement and "FOR SHARE" in statement:
            locked.set()
            assert release.wait(5)

    def before(connection, cursor, statement, *args):
        if "FROM architecture_versions" in statement and "FOR UPDATE" in statement:
            writing.set()

    event.listen(engine, "after_cursor_execute", after)
    event.listen(engine, "before_cursor_execute", before)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            reader = pool.submit(client.get, path)
            assert locked.wait(5)
            writer = pool.submit(
                client.put, path, json={"expected_revision": 1, "document": document}
            )
            try:
                assert writing.wait(5)
                with pytest.raises(FutureTimeout):
                    writer.result(timeout=0.1)
            finally:
                release.set()
            original = reader.result(timeout=5)
            assert original.status_code == 200 and original.json()["revision"] == 1
            assert original.json()["content_hash"] == saved["content_hash"]
            assert writer.result(timeout=5).status_code == 200
    finally:
        release.set()
        event.remove(engine, "after_cursor_execute", after)
        event.remove(engine, "before_cursor_execute", before)


def test_partial_publication_is_not_visible_in_an_independent_session(client):
    from sqlalchemy import event

    project_id, source = approved_source(client)
    inserted, release = Event(), Event()
    engine = client.app.state.engine

    def after(connection, cursor, statement, *args):
        if "INSERT INTO architecture_versions" in statement:
            inserted.set()
            assert release.wait(5)

    event.listen(engine, "after_cursor_execute", after)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            running = pool.submit(generate, client, project_id, source)
            try:
                assert inserted.wait(5)
                with Session(engine) as independent:
                    assert (
                        independent.scalar(select(func.count()).select_from(ArchitectureVersion))
                        == 0
                    )
            finally:
                release.set()
            assert running.result(timeout=5)[0].status_code == 201
    finally:
        release.set()
        event.remove(engine, "after_cursor_execute", after)

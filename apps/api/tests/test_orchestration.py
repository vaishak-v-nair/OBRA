"""Real PostgreSQL/auth/API control-plane integration. No model/executor doubles."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from orba.architect_models import ArchitectureVersion, EngineeringTask, TaskDependency
from orba.models import AuthSession, WorkspaceMember
from orba.orchestration_graph import evaluate
from orba.orchestration_models import (
    OrchestrationDependency,
    OrchestrationEvent,
    OrchestrationRun,
    OrchestrationTask,
)
from orba.orchestration_schemas import RunCreate
from orba.orchestration_service import OrchestrationError, checksum, create_run, transition
from orba.pm_service import db_now
from scripts.architect_sample import controlled_document
from tests.conftest import register
from tests.orchestration_support import body, initialize, path, source_architecture
from tests.pm_support import identity, project, seed


def counts(client):
    with Session(client.app.state.engine) as db:
        return [
            db.scalar(select(func.count()).select_from(model))
            for model in (
                OrchestrationRun,
                OrchestrationTask,
                OrchestrationDependency,
                OrchestrationEvent,
            )
        ]


def test_approved_source_creates_durable_bound_snapshot_and_truthful_events(client):
    project_id, source, payload, saved = initialize(client)
    assert saved["status"] == "awaiting_executor" and saved["revision"] == 2
    assert saved["execution_performed"] is False
    for field, original in (
        ("architecture_id", "id"),
        ("architecture_version", "version"),
        ("architecture_revision", "revision"),
        ("architecture_hash", "content_hash"),
    ):
        assert saved[field] == source[original]
    assert saved["source_plan_id"] == source["source_plan_id"]
    assert saved["source_version"] == source["source_version"]
    assert saved["source_revision"] == source["source_revision"]
    assert saved["source_hash"] == source["source_hash"]
    assert [task["definition"] for task in saved["tasks"]] == source["document"]["tasks"]
    assert saved["graph"]["topological_order"] == ["storage", "screen"]
    assert saved["graph"]["roots"] == saved["graph"]["eligible"] == ["storage"]
    assert saved["graph"]["blocked"] == ["screen"]
    assert saved["tasks"][0]["eligibility"] == "eligible"
    assert saved["tasks"][1]["eligibility"] == "waiting_prerequisites"
    assert all(task["execution_status"] == "awaiting_executor" for task in saved["tasks"])
    assert counts(client) == [1, 2, 1, 2]
    with Session(client.app.state.engine) as db:
        run = db.get(OrchestrationRun, UUID(saved["id"]))
        assert checksum(run.source_snapshot) == saved["snapshot_hash"]
        assert run.source_snapshot["product_plan"]["document"]["epics"]
        assert len(run.source_snapshot["traces"]) == 3
        assert run.client_request_id == UUID(payload["client_request_id"])
    for suffix in (
        f"/{saved['id']}",
        f"/{saved['id']}/tasks",
        f"/{saved['id']}/graph",
        f"/{saved['id']}/events",
    ):
        assert client.get(path(project_id, suffix)).status_code == 200
    events = client.get(path(project_id, f"/{saved['id']}/events")).json()["items"]
    assert [event["sequence"] for event in events] == [1, 2]
    assert [event["event_type"] for event in events] == ["run_created", "run_awaiting_executor"]
    assert events[0]["actor_id"] == saved["creator_id"] and events[1]["actor_type"] == "system"
    assert events[1]["actor_id"] is None
    assert events[0]["occurred_at"] and events[1]["run_revision"] == 2
    assert all(event["details"] == {"execution_performed": False} for event in events)
    # Fresh application/session proves persistence rather than a process-local cache.
    from orba.main import create_app

    with TestClient(create_app(client.app.state.settings)) as restarted:
        restarted.cookies.update(client.cookies)
        assert restarted.get(path(project_id, f"/{saved['id']}")).json() == saved


@pytest.mark.parametrize(
    "case",
    [
        "draft",
        "version",
        "revision",
        "foreign",
        "missing",
        "stale_prd",
        "approval_disposition",
        "source_hash",
        "cycle",
        "missing_edge",
    ],
)
def test_invalid_sources_are_rejected_without_orphans(client, case):
    project_id, source = source_architecture(client, approved=case != "draft")
    payload = body(source)
    if case in {"version", "revision"}:
        payload["architecture_" + case] = 99
    elif case == "foreign":
        _, foreign = source_architecture(client)
        payload["architecture_id"] = foreign["id"]
    elif case == "missing":
        payload["architecture_id"] = str(uuid4())
    elif case == "stale_prd":
        source_id = seed(client, project_id)
        response = client.post(
            f"/api/v1/projects/{project_id}/pm-plans/{source_id}/approve",
            json={"version": 2, "expected_revision": 1},
        )
        assert response.status_code == 200, response.text
    elif case.startswith("approval_") or case == "source_hash":
        with Session(client.app.state.engine) as db, db.begin():
            row = db.get(ArchitectureVersion, UUID(source["id"]))
            if case == "approval_disposition":
                row.approval_dispositions = {"forged": {"revision": 99}}
            else:
                row.source_hash = "0" * 64
    elif case == "cycle":
        with Session(client.app.state.engine) as db, db.begin():
            tasks = db.scalars(
                select(EngineeringTask)
                .where(EngineeringTask.architecture_id == UUID(source["id"]))
                .order_by(EngineeringTask.display_order)
            ).all()
            db.add(
                TaskDependency(
                    architecture_id=UUID(source["id"]),
                    project_id=UUID(project_id),
                    prerequisite_id=tasks[1].id,
                    dependent_id=tasks[0].id,
                    display_order=0,
                )
            )
    elif case == "missing_edge":
        with Session(client.app.state.engine) as db, db.begin():
            db.execute(
                text("DELETE FROM task_dependencies WHERE architecture_id=:id"),
                {"id": source["id"]},
            )
    response = client.post(path(project_id), json=payload)
    assert response.status_code == (404 if case in {"foreign", "missing"} else 409), response.text
    assert counts(client) == [0, 0, 0, 0]


@pytest.mark.parametrize("field", ["approved_by", "approved_at"])
def test_database_rejects_missing_human_approval_before_it_can_authorize_a_run(client, field):
    _, source = source_architecture(client)
    with (
        pytest.raises(IntegrityError, match="arch_approval_metadata"),
        Session(client.app.state.engine) as db,
        db.begin(),
    ):
        artifact = db.get(ArchitectureVersion, UUID(source["id"]))
        setattr(artifact, field, None)
    assert counts(client) == [0, 0, 0, 0]


def test_idempotency_replay_and_conflict_are_persisted_not_in_memory(client):
    project_id, source, payload, saved = initialize(client)
    repeated = client.post(path(project_id), json=payload)
    assert repeated.status_code == 200 and repeated.json() == saved
    conflict = client.post(path(project_id), json=payload | {"architecture_revision": 99})
    assert (
        conflict.status_code == 409 and conflict.json()["error"]["code"] == "idempotency_conflict"
    )
    assert counts(client) == [1, 2, 1, 2]
    # Same source, deliberately different request -> new auditable run, stable snapshot hash.
    second = client.post(path(project_id), json=body(source))
    assert second.status_code == 201
    assert second.json()["snapshot_hash"] == saved["snapshot_hash"]
    assert second.json()["id"] != saved["id"]
    lookup = client.get(
        path(project_id) + f"?client_request_id={payload['client_request_id']}"
    ).json()
    assert [item["id"] for item in lookup["items"]] == [saved["id"]]


def test_two_concurrent_identical_creations_have_one_run_and_event_sequence(client):
    project_id, source = source_architecture(client)
    payload = RunCreate(**body(source))
    actor, session_id = identity(client)

    def create():
        return create_run(client.app.state.engine, UUID(project_id), actor, session_id, payload)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: create(), range(2)))
    assert {result[0]["id"] for result in results} == {results[0][0]["id"]}
    assert sorted(result[1] for result in results) == [False, True]
    assert counts(client) == [1, 2, 1, 2]


def test_initialization_failure_rolls_back_all_records(client, monkeypatch):
    import orba.orchestration_service as service

    project_id, source = source_architecture(client)
    actor, session_id = identity(client)

    # Narrow fault injection after real tasks/edges were flushed; not a fake database.
    def fail(*args, **kwargs):
        raise RuntimeError("Isolated post-child-write fault")

    monkeypatch.setattr(service, "append_event", fail)
    with pytest.raises(RuntimeError, match="post-child-write"):
        create_run(
            client.app.state.engine, UUID(project_id), actor, session_id, RunCreate(**body(source))
        )
    assert counts(client) == [0, 0, 0, 0]
    assert (
        client.get(f"/api/v1/projects/{project_id}/architectures/{source['id']}").json()["state"]
        == "approved"
    )


def test_historical_snapshot_survives_new_architecture_approval_and_old_key_replay(client):
    project_id, source, payload, saved = initialize(client)
    copied = client.post(
        f"/api/v1/projects/{project_id}/architectures/{source['id']}/draft",
        json={"version": 1, "expected_revision": 1, "client_request_id": str(uuid4())},
    )
    assert copied.status_code == 201, copied.text
    draft = copied.json()
    document = draft["document"]
    document["tasks"][0]["title"] = "A revised source task"
    edited = client.put(
        f"/api/v1/projects/{project_id}/architectures/{draft['id']}",
        json={"expected_revision": 1, "document": document},
    )
    assert edited.status_code == 200
    approved = client.post(
        f"/api/v1/projects/{project_id}/architectures/{draft['id']}/approve",
        json={"version": 2, "expected_revision": 2},
    )
    assert approved.status_code == 200, approved.text
    historical = client.get(path(project_id, f"/{saved['id']}")).json()
    assert historical == saved | {"source_current": False}
    replay = client.post(path(project_id), json=payload)
    assert replay.status_code == 200 and replay.json()["id"] == saved["id"]
    assert client.post(path(project_id), json=body(source)).status_code == 409


@pytest.mark.parametrize(
    "kind",
    [
        "task_definition",
        "edge",
        "run_snapshot",
        "event_update",
        "event_delete",
        "append_task",
        "append_edge",
    ],
)
def test_database_prevents_rewriting_published_snapshots_and_ledger(client, kind):
    _, _, _, saved = initialize(client)
    with Session(client.app.state.engine) as db:
        task = db.scalar(select(OrchestrationTask))
        with pytest.raises(IntegrityError), db.begin_nested():
            if kind == "task_definition":
                task.definition = task.definition | {"title": "Forged mutation"}
            elif kind == "edge":
                db.execute(text("UPDATE orchestration_dependencies SET display_order=5"))
            elif kind == "run_snapshot":
                db.execute(update(OrchestrationRun).values(source_snapshot={}))
            elif kind == "event_update":
                db.execute(text("UPDATE orchestration_events SET new_state='verified_complete'"))
            elif kind == "event_delete":
                db.execute(text("DELETE FROM orchestration_events"))
            elif kind == "append_task":
                db.execute(
                    text(
                        "INSERT INTO orchestration_tasks SELECT gen_random_uuid(),run_id,project_id,architecture_id,source_task_id,key||'x',definition,display_order+3,eligibility,execution_status,created_at,updated_at FROM orchestration_tasks LIMIT 1"
                    )
                )
            else:
                db.execute(
                    text(
                        "INSERT INTO orchestration_dependencies SELECT gen_random_uuid(),run_id,project_id,source_dependency_id,dependent_id,prerequisite_id,display_order+3 FROM orchestration_dependencies LIMIT 1"
                    )
                )
            db.flush()
    assert counts(client) == [1, 2, 1, 2]
    assert saved["tasks"][0]["execution_status"] == "awaiting_executor"


def test_cancel_is_atomic_revisioned_and_events_are_ordered(client):
    project_id, _, _, saved = initialize(client)
    target = path(project_id, f"/{saved['id']}/cancel")
    assert client.post(target, json={"expected_revision": 1}).status_code == 409
    cancelled = client.post(target, json={"expected_revision": 2})
    assert cancelled.status_code == 200, cancelled.text
    value = cancelled.json()
    assert value["status"] == "cancelled" and value["revision"] == 3 and value["cancelled_at"]
    assert value["snapshot_hash"] == saved["snapshot_hash"]
    assert all(task["execution_status"] == "cancelled" for task in value["tasks"])
    assert value["graph"]["eligible"] == [] and value["graph"]["roots"] == ["storage"]
    assert client.post(target, json={"expected_revision": 3}).status_code == 409
    events = client.get(path(project_id, f"/{saved['id']}/events")).json()["items"]
    assert [event["sequence"] for event in events] == [1, 2, 3, 4, 5]
    assert [event["event_type"] for event in events[2:]] == [
        "task_cancelled",
        "task_cancelled",
        "run_cancelled",
    ]
    assert all(
        event["run_revision"] == 3 and event["actor_id"] == saved["creator_id"]
        for event in events[2:]
    )
    page1 = client.get(path(project_id, f"/{saved['id']}/events?limit=2")).json()
    assert page1["next_sequence"] == 2
    assert len(client.get(path(project_id, f"/{saved['id']}/events?after=2")).json()["items"]) == 3


@pytest.mark.parametrize(
    "target", ["running", "succeeded", "verified_complete", "blocked", "created"]
)
def test_central_transition_service_rejects_unsupported_execution_states(client, target):
    initialize(client)
    with Session(client.app.state.engine) as db, db.begin():
        run = db.scalar(select(OrchestrationRun).with_for_update())
        with pytest.raises(OrchestrationError, match="unavailable"):
            transition(db, run, target, run.creator_id, db_now(db), expected_revision=2)
        assert run.status == "awaiting_executor" and run.revision == 2
    assert counts(client) == [1, 2, 1, 2]


def test_no_public_endpoint_can_forge_execution_or_system_events(client):
    project_id, _, _, saved = initialize(client)
    root = path(project_id, f"/{saved['id']}")
    for suffix, method in (
        ("", "patch"),
        (f"/tasks/{saved['tasks'][0]['id']}/complete", "post"),
        ("/events", "post"),
    ):
        response = getattr(client, method)(
            root + suffix, json={"status": "verified_complete", "actor_type": "system"}
        )
        assert response.status_code in {404, 405}
    assert client.get(root).json() == saved
    assert counts(client) == [1, 2, 1, 2]


def test_viewer_reads_but_cannot_create_or_cancel(client):
    project_id, source, _, saved = initialize(client)
    actor, _ = identity(client)
    with Session(client.app.state.engine) as db, db.begin():
        member = db.scalar(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == UUID(client.workspace_id),
                WorkspaceMember.user_id == actor,
            )
        )
        member.role = "viewer"
    assert client.get(path(project_id, f"/{saved['id']}")).status_code == 200
    assert client.post(path(project_id), json=body(source)).status_code == 403
    assert (
        client.post(
            path(project_id, f"/{saved['id']}/cancel"), json={"expected_revision": 2}
        ).status_code
        == 403
    )
    assert counts(client) == [1, 2, 1, 2]


def test_unrelated_workspace_and_wrong_project_do_not_reveal_run(client):
    project_id, source, _, saved = initialize(client)
    other_project = project(client)
    assert client.get(path(other_project, f"/{saved['id']}")).status_code == 404
    with TestClient(client.app) as outsider:
        register(outsider, "other-workspace@example.com")
        for suffix in (
            "",
            f"/{saved['id']}",
            f"/{saved['id']}/tasks",
            f"/{saved['id']}/graph",
            f"/{saved['id']}/events",
        ):
            denied = outsider.get(path(project_id, suffix))
            assert denied.status_code == 404 and "Human-authored" not in denied.text
        assert outsider.post(path(project_id), json=body(source)).status_code == 404
    assert counts(client) == [1, 2, 1, 2]


def test_auth_csrf_original_session_and_input_guards(client):
    project_id, source = source_architecture(client)
    with TestClient(client.app) as anonymous:
        assert anonymous.get(path(project_id)).status_code == 401
    token = client.headers.pop("X-CSRF-Token")
    assert client.post(path(project_id), json=body(source)).status_code == 403
    client.headers["X-CSRF-Token"] = token
    assert (
        client.post(path(project_id), json=body(source) | {"status": "succeeded"}).status_code
        == 422
    )
    assert (
        client.post(path(project_id), json=body(source) | {"architecture_revision": 0}).status_code
        == 422
    )
    actor, session_id = identity(client)
    with Session(client.app.state.engine) as db, db.begin():
        auth = db.get(AuthSession, session_id)
        auth.expires_at = db_now(db) - timedelta(seconds=1)
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as error:
        create_run(
            client.app.state.engine, UUID(project_id), actor, session_id, RunCreate(**body(source))
        )
    assert error.value.status_code == 401
    assert counts(client) == [0, 0, 0, 0]


def test_dependency_evaluator_uses_real_dag_and_never_accepts_completion_input():
    tasks = controlled_document().tasks
    graph = evaluate(tasks)
    assert graph["topological_order"] == ["storage", "screen"]
    assert graph == evaluate(tasks)
    assert graph["nodes"][0]["execution_status"] == "awaiting_executor"
    assert "verified evidence" in graph["nodes"][1]["explanation"]
    cancelled = evaluate(tasks, cancelled=True)
    assert cancelled["eligible"] == []
    assert all("cancelled" in node["explanation"] for node in cancelled["nodes"])
    tasks[0].dependencies = ["screen"]
    with pytest.raises(ValueError, match="cycle"):
        evaluate(tasks)


@pytest.mark.parametrize("dependencies", [["missing"], ["storage"], ["screen", "screen"]])
def test_evaluator_rejects_missing_self_duplicate_dependencies(dependencies):
    tasks = controlled_document().tasks
    tasks[0].dependencies = dependencies
    with pytest.raises(ValueError):
        evaluate(tasks)


def test_concurrent_cancellations_allow_one_revision_and_one_atomic_ledger(client):
    project_id, _, _, saved = initialize(client)

    def cancel(_):
        with TestClient(client.app) as caller:
            caller.cookies.update(client.cookies)
            caller.headers.update(client.headers)
            return caller.post(
                path(project_id, f"/{saved['id']}/cancel"), json={"expected_revision": 2}
            ).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(cancel, range(2))) == [200, 409]
    assert counts(client) == [1, 2, 1, 5]
    events = client.get(path(project_id, f"/{saved['id']}/events?after=5&limit=1")).json()
    assert events["items"] == [] and events["next_sequence"] is None
    assert (
        client.get(path(project_id, f"/{saved['id']}/events?after=4&limit=1")).json()["items"][0][
            "sequence"
        ]
        == 5
    )


def test_request_recovery_is_scoped_to_original_actor_even_with_shared_workspace(client):
    project_id, _, payload, saved = initialize(client)
    with TestClient(client.app) as other:
        user = register(other, "shared-recovery@example.com")
        with Session(client.app.state.engine) as db, db.begin():
            db.add(
                WorkspaceMember(
                    workspace_id=UUID(client.workspace_id), user_id=UUID(user["id"]), role="member"
                )
            )
        query = path(project_id) + f"?client_request_id={payload['client_request_id']}"
        assert other.get(query).json()["items"] == []
        assert other.get(path(project_id, f"/{saved['id']}")).status_code == 200


@pytest.mark.parametrize("kind", ["cross_run", "cross_project", "self", "duplicate"])
def test_real_postgresql_edge_ownership_self_and_unique_constraints(client, kind):
    _, _, _, saved = initialize(client)
    if kind == "cross_project":
        _, _, _, foreign = initialize(client)
    else:
        foreign = saved
    with Session(client.app.state.engine) as db:
        original = db.get(OrchestrationRun, UUID(saved["id"]))
        values = {
            column.name: getattr(original, column.name)
            for column in OrchestrationRun.__table__.columns
        }
        values.update(
            id=uuid4(),
            client_request_id=uuid4(),
            status="created",
            revision=1,
            last_event_sequence=0,
        )
        temporary = OrchestrationRun(**values)
        db.add(temporary)
        db.flush()
        copies = []
        for source_task in db.scalars(
            select(OrchestrationTask)
            .where(OrchestrationTask.run_id == original.id)
            .order_by(OrchestrationTask.display_order)
        ).all():
            fields = {
                column.name: getattr(source_task, column.name)
                for column in OrchestrationTask.__table__.columns
            }
            fields.update(id=uuid4(), run_id=temporary.id)
            copy = OrchestrationTask(**fields)
            db.add(copy)
            copies.append(copy)
        db.flush()
        source_edge = db.scalar(
            select(OrchestrationDependency).where(OrchestrationDependency.run_id == original.id)
        )
        edge = {
            "run_id": temporary.id,
            "project_id": temporary.project_id,
            "source_dependency_id": source_edge.source_dependency_id,
            "prerequisite_id": copies[0].id,
            "dependent_id": copies[1].id,
            "display_order": 0,
        }
        if kind in {"cross_run", "cross_project"}:
            edge["dependent_id"] = UUID(foreign["tasks"][0]["id"])
        elif kind == "self":
            edge["dependent_id"] = copies[0].id
        else:
            db.add(OrchestrationDependency(**edge))
            db.flush()
        with pytest.raises(IntegrityError) as error, db.begin_nested():
            db.add(OrchestrationDependency(**edge))
            db.flush()
        assert (
            "fk_orch_dependent"
            if kind in {"cross_run", "cross_project"}
            else "orch_edge_self"
            if kind == "self"
            else "uq_orch_edge"
        ) in str(error.value)
        db.rollback()  # Temporary unpublished graph is isolated test data only.
    assert counts(client) == ([2, 4, 2, 4] if kind == "cross_project" else [1, 2, 1, 2])

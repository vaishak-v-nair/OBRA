from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from orba.architect_models import (
    ArchitectRun,
    ArchitectureVersion,
    EngineeringTask,
    RequirementTrace,
    TaskDependency,
)
from orba.models import AuthSession, WorkspaceMember
from orba.pm_models import ProductPlan
from orba.pm_provider import ProviderFailure
from scripts.architect_sample import controlled_document
from tests.architect_support import ControlledProvider, approved_source, artifact, generate, payload
from tests.conftest import register
from tests.pm_support import identity, project, seed


def test_generation_persists_relational_proposal_and_source(client):
    project_id, source = approved_source(client)
    result, provider = generate(client, project_id, source)
    assert result.status_code == 201, result.text
    run = result.json()
    saved = artifact(client, project_id, run)
    assert provider.calls == 1 and run["status"] == "succeeded"
    assert saved["state"] == "draft" and saved["approved_at"] is None
    assert (
        saved["source_plan_id"],
        saved["source_version"],
        saved["source_revision"],
        saved["source_hash"],
    ) == (source["id"], source["version"], source["revision"], source["content_hash"])
    with Session(client.app.state.engine) as db:
        assert db.scalar(select(func.count()).select_from(EngineeringTask)) == 2
        assert db.scalar(select(func.count()).select_from(TaskDependency)) == 1
        assert db.scalar(select(func.count()).select_from(RequirementTrace)) == 3
        assert db.get(ArchitectRun, UUID(run["id"])).status == "succeeded"
    for path in ("tasks", "graph", "coverage"):
        view = client.get(f"/api/v1/projects/{project_id}/architectures/{saved['id']}/{path}")
        assert view.status_code == 200 and view.json()["content_hash"] == saved["content_hash"]


@pytest.mark.parametrize("kind", ["draft", "wrong_revision", "wrong_version", "foreign", "missing"])
def test_generation_requires_exact_current_approved_source(client, kind):
    project_id, source = approved_source(client)
    body = payload(source)
    if kind == "draft":
        body["source_plan_id"] = str(seed(client, project_id))
    elif kind == "foreign":
        body["source_plan_id"] = str(seed(client, project(client)))
    elif kind == "missing":
        body["source_plan_id"] = str(uuid4())
    else:
        body["source_revision" if kind == "wrong_revision" else "source_version"] = 99
    response, provider = generate(client, project_id, source, body=body)
    assert response.status_code == (404 if kind in {"foreign", "missing"} else 409)
    assert provider.calls == 0
    with Session(client.app.state.engine) as db:
        assert db.scalar(select(func.count()).select_from(ArchitectRun)) == 0


@pytest.mark.parametrize(
    "failure",
    [
        ProviderFailure(
            "provider_unavailable",
            "Controlled HTTP503",
            502,
            diagnostic={"provider_http_status": 503},
        ),
        ProviderFailure(
            "provider_timeout", "Controlled HTTP504", 504, diagnostic={"provider_http_status": 504}
        ),
        TimeoutError("Controlled local timeout"),
    ],
)
def test_provider_failures_are_terminal_without_artifact(client, failure):
    project_id, source = approved_source(client)
    response, provider = generate(client, project_id, source, ControlledProvider(failure=failure))
    assert response.status_code in {502, 504}, response.text
    assert provider.calls == 1
    run_id = response.json()["error"]["run_id"]
    with Session(client.app.state.engine) as db:
        run = db.get(ArchitectRun, UUID(run_id))
        assert run.status == "failed" and run.completed_at is not None
        assert db.scalar(select(func.count()).select_from(ArchitectureVersion)) == 0
        if isinstance(failure, ProviderFailure):
            assert run.diagnostic["provider_http_status"] in {503, 504}


@pytest.mark.parametrize("output", ["not JSON", "{}", '{"schema_version":1,"overview":null}'])
def test_invalid_model_output_never_persists(client, output):
    project_id, source = approved_source(client)
    response, _ = generate(client, project_id, source, ControlledProvider(document=output))
    assert (
        response.status_code == 502 and response.json()["error"]["code"] == "invalid_model_response"
    )
    with Session(client.app.state.engine) as db:
        assert db.scalar(select(ArchitectRun)).status == "failed"
        assert db.scalar(select(func.count()).select_from(EngineeringTask)) == 0


def test_missing_configuration_records_honest_failure(client):
    project_id, source = approved_source(client)
    client.app.state.settings.architect_model = None
    response = client.post(f"/api/v1/projects/{project_id}/architect-runs", json=payload(source))
    assert (
        response.status_code == 503
        and response.json()["error"]["code"] == "architect_not_configured"
    )
    with Session(client.app.state.engine) as db:
        assert db.scalar(select(ArchitectRun)).status == "failed"


def test_edit_revision_approval_history_and_stale_editor(client):
    project_id, source = approved_source(client)
    result, _ = generate(client, project_id, source)
    saved = artifact(client, project_id, result.json())
    url = f"/api/v1/projects/{project_id}/architectures/{saved['id']}"
    saved["document"]["tasks"][0]["acceptance_criteria"][0] = (
        "Reload preserves the human-edited check-in."
    )
    changed = client.put(url, json={"expected_revision": 1, "document": saved["document"]})
    assert changed.status_code == 200, changed.text
    assert changed.json()["revision"] == 2
    assert (
        client.put(url, json={"expected_revision": 1, "document": saved["document"]}).status_code
        == 409
    )
    assert (
        client.post(url + "/approve", json={"version": 1, "expected_revision": 1}).status_code
        == 409
    )
    approved = client.post(url + "/approve", json={"version": 1, "expected_revision": 2})
    assert approved.status_code == 200, approved.text
    assert approved.json()["approved_by"] == str(identity(client)[0])
    assert approved.json()["approved_at"] and approved.json()["state"] == "approved"
    assert (
        client.put(url, json={"expected_revision": 2, "document": saved["document"]}).status_code
        == 409
    )
    copy_body = {"version": 1, "expected_revision": 2, "client_request_id": str(uuid4())}
    copied = client.post(url + "/draft", json=copy_body)
    assert copied.status_code == 201 and copied.json()["version"] == 2
    assert client.post(url + "/draft", json=copy_body).json()["id"] == copied.json()["id"]
    with Session(client.app.state.engine) as db:
        prior = db.get(ArchitectureVersion, UUID(saved["id"]))
        assert prior.state == "approved" and prior.revision == 2


@pytest.mark.parametrize(
    "mutation",
    [
        lambda d: d["tasks"][0].update(dependencies=["screen"]),
        lambda d: d["tasks"][0].update(dependencies=["storage"]),
        lambda d: d["tasks"][0].update(dependencies=["missing"]),
        lambda d: d["tasks"][1].update(dependencies=["storage", "storage"]),
        lambda d: d["tasks"][0].update(story_refs=["forged"]),
    ],
)
def test_invalid_edits_roll_back_saved_graph(client, mutation):
    project_id, source = approved_source(client)
    result, _ = generate(client, project_id, source)
    saved = artifact(client, project_id, result.json())
    url = f"/api/v1/projects/{project_id}/architectures/{saved['id']}"
    mutation(saved["document"])
    response = client.put(url, json={"expected_revision": 1, "document": saved["document"]})
    assert response.status_code == 422, response.text
    after = client.get(url).json()
    assert after["revision"] == 1 and after["content_hash"] == saved["content_hash"]
    assert after["graph"]["topological_order"] == ["storage", "screen"]


def test_incomplete_coverage_draft_cannot_be_approved(client):
    project_id, source = approved_source(client)
    doc = controlled_document()
    for task in doc.tasks:
        task.criterion_refs = []
    result, _ = generate(client, project_id, source, ControlledProvider(document=doc))
    saved = artifact(client, project_id, result.json())
    assert not saved["coverage"]["approvable"]
    response = client.post(
        f"/api/v1/projects/{project_id}/architectures/{saved['id']}/approve",
        json={"version": 1, "expected_revision": 1},
    )
    assert response.status_code == 422


def test_replay_and_explicit_failed_retry_are_auditable(client):
    project_id, source = approved_source(client)
    body = payload(source)
    failed, first = generate(
        client,
        project_id,
        source,
        ControlledProvider(failure=ProviderFailure("provider_unavailable", "Controlled503")),
        body,
    )
    assert failed.status_code == 502 and first.calls == 1
    replay, second = generate(client, project_id, source, body=body)
    assert replay.status_code == 409 and second.calls == 0
    result, second = generate(client, project_id, source)
    assert result.status_code == 201 and second.calls == 1
    with Session(client.app.state.engine) as db:
        assert sorted(db.scalars(select(ArchitectRun.status)).all()) == ["failed", "succeeded"]


def test_success_replay_survives_source_supersession_and_new_caps(client):
    project_id, source = approved_source(client)
    body = payload(source)
    result, first = generate(client, project_id, source, body=body)
    copied = client.post(
        f"/api/v1/projects/{project_id}/pm-plans/{source['id']}/draft",
        json={"version": 1, "expected_revision": 1, "client_request_id": str(uuid4())},
    ).json()
    approved = client.post(
        f"/api/v1/projects/{project_id}/pm-plans/{copied['id']}/approve",
        json={"version": 2, "expected_revision": 1},
    )
    assert approved.status_code == 200
    client.app.state.settings.architect_max_input_bytes = 8192
    replay, second = generate(client, project_id, source, body=body)
    assert replay.status_code == 200 and replay.json()["id"] == result.json()["id"]
    assert first.calls == 1 and second.calls == 0
    saved = artifact(client, project_id, result.json())
    assert not saved["source_current"]
    assert (
        client.post(
            f"/api/v1/projects/{project_id}/architectures/{saved['id']}/approve",
            json={"version": 1, "expected_revision": 1},
        ).status_code
        == 409
    )


@pytest.mark.parametrize("role", ["viewer", "member"])
def test_roles_enforced_server_side(client, role):
    project_id, source = approved_source(client)
    result, _ = generate(client, project_id, source)
    saved = artifact(client, project_id, result.json())
    with Session(client.app.state.engine) as db, db.begin():
        db.execute(
            update(WorkspaceMember)
            .where(WorkspaceMember.user_id == identity(client)[0])
            .values(role=role)
        )
    if role == "viewer":
        denied, provider = generate(client, project_id, source)
        assert denied.status_code == 403 and provider.calls == 0
        assert (
            client.put(
                f"/api/v1/projects/{project_id}/architectures/{saved['id']}",
                json={"expected_revision": 1, "document": saved["document"]},
            ).status_code
            == 403
        )
    assert (
        client.post(
            f"/api/v1/projects/{project_id}/architectures/{saved['id']}/approve",
            json={"version": 1, "expected_revision": 1},
        ).status_code
        == 403
    )
    assert (
        client.get(f"/api/v1/projects/{project_id}/architectures/{saved['id']}").status_code == 200
    )


def test_tenant_denials_return_no_content_and_rows_remain(client):
    project_id, source = approved_source(client)
    result, _ = generate(client, project_id, source)
    saved = artifact(client, project_id, result.json())
    with TestClient(client.app) as outsider:
        register(outsider, "outsider@example.com")
        for path in (
            "architect-runs",
            f"architect-runs/{result.json()['id']}",
            "architectures",
            f"architectures/{saved['id']}",
            f"architectures/{saved['id']}/graph",
            f"architectures/{saved['id']}/coverage",
        ):
            response = outsider.get(f"/api/v1/projects/{project_id}/{path}")
            assert (
                response.status_code == 404
                and saved["document"]["overview"]["title"] not in response.text
            )
        assert (
            outsider.put(
                f"/api/v1/projects/{project_id}/architectures/{saved['id']}",
                json={"expected_revision": 1, "document": saved["document"]},
            ).status_code
            == 404
        )
    with Session(client.app.state.engine) as db:
        assert db.get(ArchitectureVersion, UUID(saved["id"])) is not None


def test_source_or_original_session_change_during_call_blocks_publication(client):
    project_id, source = approved_source(client)
    _, session_id = identity(client)

    def revoke(snapshot):
        with Session(client.app.state.engine) as db, db.begin():
            db.execute(
                update(AuthSession)
                .where(AuthSession.id == session_id)
                .values(revoked_at=func.now())
            )

    response, _ = generate(client, project_id, source, ControlledProvider(callback=revoke))
    assert response.status_code == 401
    with Session(client.app.state.engine) as db:
        assert db.scalar(select(ArchitectRun)).status == "failed"
        assert db.scalar(select(func.count()).select_from(ArchitectureVersion)) == 0


def test_database_rejects_self_and_cross_architecture_edges(client):
    project_id, source = approved_source(client)
    result, _ = generate(client, project_id, source)
    first = result.json()["architecture_id"]
    result, _ = generate(client, project_id, source)
    second = result.json()["architecture_id"]
    with Session(client.app.state.engine) as db:
        task_a = db.scalar(
            select(EngineeringTask).where(EngineeringTask.architecture_id == UUID(first))
        )
        task_b = db.scalar(
            select(EngineeringTask).where(EngineeringTask.architecture_id == UUID(second))
        )
        for parent, child in ((task_a.id, task_a.id), (task_a.id, task_b.id)):
            with pytest.raises(IntegrityError), db.begin_nested():
                db.add(
                    TaskDependency(
                        architecture_id=UUID(first),
                        project_id=UUID(project_id),
                        prerequisite_id=parent,
                        dependent_id=child,
                        display_order=0,
                    )
                )
                db.flush()


def test_approved_architecture_and_prd_survive_failed_regeneration(client):
    project_id, source = approved_source(client)
    result, _ = generate(client, project_id, source)
    saved = artifact(client, project_id, result.json())
    path = f"/api/v1/projects/{project_id}/architectures/{saved['id']}"
    approved = client.post(path + "/approve", json={"version": 1, "expected_revision": 1}).json()
    failed, _ = generate(
        client,
        project_id,
        source,
        ControlledProvider(
            failure=ProviderFailure("provider_timeout", "Controlled upstream504", 504)
        ),
    )
    assert failed.status_code == 504
    after = client.get(path).json()
    for key in ("content_hash", "approved_by", "approved_at", "version", "revision", "state"):
        assert after[key] == approved[key]
    with Session(client.app.state.engine) as db:
        assert db.get(ProductPlan, UUID(source["id"])).content_hash == source["content_hash"]
        assert db.scalar(select(func.count()).select_from(ArchitectureVersion)) == 1


def test_graph_tampering_cannot_be_approved_even_when_diagram_could_render(client):
    project_id, source = approved_source(client)
    result, _ = generate(client, project_id, source)
    architecture_id = UUID(result.json()["architecture_id"])
    with Session(client.app.state.engine) as db, db.begin():
        tasks = {
            row.key: row.id
            for row in db.scalars(
                select(EngineeringTask).where(EngineeringTask.architecture_id == architecture_id)
            )
        }
        db.add(
            TaskDependency(
                architecture_id=architecture_id,
                project_id=UUID(project_id),
                prerequisite_id=tasks["screen"],
                dependent_id=tasks["storage"],
                display_order=0,
            )
        )
    denied = client.post(
        f"/api/v1/projects/{project_id}/architectures/{architecture_id}/approve",
        json={"version": 1, "expected_revision": 1},
    )
    assert (
        denied.status_code == 409
        and denied.json()["error"]["code"] == "architecture_integrity_error"
    )
    with Session(client.app.state.engine) as db:
        assert db.get(ArchitectureVersion, architecture_id).state == "draft"


def test_exact_human_obligation_disposition_is_required_and_persisted(client):
    from orba.architect_schemas import Decision

    project_id, source = approved_source(client)
    document = controlled_document()
    document.open_decisions = [
        Decision(key="hosting", question="Confirm hosting topology", blocking=True)
    ]
    result, _ = generate(client, project_id, source, ControlledProvider(document=document))
    saved = artifact(client, project_id, result.json())
    path = f"/api/v1/projects/{project_id}/architectures/{saved['id']}/approve"
    body = {"version": 1, "expected_revision": 1}
    assert client.post(path, json=body).status_code == 422
    assert (
        client.post(
            path, json=body | {"acknowledgments": {"decision:forged": "Accept"}}
        ).status_code
        == 422
    )
    approved = client.post(
        path,
        json=body
        | {
            "acknowledgments": {
                "decision:hosting": "The owner defers hosted deployment for this local release."
            }
        },
    )
    assert approved.status_code == 200
    disposition = approved.json()["approval_dispositions"]["decision:hosting"]
    assert (
        disposition["actor_id"] == str(identity(client)[0])
        and disposition["revision"] == 1
        and disposition["decided_at"]
    )


def test_new_unapproved_prd_does_not_stale_current_architecture(client):
    project_id, source = approved_source(client)
    result, _ = generate(client, project_id, source)
    draft = seed(client, project_id)
    assert str(draft) != source["id"]
    assert artifact(client, project_id, result.json())["source_current"] is True


def test_source_approval_change_during_call_fences_publication(client):
    project_id, source = approved_source(client)

    def replace(snapshot):
        copied = client.post(
            f"/api/v1/projects/{project_id}/pm-plans/{source['id']}/draft",
            json={"version": 1, "expected_revision": 1, "client_request_id": str(uuid4())},
        ).json()
        approved = client.post(
            f"/api/v1/projects/{project_id}/pm-plans/{copied['id']}/approve",
            json={"version": 2, "expected_revision": 1},
        )
        assert approved.status_code == 200

    result, _ = generate(client, project_id, source, ControlledProvider(callback=replace))
    assert result.status_code == 409 and result.json()["error"]["code"] == "source_changed"
    with Session(client.app.state.engine) as db:
        assert db.scalar(select(ArchitectRun)).status == "failed"
        assert db.scalar(select(func.count()).select_from(ArchitectureVersion)) == 0


@pytest.mark.parametrize("defect", ["origin", "csrf", "oversized", "forged_owner"])
def test_architect_mutations_reject_invalid_authority_or_input_before_dispatch(client, defect):
    project_id, source = approved_source(client)
    from orba.architect import model_provider

    provider = ControlledProvider()
    client.app.dependency_overrides[model_provider] = lambda: provider
    body = payload(source)
    if defect == "origin":
        client.headers.pop("Origin")
    elif defect == "csrf":
        client.headers["X-CSRF-Token"] = "invalid"
    elif defect == "oversized":
        body["constraints"] = "x" * 4001
    else:
        body["workspace_id"] = str(uuid4())
        body["initiator_id"] = str(uuid4())
    response = client.post(f"/api/v1/projects/{project_id}/architect-runs", json=body)
    assert response.status_code == (403 if defect in {"origin", "csrf"} else 422)
    assert provider.calls == 0
    with Session(client.app.state.engine) as db:
        assert db.scalar(select(func.count()).select_from(ArchitectRun)) == 0


def test_unauthenticated_architect_reads_and_generation_are_rejected(client):
    project_id, source = approved_source(client)
    assert client.post("/api/v1/auth/logout").status_code == 204
    assert client.get(f"/api/v1/projects/{project_id}/architectures").status_code == 401
    response, provider = generate(client, project_id, source)
    assert response.status_code in {401, 403} and provider.calls == 0


def test_real_sql_failure_rolls_back_every_artifact_and_records_failure(client, monkeypatch):
    from sqlalchemy import text

    from orba import architect_service

    original = architect_service.create_architecture

    def fail_after_flush(db, *args, **kwargs):
        original(db, *args, **kwargs)
        db.execute(text("SELECT 1/0"))  # Actual PostgreSQL rollback, not a database mock.

    monkeypatch.setattr(architect_service, "create_architecture", fail_after_flush)
    project_id, source = approved_source(client)
    response, _ = generate(client, project_id, source)
    assert response.status_code == 503 and response.json()["error"]["code"] == "persistence_failed"
    with Session(client.app.state.engine) as db:
        assert db.scalar(select(ArchitectRun)).status == "failed"
        for model in (ArchitectureVersion, EngineeringTask, RequirementTrace, TaskDependency):
            assert db.scalar(select(func.count()).select_from(model)) == 0


def test_expired_execution_lease_cannot_publish_and_is_reconciled(client):
    from sqlalchemy import text

    project_id, source = approved_source(client)

    def expire(snapshot):
        with client.app.state.engine.begin() as db:
            db.execute(
                text(
                    "UPDATE architect_runs SET deadline_at=clock_timestamp()-interval '1 second' WHERE status='running'"
                )
            )

    response, _ = generate(client, project_id, source, ControlledProvider(callback=expire))
    assert response.status_code == 409
    runs = client.get(f"/api/v1/projects/{project_id}/architect-runs").json()["items"]
    assert runs[0]["status"] == "interrupted" and runs[0]["architecture_id"] is None

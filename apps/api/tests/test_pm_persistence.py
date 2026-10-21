"""Real PostgreSQL/API integration with explicitly HUMAN-authored plans.

No model calls or fake generated runs. Live generation has a separate gate.
"""

from uuid import UUID, uuid4

from pm_support import counts, project, seed
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from test_auth_workspaces import account, join

from orba.pm_models import ProductCriterion, ProductEpic, ProductPlan, ProductStory
from orba.pm_repository import read_document, write_document
from orba.pm_schemas import Confirmation, Source


def paths(client):
    pid = project(client)
    plan_id = seed(client, pid)
    return pid, str(plan_id), f"/api/v1/projects/{pid}"


def test_human_plan_roundtrip_relational_graph_and_pagination(client):
    _pid, plan_id, base = paths(client)
    value = client.get(f"{base}/pm-plans/{plan_id}")
    assert value.status_code == 200, value.text
    saved = value.json()
    assert saved["state"] == "draft" and saved["origin"] == "human_authored"
    assert saved["generation"] is None and saved["inputs"] is None
    with Session(client.app.state.engine) as db:
        plan = db.get(ProductPlan, UUID(plan_id))
        assert read_document(db, plan).model_dump(mode="json") == saved["document"]
        epic = db.scalar(select(ProductEpic).where(ProductEpic.plan_id == plan.id))
        story = db.scalar(select(ProductStory).where(ProductStory.plan_id == plan.id))
        criterion = db.scalar(select(ProductCriterion).where(ProductCriterion.plan_id == plan.id))
        assert story.epic_id == epic.id and criterion.story_id == story.id
        assert story.plan_id == criterion.plan_id == epic.plan_id == plan.id
    listing = client.get(f"{base}/pm-plans?limit=1").json()
    assert listing["items"][0]["id"] == plan_id and listing["next_offset"] == 1
    assert client.get(f"{base}/pm-plans?offset=1").json()["items"] == []
    assert client.get(f"{base}/pm-plans?limit=10000").status_code == 422
    assert counts(client) == (0, 1, 1)


def test_edit_revision_provenance_validation_and_persistence(client):
    _, plan_id, base = paths(client)
    old = client.get(f"{base}/pm-plans/{plan_id}").json()
    doc = old["document"]
    doc["summary"]["text"] = "Corrected by the owner"
    doc["summary"]["source"] = {"kind": "brief", "quote": "forged"}
    doc["epics"][0]["stories"][0]["acceptance_criteria"][0]["then"] = (
        "The saved check-in remains visible after reload"
    )
    response = client.put(
        f"{base}/pm-plans/{plan_id}", json={"expected_revision": 1, "document": doc}
    )
    assert response.status_code == 200, response.text
    saved = client.get(f"{base}/pm-plans/{plan_id}").json()
    assert saved["revision"] == 2 and saved["content_hash"] != old["content_hash"]
    assert saved["document"]["summary"]["source"]["kind"] == "human"
    assert saved["document"]["summary"]["source"]["actor_id"] == saved["editor_id"]
    assert (
        "after reload"
        in saved["document"]["epics"][0]["stories"][0]["acceptance_criteria"][0]["then"]
    )
    assert (
        client.put(
            f"{base}/pm-plans/{plan_id}", json={"expected_revision": 1, "document": doc}
        ).status_code
        == 409
    )
    doc["epics"] = []
    assert (
        client.put(
            f"{base}/pm-plans/{plan_id}", json={"expected_revision": 2, "document": doc}
        ).status_code
        == 422
    )
    assert client.get(f"{base}/pm-plans/{plan_id}").json()["revision"] == 2


def test_approval_exact_revision_copy_history_and_idempotency(client):
    _, plan_id, base = paths(client)
    assert (
        client.post(
            f"{base}/pm-plans/{plan_id}/approve", json={"version": 1, "expected_revision": 2}
        ).status_code
        == 409
    )
    response = client.post(
        f"{base}/pm-plans/{plan_id}/approve", json={"version": 1, "expected_revision": 1}
    )
    assert response.status_code == 200, response.text
    approved = response.json()
    assert approved["approved_by"] == approved["creator_id"] and approved["approved_at"]
    assert (
        client.post(
            f"{base}/pm-plans/{plan_id}/approve", json={"version": 1, "expected_revision": 1}
        ).json()["approved_at"]
        == approved["approved_at"]
    )
    assert (
        client.put(
            f"{base}/pm-plans/{plan_id}",
            json={"expected_revision": 1, "document": approved["document"]},
        ).status_code
        == 409
    )
    payload = {"version": 1, "expected_revision": 1, "client_request_id": str(uuid4())}
    copied = client.post(f"{base}/pm-plans/{plan_id}/draft", json=payload)
    assert copied.status_code == 201, copied.text
    draft = copied.json()
    assert (
        draft["state"] == "draft" and draft["version"] == 2 and draft["source_plan_id"] == plan_id
    )
    assert draft["origin"] == "human_copy" and draft["generation"] is None
    replay = client.post(f"{base}/pm-plans/{plan_id}/draft", json=payload)
    assert replay.status_code == 200 and replay.json()["id"] == draft["id"]
    payload["version"] = 2
    assert client.post(f"{base}/pm-plans/{plan_id}/draft", json=payload).status_code == 409
    assert client.get(f"{base}/pm-plans/{plan_id}").json()["state"] == "approved"
    assert (
        client.post(
            f"{base}/pm-plans/{draft['id']}/approve", json={"version": 2, "expected_revision": 1}
        ).status_code
        == 200
    )
    history = client.get(f"{base}/pm-plans/{plan_id}").json()
    assert history["state"] == "superseded" and history["document"] == approved["document"]
    assert history["approved_at"] == approved["approved_at"]


def test_blocking_confirmations_require_recorded_human_disposition(client):
    _, plan_id, base = paths(client)
    with Session(client.app.state.engine) as db, db.begin():
        plan = db.get(ProductPlan, UUID(plan_id))
        doc = read_document(db, plan)
        doc.confirmations = [
            Confirmation(
                key="blocker",
                text="Confirm timezone",
                blocking=True,
                source=Source(kind="assumption"),
            )
        ]
        write_document(db, plan, doc)
    assert (
        client.post(
            f"{base}/pm-plans/{plan_id}/approve", json={"version": 1, "expected_revision": 1}
        ).status_code
        == 422
    )
    current = client.get(f"{base}/pm-plans/{plan_id}").json()["document"]
    omitted = {**current, "confirmations": []}
    assert (
        client.put(
            f"{base}/pm-plans/{plan_id}", json={"expected_revision": 1, "document": omitted}
        ).status_code
        == 422
    )
    current["confirmations"][0].update(
        disposition="deferred", reason="Decide before development", actor_id="forged"
    )
    saved = client.put(
        f"{base}/pm-plans/{plan_id}", json={"expected_revision": 1, "document": current}
    ).json()
    assert saved["document"]["confirmations"][0]["actor_id"] == saved["editor_id"]
    assert (
        client.post(
            f"{base}/pm-plans/{plan_id}/approve", json={"version": 1, "expected_revision": 2}
        ).status_code
        == 200
    )


def test_viewer_member_approval_and_cross_workspace_isolation(client):
    pid, plan_id, base = paths(client)
    for role in ("viewer", "member"):
        other, user = account(client.app, f"{role}@example.com")
        join(client, other, client.workspace_id, user, role)
        saved = other.get(f"{base}/pm-plans/{plan_id}").json()
        assert saved["id"] == plan_id
        assert (
            other.post(
                f"{base}/pm-plans/{plan_id}/approve", json={"version": 1, "expected_revision": 1}
            ).status_code
            == 403
        )
        edited = other.put(
            f"{base}/pm-plans/{plan_id}",
            json={"expected_revision": 1, "document": saved["document"]},
        )
        assert edited.status_code == (403 if role == "viewer" else 200)
        if role == "viewer":
            assert (
                other.post(
                    f"{base}/pm-runs",
                    json={"client_request_id": str(uuid4()), "brief": "Track habits"},
                ).status_code
                == 403
            )
            assert (
                other.post(
                    f"{base}/pm-plans/{plan_id}/draft",
                    json={"client_request_id": str(uuid4()), "version": 1, "expected_revision": 1},
                ).status_code
                == 403
            )
        other.close()
    outsider, _ = account(client.app, "outsider@example.com")
    for path in ("pm-plans", f"pm-plans/{plan_id}", "pm-runs", f"pm-runs/{uuid4()}"):
        denied = outsider.get(f"{base}/{path}")
        assert denied.status_code == 404 and "Habit" not in denied.text
    assert (
        outsider.put(
            f"{base}/pm-plans/{plan_id}",
            json={"expected_revision": 2, "document": saved["document"]},
        ).status_code
        == 404
    )
    with Session(client.app.state.engine) as db:
        assert db.get(ProductPlan, UUID(plan_id)).project_id == UUID(pid)
        assert db.scalar(select(func.count()).select_from(ProductPlan)) == 1
    outsider.close()


def test_pm_auth_csrf_missing_records_and_size_guards(client):
    _, plan_id, base = paths(client)
    response = client.post(
        f"{base}/pm-runs", json={"client_request_id": str(uuid4()), "brief": " "}
    )
    assert response.status_code == 422 and counts(client)[0] == 0
    assert client.get(f"{base}/pm-plans/{uuid4()}").status_code == 404
    assert client.get(f"{base}/pm-runs/{uuid4()}").status_code == 404
    headers = dict(client.headers)
    client.headers["X-CSRF-Token"] = "wrong"
    assert (
        client.post(
            f"{base}/pm-runs", json={"client_request_id": str(uuid4()), "brief": "Track habits"}
        ).status_code
        == 403
    )
    client.headers.update(headers)
    oversized = client.put(f"{base}/pm-plans/{plan_id}", content=b"x" * (512 * 1024 + 1))
    assert oversized.status_code == 413
    client.cookies.clear()
    assert client.get(f"{base}/pm-plans").status_code == 401


def test_corrupt_plan_cannot_be_read_or_approved(client):
    _, plan_id, base = paths(client)
    with Session(client.app.state.engine) as db, db.begin():
        plan = db.get(ProductPlan, UUID(plan_id))
        plan.content = {**plan.content, "target_users": []}
    assert client.get(f"{base}/pm-plans/{plan_id}").status_code == 409
    assert (
        client.post(
            f"{base}/pm-plans/{plan_id}/approve", json={"version": 1, "expected_revision": 1}
        ).status_code
        == 409
    )
    with Session(client.app.state.engine) as db:
        assert db.get(ProductPlan, UUID(plan_id)).state == "draft"


def test_context_requires_same_project_and_exact_saved_revision_before_dispatch(client):
    pid, plan_id, base = paths(client)
    second = project(client)
    other_plan = seed(client, second)
    forged = client.post(
        f"{base}/pm-runs",
        json={
            "client_request_id": str(uuid4()),
            "brief": "Track habits",
            "context_plan_id": str(other_plan),
            "context_revision": 1,
        },
    )
    assert forged.status_code == 404
    stale = client.post(
        f"{base}/pm-runs",
        json={
            "client_request_id": str(uuid4()),
            "brief": "Track habits",
            "context_plan_id": plan_id,
            "context_revision": 2,
        },
    )
    assert stale.status_code == 409
    unpaired = client.post(
        f"{base}/pm-runs",
        json={
            "client_request_id": str(uuid4()),
            "brief": "Track habits",
            "context_plan_id": plan_id,
        },
    )
    assert unpaired.status_code == 422 and counts(client)[0] == 0
    assert client.get(f"/api/v1/projects/{pid}/pm-plans/{other_plan}").status_code == 404


def test_expired_pending_leases_reconcile_on_get_and_lifespan_sweep(client):
    """Real admission/SQL/HTTP/lifespan; no provider double or resumed execution."""
    import time
    from datetime import timedelta

    from fastapi.testclient import TestClient
    from pm_support import identity

    from orba.config import Settings
    from orba.main import create_app
    from orba.pm_models import ProductManagerRun
    from orba.pm_schemas import RunCreate
    from orba.pm_service import reserve
    from orba.security import now

    pid = project(client)
    actor, sid = identity(client)
    engine = client.app.state.engine

    def orphan():
        run_id, _, _ = reserve(
            engine,
            client.app.state.settings,
            UUID(pid),
            actor,
            sid,
            RunCreate(client_request_id=uuid4(), brief="Track daily habits"),
        )
        with Session(engine) as db, db.begin():
            db.get(ProductManagerRun, run_id).deadline_at = now() - timedelta(seconds=1)
        return run_id

    first = orphan()
    response = client.get(f"/api/v1/projects/{pid}/pm-runs/{first}")
    assert (
        response.status_code == 200
        and response.json()["status"] == "interrupted"
        and response.json()["plan_id"] is None
    )
    second = orphan()
    # A fresh application lifespan performs its actual bounded startup sweep.
    config = Settings(
        database_url=client.app.state.settings.database_url, pm_api_key=None, pm_model=None
    )
    with TestClient(create_app(config)):
        deadline = time.monotonic() + 3
        while True:
            with Session(engine) as db:
                saved = db.get(ProductManagerRun, second)
                if saved.status == "interrupted":
                    assert saved.started_at is None and saved.completed_at and saved.diagnostic_id
                    break
            assert time.monotonic() < deadline, (
                "The real lifespan sweep did not reconcile the expired lease"
            )
            time.sleep(0.03)
    assert counts(client)[:2] == (2, 0)

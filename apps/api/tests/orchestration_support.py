"""Human-authored deterministic source fixtures, never AI or executor evidence."""

from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from orba.architect_repository import create_architecture
from orba.pm_models import ProductPlan
from scripts.architect_sample import controlled_document
from tests.architect_support import approved_source
from tests.pm_support import identity


def source_architecture(client, *, approved=True, project_id=None):
    project_id, source = approved_source(client, project_id)
    actor, _ = identity(client)
    with Session(client.app.state.engine) as db, db.begin():
        plan = db.get(ProductPlan, UUID(source["id"]))
        document = controlled_document()
        document.overview.title = "Human-authored orchestration test source"
        architecture = create_architecture(db, UUID(project_id), actor, plan, document)
        architecture_id = str(architecture.id)
    if approved:
        result = client.post(
            f"/api/v1/projects/{project_id}/architectures/{architecture_id}/approve",
            json={"version": 1, "expected_revision": 1},
        )
    else:
        result = client.get(f"/api/v1/projects/{project_id}/architectures/{architecture_id}")
    assert result.status_code == 200, result.text
    return project_id, result.json()


def body(architecture):
    return {
        "client_request_id": str(uuid4()),
        "architecture_id": architecture["id"],
        "architecture_version": architecture["version"],
        "architecture_revision": architecture["revision"],
    }


def path(project_id, suffix=""):
    return f"/api/v1/projects/{project_id}/orchestration-runs{suffix}"


def initialize(client):
    project_id, source = source_architecture(client)
    payload = body(source)
    response = client.post(path(project_id), json=payload)
    assert response.status_code == 201, response.text
    return project_id, source, payload, response.json()

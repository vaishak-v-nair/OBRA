from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from orba.models import AuthSession, Project
from orba.pm_repository import create_plan
from orba.pm_schemas import Source, document_nodes
from orba.security import digest
from scripts.pm_sample import human_document


def project(client):
    response = client.post(
        "/api/v1/projects",
        json={
            "title": "Habit journal",
            "description": "Track a habit with daily check-ins.",
            "workspace_id": client.workspace_id,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def identity(client):
    with Session(client.app.state.engine) as db:
        saved = db.scalar(
            select(AuthSession).where(
                AuthSession.token_hash == digest(client.cookies.get("orba_session"))
            )
        )
        return saved.user_id, saved.id


def seed(client, project_id):
    actor, _ = identity(client)
    with Session(client.app.state.engine) as db, db.begin():
        plan = create_plan(db, UUID(project_id), actor, human_document(actor))
        return plan.id


def unit_output():
    """A labeled unit double's input, NOT actual generated content."""
    document = human_document("unit-fixture")
    for _, node in document_nodes(document):
        node.source = Source(kind="suggested")
    return document


def counts(client):
    from sqlalchemy import func

    from orba.pm_models import ProductManagerRun, ProductPlan

    with Session(client.app.state.engine) as db:
        return tuple(
            db.scalar(select(func.count()).select_from(model))
            for model in (ProductManagerRun, ProductPlan, Project)
        )

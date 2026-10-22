"""Labeled controlled provider only; all source/auth/API/database behavior is real."""

from uuid import uuid4

from orba.architect import model_provider
from orba.pm_provider import ProviderResult
from scripts.architect_sample import controlled_document
from tests.pm_support import project, seed


class ControlledProvider:
    def __init__(self, document=None, failure=None, callback=None):
        self.document = document or controlled_document()
        self.failure, self.callback, self.calls = failure, callback, 0

    async def generate(self, snapshot):
        self.calls += 1
        if self.callback:
            self.callback(snapshot)
        if self.failure:
            raise self.failure
        return ProviderResult(
            self.document if isinstance(self.document, str) else self.document.model_dump_json()
        )


def approved_source(client, project_id=None):
    project_id = project_id or project(client)
    source_id = str(seed(client, project_id))
    approved = client.post(
        f"/api/v1/projects/{project_id}/pm-plans/{source_id}/approve",
        json={"version": 1, "expected_revision": 1},
    )
    assert approved.status_code == 200, approved.text
    return project_id, approved.json()


def payload(source):
    return {
        "client_request_id": str(uuid4()),
        "source_plan_id": source["id"],
        "source_version": source["version"],
        "source_revision": source["revision"],
        "constraints": "Local first release",
    }


def generate(client, project_id, source, provider=None, body=None):
    selected = provider or ControlledProvider()
    client.app.dependency_overrides[model_provider] = lambda: selected
    result = client.post(
        f"/api/v1/projects/{project_id}/architect-runs", json=body or payload(source)
    )
    return result, selected


def artifact(client, project_id, run):
    response = client.get(f"/api/v1/projects/{project_id}/architectures/{run['architecture_id']}")
    assert response.status_code == 200, response.text
    return response.json()

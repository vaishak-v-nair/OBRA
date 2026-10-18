import json
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path
from threading import Barrier
from uuid import UUID

import pytest
from conftest import csrf, register
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from orba.models import AuthSession, Project, User, WorkspaceInvitation, WorkspaceMember
from orba.security import digest, now, passwords

PASSWORD = "A long test password!"


def account(app, email):
    other = TestClient(app)
    user = register(other, email)
    return other, user


def invite(owner, space, email, role="member"):
    response = owner.post(
        f"/api/v1/workspaces/{space}/invitations", json={"email": email, "role": role}
    )
    assert response.status_code == 201, response.text
    data = response.json()
    return data, data["invitation_link"].split("#token=")[1]


def join(owner, other, space, user, role="member"):
    _, token = invite(owner, space, user["email"], role)
    response = other.post("/api/v1/invitations/accept", json={"token": token})
    assert response.status_code == 200, response.text


def test_registration_hashes_and_cookie_security(raw_client):
    user = register(raw_client, " First@Example.com ")
    assert user["email"] == "first@example.com"
    assert set(user) == {"id", "email", "display_name"}
    token = raw_client.cookies.get("orba_session")
    with Session(raw_client.app.state.engine) as db:
        saved = db.get(User, UUID(user["id"]))
        assert saved.password_hash.startswith("$argon2id$")
        assert passwords.verify(saved.password_hash, PASSWORD)
        session = db.scalar(select(AuthSession).where(AuthSession.user_id == saved.id))
        assert session.token_hash == digest(token) and session.token_hash != token
        assert session.expires_at > session.created_at
    other, second = account(raw_client.app, "second@example.com")
    with Session(raw_client.app.state.engine) as db:
        assert db.get(User, UUID(second["id"])).password_hash != saved.password_hash
    csrf(raw_client)
    response = raw_client.post(
        "/api/v1/auth/login", json={"email": user["email"], "password": PASSWORD}
    )
    assert response.status_code == 200
    cookie = response.headers["set-cookie"]
    assert "HttpOnly" in cookie and "SameSite=lax" in cookie
    assert raw_client.cookies.get("orba_session") != token
    with Session(raw_client.app.state.engine) as db:
        assert (
            db.scalar(select(AuthSession).where(AuthSession.token_hash == digest(token))).revoked_at
            is not None
        )
    other.close()


def test_duplicate_normalized_email_and_password_policy(raw_client):
    register(raw_client)
    response = raw_client.post(
        "/api/v1/auth/register",
        json={"email": " OWNER@EXAMPLE.COM ", "password": PASSWORD, "display_name": "Duplicate"},
    )
    assert response.status_code == 409
    assert (
        raw_client.post(
            "/api/v1/auth/register",
            json={"email": "weak@example.com", "password": "short", "display_name": "Weak"},
        ).status_code
        == 422
    )
    with Session(raw_client.app.state.engine) as db:
        assert db.scalar(select(func.count()).select_from(User)) == 1


def test_login_invalid_and_logout_revocation(raw_client):
    user = register(raw_client)
    response = raw_client.post(
        "/api/v1/auth/login", json={"email": user["email"], "password": "wrong"}
    )
    assert response.status_code == 401
    assert "password_hash" not in response.text
    assert (
        raw_client.post(
            "/api/v1/auth/login", json={"email": user["email"], "password": PASSWORD}
        ).status_code
        == 200
    )
    csrf(raw_client)
    token = raw_client.cookies.get("orba_session")
    assert raw_client.get("/api/v1/auth/me").json()["id"] == user["id"]
    assert raw_client.post("/api/v1/auth/logout").status_code == 204
    raw_client.cookies.set("orba_session", token)
    assert raw_client.get("/api/v1/auth/me").status_code == 401
    with Session(raw_client.app.state.engine) as db:
        assert db.scalar(
            select(AuthSession).where(AuthSession.token_hash == digest(token))
        ).revoked_at


@pytest.mark.parametrize("state", ["expired", "revoked"])
def test_invalid_sessions_rejected(raw_client, state):
    register(raw_client)
    token = raw_client.cookies.get("orba_session")
    with Session(raw_client.app.state.engine) as db:
        session = db.scalar(select(AuthSession).where(AuthSession.token_hash == digest(token)))
        if state == "expired":
            session.expires_at = now() - timedelta(seconds=1)
        else:
            session.revoked_at = now()
        db.commit()
    assert raw_client.get("/api/v1/auth/me").status_code == 401
    assert raw_client.get("/api/v1/workspaces").status_code == 401


def test_anonymous_and_csrf_origin_guards(raw_client):
    assert raw_client.get("/api/v1/projects").status_code == 401
    csrf(raw_client)
    body = {"email": "a@example.com", "password": PASSWORD, "display_name": "A"}
    assert (
        raw_client.post(
            "/api/v1/auth/register", json=body, headers={"X-CSRF-Token": "wrong"}
        ).status_code
        == 403
    )
    assert (
        raw_client.post(
            "/api/v1/auth/register", json=body, headers={"Origin": "https://evil.example"}
        ).status_code
        == 403
    )
    register(raw_client)
    raw_client.headers.pop("X-CSRF-Token")
    assert raw_client.post("/api/v1/workspaces", json={"name": "Denied"}).status_code == 403
    csrf(raw_client)
    old_csrf = raw_client.headers["X-CSRF-Token"]
    assert (
        raw_client.post(
            "/api/v1/auth/login", json={"email": "owner@example.com", "password": PASSWORD}
        ).status_code
        == 200
    )
    assert (
        raw_client.post(
            "/api/v1/workspaces", json={"name": "Stale token"}, headers={"X-CSRF-Token": old_csrf}
        ).status_code
        == 403
    )
    with Session(raw_client.app.state.engine) as db:
        assert db.scalar(select(func.count()).select_from(WorkspaceMember)) == 0


def test_non_ascii_csrf_is_safely_rejected(raw_client):
    csrf(raw_client)
    response = raw_client.post(
        "/api/v1/auth/register",
        json={
            "email": "invalid-header@example.com",
            "password": PASSWORD,
            "display_name": "Rejected",
        },
        headers=[(b"x-csrf-token", b"\xff")],
    )
    assert response.status_code == 403
    assert "CSRF validation failed" in response.text


def test_secure_cookie_configuration_and_https(raw_client):
    from conftest import TEST_DATABASE_URL

    from orba.config import Settings
    from orba.main import create_app

    with pytest.raises(ValueError, match="COOKIE_SECURE"):
        Settings(web_origin="https://orba.example", cookie_secure=False)
    app = create_app(
        Settings(
            database_url=TEST_DATABASE_URL, web_origin="https://orba.example", cookie_secure=True
        )
    )
    with TestClient(app, base_url="https://orba.example") as client:
        token = client.get("/api/v1/auth/csrf").json()["csrf_token"]
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "secure@example.com", "password": PASSWORD, "display_name": "Secure"},
            headers={"Origin": "https://orba.example", "X-CSRF-Token": token},
        )
        assert response.status_code == 201
        assert "Secure" in response.headers["set-cookie"]
        assert client.get("/api/v1/auth/me").json()["email"] == "secure@example.com"


def test_login_throttle_is_persisted(raw_client):
    csrf(raw_client)
    body = {"email": "unknown@example.com", "password": "incorrect"}
    for _ in range(5):
        assert raw_client.post("/api/v1/auth/login", json=body).status_code == 401
    other = TestClient(raw_client.app)
    csrf(other)
    response = other.post("/api/v1/auth/login", json=body)
    assert response.status_code == 429
    assert response.headers["retry-after"] == "900"
    other.close()


def test_workspace_owner_and_invitation_hash_atomic_membership(client):
    space = client.workspace_id
    owner = client.get("/api/v1/auth/me").json()
    assert client.get(f"/api/v1/workspaces/{space}").json()["role"] == "owner"
    with Session(client.app.state.engine) as db:
        assert (
            db.scalar(
                select(WorkspaceMember).where(
                    WorkspaceMember.workspace_id == UUID(space),
                    WorkspaceMember.user_id == UUID(owner["id"]),
                )
            ).role
            == "owner"
        )
    other, user = account(client.app, "invitee@example.com")
    data, token = invite(client, space, user["email"])
    with Session(client.app.state.engine) as db:
        saved = db.get(WorkspaceInvitation, UUID(data["id"]))
        assert saved.token_hash == digest(token) and saved.token_hash != token
    listing = client.get(f"/api/v1/workspaces/{space}/invitations")
    assert (
        token not in listing.text
        and "token_hash" not in listing.text
        and "invitation_link" not in listing.text
    )
    assert other.post("/api/v1/invitations/accept", json={"token": token}).status_code == 200
    assert other.post("/api/v1/invitations/accept", json={"token": token}).status_code == 400
    with Session(client.app.state.engine) as db:
        saved = db.get(WorkspaceInvitation, UUID(data["id"]))
        assert saved.status == "accepted" and saved.accepted_at
        assert (
            db.scalar(
                select(func.count())
                .select_from(WorkspaceMember)
                .where(
                    WorkspaceMember.workspace_id == UUID(space),
                    WorkspaceMember.user_id == UUID(user["id"]),
                )
            )
            == 1
        )
    other.close()


@pytest.mark.parametrize("failure", ["expired", "revoked", "wrong_email", "inviter_removed"])
def test_invitation_failure_states(client, failure):
    other, user = account(client.app, "intended@example.com")
    data, token = invite(
        client,
        client.workspace_id,
        "different@example.com" if failure == "wrong_email" else user["email"],
    )
    with Session(client.app.state.engine) as db:
        invitation = db.get(WorkspaceInvitation, UUID(data["id"]))
        if failure == "expired":
            invitation.expires_at = now() - timedelta(seconds=1)
        if failure == "revoked":
            invitation.status, invitation.revoked_at = "revoked", now()
        if failure == "inviter_removed":
            member = db.scalar(
                select(WorkspaceMember).where(
                    WorkspaceMember.workspace_id == UUID(client.workspace_id)
                )
            )
            db.delete(member)
        db.commit()
    response = other.post("/api/v1/invitations/accept", json={"token": token})
    assert response.status_code == 400
    with Session(client.app.state.engine) as db:
        assert (
            db.scalar(select(WorkspaceMember).where(WorkspaceMember.user_id == UUID(user["id"])))
            is None
        )
    other.close()


@pytest.mark.parametrize("role", ["viewer", "member", "admin"])
def test_permission_matrix(client, role):
    other, user = account(client.app, f"{role}@example.com")
    join(client, other, client.workspace_id, user, role)
    project = {
        "title": "Role project",
        "description": "Real write",
        "workspace_id": client.workspace_id,
    }
    response = other.post("/api/v1/projects", json=project)
    assert response.status_code == (403 if role == "viewer" else 201)
    if role != "admin":
        assert (
            other.post(
                f"/api/v1/workspaces/{client.workspace_id}/invitations",
                json={"email": "new@example.com", "role": "viewer"},
            ).status_code
            == 403
        )
    assert (
        other.patch(
            f"/api/v1/workspaces/{client.workspace_id}/members/{user['id']}", json={"role": "owner"}
        ).status_code
        == 403
    )
    owner = client.get("/api/v1/auth/me").json()
    assert (
        other.delete(f"/api/v1/workspaces/{client.workspace_id}/members/{owner['id']}").status_code
        == 403
    )
    assert (
        other.patch(
            f"/api/v1/workspaces/{client.workspace_id}/members/{owner['id']}",
            json={"role": "viewer"},
        ).status_code
        == 403
    )
    other.close()


def test_final_owner_and_role_changes(client):
    user = client.get("/api/v1/auth/me").json()
    url = f"/api/v1/workspaces/{client.workspace_id}/members/{user['id']}"
    assert client.delete(url).status_code == 409
    assert client.patch(url, json={"role": "admin"}).status_code == 409
    other, second = account(client.app, "second-owner@example.com")
    join(client, other, client.workspace_id, second)
    assert (
        client.patch(
            f"/api/v1/workspaces/{client.workspace_id}/members/{second['id']}",
            json={"role": "owner"},
        ).status_code
        == 200
    )
    assert client.patch(url, json={"role": "viewer"}).status_code == 200
    assert (
        client.post(
            "/api/v1/projects",
            json={"title": "Denied", "description": "Demoted", "workspace_id": client.workspace_id},
        ).status_code
        == 403
    )
    assert other.delete(url).status_code == 204
    assert client.get(f"/api/v1/workspaces/{client.workspace_id}/members").status_code == 404
    other.close()


def test_private_project_isolation_and_forged_ids(client):
    project = client.post(
        "/api/v1/projects",
        json={
            "title": "Private secret title",
            "description": "Private secret body",
            "workspace_id": client.workspace_id,
        },
    ).json()
    other, user = account(client.app, "unrelated@example.com")
    own = other.post("/api/v1/workspaces", json={"name": "Other workspace"}).json()
    private_response = other.get(f"/api/v1/projects/{project['id']}")
    assert private_response.status_code == 404
    assert "Private secret" not in private_response.text
    denied = other.patch(
        f"/api/v1/projects/{project['id']}", json={"title": "Stolen", "description": "Forged"}
    )
    assert denied.status_code == 404 and "Private secret" not in denied.text
    assert other.get(f"/api/v1/workspaces/{client.workspace_id}/members").status_code == 404
    assert other.get(f"/api/v1/projects?workspace_id={client.workspace_id}").status_code == 404
    assert other.get(f"/api/v1/projects?workspace_id={own['id']}").json() == []
    assert (
        other.post(
            "/api/v1/projects",
            json={"title": "Forged", "description": "Bad", "workspace_id": client.workspace_id},
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/api/v1/projects",
            json={
                "title": "Forged creator",
                "description": "Bad",
                "workspace_id": client.workspace_id,
                "creator_id": user["id"],
            },
        ).status_code
        == 422
    )
    with Session(client.app.state.engine) as db:
        saved = db.get(Project, UUID(project["id"]))
        assert saved.title == "Private secret title" and saved.workspace_id == UUID(
            client.workspace_id
        )
        evidence = {
            "project_id": project["id"],
            "http_status": private_response.status_code,
            "response": private_response.json(),
            "database_project_still_exists": saved is not None,
            "database_workspace_unchanged": str(saved.workspace_id) == client.workspace_id,
        }
        path = Path("../../docs/evidence/stage02-authorization.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(evidence, indent=2))
    other.close()


def test_viewer_cannot_edit_and_member_can_edit(client):
    project = client.post(
        "/api/v1/projects",
        json={"title": "Before", "description": "Original", "workspace_id": client.workspace_id},
    ).json()
    other, user = account(client.app, "reader@example.com")
    join(client, other, client.workspace_id, user, "viewer")
    url = f"/api/v1/projects/{project['id']}"
    assert other.get(url).status_code == 200
    assert other.patch(url, json={"title": "After", "description": "Changed"}).status_code == 403
    assert (
        client.patch(
            f"/api/v1/workspaces/{client.workspace_id}/members/{user['id']}",
            json={"role": "member"},
        ).status_code
        == 200
    )
    response = other.patch(url, json={"title": "After", "description": "Changed"})
    assert response.status_code == 200
    with Session(client.app.state.engine) as db:
        assert db.get(Project, UUID(project["id"])).title == "After"
    other.close()


def test_concurrent_final_owner_demotion_is_serialized(client):
    other, user = account(client.app, "concurrent-owner@example.com")
    join(client, other, client.workspace_id, user)
    client.patch(
        f"/api/v1/workspaces/{client.workspace_id}/members/{user['id']}", json={"role": "owner"}
    )
    first_id = client.get("/api/v1/auth/me").json()["id"]
    barrier = Barrier(2)

    def demote(actor, uid):
        barrier.wait(timeout=5)
        return actor.patch(
            f"/api/v1/workspaces/{client.workspace_id}/members/{uid}", json={"role": "viewer"}
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(demote, actor, uid)
            for actor, uid in [(client, first_id), (other, user["id"])]
        ]
        statuses = sorted(f.result(timeout=15).status_code for f in futures)
    assert statuses == [200, 409]
    with Session(client.app.state.engine) as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(WorkspaceMember)
                .where(
                    WorkspaceMember.workspace_id == UUID(client.workspace_id),
                    WorkspaceMember.role == "owner",
                )
            )
            == 1
        )
    other.close()


def test_concurrent_invitation_acceptance_only_one_membership(client):
    other, user = account(client.app, "atomic@example.com")
    _, token = invite(client, client.workspace_id, user["email"])
    twin = TestClient(client.app)
    twin.cookies.update(other.cookies)
    twin.headers.update(other.headers)
    barrier = Barrier(2)

    def accept(actor):
        barrier.wait(timeout=5)
        return actor.post("/api/v1/invitations/accept", json={"token": token})

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(accept, actor) for actor in [other, twin]]
        assert sorted(f.result(timeout=15).status_code for f in futures) == [200, 400]
    with Session(client.app.state.engine) as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(WorkspaceMember)
                .where(
                    WorkspaceMember.workspace_id == UUID(client.workspace_id),
                    WorkspaceMember.user_id == UUID(user["id"]),
                )
            )
            == 1
        )
    other.close()
    twin.close()


def test_invitation_revocation_endpoint(client):
    _, user = account(client.app, "revoke@example.com")
    data, _token = invite(client, client.workspace_id, user["email"])
    assert (
        client.delete(
            f"/api/v1/workspaces/{client.workspace_id}/invitations/{data['id']}"
        ).status_code
        == 204
    )
    with Session(client.app.state.engine) as db:
        invite_row = db.get(WorkspaceInvitation, UUID(data["id"]))
        assert invite_row.revoked_at and invite_row.status == "revoked"


def test_limiter_serializes_independent_app_instances(raw_client):
    from conftest import TEST_DATABASE_URL

    from orba.config import Settings
    from orba.main import create_app

    config = Settings(database_url=TEST_DATABASE_URL, login_max_attempts=1)
    first = TestClient(create_app(config))
    second = TestClient(create_app(config))
    csrf(first)
    csrf(second)
    barrier = Barrier(2)

    def attempt(actor):
        barrier.wait(timeout=5)
        return actor.post(
            "/api/v1/auth/login",
            json={"email": "race-limit@example.com", "password": "Bad password"},
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(attempt, actor) for actor in [first, second]]
        assert sorted(f.result(timeout=15).status_code for f in futures) == [401, 429]
    first.close()
    second.close()


def test_member_revocation_and_project_write_are_serialized(client):
    other, user = account(client.app, "revoke-write@example.com")
    join(client, other, client.workspace_id, user)
    barrier = Barrier(2)

    def revoke():
        barrier.wait(timeout=5)
        return client.delete(f"/api/v1/workspaces/{client.workspace_id}/members/{user['id']}")

    def write():
        barrier.wait(timeout=5)
        return other.post(
            "/api/v1/projects",
            json={
                "title": "Racing write",
                "description": "Either commits before removal or is rejected",
                "workspace_id": client.workspace_id,
            },
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        removal = pool.submit(revoke)
        creation = pool.submit(write)
        assert removal.result(timeout=15).status_code == 204
        result = creation.result(timeout=15)
    assert result.status_code in {201, 404}
    with Session(client.app.state.engine) as db:
        assert (
            db.scalar(
                select(WorkspaceMember).where(
                    WorkspaceMember.workspace_id == UUID(client.workspace_id),
                    WorkspaceMember.user_id == UUID(user["id"]),
                )
            )
            is None
        )
        count = db.scalar(
            select(func.count()).select_from(Project).where(Project.creator_id == UUID(user["id"]))
        )
        assert count == (1 if result.status_code == 201 else 0)
    assert (
        other.post(
            "/api/v1/projects",
            json={
                "title": "After removal",
                "description": "Must fail",
                "workspace_id": client.workspace_id,
            },
        ).status_code
        == 404
    )
    other.close()

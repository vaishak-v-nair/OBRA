"""Real PostgreSQL credential-policy integration; no mocked authentication."""

import secrets
import unicodedata
from datetime import timedelta
from uuid import UUID

import pytest
from argon2 import PasswordHasher, Type
from conftest import csrf, register
from fastapi.testclient import TestClient
from pydantic import TypeAdapter, ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from orba.models import AuthSession, User
from orba.schemas import NewPassword
from orba.security import digest, now, passwords, verify_password
from tests.password_support import LEGACY_PASSWORD, seed_legacy_user


def test_fourteen_character_registration_is_rejected_without_rows(raw_client):
    csrf(raw_client)
    response = raw_client.post(
        "/api/v1/auth/register",
        json={
            "email": "boundary@example.com",
            "password": "a" * 14,
            "display_name": "Boundary",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert "orba_session" not in raw_client.cookies
    with Session(raw_client.app.state.engine) as db:
        assert db.scalar(select(func.count()).select_from(User)) == 0
        assert db.scalar(select(func.count()).select_from(AuthSession)) == 0


def test_fifteen_lowercase_characters_register_with_real_hash_and_session(raw_client):
    csrf(raw_client)
    response = raw_client.post(
        "/api/v1/auth/register",
        json={"email": "fifteen@example.com", "password": "a" * 15, "display_name": "Fifteen"},
    )
    assert response.status_code == 201
    user_id = UUID(response.json()["id"])
    assert raw_client.get("/api/v1/auth/me").json()["id"] == str(user_id)
    with Session(raw_client.app.state.engine) as db:
        user = db.get(User, user_id)
        assert user.password_hash.startswith("$argon2id$")
        assert verify_password(user.password_hash, "a" * 15)
        assert not verify_password(user.password_hash, "a" * 14)
        session = db.scalar(select(AuthSession).where(AuthSession.user_id == user_id))
        assert session and session.revoked_at is None


@pytest.mark.parametrize(
    "patch",
    [
        {"password": "a" * 12},
        {"password": "a" * 129},
        {"password": " " * 15},
        {"password": ""},
        {},
        {"password": 123456789012345},
    ],
    ids=["legacy-length-new", "too-long", "whitespace", "empty", "missing", "wrong-type"],
)
def test_invalid_new_credentials_preserve_existing_user_and_session(raw_client, patch):
    owner = register(raw_client)
    user_id = UUID(owner["id"])
    token_hash = digest(raw_client.cookies.get("orba_session"))
    with Session(raw_client.app.state.engine) as db:
        original_hash = db.get(User, user_id).password_hash
    response = raw_client.post(
        "/api/v1/auth/register",
        json={"email": "invalid-new@example.com", "display_name": "Invalid", **patch},
    )
    assert response.status_code == 422
    assert any(d["field"] == "body.password" for d in response.json()["error"]["details"])
    assert "input" not in response.text and "password_hash" not in response.text
    assert raw_client.get("/api/v1/auth/me").json()["id"] == owner["id"]
    with Session(raw_client.app.state.engine) as db:
        assert db.scalar(select(func.count()).select_from(User)) == 1
        assert db.scalar(select(func.count()).select_from(AuthSession)) == 1
        preserved_hash = db.get(User, user_id).password_hash == original_hash
        assert preserved_hash
        session = db.scalar(select(AuthSession).where(AuthSession.token_hash == token_hash))
        assert session.revoked_at is None


@pytest.mark.parametrize(
    "value",
    ["a" * 64, "a" * 128, "\U0001f510" * 128, "  a long exact passphrase  ", "cafe\u0301" * 4],
    ids=["ascii64", "ascii128", "astral128", "surrounding-spaces", "combining-sequence"],
)
def test_passphrases_hash_and_authenticate_the_exact_complete_value(raw_client, value):
    csrf(raw_client)
    response = raw_client.post(
        "/api/v1/auth/register",
        json={"email": "exact@example.com", "password": value, "display_name": "Exact"},
    )
    assert response.status_code == 201
    user_id = UUID(response.json()["id"])
    altered = (
        value.strip()
        if value != value.strip()
        else unicodedata.normalize("NFC", value)
        if value != unicodedata.normalize("NFC", value)
        else value[:-1]
    )
    with Session(raw_client.app.state.engine) as db:
        original_hash = db.get(User, user_id).password_hash
        assert verify_password(original_hash, value)
        assert not verify_password(original_hash, altered)
    csrf(raw_client)
    assert (
        raw_client.post(
            "/api/v1/auth/login", json={"email": "exact@example.com", "password": altered}
        ).status_code
        == 401
    )
    assert (
        raw_client.post(
            "/api/v1/auth/login", json={"email": "exact@example.com", "password": value}
        ).status_code
        == 200
    )
    with Session(raw_client.app.state.engine) as db:
        preserved_hash = db.get(User, user_id).password_hash == original_hash
        assert preserved_hash


def test_legacy_twelve_character_login_preserves_hash_and_independent_session(raw_client):
    user_id = UUID(seed_legacy_user("legacy@example.com"))
    presented, independent = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    with Session(raw_client.app.state.engine) as db:
        original = db.get(User, user_id)
        original_hash, created_at = original.password_hash, original.created_at
        for token in (presented, independent):
            db.add(
                AuthSession(
                    user_id=user_id,
                    token_hash=digest(token),
                    expires_at=now() + timedelta(hours=1),
                )
            )
        db.commit()
    raw_client.cookies.set("orba_session", presented, domain="testserver.local", path="/")
    assert raw_client.get("/api/v1/auth/me").json()["id"] == str(user_id)
    csrf(raw_client)
    response = raw_client.post(
        "/api/v1/auth/login", json={"email": "legacy@example.com", "password": LEGACY_PASSWORD}
    )
    assert response.status_code == 200
    rotated = raw_client.cookies.get("orba_session") != presented
    assert rotated
    assert raw_client.get("/api/v1/auth/me").json()["id"] == str(user_id)
    with Session(raw_client.app.state.engine) as db:
        user = db.get(User, user_id)
        preserved_hash = user.password_hash == original_hash
        assert preserved_hash and user.created_at == created_at
        assert (
            db.scalar(
                select(AuthSession).where(AuthSession.token_hash == digest(presented))
            ).revoked_at
            is not None
        )
        assert (
            db.scalar(
                select(AuthSession).where(AuthSession.token_hash == digest(independent))
            ).revoked_at
            is None
        )
    other = TestClient(raw_client.app)
    try:
        other.cookies.set("orba_session", independent, domain="testserver.local", path="/")
        assert other.get("/api/v1/auth/me").json()["id"] == str(user_id)
    finally:
        other.close()


def test_legacy_twelve_character_password_can_receive_normal_argon2_parameter_upgrade(raw_client):
    old_hash = PasswordHasher(time_cost=1, memory_cost=1024, parallelism=1, type=Type.ID).hash(
        LEGACY_PASSWORD
    )
    assert passwords.check_needs_rehash(old_hash)
    user_id = UUID(seed_legacy_user("rehash@example.com", password_hash=old_hash))
    csrf(raw_client)
    response = raw_client.post(
        "/api/v1/auth/login", json={"email": "rehash@example.com", "password": LEGACY_PASSWORD}
    )
    assert response.status_code == 200
    with Session(raw_client.app.state.engine) as db:
        updated_hash = db.get(User, user_id).password_hash
        upgraded = updated_hash != old_hash
        assert upgraded and not passwords.check_needs_rehash(updated_hash)
        assert verify_password(updated_hash, LEGACY_PASSWORD)


def test_openapi_publishes_new_credential_policy_without_changing_login(raw_client):
    schemas = raw_client.get("/openapi.json").json()["components"]["schemas"]
    new = schemas["RegisterInput"]["properties"]["password"]
    existing = schemas["LoginInput"]["properties"]["password"]
    assert (new["minLength"], new["maxLength"]) == (15, 128)
    assert (existing["minLength"], existing["maxLength"]) == (1, 128)


def test_future_credential_write_schemas_can_reuse_the_new_password_type():
    policy = TypeAdapter(NewPassword)
    assert policy.validate_python("a" * 15) == "a" * 15
    for value in ("a" * 14, "a" * 129, " " * 15):
        with pytest.raises(ValidationError):
            policy.validate_python(value)


def test_legacy_fixture_refuses_a_development_database_before_connection():
    with pytest.raises(RuntimeError, match="Refusing test mutation"):
        seed_legacy_user(
            "unsafe@example.com",
            database_url="postgresql+psycopg://orba:orba@127.0.0.1:54329/orba",
        )

"""Password hashing, opaque credentials and backend authorization boundaries."""

import hashlib
import hmac
import logging
import secrets
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from argon2 import PasswordHasher, Type
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from orba.db import get_session
from orba.models import AuthSession, User, Workspace, WorkspaceMember

passwords = PasswordHasher(type=Type.ID)
# Valid Argon2 work for unknown identities reduces username timing differences.
dummy_hash = passwords.hash(secrets.token_urlsafe(32))
DB = Annotated[Session, Depends(get_session)]


def audit(event: str, actor_id=None, workspace_id=None):
    # No raw credentials, email, CSRF value, session token or invitation token.
    logging.getLogger("uvicorn.error").info(
        "security_event=%s actor_id=%s workspace_id=%s", event, actor_id or "-", workspace_id or "-"
    )


def now():
    return datetime.now(UTC)


def digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def csrf_for(token: str) -> str:
    return hmac.new(token.encode(), b"orba-csrf-v1", hashlib.sha256).hexdigest()


def verify_password(hashed: str, plain: str) -> bool:
    try:
        return passwords.verify(hashed, plain)
    except (VerificationError, InvalidHashError):
        return False


def optional_session(request: Request, db: Session) -> AuthSession | None:
    raw = request.cookies.get(request.app.state.settings.session_cookie)
    if not raw or len(raw) > 256:
        return None
    return db.scalar(
        select(AuthSession)
        .join(User)
        .where(
            AuthSession.token_hash == digest(raw),
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > now(),
            User.status == "active",
        )
    )


def authenticated(request: Request, db: DB) -> AuthSession:
    session = optional_session(request, db)
    if session is None:
        raise HTTPException(401, "Sign in to continue. Your session may have expired.")
    return session


Identity = Annotated[AuthSession, Depends(authenticated)]


def check_origin(request: Request):
    if request.headers.get("origin") != request.app.state.settings.web_origin:
        audit("origin_rejected")
        raise HTTPException(403, "Request origin is not allowed.")


def csrf_guard(request: Request, db: DB):
    check_origin(request)
    session = optional_session(request, db)
    if session:
        expected = csrf_for(request.cookies[request.app.state.settings.session_cookie])
    else:
        expected = request.cookies.get("orba_preauth", "")
    supplied = request.headers.get("x-csrf-token", "")
    if (
        not expected
        or not supplied
        or len(supplied) > 128
        or not secrets.compare_digest(expected.encode(), supplied.encode())
    ):
        audit("csrf_rejected")
        raise HTTPException(403, "CSRF validation failed. Refresh and try again.")


def membership(db: Session, workspace_id: UUID, user_id: UUID, *, lock: bool = False):
    query = select(Workspace).where(Workspace.id == workspace_id, Workspace.is_legacy.is_(False))
    if lock:
        query = query.with_for_update()
    workspace = db.scalar(query)
    member = db.scalar(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
    )
    if workspace is None or member is None:
        raise HTTPException(404, "Workspace not found.")
    return workspace, member


def require_role(member: WorkspaceMember, roles: set[str]):
    if member.role not in roles:
        raise HTTPException(403, "Your workspace role does not permit this action.")

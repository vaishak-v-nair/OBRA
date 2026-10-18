import secrets
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import delete, func, select, text
from sqlalchemy.exc import IntegrityError

from orba.models import AuthSession, LoginAttempt, User
from orba.schemas import LoginInput, RegisterInput, UserRead
from orba.security import (
    DB,
    Identity,
    audit,
    csrf_for,
    csrf_guard,
    digest,
    dummy_hash,
    now,
    optional_session,
    passwords,
    verify_password,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def establish(request: Request, response: Response, db, user: User):
    config = request.app.state.settings
    old = optional_session(request, db)
    if old:
        old.revoked_at = now()
    token = secrets.token_urlsafe(32)
    db.add(
        AuthSession(
            user_id=user.id,
            token_hash=digest(token),
            expires_at=now() + timedelta(seconds=config.session_lifetime_seconds),
        )
    )
    db.commit()
    audit("session_rotated", user.id)
    response.set_cookie(
        config.session_cookie,
        token,
        max_age=config.session_lifetime_seconds,
        httponly=True,
        secure=config.cookie_secure,
        samesite="lax",
        path="/",
    )
    response.delete_cookie(
        "orba_preauth", path="/", secure=config.cookie_secure, httponly=True, samesite="strict"
    )
    return user


def rate_limit(request: Request, db, email: str):
    """Serialize account/IP buckets in PostgreSQL; count attempts before hashing work."""
    config = request.app.state.settings
    # Never trust caller-controlled X-Forwarded-For. Behind local proxy IP is shared.
    peer = request.client.host if request.client else "unknown"
    keys = sorted([digest(f"email:{email}"), digest(f"ip:{peer}")])
    cutoff = now() - timedelta(seconds=config.login_window_seconds)
    for key in keys:
        lock_key = int.from_bytes(bytes.fromhex(key[:16]), "big", signed=True)
        db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": lock_key})
    for key in keys:
        count = db.scalar(
            select(func.count())
            .select_from(LoginAttempt)
            .where(LoginAttempt.key == key, LoginAttempt.created_at > cutoff)
        )
        # Shared proxy IP allows a wider budget than any single account.
        maximum = (
            config.login_max_attempts
            if key == digest(f"email:{email}")
            else config.login_max_attempts * 20
        )
        if count >= maximum:
            audit("login_throttled")
            raise HTTPException(
                429,
                "Too many sign-in attempts. Try again later.",
                headers={"Retry-After": str(config.login_window_seconds)},
            )
        db.add(LoginAttempt(key=key))
    db.execute(delete(LoginAttempt).where(LoginAttempt.created_at < cutoff))
    db.commit()  # Failed credentials still consume an attempt; locks release after persistence.


@router.get("/csrf")
def csrf(request: Request, response: Response, db: DB):
    session = optional_session(request, db)
    if session:
        token = csrf_for(request.cookies[request.app.state.settings.session_cookie])
    else:
        token = secrets.token_urlsafe(32)
        response.set_cookie(
            "orba_preauth",
            token,
            max_age=900,
            httponly=True,
            secure=request.app.state.settings.cookie_secure,
            samesite="strict",
            path="/",
        )
    response.headers["Cache-Control"] = "no-store"
    return {"csrf_token": token}


@router.post(
    "/register", response_model=UserRead, status_code=201, dependencies=[Depends(csrf_guard)]
)
def register(payload: RegisterInput, request: Request, response: Response, db: DB):
    rate_limit(request, db, payload.email)
    user = User(
        email=str(payload.email),
        password_hash=passwords.hash(payload.password),
        display_name=payload.display_name,
    )
    db.add(user)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Unable to register with this email.") from None
    return establish(request, response, db, user)


@router.post("/login", response_model=UserRead, dependencies=[Depends(csrf_guard)])
def login(payload: LoginInput, request: Request, response: Response, db: DB):
    rate_limit(request, db, payload.email)
    user = db.scalar(select(User).where(User.email == payload.email))
    valid = verify_password(user.password_hash if user else dummy_hash, payload.password)
    if not valid or user is None or user.status != "active":
        audit("login_rejected")
        raise HTTPException(401, "Email or password is incorrect.")
    if passwords.check_needs_rehash(user.password_hash):
        user.password_hash = passwords.hash(payload.password)
    return establish(request, response, db, user)


@router.get("/me", response_model=UserRead)
def me(identity: Identity, db: DB):
    return db.get(User, identity.user_id)


@router.post("/logout", status_code=204, dependencies=[Depends(csrf_guard)])
def logout(identity: Identity, request: Request, response: Response, db: DB):
    identity.revoked_at = now()
    db.commit()
    audit("session_revoked", identity.user_id)
    response.delete_cookie(
        request.app.state.settings.session_cookie,
        path="/",
        secure=request.app.state.settings.cookie_secure,
        httponly=True,
        samesite="lax",
    )

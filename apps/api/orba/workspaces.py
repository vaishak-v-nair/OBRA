import re
import secrets
from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func, select

from orba.models import User, Workspace, WorkspaceInvitation, WorkspaceMember
from orba.schemas import InvitationAccept, InvitationCreate, RoleUpdate, WorkspaceCreate
from orba.security import DB, Identity, audit, csrf_guard, digest, membership, now, require_role

router = APIRouter(prefix="/api/v1", tags=["workspaces"])


def workspace_data(workspace, member):
    return {
        "id": workspace.id,
        "name": workspace.name,
        "slug": workspace.slug,
        "role": member.role,
        "created_at": workspace.created_at,
    }


def invitation_data(invite):
    status = (
        "expired" if invite.status == "pending" and invite.expires_at <= now() else invite.status
    )
    return {
        "id": invite.id,
        "email": invite.email,
        "role": invite.role,
        "status": status,
        "expires_at": invite.expires_at,
        "created_at": invite.created_at,
    }


@router.post("/workspaces", status_code=201, dependencies=[Depends(csrf_guard)])
def create_workspace(payload: WorkspaceCreate, identity: Identity, db: DB):
    slug = re.sub(r"[^a-z0-9]+", "-", payload.name.lower()).strip("-")[:80] or "workspace"
    workspace = Workspace(
        name=payload.name, slug=f"{slug}-{secrets.token_hex(8)}", creator_id=identity.user_id
    )
    db.add(workspace)
    db.flush()
    member = WorkspaceMember(workspace_id=workspace.id, user_id=identity.user_id, role="owner")
    db.add(member)
    db.commit()
    audit("workspace_membership_saved", identity.user_id, workspace.id)
    return workspace_data(workspace, member)


@router.get("/workspaces")
def list_workspaces(identity: Identity, db: DB):
    rows = db.execute(
        select(Workspace, WorkspaceMember)
        .join(WorkspaceMember)
        .where(
            WorkspaceMember.user_id == identity.user_id,
            Workspace.is_legacy.is_(False),
        )
        .order_by(Workspace.created_at, Workspace.id)
    ).all()
    return [workspace_data(workspace, member) for workspace, member in rows]


@router.get("/workspaces/{workspace_id}")
def get_workspace(workspace_id: UUID, identity: Identity, db: DB):
    return workspace_data(*membership(db, workspace_id, identity.user_id))


@router.get("/workspaces/{workspace_id}/members")
def list_members(workspace_id: UUID, identity: Identity, db: DB):
    membership(db, workspace_id, identity.user_id)
    rows = db.execute(
        select(WorkspaceMember, User)
        .join(User)
        .where(WorkspaceMember.workspace_id == workspace_id)
        .order_by(WorkspaceMember.joined_at)
    ).all()
    return [
        {
            "user_id": user.id,
            "email": user.email,
            "display_name": user.display_name,
            "role": member.role,
            "joined_at": member.joined_at,
        }
        for member, user in rows
    ]


@router.post(
    "/workspaces/{workspace_id}/invitations", status_code=201, dependencies=[Depends(csrf_guard)]
)
def invite(
    workspace_id: UUID, payload: InvitationCreate, request: Request, identity: Identity, db: DB
):
    _, caller = membership(db, workspace_id, identity.user_id, lock=True)
    require_role(caller, {"owner", "admin"})
    if caller.role == "admin" and payload.role == "admin":
        raise HTTPException(403, "Only Owners can invite Admins.")
    existing = db.scalar(
        select(WorkspaceMember)
        .join(User)
        .where(WorkspaceMember.workspace_id == workspace_id, User.email == payload.email)
    )
    if existing:
        raise HTTPException(409, "This user is already a member.")
    pending = db.scalar(
        select(WorkspaceInvitation).where(
            WorkspaceInvitation.workspace_id == workspace_id,
            WorkspaceInvitation.email == payload.email,
            WorkspaceInvitation.status == "pending",
        )
    )
    if pending and pending.expires_at > now():
        raise HTTPException(
            409, "A pending invitation already exists. Revoke it before creating another."
        )
    if pending:
        pending.status = "revoked"
        pending.revoked_at = now()
        db.flush()
    token = secrets.token_urlsafe(32)
    invitation = WorkspaceInvitation(
        workspace_id=workspace_id,
        inviter_id=identity.user_id,
        email=str(payload.email),
        role=payload.role,
        token_hash=digest(token),
        expires_at=now()
        + timedelta(seconds=request.app.state.settings.invitation_lifetime_seconds),
    )
    db.add(invitation)
    db.commit()
    return {
        **invitation_data(invitation),
        "invitation_link": f"{request.app.state.settings.web_origin}/invitations/accept#token={token}",
    }


@router.get("/workspaces/{workspace_id}/invitations")
def list_invitations(workspace_id: UUID, identity: Identity, db: DB):
    _, caller = membership(db, workspace_id, identity.user_id)
    require_role(caller, {"owner", "admin"})
    return [
        invitation_data(row)
        for row in db.scalars(
            select(WorkspaceInvitation)
            .where(WorkspaceInvitation.workspace_id == workspace_id)
            .order_by(WorkspaceInvitation.created_at.desc())
        ).all()
    ]


@router.delete(
    "/workspaces/{workspace_id}/invitations/{invitation_id}",
    status_code=204,
    dependencies=[Depends(csrf_guard)],
)
def revoke_invitation(workspace_id: UUID, invitation_id: UUID, identity: Identity, db: DB):
    _, caller = membership(db, workspace_id, identity.user_id, lock=True)
    require_role(caller, {"owner", "admin"})
    invitation = db.scalar(
        select(WorkspaceInvitation)
        .where(
            WorkspaceInvitation.id == invitation_id,
            WorkspaceInvitation.workspace_id == workspace_id,
        )
        .with_for_update()
    )
    if invitation is None:
        raise HTTPException(404, "Invitation not found.")
    if caller.role == "admin" and invitation.role == "admin":
        raise HTTPException(403, "Only Owners can manage Admin invitations.")
    if invitation.status != "pending":
        raise HTTPException(409, "Invitation is no longer pending.")
    invitation.status, invitation.revoked_at = "revoked", now()
    db.commit()


@router.post("/invitations/accept", dependencies=[Depends(csrf_guard)])
def accept_invitation(payload: InvitationAccept, identity: Identity, db: DB):
    invitation = db.scalar(
        select(WorkspaceInvitation).where(WorkspaceInvitation.token_hash == digest(payload.token))
    )
    if invitation is None:
        raise HTTPException(400, "Invitation is invalid or no longer available.")
    # All writers take workspace lock before invitation/member rows, in this order.
    workspace = db.scalar(
        select(Workspace)
        .where(Workspace.id == invitation.workspace_id, Workspace.is_legacy.is_(False))
        .with_for_update()
    )
    db.refresh(invitation, with_for_update=True)
    user = db.get(User, identity.user_id)
    inviter = db.scalar(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == invitation.workspace_id,
            WorkspaceMember.user_id == invitation.inviter_id,
        )
    )
    if (
        inviter is None
        or inviter.role not in {"owner", "admin"}
        or (inviter.role == "admin" and invitation.role == "admin")
    ):
        raise HTTPException(400, "Invitation is no longer available.")
    if (
        workspace is None
        or invitation.status != "pending"
        or invitation.expires_at <= now()
        or user.email != invitation.email
    ):
        raise HTTPException(
            400, "Invitation is invalid, expired, used, or belongs to another email."
        )
    if db.scalar(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace.id, WorkspaceMember.user_id == user.id
        )
    ):
        raise HTTPException(409, "You are already a member.")
    member = WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role=invitation.role)
    db.add(member)
    invitation.status, invitation.accepted_at = "accepted", now()
    db.commit()
    audit("workspace_membership_saved", identity.user_id, workspace.id)
    return workspace_data(workspace, member)


def manageable(workspace_id, user_id, identity, db, new_role=None):
    _, caller = membership(db, workspace_id, identity.user_id, lock=True)
    require_role(caller, {"owner", "admin"})
    target = db.scalar(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.user_id == user_id
        )
    )
    if target is None:
        raise HTTPException(404, "Member not found.")
    if caller.role == "admin" and (
        target.role in {"owner", "admin"} or new_role in {"owner", "admin"}
    ):
        raise HTTPException(403, "Admins can manage only Member and Viewer roles.")
    if target.role == "owner" and new_role != "owner":
        owners = db.scalar(
            select(func.count())
            .select_from(WorkspaceMember)
            .where(WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.role == "owner")
        )
        if owners <= 1:
            raise HTTPException(409, "The final Owner cannot be removed or demoted.")
    return target


@router.patch("/workspaces/{workspace_id}/members/{user_id}", dependencies=[Depends(csrf_guard)])
def update_member(
    workspace_id: UUID, user_id: UUID, payload: RoleUpdate, identity: Identity, db: DB
):
    target = manageable(workspace_id, user_id, identity, db, payload.role)
    target.role = payload.role
    db.commit()
    return {"user_id": target.user_id, "role": target.role}


@router.delete(
    "/workspaces/{workspace_id}/members/{user_id}",
    status_code=204,
    dependencies=[Depends(csrf_guard)],
)
def remove_member(workspace_id: UUID, user_id: UUID, identity: Identity, db: DB):
    target = manageable(workspace_id, user_id, identity, db)
    # Pending invites are independently revoked on member removal to prevent rejoin.
    user = db.get(User, user_id)
    for invitation in db.scalars(
        select(WorkspaceInvitation).where(
            WorkspaceInvitation.workspace_id == workspace_id,
            WorkspaceInvitation.email == user.email,
            WorkspaceInvitation.status == "pending",
        )
    ):
        invitation.status, invitation.revoked_at = "revoked", now()
    db.delete(target)
    db.commit()

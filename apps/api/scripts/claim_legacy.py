"""Local operator-only transfer. No HTTP route. Explicit project IDs, target and Owner."""

import argparse
import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from orba.config import Settings
from orba.db import make_engine
from orba.models import Project, Workspace, WorkspaceMember

LEGACY_ID = UUID("00000000-0000-0000-0000-000000000001")


def claim(db: Session, workspace_id: UUID, owner_id: UUID, project_ids: list[UUID], apply: bool):
    target = db.scalar(
        select(Workspace)
        .where(Workspace.id == workspace_id, Workspace.is_legacy.is_(False))
        .with_for_update()
    )
    owner = db.scalar(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == owner_id,
            WorkspaceMember.role == "owner",
        )
    )
    if (
        target is None
        or owner is None
        or not project_ids
        or len(set(project_ids)) != len(project_ids)
    ):
        raise ValueError(
            "Specify a regular target workspace, an existing Owner, and unique project IDs."
        )
    records = db.scalars(select(Project).where(Project.id.in_(project_ids)).with_for_update()).all()
    if len(records) != len(project_ids) or any(p.workspace_id != LEGACY_ID for p in records):
        raise ValueError(
            "Every selected project must still belong to the restricted legacy workspace. Nothing changed."
        )
    result = {
        "applied": apply,
        "workspace_id": str(workspace_id),
        "project_ids": [str(p.id) for p in records],
    }
    if apply:
        for project in records:
            # Core update avoids ORM onupdate changing original legacy timestamps.
            db.execute(
                Project.__table__.update()
                .where(Project.id == project.id)
                .values(
                    workspace_id=workspace_id,
                    creator_id=owner_id,
                    updated_at=project.updated_at,
                )
            )
        db.commit()
    else:
        db.rollback()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=UUID, required=True)
    parser.add_argument("--owner", type=UUID, required=True)
    parser.add_argument("--project", type=UUID, action="append", required=True)
    parser.add_argument(
        "--apply", action="store_true", help="Commit the transfer. Default is dry run."
    )
    args = parser.parse_args()
    engine = make_engine(Settings().database_url)
    try:
        with Session(engine) as db:
            print(json.dumps(claim(db, args.workspace, args.owner, args.project, args.apply)))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()

"""Bounded relational document assembly and transaction-local persistence primitives."""

import hashlib
from uuid import uuid4

from sqlalchemy import delete, func, select

from orba.pm_models import (
    ProductCriterion,
    ProductEpic,
    ProductManagerRun,
    ProductPlan,
    ProductStory,
)
from orba.pm_schemas import HASH_VERSION, ProductDocument, canonical


def content_hash(document: ProductDocument) -> str:
    return hashlib.sha256(canonical(document.model_dump(mode="json")).encode()).hexdigest()


def read_document(db, plan: ProductPlan) -> ProductDocument:
    epics = (
        db.execute(
            select(ProductEpic.__table__)
            .where(ProductEpic.plan_id == plan.id)
            .order_by(ProductEpic.display_order)
        )
        .mappings()
        .all()
    )
    stories = (
        db.execute(
            select(ProductStory.__table__)
            .where(ProductStory.plan_id == plan.id)
            .order_by(ProductStory.display_order)
        )
        .mappings()
        .all()
    )
    criteria = (
        db.execute(
            select(ProductCriterion.__table__)
            .where(ProductCriterion.plan_id == plan.id)
            .order_by(ProductCriterion.display_order)
        )
        .mappings()
        .all()
    )
    by_story, by_epic = {}, {}
    for row in criteria:
        by_story.setdefault(row["story_id"], []).append(
            {key: row[key] for key in ("key", "given", "when", "then", "source")}
        )
    for row in stories:
        value = {
            key: row[key]
            for key in (
                "key",
                "title",
                "statement",
                "description",
                "priority",
                "requirement_refs",
                "dependencies",
                "source",
            )
        }
        value["acceptance_criteria"] = by_story.get(row["id"], [])
        by_epic.setdefault(row["epic_id"], []).append(value)
    body = dict(plan.content)
    body["epics"] = []
    for row in epics:
        value = {key: row[key] for key in ("key", "title", "goal", "priority", "source")}
        value["stories"] = by_epic.get(row["id"], [])
        body["epics"].append(value)
    return ProductDocument.model_validate(body)


def write_document(db, plan: ProductPlan, document: ProductDocument):
    """The caller owns authorization, workspace lock, revision and commit.

    Root JSON excludes children. Stable keys retain UUIDs. Three ordered bulk
    flushes replace the child graph atomically without one query per story.
    """
    old_ids = {}
    for model in (ProductCriterion, ProductStory, ProductEpic):
        old_ids[model] = dict(
            db.execute(select(model.key, model.id).where(model.plan_id == plan.id)).all()
        )
        db.execute(delete(model).where(model.plan_id == plan.id))
    plan.content = document.model_dump(mode="json", exclude={"epics"})
    plan.content_hash, plan.hash_version = content_hash(document), HASH_VERSION
    epic_rows, story_rows, criterion_rows = [], [], []
    for epic_order, epic in enumerate(document.epics):
        epic_id = old_ids[ProductEpic].get(epic.key, uuid4())
        epic_rows.append(
            ProductEpic(
                id=epic_id,
                plan_id=plan.id,
                display_order=epic_order,
                **epic.model_dump(mode="json", exclude={"stories"}),
            )
        )
        for story_order, story in enumerate(epic.stories):
            story_id = old_ids[ProductStory].get(story.key, uuid4())
            story_rows.append(
                ProductStory(
                    id=story_id,
                    plan_id=plan.id,
                    epic_id=epic_id,
                    display_order=story_order,
                    **story.model_dump(mode="json", exclude={"acceptance_criteria"}),
                )
            )
            for criterion_order, criterion in enumerate(story.acceptance_criteria):
                criterion_rows.append(
                    ProductCriterion(
                        id=old_ids[ProductCriterion].get(criterion.key, uuid4()),
                        plan_id=plan.id,
                        story_id=story_id,
                        display_order=criterion_order,
                        **criterion.model_dump(mode="json"),
                    )
                )
    for rows in (epic_rows, story_rows, criterion_rows):
        db.add_all(rows)
        db.flush()


def create_plan(
    db, project_id, actor_id, document, *, run_id=None, source=None, copy_id=None, copy_hash=None
):
    version = (
        db.scalar(
            select(func.coalesce(func.max(ProductPlan.version), 0)).where(
                ProductPlan.project_id == project_id
            )
        )
        + 1
    )
    plan = ProductPlan(
        id=uuid4(),
        project_id=project_id,
        version=version,
        revision=1,
        state="draft",
        content={},
        content_hash=content_hash(document),
        hash_version=HASH_VERSION,
        creator_id=actor_id,
        editor_id=actor_id,
        generating_run_id=run_id,
        source_plan_id=source.id if source else None,
        source_revision=source.revision if source else None,
        source_hash=source.content_hash if source else None,
        copy_request_id=copy_id,
        copy_request_hash=copy_hash,
    )
    db.add(plan)
    db.flush()
    write_document(db, plan, document)
    return plan


def plan_summary(plan):
    return {
        key: getattr(plan, key)
        for key in (
            "id",
            "project_id",
            "version",
            "revision",
            "state",
            "content_hash",
            "hash_version",
            "creator_id",
            "editor_id",
            "approved_by",
            "approved_at",
            "created_at",
            "updated_at",
            "generating_run_id",
            "source_plan_id",
            "source_revision",
            "copy_request_id",
        )
    } | {
        "origin": "generated"
        if plan.generating_run_id
        else "human_copy"
        if plan.source_plan_id
        else "human_authored"
    }


_UNSET = object()


def run_summary(db, run, *, plan_id=_UNSET):
    if plan_id is _UNSET:
        plan_id = db.scalar(select(ProductPlan.id).where(ProductPlan.generating_run_id == run.id))
    return {
        key: getattr(run, key)
        for key in (
            "id",
            "project_id",
            "workspace_id",
            "initiator_id",
            "client_request_id",
            "status",
            "provider",
            "requested_model",
            "returned_model",
            "prompt_version",
            "created_at",
            "started_at",
            "completed_at",
            "deadline_at",
            "provider_response_id",
            "provider_request_id",
            "usage",
            "error_category",
            "diagnostic_id",
        )
    } | {"plan_id": plan_id}


def plan_detail(db, plan):
    result = plan_summary(plan) | {"document": read_document(db, plan).model_dump(mode="json")}
    run = db.get(ProductManagerRun, plan.generating_run_id) if plan.generating_run_id else None
    result["generation"] = run_summary(db, run) if run else None
    # Input snapshots are intentionally distinct from current project text.
    result["inputs"] = run.input_snapshot if run else None
    return result

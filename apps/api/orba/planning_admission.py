"""Combined PostgreSQL admission counters. Caller holds the shared advisory lock."""

from datetime import timedelta

from sqlalchemy import func, select

from orba.architect_models import ArchitectRun
from orba.pm_errors import PMError
from orba.pm_models import ProductManagerRun


def check_limits(db, config, actor_id, moment):
    active = account = recent = 0
    for model in (ProductManagerRun, ArchitectRun):
        active += db.scalar(
            select(func.count())
            .select_from(model)
            .where(model.status.in_({"pending", "running"}), model.deadline_at > moment)
        )
        window = model.created_at >= moment - timedelta(hours=1)
        account += db.scalar(
            select(func.count()).select_from(model).where(window, model.initiator_id == actor_id)
        )
        recent += db.scalar(select(func.count()).select_from(model).where(window))
    if (
        active >= config.pm_max_concurrent
        or account >= config.pm_account_attempts
        or recent >= config.pm_global_attempts
    ):
        raise PMError(
            429,
            "generation_admission_limited",
            "The combined local planning request limit was reached. Wait before trying again.",
            retry_after=60,
        )

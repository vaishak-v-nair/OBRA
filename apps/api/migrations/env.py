from alembic import context

from orba import architect_models, models, orchestration_models, pm_models, scheduler_models  # noqa: F401
from orba.config import Settings
from orba.db import Base, make_engine

target_metadata = Base.metadata

if context.is_offline_mode():
    context.configure(
        url=Settings().database_url, target_metadata=target_metadata, literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    provided = context.config.attributes.get("connection")
    if provided is not None:
        context.configure(connection=provided, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    else:
        engine = make_engine(Settings().database_url)
        with engine.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)
            with context.begin_transaction():
                context.run_migrations()
        engine.dispose()

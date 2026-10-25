import asyncio
from logging.config import fileConfig

from sqlalchemy import pool, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from alembic.script import ScriptDirectory

from xshared.db import SharedBase
from xshared.db.session import build_connect_args
import xshared.models  # noqa: F401

from xshared.config import settings


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = SharedBase.metadata

# Если нужна защита от параллельных миграций — включите.
# Если миграции всегда запускаются последовательно — можно убрать.
ADVISORY_LOCK_KEY = 1001


def process_revision_directives(context, revision, directives):
    script = ScriptDirectory.from_config(context.config)
    head = script.get_current_head()

    if head is None:
        new_rev_id = "0001"
    else:
        last_num = int(head)
        new_rev_id = f"{last_num + 1:04d}"

    migration_script = directives[0]
    migration_script.rev_id = new_rev_id


def include_object(obj, name, type_, reflected, compare_to):
    if type_ == "table" and obj.schema != "shared":
        return False
    return True


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_object=include_object,
        version_table="alembic_version_shared",
        version_table_schema="shared",
        compare_type=True,
        compare_server_default=True,
        process_revision_directives=process_revision_directives,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Выполняется внутри явной транзакции из run_async_migrations."""
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS shared"))

    # Неблокирующий lock: если занят — сразу ошибка, а не вечное ожидание.
    # Уберите, если миграции всегда последовательны.
    locked = connection.execute(
        text("SELECT pg_try_advisory_lock(:key)"), {"key": ADVISORY_LOCK_KEY}
    ).scalar()
    if not locked:
        raise RuntimeError(
            f"Не удалось захватить advisory lock {ADVISORY_LOCK_KEY}: "
            "другая миграция уже выполняется"
        )

    try:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_object=include_object,
            version_table="alembic_version_shared",
            version_table_schema="shared",
            compare_type=True,
            compare_server_default=True,
            process_revision_directives=process_revision_directives,
        )
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.execute(
            text("SELECT pg_advisory_unlock(:key)"), {"key": ADVISORY_LOCK_KEY}
        )


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=build_connect_args(),
    )
    async with connectable.connect() as connection:
        # Явная транзакция: COMMIT при успехе, ROLLBACK при ошибке.
        async with connection.begin():
            await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
# xshared

# 1. Откатить (если применена)
alembic downgrade base

# 2. Удалить старую миграцию
rm alembic/versions/*.py
rm -rf alembic/versions/__pycache__

# 3. Сбросить БД
python -c "
import asyncio
from sqlalchemy import text
from xshared.db import engine

async def main():
    async with engine.begin() as conn:
        await conn.execute(text('DROP SCHEMA IF EXISTS shared CASCADE'))
    await engine.dispose()

asyncio.run(main())
"

# 4. Создать новую пустую миграцию
alembic revision --autogenerate --rev-id "init shared"


# 5. Проверить, что Alembic видит актуальную схему
alembic -c alembic.ini check

# 6. Создать новую миграцию для триггеров
alembic -c alembic.ini revision --rev-id add_triggers

Флаг --rev-id опционален, но удобно: имя ревизии становится предсказуемым, и down_revision в следующей миграции легко указать.


# Проверка
## накатить всё с нуля
alembic -c alembic.ini downgrade base
alembic -c alembic.ini upgrade head

## проверить, что триггеры на месте
python - <<'PY'
import asyncio
from sqlalchemy import text
from xshared.db import engine

SQL = """
    SELECT t.tgname, c.relname
    FROM pg_trigger t
    JOIN pg_class c ON c.oid = t.tgrelid
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'shared' AND NOT t.tgisinternal
    ORDER BY t.tgname
"""


async def main() -> None:
    try:
        async with engine.connect() as conn:
            rows = (await conn.execute(text(SQL))).all()
        if not rows:
            print("❌ Триггеров в shared нет")
            return
        for tgname, relname in rows:
            print(f"✅ {tgname:<45} → {relname}")
    finally:
        await engine.dispose()


asyncio.run(main())
PY


# 7. Проверить, что Pydantic читает .env

python -c "
from xshared.config import settings
print('DATABASE_URL:', settings.database_url)
print('DB_SSL_ENABLED:', settings.db_ssl_enabled)
print('DB_POOL_SIZE:', settings.db_pool_size)
"

Подключение работает

python -c "
import asyncio
from sqlalchemy import text
from xshared.db import engine

async def main():
    async with engine.connect() as conn:
        print((await conn.execute(text('SELECT version()'))).scalar())
    await engine.dispose()

asyncio.run(main())
"

# Миграция seed_kpp
alembic revision --rev-id seed_data

# xshared
shared DB for other services


    # ============================================================
    # Триггер 1: один основной КПП у контрагента
    # ============================================================
    op.execute(sa.text("""
        CREATE OR REPLACE FUNCTION shared.fn_ca_kpp_mapping_single_basic()
        RETURNS TRIGGER LANGUAGE plpgsql AS $$
        BEGIN
            IF pg_trigger_depth() > 1 THEN RETURN NEW; END IF;
            IF NEW.is_basic IS NOT TRUE THEN RETURN NEW; END IF;

            UPDATE shared.ca_kpp_mappings
               SET is_basic = false
             WHERE counterparty_id = NEW.counterparty_id
               AND id <> COALESCE(NEW.id, -1)
               AND is_basic = true;

            RETURN NEW;
        END;
        $$;
    """))

    op.execute(sa.text("""
        CREATE TRIGGER trg_ca_kpp_mapping_single_basic
        BEFORE INSERT OR UPDATE OF is_basic, counterparty_id
        ON shared.ca_kpp_mappings
        FOR EACH ROW
        WHEN (NEW.is_basic IS TRUE)
        EXECUTE FUNCTION shared.fn_ca_kpp_mapping_single_basic();
    """))

    # ================================================
    # Триггер 2: авто-закрытие предыдущей должности
    # ================================================
    op.execute(sa.text("""
        CREATE OR REPLACE FUNCTION shared.fn_employee_assignment_close_previous()
        RETURNS TRIGGER LANGUAGE plpgsql AS $$
        BEGIN
            IF pg_trigger_depth() > 1 THEN RETURN NEW; END IF;
            IF NEW.valid_to IS NOT NULL THEN RETURN NEW; END IF;

            UPDATE shared.employee_assignments
               SET valid_to = NEW.valid_from
             WHERE employee_id = NEW.employee_id
               AND valid_to IS NULL
               AND id <> COALESCE(NEW.id, -1);

            RETURN NEW;
        END;
        $$;
    """))

    op.execute(sa.text("""
        CREATE TRIGGER trg_employee_assignment_close_previous
        BEFORE INSERT ON shared.employee_assignments
        FOR EACH ROW
        WHEN (NEW.valid_to IS NULL)
        EXECUTE FUNCTION shared.fn_employee_assignment_close_previous();
    """))


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(sa.text("DROP TRIGGER IF EXISTS trg_employee_assignment_close_previous ON shared.employee_assignments"))
    op.execute(sa.text("DROP FUNCTION IF EXISTS shared.fn_employee_assignment_close_previous()"))

    op.execute(sa.text("DROP TRIGGER IF EXISTS trg_ca_kpp_mapping_single_basic ON shared.ca_kpp_mappings"))
    op.execute(sa.text("DROP FUNCTION IF EXISTS shared.fn_ca_kpp_mapping_single_basic()"))



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
alembic revision --autogenerate -m "init shared"


# 5. Проверить, что Alembic видит актуальную схему
alembic -c alembic.ini check

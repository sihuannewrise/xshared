"""add triggers

Revision ID: add_triggers
Revises: 2e752d01e250
Create Date: 2026-10-27 20:09:03.104892+03:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_triggers'
down_revision: Union[str, Sequence[str], None] = '2e752d01e250'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================================
    # Триггер 1: один основной КПП у контрагента
    # ============================================================
    op.execute(sa.text("""
        CREATE OR REPLACE FUNCTION shared.fn_kpp_ca_mapping_single_basic()
        RETURNS TRIGGER LANGUAGE plpgsql AS $$
        BEGIN
            IF pg_trigger_depth() > 1 THEN RETURN NEW; END IF;
            IF NEW.is_basic IS NOT TRUE THEN RETURN NEW; END IF;

            UPDATE shared.kpp_ca_mappings
               SET is_basic = false
             WHERE counterparty_id = NEW.counterparty_id
               AND id <> COALESCE(NEW.id, -1)
               AND is_basic = true;

            RETURN NEW;
        END;
        $$;
    """))

    op.execute(sa.text("""
        CREATE TRIGGER trg_kpp_ca_mapping_single_basic
        BEFORE INSERT OR UPDATE OF is_basic, counterparty_id
        ON shared.kpp_ca_mappings
        FOR EACH ROW
        WHEN (NEW.is_basic IS TRUE)
        EXECUTE FUNCTION shared.fn_kpp_ca_mapping_single_basic();
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

    # ============================================================
    # Триггер 3: запрет циклов в departments.parent_id
    # ============================================================
    op.execute(sa.text("""
        CREATE OR REPLACE FUNCTION shared.fn_departments_prevent_cycle()
        RETURNS TRIGGER LANGUAGE plpgsql AS $$
        DECLARE
            current_parent_id INTEGER;
            visited_ids INTEGER[] := ARRAY[NEW.id];
        BEGIN
            -- Нет родителя — цикла быть не может
            IF NEW.parent_id IS NULL THEN
                RETURN NEW;
            END IF;

            current_parent_id := NEW.parent_id;

            -- Идём вверх по цепочке родителей
            WHILE current_parent_id IS NOT NULL LOOP
                IF current_parent_id = ANY(visited_ids) THEN
                    RAISE EXCEPTION
                        'Циклическая ссылка в departments: id=% не может иметь предком %',
                        NEW.id, current_parent_id
                        USING ERRCODE = '23514';  -- check_violation
                END IF;

                visited_ids := array_append(visited_ids, current_parent_id);

                SELECT parent_id INTO current_parent_id
                FROM shared.departments
                WHERE id = current_parent_id;

                -- Родитель не найден (битые данные) — выходим
                IF NOT FOUND THEN
                    current_parent_id := NULL;
                END IF;
            END LOOP;

            RETURN NEW;
        END;
        $$;
    """))

    op.execute(sa.text("""
        CREATE TRIGGER trg_departments_prevent_cycle
        BEFORE INSERT OR UPDATE OF parent_id
        ON shared.departments
        FOR EACH ROW
        EXECUTE FUNCTION shared.fn_departments_prevent_cycle();
    """))

def downgrade() -> None:
    """Downgrade schema."""
    op.execute(sa.text("DROP TRIGGER IF EXISTS trg_departments_prevent_cycle ON shared.departments"))
    op.execute(sa.text("DROP FUNCTION IF EXISTS shared.fn_departments_prevent_cycle()"))

    op.execute(sa.text("DROP TRIGGER IF EXISTS trg_employee_assignment_close_previous ON shared.employee_assignments"))
    op.execute(sa.text("DROP FUNCTION IF EXISTS shared.fn_employee_assignment_close_previous()"))

    op.execute(sa.text("DROP TRIGGER IF EXISTS trg_ca_kpp_mapping_single_basic ON shared.kpp_ca_mappings"))
    op.execute(sa.text("DROP FUNCTION IF EXISTS shared.fn_kpp_ca_mapping_single_basic()"))


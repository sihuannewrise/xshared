from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE OR REPLACE FUNCTION shared.fn_ca_kpp_mapping_single_basic()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF pg_trigger_depth() > 1 THEN
                RETURN NEW;
            END IF;
            IF NEW.is_basic IS NOT TRUE THEN
                RETURN NEW;
            END IF;
            UPDATE shared.ca_kpp_mappings
               SET is_basic = false
             WHERE counterparty_id = NEW.counterparty_id
               AND id <> COALESCE(NEW.id, -1)
               AND is_basic = true;
            RETURN NEW;
        END;
        $$;
    """)

    op.execute("""
        CREATE TRIGGER trg_ca_kpp_mapping_single_basic
        BEFORE INSERT OR UPDATE OF is_basic, counterparty_id
        ON shared.ca_kpp_mappings
        FOR EACH ROW
        WHEN (NEW.is_basic IS TRUE)
        EXECUTE FUNCTION shared.fn_ca_kpp_mapping_single_basic();
    """)


def downgrade() -> None:
    op.execute("""
        DROP TRIGGER IF EXISTS trg_ca_kpp_mapping_single_basic
        ON shared.ca_kpp_mappings;
    """)
    op.execute("""
        DROP FUNCTION IF EXISTS shared.fn_ca_kpp_mapping_single_basic();
    """)

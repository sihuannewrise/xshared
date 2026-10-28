import json
from pathlib import Path

from alembic import op
import sqlalchemy as sa


revision = 'seed_data'
down_revision = 'add_triggers'
branch_labels = None
depends_on = None

DATA_DIR = Path(__file__).parent.parent.parent / "src" / "xshared" / "seed" / "data"


def upgrade() -> None:
    # seed kpp
    kpp_list = json.loads((DATA_DIR / "kpp_list.json").read_text(encoding="utf-8"))

    conn = op.get_bind()
    conn.execute(
        sa.text("""
            INSERT INTO shared.kpps (name)
            SELECT unnest(CAST(:names AS text[]))
            ON CONFLICT (name) DO NOTHING
        """),
        {"names": kpp_list},
    )


def downgrade() -> None:
    # unseed kpp
    kpp_list = json.loads((DATA_DIR / "kpp_list.json").read_text(encoding="utf-8"))
    conn = op.get_bind()

    # 1. Удалить только те КПП, что добавила эта миграция
    conn.execute(
        sa.text("DELETE FROM shared.kpps WHERE name = ANY(CAST(:names AS text[]))"),
        {"names": kpp_list},
    )

    # 2. Сбросить счётчик ТОЛЬКО если таблица пуста
    #    (иначе следующий INSERT получит id, конфликтующий с существующими)
    count = conn.execute(sa.text("SELECT count(*) FROM shared.kpps")).scalar()
    if count == 0:
        conn.execute(sa.text("ALTER SEQUENCE shared.kpps_id_seq RESTART WITH 1"))

    # extra method^ simply flash table KPP
    # conn = op.get_bind()
    # conn.execute(sa.text("TRUNCATE TABLE shared.kpps RESTART IDENTITY"))
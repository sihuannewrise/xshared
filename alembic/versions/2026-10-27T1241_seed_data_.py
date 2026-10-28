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

    kpps_table = sa.table(
        "kpps",
        sa.column("name", sa.String(9)),
        schema="shared",
    )
    op.bulk_insert(
        kpps_table,
        [{"name": k} for k in sorted(kpp_list)],
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM shared.kpps"))
    # kpp_list = json.loads((DATA_DIR / "kpp_list.json").read_text(encoding="utf-8"))
    # op.execute(
    #     sa.text("DELETE FROM shared.kpps WHERE name = ANY(:names)"),
    #     {"names": kpp_list},
    # )
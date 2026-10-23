from alembic import op

revision: str = '0000'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS shared")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS shared CASCADE")

"""added dashboard details

Revision ID: 9e73ead711bd
Revises: 8437c66cbf1c
Create Date: 2026-08-04 17:22:05.128536

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '9e73ead711bd'
down_revision: Union[str, Sequence[str], None] = '8437c66cbf1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
CREATE OR REPLACE VIEW dashboard_details AS
SELECT
    1 AS id,
    COUNT(*) FILTER (WHERE status = 1) AS pending,
    COUNT(*) FILTER (WHERE status = 4) AS in_progress,
    COUNT(*) FILTER (WHERE status = 6) AS delivered
FROM orders;
""")


def downgrade() -> None:
    op.execute("drop view if exists dashboard_details;")

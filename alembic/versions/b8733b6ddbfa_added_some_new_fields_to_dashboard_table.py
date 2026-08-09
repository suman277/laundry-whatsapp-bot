"""added some new fields to dashboard table

Revision ID: b8733b6ddbfa
Revises: bc646ac37618
Create Date: 2026-08-05 18:01:50.478215

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'b8733b6ddbfa'
down_revision: Union[str, Sequence[str], None] = 'bc646ac37618'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("drop view if exists dashboard_details;")
    op.execute("""
CREATE OR REPLACE VIEW dashboard_details AS
SELECT
    1 AS id,
    COUNT(*) FILTER (WHERE status = 1) AS pending,
    COUNT(*) FILTER (WHERE status = 2) AS accepted,
    COUNT(*) FILTER (WHERE status = 3) AS in_progress,
    COUNT(*) FILTER (WHERE status = 4) AS delivered
FROM orders;
""")


def downgrade() -> None:
    op.execute("drop view if exists dashboard_details;")
    op.execute("""
CREATE OR REPLACE VIEW dashboard_details AS
SELECT
    1 AS id,
    COUNT(*) FILTER (WHERE status = 1) AS pending,
    COUNT(*) FILTER (WHERE status = 4) AS in_progress,
    COUNT(*) FILTER (WHERE status = 6) AS delivered
FROM orders;
""")

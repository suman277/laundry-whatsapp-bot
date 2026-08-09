"""added order views

Revision ID: 90e893507b94
Revises: 38183eb0f693
Create Date: 2026-07-31 10:04:14.265598

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '90e893507b94'
down_revision: Union[str, Sequence[str], None] = '38183eb0f693'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
            create or replace view order_view as 
            select 
            o.id,
            o.pickup_address,
            o.user_id, 
            o.longitude, 
            o.latitude, 
            o.pickup_date, 
            o.pickup_time, 
            o.created_at, 
            case 
                when o.status = 1 then 'Pending' 
                when o.status = 2 then 'Confirmed' 
                when o.status = 3 then 'Picked Up' 
                when o.status = 4 then 'Processing'
                when o.status = 5 then 'Out For Delivery'
                when o.status = 6 then 'Delivered'
                when o.status = 7 then 'Cancelled'
            end
            as status,
            u.name,
            u.phone_number
            from orders as o join users as u
            on o.user_id = u.id;
            """)


def downgrade() -> None:
    op.execute("drop view if exists order_view")
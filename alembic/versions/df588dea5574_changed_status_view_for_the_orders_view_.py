"""changed status view for the orders_view table

Revision ID: df588dea5574
Revises: b8733b6ddbfa
Create Date: 2026-08-05 18:05:23.907197

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'df588dea5574'
down_revision: Union[str, Sequence[str], None] = 'b8733b6ddbfa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("drop view if exists order_view")
    op.execute("""
            create or replace view order_view as 
            select 
            o.id,
            o.pickup_address,
            o.user_id, 
            o.longitude, 
            o.latitude, 
            o.landmark,
            o.pickup_date, 
            o.pickup_time, 
            o.created_at, 
            case 
                when o.status = 1 then 'Pending' 
                when o.status = 2 then 'Confirmed' 
                when o.status = 3 then 'Processing' 
                when o.status = 4 then 'Delivered'
            end
            as status,
            u.name,
            u.phone_number
            from orders as o join users as u
            on o.user_id = u.id;
            """)


def downgrade() -> None:
    op.execute("drop view if exists order_view")
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

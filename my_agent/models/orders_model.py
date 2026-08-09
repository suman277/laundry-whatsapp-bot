from datetime import datetime, date, time
from sqlmodel import SQLModel, Field
from typing import Optional


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: Optional[int] = Field(primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    pickup_address: Optional[str] = None
    landmark: Optional[str] = None
    latitude: float
    longitude: float
    pickup_date: Optional[date] = None
    pickup_time: Optional[time] = None
    status: int
    notes: str | None = None
    total_price: float = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id: Optional[int] = Field(primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    item_name: str
    service_name: str
    quantity: int
    unit_price: float
    total_price: float
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OrderView(SQLModel, table=True):
    __tablename__ = "order_view"

    id: Optional[int] = Field(primary_key=True)
    user_id: int
    latitude: float
    landmark: str
    longitude: float
    pickup_date: date
    pickup_time: time
    pickup_address: str
    status: int
    name: str
    phone_number: str = Field(index=True, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DashboardView(SQLModel, table=True):
    __tablename__ = "dashboard_details"

    id: Optional[int] = Field(primary_key=True)
    pending: Optional[int] = None
    accepted: Optional[int] = None
    in_progress: Optional[int] = None
    delivered: Optional[int] = None

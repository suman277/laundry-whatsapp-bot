from sqlmodel import SQLModel
from datetime import datetime, date, time
from typing import List, Optional


class OrderSchema(SQLModel, table=False):
    name: str
    phone_number: str
    pickup_address: Optional[str] = None
    longitude: float
    latitude: float
    pickup_time: Optional[time] = None
    pickup_date: Optional[date] = None


class OrderDetailSchema(OrderSchema):
    id: int
    status: str
    landmark: Optional[str] = None


class OrderDetailListSchema(SQLModel, table=False):
    data: List[OrderDetailSchema] = None
    has_next: Optional[bool] = None
    has_previous: Optional[bool] = None
    next_cursor: Optional[int] = None
    previous_cursor: Optional[int] = None


class OrderItemDetailSchema(SQLModel, table=False):
    item_name: str
    service_name: str
    quantity: int
    unit_price: float


class OrderItemDetailsRequestSchema(OrderItemDetailSchema):
    id: int
    order_id: int
    total_price: float


class OrderItemDetailsRequestModel(SQLModel, table=False):
    item_details: List[OrderItemDetailsRequestSchema] = None


class OrderItemDetailsPayloadSchema(SQLModel, table=False):
    order_details: List[OrderItemDetailSchema] = None


class OrderSchemaRequestSchema(SQLModel, table=False):
    name: str
    phone_number: str
    pickup_address: Optional[str] = None
    longitude: float
    latitude: float
    pickup_time: Optional[time] = None
    pickup_date: Optional[date] = None
    landmark: Optional[str] = None
    notes: Optional[str] = None


class OrderRequestSchema(SQLModel, table=False):
    phone_number: str
    name: str
    status: str


class DashBoardRequestSchema(SQLModel, table=False):
    pending: Optional[int] = None
    accepted: Optional[int] = None
    in_progress: Optional[int] = None
    delivered: Optional[int] = None


class OrderUpdatePayloadSchema(SQLModel, table=False):
    status: int

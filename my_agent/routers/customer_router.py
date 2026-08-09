from fastapi import APIRouter, Depends, Response
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.common_schema import (OrderDetailListSchema, OrderItemDetailsPayloadSchema, OrderItemDetailSchema,
                                     OrderItemDetailsRequestModel, OrderSchemaRequestSchema, OrderRequestSchema, DashBoardRequestSchema, OrderUpdatePayloadSchema)
from ..database.db import get_session
from ..models.user_model import User
from ..models.orders_model import Order, OrderItem
from ..repositories.common_repository import UserRepository, OrderRepository, OrderViewRepository, OrderItemRepository, DashboardViewRepository
from ..repositories.generic_repository import OrderByEnum
from ..enums.common_enums import StatusEnum
from utils.common_utils import verify_geo_location
from fastapi import HTTPException
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT
order_rotuer = APIRouter(prefix="/order", tags=["Order APIs"])


@order_rotuer.post("/")
async def create_order(
    payload: OrderSchemaRequestSchema,
    session: AsyncSession = Depends(get_session)
):
    # if not verify_geo_location(payload.longitude, payload.latitude):
    #     raise HTTPException(
    #         status_code=HTTP_400_BAD_REQUEST,
    #         detail="Oops! Your area is not serviceable.",
    #     )

    user = await UserRepository.get_by_columns(
        session,
        {"phone_number": payload.phone_number},
    )

    if user is None:
        user = User(
            name=payload.name,
            phone_number=payload.phone_number,
        )

        user = await UserRepository.create(session, user)

    order = Order(
        user_id=user.id,
        pickup_address=payload.pickup_address,
        landmark=payload.landmark,
        latitude=payload.latitude,
        pickup_date=payload.pickup_date,
        pickup_time=payload.pickup_time,
        longitude=payload.longitude,
        status=StatusEnum.PENDING,
        notes=payload.notes
    )

    created_order = await OrderRepository.create(session, order)

    return created_order



@order_rotuer.get("/dashboard", response_model=DashBoardRequestSchema)
async def get_dashboard_details(
    session: AsyncSession = Depends(get_session)
):
    dashboard_details = await DashboardViewRepository.get_all(session)
    return dashboard_details[0] if dashboard_details else None


@order_rotuer.get("/", response_model=OrderDetailListSchema)
async def get_orders(
    search: Optional[str] = None,
    cursor: Optional[int] = None,
    limit: Optional[int] = 10,
    offset: Optional[int] = None,
    is_reverse: Optional[bool] = None,
    status: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    query_obj = {}
    order_by = {
        "id": OrderByEnum.ASCENDING.value
    }
    if search:
        query_obj["LIKE"] = {
            "landmark": search,
            "name": search,
            "phone_number": search
        }
    if status:
        query_obj["status"] = status
    details = await OrderViewRepository.get_all(session, filters=query_obj, cursor=cursor, order_by=order_by,
                                                limit=(limit+1), offset=offset, is_reverse=is_reverse)
    has_more = len(details) > limit
    print([item.id for item in details])

    if has_more:
        details = details[:-1]
    if is_reverse:
        details.reverse()

    next_cursor = None
    previous_cursor = None
    if details:
        next_cursor = details[-1].id
        previous_cursor = details[0].id

    if is_reverse:
        has_previous = has_more
        has_next = cursor is not None
    else:
        has_next = has_more
        has_previous = cursor is not None

    return OrderDetailListSchema(
        data=details,
        has_next=has_next,
        has_previous=has_previous,
        next_cursor=next_cursor,
        previous_cursor=previous_cursor,
    )

@order_rotuer.get("/{phone_number}")
async def get_customer_by_contact(
    phone_number : str,
    session : AsyncSession = Depends(get_session)
):
    if not phone_number:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid contact number")
    user_details = await UserRepository.get_by_columns(session, {"phone_number": phone_number})
    if not user_details:
        HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User doesn't exists")
    return {
        "name" : user_details.name}


@order_rotuer.get("/{order_id}", response_model=OrderRequestSchema)
async def get_order_by_id(
    order_id: int,
    session: AsyncSession = Depends(get_session)
):
    order_detail = await OrderViewRepository.get_by_id(session, order_id)
    return order_detail


@order_rotuer.post("/items/{order_id}")
async def create_order_items(
    order_id: int,
    payload: OrderItemDetailsPayloadSchema,
    session: AsyncSession = Depends(get_session),
):
    instances = []
    if not order_id:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Order Id is not provided")
    print(payload)

    order_detail = await OrderRepository.get_by_id(session, id=order_id)

    if not order_detail:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Invalid order")
    await OrderItemRepository.delete_all(session, order_detail.id)
    print(payload.order_details)
    for order_item in payload.order_details:
        if order_item.item_name is None or order_item.service_name is None:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                                detail="Invalid Item Details")
        order_details_instance = OrderItem(
            order_id=order_id,
            item_name=order_item.item_name,
            service_name=order_item.service_name,
            quantity=order_item.quantity,
            unit_price=order_item.unit_price,
            total_price=((order_item.quantity)*(order_item.unit_price))
        )
        instances.append(order_details_instance)

    order_item_details = await OrderItemRepository.create_all(session, instances)
    return order_item_details


@order_rotuer.put("/items/{order_id}")
async def edit_order_item(
    order_id: int,
    payload: OrderItemDetailSchema,
    session: AsyncSession = Depends(get_session)
):
    if order_id is None:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Invalid Order")

    order_detail = await OrderItemRepository.get_by_id(session, id=order_id)
    if not order_detail:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Invalid order")
    if order_detail:
        order_detail.item_name = payload.item_name
        order_detail.service_name = payload.service_name
        order_detail.quantity = payload.quantity
        order_detail.unit_price = payload.unit_price
        order_detail.total_price = ((payload.quantity)*(payload.quantity))

    await OrderItemRepository.update(session, order_id, order_detail)

    return order_detail


@order_rotuer.get("/item-details/{order_id}", response_model=OrderItemDetailsRequestModel)
async def get_order_items_by_order_id(
    order_id: int,
    session: AsyncSession = Depends(get_session)
):
    if order_id is None:
        print("No valid Order Id")
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Invalid Order Details")
    order_detail = await OrderRepository.get_by_id(session, id=order_id)
    if not order_detail:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Invalid order")
    order_item_details = await OrderItemRepository.get_all(session, {"order_id": order_id})
    return OrderItemDetailsRequestModel(
        item_details=order_item_details
    )


@order_rotuer.put("/{order_id}")
async def update_order(
    order_id: int,
    payload: OrderUpdatePayloadSchema,
    session: AsyncSession = Depends(get_session)
):
    if order_id is None:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Invalid Order")
    order_existance = await OrderRepository.get_by_id(session, order_id)
    print(order_existance)
    if not order_existance:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Order doesn't exists")
    order_existance.status = payload.status
    return await OrderRepository.update(session, order_id, order_existance)


@order_rotuer.delete("/{order_id}")
async def delete_order(
    order_id: int,
    session: AsyncSession = Depends(get_session)
):
    if not order_id:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Invalid Order")

    order_exists = await OrderRepository.get_by_id(session, order_id)
    if not order_exists:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Invalid Order")
    await OrderItemRepository.delete_all(session, order_exists.id)
    await OrderRepository.delete(session, order_id)
    return Response(status_code=HTTP_204_NO_CONTENT)

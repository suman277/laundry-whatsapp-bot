from typing import TypeVar, Generic, List, Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel
from sqlalchemy import select, or_, and_, asc, desc, nullslast
from starlette.status import HTTP_404_NOT_FOUND
from fastapi import HTTPException
from enum import Enum


class OrderByEnum(int, Enum):
    ASCENDING = 1
    DESCENDING = 2


T = TypeVar("T", bound=SQLModel)


class GenericRepository:
    def __init__(self, model):
        self.model = model

    async def get_by_id(self, session: AsyncSession, id: int):
        statement = select(self.model).where(getattr(self.model, "id") == id)
        response = await session.execute(statement)
        return response.scalar_one_or_none()

    async def create(self, session: AsyncSession, instance: T):
        if instance is not None:
            session.add(instance)
            await session.commit()
        return instance

    async def _filters(self, filters: dict, statement):
        or_clauses = []
        and_clauses = []
        like_clauses = []
        mul_clauses = None

        for key, value in filters.items():
            if key == "OR":
                for filter_key, filter_value in value.items():
                    if hasattr(self.model, filter_key):

                        if isinstance(filter_value, (list, tuple, set)):
                            or_conditions = [
                                getattr(self.model, filter_key).is_(None)
                                if v is None
                                else getattr(self.model, filter_key) == v
                                for v in filter_value
                            ]
                            or_clauses.append(or_(*or_conditions))

                        else:
                            or_clauses.append(
                                getattr(self.model, filter_key) == filter_value
                            )

            elif key == "RANGE":
                for range_key, range_ops in value.items():
                    if hasattr(self.model, range_key):

                        for op_key, op_value in range_ops.items():

                            if op_key == "GREATER_THAN":
                                and_clauses.append(
                                    getattr(self.model, range_key) > op_value
                                )

                            elif op_key == "LESS_THAN":
                                and_clauses.append(
                                    getattr(self.model, range_key) < op_value
                                )
                            elif op_key == "GREATER_THAN_EQUAL_TO":
                                and_clauses.append(
                                    getattr(self.model, range_key) >= op_value
                                )

            elif key == "LIKE":
                for like_key, like_value in value.items():
                    if hasattr(self.model, like_key):
                        column = getattr(self.model, like_key)
                        if isinstance(like_value, (list, tuple, set)):
                            l_clauses = [
                                column.ilike(f"%{v}%")
                                for v in like_value
                            ]
                            like_clauses.append(or_(*l_clauses))
                        else:
                            like_clauses.append(
                                column.ilike(f"%{like_value}%")
                            )
            elif key == "MULTIPLE_VALUES":
                for mul_key, mul_values in value.items():
                    if mul_key is not None:
                        column = getattr(self.model, mul_key)
                        mul_clauses = column.in_(mul_values)
                        break

            else:
                statement = statement.where(getattr(self.model, key) == value)

        if or_clauses:
            statement = statement.where(or_(*or_clauses))

        if and_clauses:
            statement = statement.where(and_(*and_clauses))

        if like_clauses:
            statement = statement.where(or_(*like_clauses))
        if mul_clauses is not None:
            statement = statement.where(mul_clauses)

        return statement

    async def get_by_columns(self, session: AsyncSession, filters: Dict[str, any] = None, order_by: Dict[str, any] = None, for_update: bool = False):
        statement = select(self.model)
        if filters:
            # fallback code
            # for key, value in filters.items():
            #     if key and value is not None:
            #         column = getattr(self.model, key)
            #         stmt = stmt.where(column == value)
            statement = await self._filters(filters, statement)

        if order_by is not None:
            for column, direction in order_by.items():
                if direction == OrderByEnum.ASCENDING:
                    statement = statement.order_by(
                        nullslast(asc(getattr(self.model, column)))
                    )
                elif direction == OrderByEnum.DESCENDING:
                    statement = statement.order_by(
                        nullslast(desc(getattr(self.model, column)))
                    )

        if for_update:
            statement = statement.with_for_update()
        result = await session.execute(statement)
        return result.scalars().first()

    async def delete(self, session: AsyncSession, id: int):
        result = await self.get_by_id(session, id)
        if not result:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                                detail="Details Not Found")
        await session.delete(result)
        await session.commit()

    async def update(self, session, id: int, instance: Optional[T]):
        result = await self.get_by_id(session, id)
        print(result)
        if not result:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                                detail="Details Not Found")
        response = instance.model_dump()
        for key, value in response.items():
            if hasattr(result, key) and value is not None:
                setattr(result, key,  value)

        session.add(result)
        await session.commit()
        await session.refresh(result)
        return response

    async def create_all(self, session: AsyncSession, instances: List[T]):
        if instances:
            session.add_all(instances)
        await session.commit()
        for instance in instances:
            await session.refresh(instance)
        return instances

    async def delete_all(self, session: AsyncSession, id: int):
        results = await self.get_all(session, filters={"order_id": id})
        print(results)
        print("Deleting results")
        for result in results:
            await session.delete(result)
        await session.commit()

    async def get_all(self, session: AsyncSession, filters: Dict[str, any] = None, order_by: int = None, cursor: int = None, limit: int = None, offset: int = None, is_reverse: bool = None) -> List[T]:
        statement = select(self.model)
        if filters:
            statement = await self._filters(filters, statement)

        if cursor is not None:
            if is_reverse:
                statement = (
                    statement
                    .where(self.model.id < cursor)
                )
            else:
                statement = (
                    statement
                    .where(self.model.id > cursor)
                )

        if order_by is not None:
            for column, direction in order_by.items():

                if is_reverse:
                    if direction == OrderByEnum.ASCENDING:
                        statement = statement.order_by(
                            nullslast(desc(getattr(self.model, column)))
                        )
                    elif direction == OrderByEnum.DESCENDING:
                        statement = statement.order_by(
                            nullslast(asc(getattr(self.model, column)))
                        )

                else:
                    if direction == OrderByEnum.ASCENDING:
                        statement = statement.order_by(
                            nullslast(asc(getattr(self.model, column)))
                        )
                    elif direction == OrderByEnum.DESCENDING:
                        statement = statement.order_by(
                            nullslast(desc(getattr(self.model, column)))
                        )

        if limit is not None:
            statement = statement.limit(limit)
        if offset:
            statement = statement.offset(offset)
        results = await session.execute(statement)
        return results.scalars().all()

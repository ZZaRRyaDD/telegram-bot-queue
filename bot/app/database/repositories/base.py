from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select

from app.database.connection import get_session


class BaseRepository:
    async def get(self, obj_id: Any):
        query = select(self.model).filter(self.model.id == obj_id)
        async with get_session() as session:
            result = await session.execute(query)
            return result.scalar()

    async def create(self, *, obj_in: dict[Any]):
        if isinstance(obj_in, dict):
            obj_in_data = obj_in
        else:
            obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        async with get_session() as session:
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

    async def update(self, *, db_obj, obj_in: dict[Any]):
        for field in obj_in:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_in[field])
        async with get_session() as session:
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

    async def remove(self, *, obj_id: int):
        obj = await self.get(obj_id=obj_id)
        async with get_session() as session:
            await session.delete(obj)
            await session.commit()

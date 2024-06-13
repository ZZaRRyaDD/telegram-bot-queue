from sqlalchemy import select

from app.database.connection import get_session


class BaseRepository:
    """Base class for repository."""

    @classmethod
    async def get(cls, obj_id):
        query = select(cls.model).filter(cls.model.id == obj_id)
        async with get_session() as session:
            result = await session.execute(query)
            return result.scalar()

    @classmethod
    async def create(cls, *, obj_in: dict):
        db_obj = cls.model(**obj_in)
        async with get_session() as session:
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

    @classmethod
    async def update(cls, *, db_obj, obj_in: dict):
        for field in obj_in:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_in[field])
        async with get_session() as session:
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

    @classmethod
    async def remove(cls, *, obj_id: int):
        obj = await cls.get(obj_id=obj_id)
        async with get_session() as session:
            await session.delete(obj)
            await session.commit()

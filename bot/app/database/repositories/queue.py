from sqlalchemy import delete, select, sql, update

from app.database.connection import get_session
from app.database.models import Queue

from .base import BaseRepository


class QueueRepository(BaseRepository):
    model = Queue

    @classmethod
    async def get_queue_info(cls, user_id: int) -> list[Queue]:
        """Get position, where user stay."""
        query = select(cls.model).where(cls.model.user_id == user_id)
        async with get_session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def update_queue_info(cls, params: dict) -> None:
        query = update(cls.model).where(
            cls.model.subject_id == params["subject_id"],
            cls.model.user_id == params["user_id"],
            cls.model.number_practice == params["number_practice"],
        ).values(number_in_list=params["number_in_list"])
        async with get_session() as session:
            await session.execute(query)
            await session.commit()

    @classmethod
    async def cleaning_user(cls, user_id: int) -> None:
        """Cleaning user queue."""
        query = delete(cls.model).where(cls.model.user_id == user_id)
        async with get_session() as session:
            await session.execute(query)
            await session.commit()

    @classmethod
    async def cleaning_subject(cls) -> None:
        query = delete(cls.model).where(cls.model.number_in_list.is_not(None))
        async with get_session() as session:
            await session.execute(query)
            await session.commit()

    @classmethod
    async def get_users_by_number(cls, params: dict) -> list:
        """Check exists queue with current params."""
        query = select(cls.model).where(
            sql.and_(
                cls.model.subject_id == params["subject_id"],
                cls.model.number_practice == params["number_practice"],
            ),
        ).order_by(cls.model.id)
        async with get_session() as session:
            result = await session.execute(query)
            queues = result.scalars().all()
            return [queue.user_id for queue in queues]

    @classmethod
    async def exists_queue(cls, params: dict) -> bool:
        """Check exists queue with current params."""
        query = select(cls.model).where(
            sql.and_(
                cls.model.user_id == params["user_id"],
                cls.model.subject_id == params["subject_id"],
                cls.model.number_practice == params["number_practice"],
            ),
        )
        async with get_session() as session:
            result = await session.execute(query)
            return result.scalar()

    @classmethod
    async def remove_queue(cls, params: dict) -> None:
        """Remove user from queue."""
        query = delete(Queue).where(
            sql.and_(
                Queue.user_id == params["user_id"],
                Queue.subject_id == params["subject_id"],
                Queue.number_practice == params["number_practice"],
            ),
        )
        async with get_session() as session:
            await session.execute(query)
            await session.commit()

    @classmethod
    async def action_user(cls, params: dict) -> bool:
        """Append/remove user to subject."""
        item = await QueueRepository.exists_queue(params)
        if item is None:
            await QueueRepository.create(obj_in=params)
            return True
        if item and item.number_in_list is None:
            await QueueRepository.remove_queue(params)
            return False
        return None

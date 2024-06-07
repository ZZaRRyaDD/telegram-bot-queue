from sqlalchemy import delete, insert, select, sql, update

from app.database.connection import connect
from app.database.models import Queue


class QueueActions:
    """Class for actions with queue."""

    @staticmethod
    async def get_queue_info(user_id: int) -> list[Queue]:
        """Get position, where user stay."""
        query = select(Queue).where(Queue.user_id == user_id)
        async with anext(connect.get_session()) as session:
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def update_queue_info(params: dict) -> None:
        query = update(Queue).where(
            Queue.subject_id == params["subject_id"],
            Queue.user_id == params["user_id"],
            Queue.number_practice == params["number_practice"],
        ).values(number_in_list=params["number_in_list"])
        async with anext(connect.get_session()) as session:
            await session.execute(query)

    @staticmethod
    async def cleaning_user(user_id: int) -> None:
        """Cleaning user queue."""
        query = delete(Queue).where(Queue.user_id == user_id)
        async with anext(connect.get_session()) as session:
            await session.execute(query)

    @staticmethod
    async def cleaning_subject() -> None:
        """Cleaning subject queue."""
        query = delete(Queue).where(Queue.number_in_list.is_not(None))
        async with anext(connect.get_session()) as session:
            await session.execute(query)

    @staticmethod
    async def get_users_by_number(params: dict) -> list:
        """Check exists queue with current params."""
        query = select(Queue).where(
            sql.and_(
                Queue.subject_id == params["subject_id"],
                Queue.number_practice == params["number_practice"],
            ),
        ).order_by(Queue.id)
        async with anext(connect.get_session()) as session:
            result = await session.execute(query)
            queues = result.scalars().all()
            return [queue.user_id for queue in queues]

    @staticmethod
    async def exists_queue(params: dict) -> bool:
        """Check exists queue with current params."""
        query = select(Queue).where(
            sql.and_(
                Queue.user_id == params["user_id"],
                Queue.subject_id == params["subject_id"],
                Queue.number_practice == params["number_practice"],
            ),
        )
        async with anext(connect.get_session()) as session:
            result = await session.execute(query)
            return result.scalar()

    @staticmethod
    async def append_queue(params: dict) -> None:
        """Append user in queue."""
        query = insert(Queue).values(**params)
        async with anext(connect.get_session()) as session:
            await session.execute(query)

    @staticmethod
    async def remove_queue(params: dict) -> None:
        """Remove user from queue."""
        query = delete(Queue).where(
            sql.and_(
                Queue.user_id == params["user_id"],
                Queue.subject_id == params["subject_id"],
                Queue.number_practice == params["number_practice"],
            ),
        )
        async with anext(connect.get_session()) as session:
            await session.execute(query)

    @staticmethod
    async def action_user(params: dict) -> bool:
        """Append/remove user to subject."""
        item = await QueueActions.exists_queue(params)
        if item is None:
            await QueueActions.append_queue(params)
            return True
        if item and item.number_in_list is None:
            await QueueActions.remove_queue(params)
            return False
        return None

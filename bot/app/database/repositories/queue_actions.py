from sqlalchemy import delete, insert, select, sql, update

from .. import connect
from ..models import Queue


class QueueActions:
    """Class for actions with queue."""

    @staticmethod
    async def get_queue_info(user_id: int) -> list[Queue]:
        """Get position, where user stay."""
        async with anext(connect.get_session()) as session:
            positions = await session.execute(
                select(Queue).where(
                    Queue.user_id == user_id,
                ),
            ).all()
            return (
                [position[0] for position in positions]
                if positions
                else []
            )

    @staticmethod
    async def update_queue_info(params: dict) -> None:
        async with anext(connect.get_session()) as session:
            await session.execute(
                update(Queue).where(
                    Queue.subject_id == params["subject_id"],
                    Queue.user_id == params["user_id"],
                    Queue.number_practice == params["number_practice"],
                ).values(number_in_list=params["number_in_list"]),
            )

    @staticmethod
    async def cleaning_user(user_id: int) -> None:
        """Cleaning user queue."""
        async with anext(connect.get_session()) as session:
            await session.execute(
                delete(Queue).where(
                    Queue.user_id == user_id,
                ),
            )

    @staticmethod
    async def cleaning_subject() -> None:
        """Cleaning subject queue."""
        async with anext(connect.get_session()) as session:
            await session.execute(
                delete(Queue).where(
                    Queue.number_in_list.is_not(None),
                ),
            )

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
            queues = await session.execute(query).all()
            return [queue[0].user_id for queue in queues] if queues else []

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
            result = await session.execute(query).first()
            return result[0] if result else None

    @staticmethod
    async def append_queue(params: dict) -> None:
        """Append user in queue."""
        async with anext(connect.get_session()) as session:
            await session.execute(
                insert(Queue).values(**params),
            )

    @staticmethod
    async def remove_queue(params: dict) -> None:
        """Remove user from queue."""
        async with anext(connect.get_session()) as session:
            await session.execute(
                delete(Queue).where(
                    sql.and_(
                        Queue.user_id == params["user_id"],
                        Queue.subject_id == params["subject_id"],
                        Queue.number_practice == params["number_practice"],
                    ),
                ),
            )

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

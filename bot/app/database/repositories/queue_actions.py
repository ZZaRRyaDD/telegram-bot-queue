from sqlalchemy import delete, insert, select, sql, update

from .. import connect
from ..models import Queue


class QueueActions:
    """Class for actions with queue."""

    @staticmethod
    def get_queue_info(user_id: int) -> list[Queue]:
        """Get position, where user stay."""
        with connect.SessionLocal() as session:
            positions = session.execute(
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
    def update_queue_info(params: dict) -> None:
        with connect.SessionLocal.begin() as session:
            session.execute(
                update(Queue).where(
                    Queue.subject_id == params["subject_id"],
                    Queue.user_id == params["user_id"],
                    Queue.number_practice == params["number_practice"],
                ).values(number_in_list=params["number_in_list"]),
            )

    @staticmethod
    def cleaning_user(user_id: int) -> None:
        """Cleaning user queue."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                delete(Queue).where(
                    Queue.user_id == user_id,
                ),
            )

    @staticmethod
    def cleaning_subject() -> None:
        """Cleaning subject queue."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                delete(Queue).where(
                    Queue.number_in_list.is_not(None),
                ),
            )

    @staticmethod
    def get_users_by_number(params: dict) -> list:
        """Check exists queue with current params."""
        query = select(Queue).where(
            sql.and_(
                Queue.subject_id == params["subject_id"],
                Queue.number_practice == params["number_practice"],
            ),
        ).order_by(Queue.id)
        with connect.SessionLocal() as session:
            queues = session.execute(query).all()
            return [queue[0].user_id for queue in queues] if queues else []

    @staticmethod
    def exists_queue(params: dict) -> bool:
        """Check exists queue with current params."""
        query = select(Queue).where(
            sql.and_(
                Queue.user_id == params["user_id"],
                Queue.subject_id == params["subject_id"],
                Queue.number_practice == params["number_practice"],
            ),
        )
        with connect.SessionLocal() as session:
            result = session.execute(query).first()
            return result[0] if result else None

    @staticmethod
    def append_queue(params: dict) -> None:
        """Append user in queue."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                insert(Queue).values(**params),
            )

    @staticmethod
    def remove_queue(params: dict) -> None:
        """Remove user from queue."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                delete(Queue).where(
                    sql.and_(
                        Queue.user_id == params["user_id"],
                        Queue.subject_id == params["subject_id"],
                        Queue.number_practice == params["number_practice"],
                    ),
                ),
            )

    @staticmethod
    def action_user(params: dict) -> bool:
        """Append/remove user to subject."""
        item = QueueActions.exists_queue(params)
        if item is None:
            QueueActions.append_queue(params)
            return True
        if item and item.number_in_list is None:
            QueueActions.remove_queue(params)
            return False
        return None

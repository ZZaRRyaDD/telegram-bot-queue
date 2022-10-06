from typing import Optional

from sqlalchemy import delete, insert, select, sql

from .. import connect
from ..models import Queue


class QueueActions:
    """Class for actions with queue."""

    @staticmethod
    def get_queue_info(user_id: int) -> Optional[list[Queue]]:
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
                else None
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
    def cleaning_subject(subject_id: int) -> None:
        """Cleaning subject queue."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                delete(Queue).where(
                    Queue.subject_id == subject_id,
                ),
            )

    @staticmethod
    def get_users_by_number(params: dict) -> bool:
        """Check exists queue with current params."""
        query = select(Queue).where(
            sql.and_(
                Queue.subject_id == params["subject_id"],
                Queue.number == params["number"],
            ),
        )
        with connect.SessionLocal() as session:
            queues = session.execute(query).all()
            return [queue[0].user_id for queue in queues] if queues else None

    @staticmethod
    def exists_queue(params: dict) -> bool:
        """Check exists queue with current params."""
        query = select(Queue).where(
            sql.and_(
                Queue.user_id == params["user_id"],
                Queue.subject_id == params["subject_id"],
                Queue.number == params["number"],
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
                        Queue.number == params["number"],
                    ),
                ),
            )

    @staticmethod
    def action_user(params: dict) -> bool:
        """Append/remove user to subject."""
        if not QueueActions.exists_queue(params):
            QueueActions.append_queue(params)
            return True
        QueueActions.remove_queue(params)
        return False

from typing import Optional

from sqlalchemy import delete, insert, select, sql

from .. import connect
from ..models import CompletedPractices


class CompletedPracticesActions:
    """Class for actions with completed_practices."""

    @staticmethod
    def get_completed_practices_info(
        complete_practices_id: int,
    ) -> Optional[list[CompletedPractices]]:
        """Get completed labs, where user stay."""
        with connect.SessionLocal() as session:
            practices = session.execute(
                select(CompletedPractices).where(
                    CompletedPractices.user_id == complete_practices_id,
                ),
            ).all()
            return (
                [practice[0] for practice in practices]
                if practices
                else None
            )

    @staticmethod
    def cleaning_user(user_id: int) -> None:
        """Cleaning user completed practices."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                delete(CompletedPractices).where(
                    CompletedPractices.user_id == user_id,
                ),
            )

    @staticmethod
    def cleaning_subject(subject_id: int) -> None:
        """Cleaning subject completed practices."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                delete(CompletedPractices).where(
                    CompletedPractices.subject_id == subject_id,
                ),
            )

    @staticmethod
    def get_users_by_number(params: dict) -> bool:
        """Check exists completed practices with current params."""
        query = select(CompletedPractices).where(
            sql.and_(
                CompletedPractices.subject_id == params["subject_id"],
                CompletedPractices.number == params["number"],
            ),
        )
        with connect.SessionLocal() as session:
            queues = session.execute(query).all()
            return [queue[0].user_id for queue in queues] if queues else None

    @staticmethod
    def exists_completed_practices(params: dict) -> bool:
        """Check exists completed practices with current params."""
        query = select(CompletedPractices).where(
            sql.and_(
                CompletedPractices.user_id == params["user_id"],
                CompletedPractices.subject_id == params["subject_id"],
                CompletedPractices.number == params["number"],
            ),
        )
        with connect.SessionLocal() as session:
            result = session.execute(query).first()
            return result[0] if result else None

    @staticmethod
    def append_completed_practices(params: dict) -> None:
        """Append user in completed practices."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                insert(CompletedPractices).values(**params),
            )

    @staticmethod
    def remove_completed_practices(params: dict) -> None:
        """Remove user from completed practices."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                delete(CompletedPractices).where(
                    sql.and_(
                        CompletedPractices.user_id == params["user_id"],
                        CompletedPractices.subject_id == params["subject_id"],
                        CompletedPractices.number == params["number"],
                    ),
                ),
            )

    @staticmethod
    def action_user(params: dict) -> None:
        """Append/remove user to subject."""
        if not CompletedPracticesActions.exists_completed_practices(params):
            CompletedPracticesActions.append_completed_practices(params)
        else:
            CompletedPracticesActions.remove_completed_practices(params)

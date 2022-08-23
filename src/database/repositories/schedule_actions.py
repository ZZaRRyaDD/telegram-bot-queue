from typing import Optional

from sqlalchemy import delete, select

from .. import connect
from ..models import Schedule


class ScheduleActions:
    """Class with actions for schedule."""

    @staticmethod
    def get_schedule(
        number: Optional[int] = None,
        subject_id: Optional[int] = None,
        can_select: Optional[bool] = None,
    ) -> Optional[list[Schedule]]:
        """Get all schedule."""
        query = select(Schedule)
        if number is not None:
            query = query.where(Schedule.date_number == number)
        if subject_id is not None:
            query = query.where(Schedule.subject_id == subject_id)
        if can_select is not None:
            query = query.where(Schedule.can_select.is_(can_select))
        with connect.SessionLocal() as session:
            schedule = session.execute(query).all()
            return [date[0] for date in schedule] if schedule else None

    @staticmethod
    def create_schedule(schedule: dict) -> None:
        """Create schedule."""
        with connect.SessionLocal.begin() as session:
            session.add(Schedule(**schedule))
            session.commit()

    @staticmethod
    def delete_schedule_by_subject(id: int) -> None:
        """Delete schedule."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                delete(Schedule).where(
                    Schedule.subject_id == id,
                ),
            )

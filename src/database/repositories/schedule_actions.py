from typing import Optional

from sqlalchemy import delete, desc, select

from .. import connect
from ..models import Schedule


class ScheduleActions:
    """Class with actions for schedule."""

    @staticmethod
    def get_schedule(
        number: Optional[int] = None,
        subject_id: Optional[int] = None,
        can_select: Optional[bool] = None,
        reverse: Optional[bool] = None,
    ) -> Optional[list[Schedule]]:
        """Get all schedule."""
        query = select(Schedule)
        if number is not None:
            query = query.where(Schedule.date_number == number)
        if subject_id is not None:
            query = query.where(Schedule.subject_id == subject_id)
        if can_select is not None:
            query = query.where(Schedule.can_select.is_(can_select))
        if reverse is True:
            query = query.order_by(desc(Schedule.id))
        with connect.SessionLocal() as session:
            schedule = session.execute(query).all()
            return [date[0] for date in schedule] if schedule else None

    @staticmethod
    def create_schedule(schedule: dict) -> None:
        """Create schedule."""
        with connect.SessionLocal.begin() as session:
            session.add(Schedule(**schedule))
            session.commit()
        return ScheduleActions.get_schedule(reverse=True)[0]

    @staticmethod
    def delete_schedule_by_subject(subject_id: int) -> None:
        """Delete schedule."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                delete(Schedule).where(
                    Schedule.subject_id == subject_id,
                ),
            )

    @staticmethod
    def delete_schedule_by_id(id: int) -> None:
        """Delete schedule."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                delete(Schedule).where(
                    Schedule.id == id,
                ),
            )

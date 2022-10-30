from typing import Optional, Union

from sqlalchemy import delete, desc, select, update

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
        date_number: Optional[int] = None,
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
        if date_number is not None:
            query = query.where(Schedule.date_number == date_number)
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
    def delete_schedule_by_id(schedule_id: int) -> None:
        """Delete schedule."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                delete(Schedule).where(
                    Schedule.id == schedule_id,
                ),
            )

    @staticmethod
    def change_status_subjects(
        schedule_id: Union[bool, int, str],
        can_select: bool,
    ) -> None:
        """Change field 'can_select' of subject."""
        query = update(Schedule)
        query = (
            query.where(Schedule.can_select == schedule_id)
            if isinstance(schedule_id, bool)
            else query.where(Schedule.id == schedule_id)
            if isinstance(schedule_id, int) else query.where(
                Schedule.on_even_week.is_(
                    True
                    if schedule_id == "True"
                    else False
                )
            )
        )
        query = query.values(can_select=can_select)
        with connect.SessionLocal.begin() as session:
            session.execute(query)
            session.commit()

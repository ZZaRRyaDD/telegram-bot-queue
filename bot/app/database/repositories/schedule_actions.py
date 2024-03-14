from datetime import date
from typing import Optional

from sqlalchemy import delete, select, update

from .. import connect
from ..models import Schedule


class ScheduleActions:
    """Class with actions for schedule."""

    @staticmethod
    async def get_schedule(
        subject_id: Optional[int] = None,
        can_select: Optional[bool] = None,
        date_number: Optional[int] = None,
        date_protection: Optional[date] = None,
    ) -> list[Schedule]:
        """Get all schedule."""
        query = select(Schedule)
        if subject_id is not None:
            query = query.where(Schedule.subject_id == subject_id)
        if can_select is not None:
            query = query.where(Schedule.can_select.is_(can_select))
        if date_number is not None:
            query = query.where(Schedule.date_number == date_number)
        if date_protection is not None:
            query = query.where(Schedule.date_protection == date_protection)
        async with anext(connect.get_session()) as session:
            schedule = await session.execute(query).all()
            return [date[0] for date in schedule] if schedule else []

    @staticmethod
    async def create_schedule(schedule: dict) -> None:
        """Create schedule."""
        async with anext(connect.get_session()) as session:
            schedule = Schedule(**schedule)
            session.add(schedule)
            session.commit()
            session.refresh(schedule)
            return schedule

    @staticmethod
    async def delete_schedule_by_id(schedule_id: int) -> None:
        """Delete schedule."""
        async with anext(connect.get_session()) as session:
            await session.execute(
                delete(Schedule).where(
                    Schedule.id == schedule_id,
                ),
            )

    @staticmethod
    async def change_status_subjects(
        can_select: bool,
        schedule_id: int = None,
        can_select_to_change: bool = None,
        on_even_week: str = None,
    ) -> None:
        """Change field 'can_select' of subject."""
        query = update(Schedule)
        if schedule_id is not None:
            query = query.where(Schedule.id == schedule_id)
        elif can_select_to_change is not None:
            query = query.where(Schedule.can_select.is_(can_select_to_change))
        elif on_even_week is not None:
            query = query.where(
                Schedule.on_even_week.is_(
                    True
                    if on_even_week == "True"
                    else False if on_even_week == "False" else None
                )
            )
        query = query.values(can_select=can_select)
        async with anext(connect.get_session()) as session:
            await session.execute(query)
            session.commit()

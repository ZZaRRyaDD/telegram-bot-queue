from datetime import date
from typing import Optional

from sqlalchemy import delete, select, update

from app.database.connection import connect
from app.database.models import Schedule


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
        async with get_session()() as session:
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def create_schedule(schedule: dict) -> None:
        """Create schedule."""
        schedule = Schedule(**schedule)
        async with get_session()() as session:
            session.add(schedule)
            session.commit()
            session.refresh(schedule)
            return schedule

    @staticmethod
    async def delete_schedule_by_id(schedule_id: int) -> None:
        """Delete schedule."""
        query = delete(Schedule).where(Schedule.id == schedule_id)
        async with get_session()() as session:
            await session.execute(query)

    @staticmethod
    async def change_status_subjects(
        can_select: bool,
        schedule_id: Optional[int] = None,
        can_select_to_change: Optional[bool] = None,
        week: Optional[str] = None,
    ) -> None:
        """Change field 'can_select' of subject."""
        query = update(Schedule)
        if schedule_id is not None:
            query = query.where(Schedule.id == schedule_id)
        elif can_select_to_change is not None:
            query = query.where(Schedule.can_select.is_(can_select_to_change))
        elif week is not None:
            query = query.where(Schedule.week == week)
        query = query.values(can_select=can_select)
        async with get_session()() as session:
            await session.execute(query)
            session.commit()

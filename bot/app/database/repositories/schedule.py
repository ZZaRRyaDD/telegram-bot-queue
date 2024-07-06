from datetime import date
from typing import Optional

from sqlalchemy import select, update

from app.database.connection import get_session
from app.database.models import Schedule

from .base import BaseRepository


class ScheduleRepository(BaseRepository):
    model = Schedule

    @classmethod
    async def get_schedule(
        cls,
        subject_id: Optional[int] = None,
        can_select: Optional[bool] = None,
        date_number: Optional[int] = None,
        date_protection: Optional[date] = None,
    ) -> list[Schedule]:
        """Get all schedule."""
        query = select(Schedule)
        if subject_id is not None:
            query = query.where(cls.model.subject_id == subject_id)
        if can_select is not None:
            query = query.where(cls.model.can_select.is_(can_select))
        if date_number is not None:
            query = query.where(cls.model.date_number == date_number)
        if date_protection is not None:
            query = query.where(cls.model.date_protection == date_protection)
        async with get_session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def change_status_subjects(
        cls,
        can_select: bool,
        schedule_id: Optional[int] = None,
        can_select_to_change: Optional[bool] = None,
        week: Optional[str] = None,
    ) -> None:
        """Change field 'can_select' of subject."""
        query = update(cls.model)
        if schedule_id is not None:
            query = query.where(cls.model.id == schedule_id)
        elif can_select_to_change is not None:
            query = query.where(cls.model.can_select.is_(can_select_to_change))
        elif week is not None:
            query = query.where(cls.model.week == week)
        query = query.values(can_select=can_select)
        async with get_session() as session:
            await session.execute(query)
            await session.commit()

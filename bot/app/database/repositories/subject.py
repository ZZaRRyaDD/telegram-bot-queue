from typing import Optional

from sqlalchemy import orm, select

from app.database.connection import get_session
from app.database.models import Subject

from .base import BaseRepository


class SubjectRepository(BaseRepository):
    model = Subject

    @classmethod
    async def get_subject(
        cls,
        subject_id: Optional[int] = None,
        users_practice: bool = False,
    ) -> Optional[Subject]:
        """Get subject."""
        query = select(cls.model)
        if subject_id is not None:
            query = query.where(cls.model.id == subject_id)
        if users_practice:
            query = query.options(
                orm.subqueryload(cls.model.users_practice),
            )
        async with get_session() as session:
            result = await session.execute(query)
            return result.scalar()

    @staticmethod
    async def get_subjects(
        cls,
        users_practice: bool = False,
    ) -> list[Subject]:
        """Get all subjects."""
        query = select(cls.model)
        if users_practice:
            query = query.options(
                orm.subqueryload(cls.model.users_practice),
            )
        async with get_session() as session:
            result = await session.execute(query)
            return result.scalars().all()

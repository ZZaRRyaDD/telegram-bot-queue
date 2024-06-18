import os
from typing import Optional

from sqlalchemy import orm, select

from app.database.connection import get_session
from app.database.models import Subject, User

from .base import BaseRepository


class UserRepository(BaseRepository):
    model = User

    @classmethod
    async def get_user(
        cls,
        user_id: int,
        group: bool = False,
        subjects_practice: bool = False,
        subjects_completed: bool = False,
    ) -> Optional[User]:
        """Get user by id."""
        query = select(cls.model).filter(cls.model.id == user_id)
        if subjects_practice:
            query = query.options(
                orm.subqueryload(cls.model.subjects_practice).options(
                    orm.subqueryload(Subject.days),
                ),
            )
        if subjects_completed:
            query = query.options(
                orm.subqueryload(cls.model.subjects_completed),
            )
        if group:
            query = query.options(
                orm.joinedload(cls.model.group),
            )
        async with get_session() as session:
            result = await session.execute(query)
            return result.scalar()

    @classmethod
    async def get_users(
        cls,
        with_group: bool = False,
        without_admin: bool = False,
    ) -> list[User]:
        """Get users."""
        query = select(cls.model)
        if with_group:
            query = query.where(
                cls.model.group.is_not(None),
            )
        if without_admin:
            query = query.where(
                cls.model.id != int(os.getenv("ADMIN_ID")),
            )
        async with get_session() as session:
            result = await session.execute(query)
            return result.scalars().all()

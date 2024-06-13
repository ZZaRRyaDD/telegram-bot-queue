from typing import Optional

from sqlalchemy import orm, select

from app.database.connection import get_session
from app.database.models import Group, Subject, User

from .base import BaseRepository


class GroupActions(BaseRepository):
    model = Group

    @classmethod
    async def get_group(
        cls,
        group_id: Optional[int] = None,
        group_name: Optional[str] = None,
        subjects: bool = False,
        students: bool = False,
    ) -> Optional[Group]:
        """Get group."""
        query = select(cls.model)
        if group_id is not None:
            query = query.where(cls.model.id == group_id)
        if group_name is not None:
            query = query.where(cls.model.name == group_name)
        if subjects:
            query = query.options(
                orm.subqueryload(cls.model.subjects).options(
                    orm.subqueryload(Subject.days),
                ),
            )
        if students:
            query = query.options(
                orm.subqueryload(cls.model.students),
            )
        async with get_session() as session:
            result = await session.execute(query)
            return result.scalar()

    @classmethod
    async def get_group_by_user_id(
        cls,
        user_id: int,
        subjects: bool = False,
        students: bool = False,
    ) -> Optional[Group]:
        """Get group by user id."""
        query = select(User).where(User.id == user_id)
        group = orm.joinedload(User.group, innerjoin=True)
        if subjects:
            group = group.options(
                orm.subqueryload(cls.model.subjects).options(
                    orm.subqueryload(Subject.days),
                ),
            )
        if students:
            group = group.options(
                orm.subqueryload(cls.model.students),
            )
        query = query.options(group)
        async with get_session() as session:
            result = await session.execute(query)
            user = result.scalar()
            if user is None:
                return None
            return user.group

    @classmethod
    async def get_groups(
        cls,
        subjects: bool = False,
        students: bool = False,
    ) -> list[Group]:
        """Get all groups."""
        query = select(cls.model)
        if subjects:
            query = query.options(
                orm.subqueryload(cls.model.subjects).options(
                    orm.subqueryload(Subject.days),
                ),
            )
        if students:
            query = query.options(
                orm.subqueryload(cls.model.students),
            )
        async with get_session() as session:
            result = await session.execute(query)
            return result.scalars().all()

from typing import Optional

from sqlalchemy import delete, orm, select, update

from app.database.connection import get_session
from app.database.models import Group, Subject, User


class GroupActions:
    """Class with actions with group."""

    @staticmethod
    async def get_group(
        group_id: Optional[int] = None,
        group_name: Optional[str] = None,
        subjects: bool = False,
        students: bool = False,
    ) -> Optional[Group]:
        """Get group."""
        query = select(Group)
        if group_id is not None:
            query = query.where(Group.id == group_id)
        if group_name is not None:
            query = query.where(Group.name == group_name)
        if subjects:
            query = query.options(
                orm.subqueryload(Group.subjects).options(
                    orm.subqueryload(Subject.days),
                ),
            )
        if students:
            query = query.options(
                orm.subqueryload(Group.students),
            )
        async with get_session() as session:
            result = await session.execute(query)
            return result.scalar()

    @staticmethod
    async def get_group_by_user_id(
        user_id: int,
        subjects: bool = False,
        students: bool = False,
    ) -> Optional[Group]:
        """Get group by user id."""
        query = select(User).where(User.id == user_id)
        group = orm.joinedload(User.group, innerjoin=True)
        if subjects:
            group = group.options(
                orm.subqueryload(Group.subjects).options(
                    orm.subqueryload(Subject.days),
                ),
            )
        if students:
            group = group.options(
                orm.subqueryload(Group.students),
            )
        query = query.options(group)
        async with get_session() as session:
            result = await session.execute(query)
            user = result.scalar()
            if user is None:
                return None
            return user.group

    @staticmethod
    async def get_groups(
        subjects: bool = False,
        students: bool = False,
    ) -> list[Group]:
        """Get all groups."""
        query = select(Group)
        if subjects:
            query = query.options(
                orm.subqueryload(Group.subjects).options(
                    orm.subqueryload(Subject.days),
                ),
            )
        if students:
            query = query.options(
                orm.subqueryload(Group.students),
            )
        async with get_session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def create_group(group: dict) -> Group:
        """Create group."""
        group = Group(**group)
        async with get_session() as session:
            session.add(group)
            await session.commit()
            await session.refresh(group)
            return group

    @staticmethod
    async def edit_group(group_id: int, group: dict) -> None:
        """Edit group."""
        query = update(Group).where(Group.id == group_id).values(**group)
        async with get_session() as session:
            await session.execute(query)

    @staticmethod
    async def delete_group(group_id: int) -> None:
        """Delete group by id."""
        query = delete(Group).where(Group.id == group_id)
        async with get_session() as session:
            await session.execute(query)

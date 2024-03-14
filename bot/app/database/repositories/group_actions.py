from typing import Optional

from sqlalchemy import delete, orm, select, update

from .. import connect
from ..models import Group, Subject, User


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
        async with anext(connect.get_session()) as session:
            group = await session.execute(query).first()
            return group[0] if group else None

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
        async with anext(connect.get_session()) as session:
            user = await session.execute(query).first()
            if user is None:
                return None
            return user[0].group

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
        async with anext(connect.get_session()) as session:
            groups = await session.execute(query).all()
            return [group[0] for group in groups] if groups else []

    @staticmethod
    async def create_group(group: dict) -> Group:
        """Create group."""
        async with anext(connect.get_session()) as session:
            group = Group(**group)
            session.add(group)
            session.commit()
            session.refresh(group)
            return group

    @staticmethod
    async def edit_group(group_id: int, group: dict) -> None:
        """Edit group."""
        async with anext(connect.get_session()) as session:
            await session.execute(
                update(Group).where(
                    Group.id == group_id
                ).values(**group),
            )

    @staticmethod
    async def delete_group(group_id: int) -> None:
        """Delete group by id."""
        async with anext(connect.get_session()) as session:
            await session.execute(
                delete(Group).where(
                    Group.id == group_id,
                ),
            )

from typing import Optional, Union

from sqlalchemy import delete, desc, orm, select, update

from .. import connect
from ..models import Group, Subject, User


class GroupActions:
    """Class with actions with group."""

    @staticmethod
    def get_group(
        id: Optional[Union[int, str]] = None,
        subjects: bool = False,
        students: bool = False,
        last: bool = False,
    ) -> Optional[Group]:
        """Get group."""
        query = select(Group)
        if id is not None:
            field = (
                Group.id
                if isinstance(id, int)
                else Group.name
            )
            query = query.where(field == id)
        if subjects:
            query = query.options(
                orm.subqueryload(Group.subjects).options(
                    orm.subqueryload(Subject.days)
                )
            )
        if students:
            query = query.options(orm.subqueryload(Group.students))
        if last:
            query = query.order_by(desc(Group.id))
        with connect.SessionLocal() as session:
            group = session.execute(query).first()
            return group[0] if group else None

    @staticmethod
    def get_groups(
        subjects: bool = False,
        students: bool = False,
    ) -> Optional[list[Group]]:
        """Get all groups."""
        query = select(Group)
        if subjects:
            query = query.options(
                orm.subqueryload(Group.subjects).options(
                    orm.subqueryload(Subject.days)
                )
            )
        if students:
            query = query.options(orm.subqueryload(Group.students))
        with connect.SessionLocal() as session:
            groups = session.execute(query).all()
            return [group[0] for group in groups] if groups else None

    @staticmethod
    def create_group(group: dict) -> Group:
        """Create group."""
        with connect.SessionLocal.begin() as session:
            session.add(Group(**group))
            session.commit()
        return GroupActions.get_group(last=True)

    @staticmethod
    def edit_group(id: int, group: dict) -> None:
        """Edit group."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                update(Group).where(
                    Group.id == id
                ).values(**group)
            )

    @staticmethod
    def delete_group(id: int) -> None:
        """Delete group by id."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                update(User).where(
                    User.group == id,
                ).values({"group": None})
            )
            session.execute(
                delete(Group).where(
                    Group.id == id
                )
            )

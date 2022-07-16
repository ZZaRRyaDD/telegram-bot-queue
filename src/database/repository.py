from typing import Optional, Union

from sqlalchemy import delete, desc, insert, select, sql, update
from sqlalchemy.orm import subqueryload

from . import connect, models


class UserActions:
    """Class with actions with user."""

    @staticmethod
    def get_user(id: int, subjects=False) -> Optional[models.User]:
        """Get user by id."""
        query = select(models.User).filter(models.User.id == id)
        query = (
            query.options(subqueryload(models.User.subjects))
            if subjects
            else query
        )
        with connect.SessionLocal() as session:
            user = session.execute(
                query
            ).first()
            return user[0] if user else None

    @staticmethod
    def get_users_with_group() -> Optional[list[models.User]]:
        """Get all users with group."""
        with connect.SessionLocal() as session:
            users = session.execute(
                select(models.User).where(
                    models.User.group is not None,
                )
            ).all()
            return [user[0] for user in users] if users else None

    @staticmethod
    def create_user(user: dict) -> None:
        """Create user."""
        user = models.User(**user)
        with connect.SessionLocal() as session:
            session.add(user)
            session.commit()

    @staticmethod
    def edit_user(id: int, user: dict) -> None:
        """Edit user by id."""
        with connect.SessionLocal() as session:
            session.execute(
                update(models.User).where(
                    models.User.id == id
                ).values(user)
            )
            session.commit()

    @staticmethod
    def delete_user(id: int) -> None:
        """Delete user by id."""
        with connect.SessionLocal() as session:
            session.execute(
                delete(models.User).where(
                    models.User.id == id
                )
            )
            session.commit()


class GroupActions:
    """Class with actions with group."""

    @staticmethod
    def get_group(
        id: Optional[Union[int, str]] = None,
        subjects: bool = False,
        students: bool = False,
        last: bool = False,
    ) -> Optional[models.Group]:
        """Get group."""
        query = select(models.Group)
        if id is not None:
            field = (
                models.Group.id
                if isinstance(id, int)
                else models.Group.name
            )
            query = query.where(field == id)
        query = (
            query.options(
                subqueryload(models.Group.subjects).options(
                    subqueryload(models.Subject.days)
                )
            ) if subjects else query
        )
        query = (
            query.options(
                subqueryload(models.Group.students)
            ) if students else query
        )
        query = (
            query.order_by(desc(models.Group.id))
            if last
            else query
        )
        with connect.SessionLocal() as session:
            group = session.execute(
                query
            ).first()
            return group[0] if group else None

    @staticmethod
    def get_groups(
        subjects: bool = False,
        students: bool = False,
    ) -> Optional[list[models.Group]]:
        """Get all groups."""
        query = select(models.Group)
        query = (
            query.options(
                subqueryload(models.Group.subjects).options(
                    subqueryload(models.Subject.days)
                )
            )
            if subjects
            else query
        )
        query = (
            query.options(subqueryload(models.Group.students))
            if students
            else query
        )
        with connect.SessionLocal() as session:
            groups = session.execute(
                query
            ).all()
            return [group[0] for group in groups] if groups else None

    @staticmethod
    def create_group(group: dict) -> models.Group:
        """Create group."""
        with connect.SessionLocal() as session:
            session.add(models.Group(**group))
            session.commit()
        return GroupActions.get_group(last=True)

    @staticmethod
    def edit_group(id: int, group: dict) -> None:
        """Edit group."""
        with connect.SessionLocal() as session:
            session.execute(
                update(models.Group).where(
                    models.Group.id == id
                ).values(**group)
            )
            session.commit()

    @staticmethod
    def delete_group(id: int) -> None:
        """Delete group by id."""
        with connect.SessionLocal() as session:
            session.execute(
                update(models.User).where(
                    models.User.group == id,
                ).values({"group": None})
            )
            session.execute(
                delete(models.Group).where(
                    models.Group.id == id
                )
            )
            session.commit()


class SubjectActions:
    """Class with actions with subject."""

    @staticmethod
    def get_subject(
        id: Optional[int] = None,
        users: bool = False,
        last: bool = False,
    ) -> Optional[models.Subject]:
        """Get subject by id."""
        query = select(models.Subject)
        if id:
            query = query.where(models.Subject.id == id)
        query = (
            query.options(subqueryload(models.Subject.users))
            if users
            else query
        )
        query = (
            query.order_by(desc(models.Subject.id))
            if last
            else query
        )
        with connect.SessionLocal() as session:
            subject = session.execute(
                query
            ).first()
            return subject[0] if subject else None

    @staticmethod
    def get_subjects(
        can_select: Optional[bool],
        users: bool = False,
    ) -> Optional[list[models.Subject]]:
        """Get all subjects."""
        query = select(models.Subject)
        if can_select:
            query = query.where(models.Subject.can_select == can_select)
        query = (
            query.options(
                subqueryload(models.Subject.users)
            )
            if users
            else query
        )
        with connect.SessionLocal() as session:
            subjects = session.execute(
                query
            ).all()
            return [subject[0] for subject in subjects] if subjects else None

    @staticmethod
    def change_status_subjects(
        id: Union[bool, int],
        can_select: bool
    ) -> None:
        """Change status of subject."""
        query = update(models.Subject)
        query = (
            query.where(models.Subject.can_select == id)
            if isinstance(id, bool)
            else query.where(models.Subject.id == id)
        )
        query = query.values(can_select=can_select)
        with connect.SessionLocal() as session:
            session.execute(
                query
            )
            session.commit()

    @staticmethod
    def create_subject(subject: dict) -> models.Subject:
        """Create subject."""
        with connect.SessionLocal() as session:
            session.add(models.Subject(**subject))
            session.commit()
        return SubjectActions.get_subject(last=True)

    @staticmethod
    def delete_subject(id: int) -> None:
        """Delete subject by id."""
        with connect.SessionLocal() as session:
            session.execute(
                delete(models.Subject).where(
                    models.Subject.id == id
                )
            )
            session.commit()


class DateActions:
    """Class with actions with date."""

    @staticmethod
    def get_dates(number: Optional[int]) -> Optional[list[models.Date]]:
        """Get all dates."""
        query = select(models.Date)
        if number:
            query = query.where(models.Date.number == number)
        with connect.SessionLocal() as session:
            dates = session.execute(
                query
            ).all()
            return [date[0] for date in dates] if dates else None

    @staticmethod
    def create_date(date: dict) -> None:
        """Create date."""
        with connect.SessionLocal() as session:
            session.add(models.Date(**date))
            session.commit()

    @staticmethod
    def delete_date_by_subject(id: int) -> None:
        """Delete date."""
        with connect.SessionLocal() as session:
            session.execute(
                delete(models.Date).where(
                    models.Date.subject == id,
                )
            )
            session.commit()


class QueueActions:
    """Class for actions with queue."""

    @staticmethod
    def get_queue_info(id: int) -> Optional[list[models.Queue]]:
        """Get position, where user stay."""
        with connect.SessionLocal() as session:
            positions = session.execute(
                select(models.Queue).where(
                    models.Queue.user_id == id,
                )
            ).all()
            return (
                [position[0] for position in positions]
                if positions
                else None
            )

    @staticmethod
    def cleaning_user(id: int) -> None:
        """Cleaning user queue."""
        with connect.SessionLocal() as session:
            session.execute(
                delete(models.Queue).where(
                    models.Queue.user_id == id,
                )
            )
            session.commit()

    @staticmethod
    def cleaning_subject(id: int) -> None:
        """Cleaning subject queue."""
        with connect.SessionLocal() as session:
            session.execute(
                delete(models.Queue).where(
                    models.Queue.subject_id == id,
                )
            )
            session.commit()

    @staticmethod
    def action_user(params: dict) -> None:
        """Append/remove user to subject."""
        with connect.SessionLocal() as session:
            stay = session.execute(
                select(models.Queue).where(
                    sql.and_(
                        models.Queue.user_id == params["user_id"],
                        models.Queue.subject_id == params["subject_id"],
                        models.Queue.number == params["number"],
                    )
                )
            ).all()
            if not stay:
                session.execute(
                    insert(models.Queue).values(**params)
                )
            else:
                session.execute(
                    delete(models.Queue).where(
                        sql.and_(
                            models.Queue.user_id == params["user_id"],
                            models.Queue.subject_id == params["subject_id"],
                            models.Queue.number == params["number"],
                        )
                    )
                )
            session.commit()

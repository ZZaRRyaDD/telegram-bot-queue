from typing import Optional

from sqlalchemy import desc, select, update
from sqlalchemy.orm import joinedload, subqueryload

from . import connect, models


class UserActions:
    """Class with actions with user."""

    @staticmethod
    def get_user(id: int) -> Optional[models.User]:
        """Get user by id."""
        with connect.SessionLocal() as session:
            user = session.execute(
                select(models.User).filter(
                    models.User.id == id
                )
            ).first()
            return user[0] if user else None

    @staticmethod
    def get_users() -> Optional[list[models.User]]:
        """Get all users."""
        with connect.SessionLocal() as session:
            users = session.execute(
                select(models.User)
            ).all()
            return [user[0] for user in users] if users else None

    @staticmethod
    def get_user_with_subject(id: int) -> Optional[models.User]:
        """Get user by id."""
        with connect.SessionLocal() as session:
            user = session.execute(
                select(models.User).filter(
                    models.User.id == id
                ).options(
                    subqueryload(models.User.subjects),
                )
            ).first()
            return user[0] if user else None

    @staticmethod
    def clear_user_queue(id: int) -> None:
        """Clear queue of user."""
        user = UserActions.get_user_with_subject(id)
        with connect.SessionLocal.begin() as session:
            subjects = user.subjects[::]
            for subject in subjects:
                user.subjects.remove(subject)
            session.commit()

    @staticmethod
    def create_user(user: dict) -> None:
        """Create user."""
        user = models.User(**user)
        with connect.SessionLocal.begin() as session:
            session.add(user)
            session.commit()

    @staticmethod
    def edit_user(id: int, user: dict) -> None:
        """Edit user by id."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                update(models.User).where(
                    models.User.id == id
                ).values(user)
            )


class GroupActions:
    """Class with actions with group."""

    @staticmethod
    def get_group(id: int) -> Optional[models.Group]:
        """Get group by id."""
        with connect.SessionLocal() as session:
            group = session.execute(
                select(models.Group).filter(
                    models.Group.id == id
                )
            ).first()
            return group[0] if group else None

    @staticmethod
    def get_group_with_subjects(id: int) -> Optional[models.Group]:
        """Get group by id."""
        with connect.SessionLocal() as session:
            group = session.execute(
                select(models.Group).filter(
                    models.Group.id == id
                ).options(
                    subqueryload(models.Group.subjects).options(
                        joinedload(models.Subject.days),
                    ),
                )
            ).first()
            return group[0] if group else None

    @staticmethod
    def get_group_by_name(name: str) -> Optional[models.Group]:
        """Get group by name."""
        with connect.SessionLocal() as session:
            group = session.execute(
                select(models.Group).filter(
                    models.Group.name == name
                )
            ).first()
            return group[0] if group else None

    @staticmethod
    def get_groups() -> Optional[list[models.Group]]:
        """Get all groups."""
        with connect.SessionLocal() as session:
            groups = session.execute(
                select(models.Group)
            ).all()
            return [group[0] for group in groups] if groups else None

    @staticmethod
    def get_last_group() -> models.Group:
        """Get last created group."""
        with connect.SessionLocal() as session:
            group = session.execute(
                select(models.Group).order_by(
                    desc(models.Group.id)
                )
            ).first()
            return group[0]

    @staticmethod
    def create_group(group: dict) -> models.Group:
        """Create group."""
        with connect.SessionLocal.begin() as session:
            session.add(models.Group(**group))
            session.commit()
        return GroupActions.get_last_group()

    @staticmethod
    def edit_group(id: int, group: dict) -> None:
        """Edit group."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                update(models.Group).where(
                    models.Group.id == id
                ).values(**group)
            )

    @staticmethod
    def delete_group(id: int) -> None:
        """Delete group by id."""
        with connect.SessionLocal.begin() as session:
            session.delete(GroupActions.get_group(id))
            session.commit()


class SubjectActions:
    """Class with actions with subject."""

    @staticmethod
    def get_subject(id: int) -> Optional[models.Subject]:
        """Get subject by id."""
        with connect.SessionLocal() as session:
            subject = session.execute(
                select(models.Subject).filter(
                    models.Subject.id == id
                ).options(
                    subqueryload(models.Subject.users),
                )
            ).first()
            return subject[0] if subject else None

    @staticmethod
    def clear_subject_queue(id: int) -> None:
        """Clear queue of user."""
        subject = SubjectActions.get_subject(id)
        with connect.SessionLocal.begin() as session:
            users = subject.users[::]
            for user in users:
                subject.users.remove(user)
            session.commit()

    @staticmethod
    def get_subjects() -> Optional[list[models.Subject]]:
        """Get all subjects."""
        with connect.SessionLocal() as session:
            subjects = session.execute(
                select(models.Subject).options(
                    subqueryload(models.Subject.users),
                )
            ).all()
            return [subject[0] for subject in subjects] if subjects else None

    @staticmethod
    def get_last_subject() -> models.Subject:
        """Get last created group."""
        with connect.SessionLocal() as session:
            subject = session.execute(
                select(models.Subject).order_by(
                    desc(models.Subject.id)
                )
            ).first()
            return subject[0]

    @staticmethod
    def action_user(user: models.User, subject: models.Subject) -> None:
        """Append/remove user to subject."""
        with connect.SessionLocal.begin() as session:
            if user in subject.users:
                subject.users.remove(user)
            else:
                subject.users.append(user)
            session.commit()

    @staticmethod
    def create_subject(subject: dict) -> models.Subject:
        """Create subject."""
        with connect.SessionLocal.begin() as session:
            session.add(models.Subject(**subject))
            session.commit()
        return SubjectActions.get_last_subject()

    @staticmethod
    def delete_subject(id: int) -> None:
        """Delete subject by id."""
        with connect.SessionLocal.begin() as session:
            session.delete(SubjectActions.get_subject(id))
            session.commit()


class DateActions:
    """Class with actions with date."""

    @staticmethod
    def create_date(date: dict) -> None:
        """Create date."""
        with connect.SessionLocal.begin() as session:
            session.add(models.Date(**date))
            session.commit()

    @staticmethod
    def get_dates() -> Optional[list[models.Date]]:
        """Get all dates."""
        with connect.SessionLocal() as session:
            dates = session.execute(
                select(models.Date)
            ).all()
            return [date[0] for date in dates] if dates else None

    @staticmethod
    def delete_date(date: models.Date) -> None:
        """Delete date."""
        with connect.SessionLocal.begin() as session:
            session.delete(date)
            session.commit()

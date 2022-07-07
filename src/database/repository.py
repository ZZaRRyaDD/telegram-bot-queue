import json
from typing import Optional

from sqlalchemy import delete, desc, select, update

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
    def create_user(user: dict) -> Optional[models.User]:
        """Create user."""
        user = models.User(**user)
        with connect.SessionLocal.begin() as session:
            session.add(user)
            session.commit()
        return UserActions.get_user(user.id)

    @staticmethod
    def edit_user(id: int, user: dict) -> Optional[models.User]:
        """Edit user by id."""
        print(user)
        print(type(user))
        with connect.SessionLocal.begin() as session:
            res = session.execute(
                update(models.User).where(
                    models.User.id == id
                ).values(user)
            )
            print(res)
        return UserActions.get_user(id)


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
    def get_groups() -> Optional[list[models.Group]]:
        """Get all groups."""
        with connect.SessionLocal() as session:
            groups = session.execute(
                select(models.Group)
            ).all()
            return groups if groups else None

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
        print(type(group))
        new_group = models.Group(json.dumps(group.__dict__))
        with connect.SessionLocal.begin() as session:
            session.add(new_group)
            session.commit()
        return GroupActions.get_last_group()

    @staticmethod
    def edit_group(id: int, group: dict) -> models.Group:
        """Edit group."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                update(models.Group).where(
                    models.Group.id == id
                ).values(json.dumps(group.__dict__))
            )
        return GroupActions.get_group(id)

    @staticmethod
    def delete_group(id: int) -> None:
        """Delete group by id."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                delete(models.Group).where(
                    models.Group.id == id
                )
            )


class SubjectActions:
    """Class with actions with subject."""

    @staticmethod
    def get_subject(id: int) -> Optional[models.Subject]:
        """Get subject by id."""
        with connect.SessionLocal() as session:
            subject = session.execute(
                select(models.Subject).filter(
                    models.Subject.id == id
                )
            ).first()
            return subject[0] if subject else None

    @staticmethod
    def get_subjects_of_group(id: int) -> Optional[list[models.Subject]]:
        """Get subjects by group id."""
        return GroupActions.get_group(id).subjects

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
    def create_subject(subject: dict) -> models.Subject:
        """Create subject."""
        new_subject = models.Subject(json.dumps(subject.__dict__))
        with connect.SessionLocal.begin() as session:
            session.add(new_subject)
            session.commit()
        return SubjectActions.get_last_subject()

    @staticmethod
    def edit_subject(id: int, subject) -> models.Subject:
        """Edit subject."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                update(models.Subject).where(
                    models.Subject.id == id
                ).values(json.dumps(subject.__dict__))
            )
        return SubjectActions.get_subject(id)

    @staticmethod
    def delete_subject(id: int) -> None:
        """Delete subject by id."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                delete(models.Subject).where(
                    models.Subject.id == id
                )
            )

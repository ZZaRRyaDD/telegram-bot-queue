import os
from typing import Optional

from sqlalchemy import delete, orm, select, update

from .. import connect
from ..models import Subject, User


class UserActions:
    """Class with actions with user."""

    @staticmethod
    def get_user(
        user_id: int,
        subjects_practice: bool = False,
        subjects_completed: bool = False,
    ) -> Optional[User]:
        """Get user by id."""
        query = select(User).filter(User.id == user_id)
        if subjects_practice:
            query = query.options(
                orm.subqueryload(User.subjects_practice).options(
                    orm.subqueryload(Subject.days),
                ),
            )
        if subjects_completed:
            query = query.options(
                orm.subqueryload(User.subjects_completed),
            )
        with connect.SessionLocal() as session:
            user = session.execute(query).first()
            return user[0] if user else None

    @staticmethod
    def get_users(
        with_group: bool = False,
        without_admin: bool = False,
    ) -> list[User]:
        """Get users."""
        query = select(User)
        if with_group:
            query = query.where(
                User.group.is_not(None),
            )
        if without_admin:
            query = query.where(
                User.id != int(os.getenv("ADMIN_ID")),
            )
        with connect.SessionLocal() as session:
            users = session.execute(query).all()
            return [user[0] for user in users] if users else []

    @staticmethod
    def create_user(user: dict) -> None:
        """Create user."""
        with connect.SessionLocal.begin() as session:
            session.add(User(**user))
            session.commit()

    @staticmethod
    def edit_user(user_id: int, user: dict) -> None:
        """Edit user by id."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                update(User).where(
                    User.id == user_id,
                ).values(user),
            )

    @staticmethod
    def delete_user(user_id: int) -> None:
        """Delete user by id."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                delete(User).where(
                    User.id == user_id,
                ),
            )

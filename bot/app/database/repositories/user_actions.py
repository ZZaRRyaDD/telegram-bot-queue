import os
from typing import Optional

from sqlalchemy import delete, orm, select, update

from app.database.connection import get_session
from app.database.models import Subject, User


class UserActions:
    """Class with actions with user."""

    @staticmethod
    async def get_user(
        user_id: int,
        group: bool = False,
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
        if group:
            query = query.options(
                orm.joinedload(User.group),
            )
        async with get_session() as session:
            result = await session.execute(query)
            return result.scalar()

    @staticmethod
    async def get_users(
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
        async with get_session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def create_user(user: dict) -> User:
        """Create user."""
        user = User(**user)
        async with get_session() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    @staticmethod
    async def update_user(user_id: int, user: dict) -> None:
        """Edit user by id."""
        query = update(User).where(User.id == user_id).values(**user)
        async with get_session() as session:
            await session.execute(query)

    @staticmethod
    async def delete_user(user_id: int) -> None:
        """Delete user by id."""
        query = delete(User).where(User.id == user_id)
        async with get_session() as session:
            await session.execute(query)

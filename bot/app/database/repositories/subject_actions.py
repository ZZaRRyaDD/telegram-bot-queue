from typing import Optional

from sqlalchemy import delete, orm, select, update

from app.database.connection import connect
from app.database.models import Subject


class SubjectActions:
    """Class with actions with subject."""

    @staticmethod
    async def get_subject(
        subject_id: Optional[int] = None,
        users_practice: bool = False,
    ) -> Optional[Subject]:
        """Get subject."""
        query = select(Subject)
        if subject_id is not None:
            query = query.where(Subject.id == subject_id)
        if users_practice:
            query = query.options(
                orm.subqueryload(Subject.users_practice),
            )
        async with anext(connect.get_session()) as session:
            result = await session.execute(query)
            return result.scalar()

    @staticmethod
    async def get_subjects(
        users_practice: bool = False,
    ) -> list[Subject]:
        """Get all subjects."""
        query = select(Subject)
        if users_practice:
            query = query.options(
                orm.subqueryload(Subject.users_practice),
            )
        async with anext(connect.get_session()) as session:
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def create_subject(subject: dict) -> Subject:
        """Create subject."""
        subject = Subject(**subject)
        async with anext(connect.get_session()) as session:
            session.add(subject)
            session.commit()
            session.refresh(subject)
            return subject

    @staticmethod
    async def update_subject(subject_id: int, subject: dict) -> None:
        """Update subject."""
        query = update(Subject).where(Subject.id == subject_id).values(subject)
        async with anext(connect.get_session()) as session:
            await session.execute(query)

    @staticmethod
    async def delete_subject(subject_id: int) -> None:
        """Delete subject by id."""
        query = delete(Subject).where(Subject.id == subject_id)
        async with anext(connect.get_session()) as session:
            await session.execute(query)

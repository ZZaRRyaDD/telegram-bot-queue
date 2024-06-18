from sqlalchemy import delete, select, sql

from app.database.connection import get_session
from app.database.models import CompletedPractices

from .base import BaseRepository


class CompletedPracticesRepository(BaseRepository):
    model = CompletedPractices

    @classmethod
    async def get_completed_practices_info(cls, complete_practices_id: int) -> list[CompletedPractices]:
        """Get completed labs, where user stay."""
        query = select(cls.model).where(cls.model.user_id == complete_practices_id)
        async with get_session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def exists_completed_practices(cls, params: dict) -> bool:
        """Check exists completed practices with current params."""
        query = select(cls.model).where(
            sql.and_(
                cls.model.user_id == params["user_id"],
                cls.model.subject_id == params["subject_id"],
                cls.model.number_practice == params["number_practice"],
            ),
        )
        async with get_session() as session:
            result = await session.execute(query)
            return result.scalar()

    @classmethod
    async def remove_completed_practices_labs(cls, params: dict) -> None:
        """Remove user from completed practices."""
        query = delete(cls.model).where(
            sql.and_(
                cls.model.subject_id == params["subject_id"],
                cls.model.number_practice == params["number_practice"],
            ),
        )
        async with get_session() as session:
            await session.execute(query)
            await session.commit()

    @classmethod
    async def remove_completed_practices(cls, params: dict) -> None:
        """Remove user from completed practices."""
        query = delete(cls.model).where(
            sql.and_(
                cls.model.user_id == params["user_id"],
                cls.model.subject_id == params["subject_id"],
                cls.model.number_practice == params["number_practice"],
            ),
        )
        async with get_session() as session:
            await session.execute(query)
            await session.commit()

    @classmethod
    async def action_user(cls, params: dict) -> None:
        """Append/remove user to subject."""
        if not (await CompletedPracticesRepository.exists_completed_practices(params)):
            await CompletedPracticesRepository.create(obj_in=params)
            return True
        await CompletedPracticesRepository.remove_completed_practices(params)
        return False

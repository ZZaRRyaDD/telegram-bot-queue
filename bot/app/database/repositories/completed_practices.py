from sqlalchemy import delete, insert, select, sql

from app.database.connection import get_session
from app.database.models import CompletedPractices


class CompletedPracticesActions:
    """Class for actions with completed_practices."""

    @staticmethod
    async def get_completed_practices_info(complete_practices_id: int) -> list[CompletedPractices]:
        """Get completed labs, where user stay."""
        query = select(CompletedPractices).where(CompletedPractices.user_id == complete_practices_id)
        async with get_session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def exists_completed_practices(params: dict) -> bool:
        """Check exists completed practices with current params."""
        query = select(CompletedPractices).where(
            sql.and_(
                CompletedPractices.user_id == params["user_id"],
                CompletedPractices.subject_id == params["subject_id"],
                CompletedPractices.number_practice == params["number_practice"],
            ),
        )
        async with get_session() as session:
            result = await session.execute(query)
            return result.scalar()

    @staticmethod
    async def append_completed_practices(params: dict) -> None:
        """Append user in completed practices."""
        query = insert(CompletedPractices).values(**params)
        async with get_session() as session:
            await session.execute(query)

    @staticmethod
    async def remove_completed_practices_labs(params: dict) -> None:
        """Remove user from completed practices."""
        query = delete(CompletedPractices).where(
            sql.and_(
                CompletedPractices.subject_id == params["subject_id"],
                CompletedPractices.number_practice == params["number_practice"],
            ),
        )
        async with get_session() as session:
            await session.execute(query)

    @staticmethod
    async def remove_completed_practices(params: dict) -> None:
        """Remove user from completed practices."""
        query = delete(CompletedPractices).where(
            sql.and_(
                CompletedPractices.user_id == params["user_id"],
                CompletedPractices.subject_id == params["subject_id"],
                CompletedPractices.number_practice == params["number_practice"],
            ),
        )
        async with get_session() as session:
            await session.execute(query)

    @staticmethod
    async def action_user(params: dict) -> None:
        """Append/remove user to subject."""
        if not (await CompletedPracticesActions.exists_completed_practices(params)):
            await CompletedPracticesActions.append_completed_practices(params)
            return True
        await CompletedPracticesActions.remove_completed_practices(params)
        return False

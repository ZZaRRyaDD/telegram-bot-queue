from sqlalchemy import delete, insert, select, sql

from .. import connect
from ..models import CompletedPractices


class CompletedPracticesActions:
    """Class for actions with completed_practices."""

    @staticmethod
    async def get_completed_practices_info(
        complete_practices_id: int,
    ) -> list[CompletedPractices]:
        """Get completed labs, where user stay."""
        async with anext(connect.get_session()) as session:
            practices = await session.execute(
                select(CompletedPractices).where(
                    CompletedPractices.user_id == complete_practices_id,
                ),
            ).all()
            return (
                [practice[0] for practice in practices]
                if practices
                else []
            )

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
        async with anext(connect.get_session()) as session:
            result = await session.execute(query).first()
            return result[0] if result else []

    @staticmethod
    async def append_completed_practices(params: dict) -> None:
        """Append user in completed practices."""
        async with anext(connect.get_session()) as session:
            await session.execute(
                insert(CompletedPractices).values(**params),
            )

    @staticmethod
    async def remove_completed_practices_labs(params: dict) -> None:
        """Remove user from completed practices."""
        async with anext(connect.get_session()) as session:
            await session.execute(
                delete(CompletedPractices).where(
                    sql.and_(
                        CompletedPractices.subject_id == params["subject_id"],
                        CompletedPractices.number_practice == params["number_practice"],
                    ),
                ),
            )

    @staticmethod
    async def remove_completed_practices(params: dict) -> None:
        """Remove user from completed practices."""
        async with anext(connect.get_session()) as session:
            await session.execute(
                delete(CompletedPractices).where(
                    sql.and_(
                        CompletedPractices.user_id == params["user_id"],
                        CompletedPractices.subject_id == params["subject_id"],
                        CompletedPractices.number_practice == params["number_practice"],
                    ),
                ),
            )

    @staticmethod
    async def action_user(params: dict) -> None:
        """Append/remove user to subject."""
        if not (await CompletedPracticesActions.exists_completed_practices(params)):
            await CompletedPracticesActions.append_completed_practices(params)
            return True
        await CompletedPracticesActions.remove_completed_practices(params)
        return False

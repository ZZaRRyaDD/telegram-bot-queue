from typing import Optional

from sqlalchemy import delete, select

from .. import connect
from ..models import Date


class DateActions:
    """Class with actions with date."""

    @staticmethod
    def get_dates(number: Optional[int] = None) -> Optional[list[Date]]:
        """Get all dates."""
        query = select(Date)
        if number is not None:
            query = query.where(Date.number == number)
        with connect.SessionLocal() as session:
            dates = session.execute(query).all()
            return [date[0] for date in dates] if dates else None

    @staticmethod
    def create_date(date: dict) -> None:
        """Create date."""
        with connect.SessionLocal.begin() as session:
            session.add(Date(**date))
            session.commit()

    @staticmethod
    def delete_date_by_subject(id: int) -> None:
        """Delete date."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                delete(Date).where(
                    Date.subject == id,
                )
            )

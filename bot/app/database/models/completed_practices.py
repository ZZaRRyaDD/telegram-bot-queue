from sqlalchemy import BigInteger, Column, ForeignKey, Integer

from .base import BaseTable


class CompletedPractices(BaseTable):
    """Model for each completed practice."""
    __tablename__ = "completed_practices"

    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    subject_id = Column(
        BigInteger,
        ForeignKey("subjects.id", ondelete="CASCADE"),
    )
    number_practice = Column(Integer)

from sqlalchemy import BigInteger, Column, ForeignKey, Integer

from .base import BaseTable


class Queue(BaseTable):
    """Model for each queue."""
    __tablename__ = "queue"

    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    subject_id = Column(
        BigInteger,
        ForeignKey("subjects.id", ondelete="CASCADE"),
    )
    number_practice = Column(Integer, nullable=True)
    number_in_list = Column(Integer, nullable=True)

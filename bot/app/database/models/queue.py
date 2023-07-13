from sqlalchemy import BigInteger, Column, ForeignKey, Integer

from ..connect import Base


class Queue(Base):
    """Model for each queue."""
    __tablename__ = "queue"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    subject_id = Column(
        Integer,
        ForeignKey("subjects.id", ondelete="CASCADE"),
    )
    number_practice = Column(Integer, nullable=True)
    number_in_list = Column(Integer, nullable=True)

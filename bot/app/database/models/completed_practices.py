from sqlalchemy import BigInteger, Column, ForeignKey, Integer

from ..connect import Base


class CompletedPractices(Base):
    """Model for each completed practice."""
    __tablename__ = "completed_practices"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    subject_id = Column(
        Integer,
        ForeignKey("subjects.id", ondelete="CASCADE"),
    )
    number_practice = Column(Integer)

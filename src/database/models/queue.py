from sqlalchemy import Column, ForeignKey, Integer

from ..connect import Base


class Queue(Base):
    """Model for each queue."""
    __tablename__ = "queue"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    number = Column(Integer)

from sqlalchemy import Boolean, Column, ForeignKey, Integer

from ..connect import Base


class Schedule(Base):
    """Model for each subject."""
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    on_even_week = Column(Boolean, default=None)
    date_number = Column(Integer)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    can_select = Column(Boolean, default=False)

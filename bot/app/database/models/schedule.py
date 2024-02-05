import enum

from sqlalchemy import Boolean, Column, Date, Enum, ForeignKey, Integer, orm

from ..connect import Base


class Weekday(int, enum.Enum):
    """Model for number weekday."""

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5


class Week(int, enum.Enum):
    """Model for type week."""

    EACH_WEEK = 0
    EACH_ODD_WEEK = 1
    EACH_EVEN_WEEK = 2


class Schedule(Base):
    """Model for each subject."""
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    week = Column(Enum(Week), nullable=False)
    date_number = Column(Enum(Weekday), nullable=False)
    subject_id = Column(
        Integer,
        ForeignKey("subjects.id", ondelete="CASCADE"),
    )
    can_select = Column(Boolean, default=False)
    date_protection = Column(Date, default=None)
    subject = orm.relationship(
        "Subject",
        lazy="joined",
        back_populates="days",
    )

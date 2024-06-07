import enum

from sqlalchemy import Boolean, Column, Date, Enum, ForeignKey, Integer, orm

from app.enums import DaysOfWeekEnum, SubjectPassesEnum

from app.database.connection import Base


class Weekday(int, enum.Enum):
    """Model for number weekday."""

    MONDAY = DaysOfWeekEnum.MONDAY.number
    TUESDAY = DaysOfWeekEnum.TUESDAY.number
    WEDNESDAY = DaysOfWeekEnum.WEDNESDAY.number
    THURSDAY = DaysOfWeekEnum.THURSDAY.number
    FRIDAY = DaysOfWeekEnum.FRIDAY.number
    SATURDAY = DaysOfWeekEnum.SATURDAY.number


class Week(str, enum.Enum):
    """Model for type week."""

    EACH_WEEK = SubjectPassesEnum.EACH_WEEK.constant
    EACH_ODD_WEEK = SubjectPassesEnum.EACH_ODD_WEEK.constant
    EACH_EVEN_WEEK = SubjectPassesEnum.EACH_EVEN_WEEK.constant


class Schedule(Base):
    """Model for each subject."""
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    week = Column(Enum(Week), nullable=False)
    date_number = Column(Enum(Weekday), nullable=False)
    can_select = Column(Boolean, default=False)
    date_protection = Column(Date, default=None)

    subject_id = Column(
        Integer,
        ForeignKey("subjects.id", ondelete="CASCADE"),
    )
    subject = orm.relationship(
        "Subject",
        lazy="joined",
        back_populates="days",
    )

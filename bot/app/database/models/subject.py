import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String, orm

from .base import BaseTable
from app.enums import SubjectTypeEnum


class SubjectType(str, enum.Enum):
    """Model for type subject."""

    LABORATORY_WORK = SubjectTypeEnum.LABORATORY_WORK.value
    COURSE_WORK = SubjectTypeEnum.COURSE_WORK.value
    SUMMER_PRACTICE = SubjectTypeEnum.SUMMER_PRACTICE.value
    GRADUATE_WORK = SubjectTypeEnum.GRADUATE_WORK.value


class Subject(BaseTable):
    """Model for each subject."""
    __tablename__ = "subjects"

    name = Column(String(128), nullable=False)
    count_practices = Column(Integer)
    subject_type = Column(Enum(SubjectType), nullable=False)
    days = orm.relationship(
        "Schedule",
        back_populates="subject",
        lazy="subquery",
    )
    users_practice = orm.relationship(
        "User",
        secondary="queue",
        back_populates="subjects_practice",
        lazy="subquery",
    )
    users_completed = orm.relationship(
        "User",
        secondary="completed_practices",
        back_populates="subjects_completed",
        lazy="subquery",
    )

    group_id = Column(
        Integer,
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
    )
    group = orm.relationship(
        "Group",
        back_populates="subjects",
        lazy="joined",
        innerjoin=True,
    )

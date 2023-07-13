import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String, orm

from ..connect import Base


class SubjectType(str, enum.Enum):
    """Model for type subject."""

    LABORATORY_WORK = "Лабораторная работа"
    COURSE_WORK = "Курсовая работа"
    SUMMER_PRACTICE = "Летняя практика"
    GRADUATE_WORK = "Дипломная работа"


class Subject(Base):
    """Model for each subject."""
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    count_practices = Column(Integer)
    group_id = Column(
        Integer,
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
    )
    subject_type = Column(Enum(SubjectType), nullable=False)
    users_practice = orm.relationship(
        "User",
        secondary="queue",
        back_populates="subjects_practice",
        lazy="subquery",
    )
    days = orm.relationship(
        "Schedule",
        back_populates="subject",
        lazy="subquery",
    )
    users_completed = orm.relationship(
        "User",
        secondary="completed_practices",
        back_populates="subjects_completed",
        lazy="subquery",
    )
    group = orm.relationship(
        "Group",
        back_populates="subjects",
        lazy="joined",
        innerjoin=True,
    )

import enum

from app.database import SubjectType


class SubjectTypeEnum(enum.Enum):
    """Class choices for type of subject."""

    COURSE_WORK = (SubjectType.COURSE_WORK, "Курсовая работа")
    SUMMER_PRACTICE = (SubjectType.SUMMER_PRACTICE, "Летняя практика")
    GRADUATE_WORK = (SubjectType.GRADUATE_WORK, "Дипломная работа")

    def __init__(self, type_: str, description: str) -> None:
        self.type = type_
        self.description = description

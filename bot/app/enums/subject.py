import enum


class SubjectTypeEnum(enum.Enum):
    """Class choices for type of subject."""

    LABORATORY_WORK = "Лабораторная работа"
    COURSE_WORK = "Курсовая работа"
    SUMMER_PRACTICE = "Летняя практика"
    GRADUATE_WORK = "Дипломная работа"

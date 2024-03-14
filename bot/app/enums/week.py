import enum


class DaysOfWeekEnum(enum.Enum):
    """Class choices for day of week."""

    MONDAY = (0, "Понедельник")
    TUESDAY = (1, "Вторник")
    WEDNESDAY = (2, "Среда")
    THURSDAY = (3, "Четверг")
    FRIDAY = (4, "Пятница")
    SATURDAY = (5, "Суббота")
    STOP = ("Stop", "Завершить выбор")

    def __init__(self, number: int | str, weekday: str) -> None:
        self.number = number
        self.weekday = weekday


class SubjectPassesEnum(enum.Enum):
    """Class choices for time of subject."""

    EACH_WEEK = ("each_week", "Каждую неделю")
    EACH_ODD_WEEK = ("each_odd_week", "По нечетным неделям")
    EACH_EVEN_WEEK = ("each_even_week", "По четным неделям")

    def __init__(self, value: str, description: str) -> None:
        self.value = value
        self.description = description

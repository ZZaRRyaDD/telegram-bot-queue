import enum

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class DaysOfWeek(enum.Enum):
    """Class choices for day of week."""

    MONDAY = (0, "Понедельник")
    TUESDAY = (1, "Вторник")
    WEDNESDAY = (2, "Среда")
    THURSDAY = (3, "Четверг")
    FRIDAY = (4, "Пятница")
    SATURDAY = (5, "Суббота")
    STOP = ("Stop", "Завершить выбор")

    def __init__(self, number: int, weekday: str) -> None:
        self.number = number
        self.weekday = weekday


class SubjectPasses(enum.Enum):
    """Class choices for time of subject."""

    EACH_WEEK = ("None", "Каждую неделю")
    EACH_ODD_WEEK = ("False", "По нечетным неделям")
    EACH_EVEN_WEEK = ("True", "По четным неделям")

    def __init__(self, value: str, description: str) -> None:
        self.value = value
        self.description = description


class ScheduleActions(enum.Enum):
    """Class choices of schedule actions."""

    ADD = ("Add", "Добавить расписание")
    DELETE = ("Delete", "Удалить расписание")

    def __init__(self, action: str, description: str) -> None:
        self.action = action
        self.description = description


def select_days() -> InlineKeyboardMarkup:
    """Create keys for select days of week."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.row(
        InlineKeyboardButton(
            text=DaysOfWeek.MONDAY.weekday,
            callback_data=DaysOfWeek.MONDAY.number,
        ),
        InlineKeyboardButton(
            text=DaysOfWeek.TUESDAY.weekday,
            callback_data=DaysOfWeek.TUESDAY.number,
        ),
    ).row(
        InlineKeyboardButton(
            text=DaysOfWeek.WEDNESDAY.weekday,
            callback_data=DaysOfWeek.WEDNESDAY.number,
        ),
        InlineKeyboardButton(
            text=DaysOfWeek.THURSDAY.weekday,
            callback_data=DaysOfWeek.THURSDAY.number,
        ),
    ).row(
        InlineKeyboardButton(
            text=DaysOfWeek.FRIDAY.weekday,
            callback_data=DaysOfWeek.FRIDAY.number,
        ),
        InlineKeyboardButton(
            text=DaysOfWeek.SATURDAY.weekday,
            callback_data=DaysOfWeek.SATURDAY.number,
        ),
    ).row(
        InlineKeyboardButton(
            text=DaysOfWeek.STOP.weekday,
            callback_data=DaysOfWeek.STOP.number,
        ),
    )
    return keyboard


def add_schedule(schedules) -> KeyboardInterrupt:
    """Create keyboard for schedule of subject."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.row(
        InlineKeyboardButton(
            text=ScheduleActions.ADD.description,
            callback_data=ScheduleActions.ADD.action,
        ),
        InlineKeyboardButton(
            text=ScheduleActions.DELETE.description,
            callback_data=ScheduleActions.DELETE.action,
        )
    )
    return keyboard



def select_subject_passes() -> KeyboardInterrupt:
    """Create keyboard for select when subject passes."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.row(
        InlineKeyboardButton(
            text=SubjectPasses.EACH_WEEK.description,
            callback_data=SubjectPasses.EACH_WEEK.value,
        ),
    ).row(
        InlineKeyboardButton(
            text=SubjectPasses.EACH_ODD_WEEK.description,
            callback_data=SubjectPasses.EACH_ODD_WEEK.value,
        ),
    ).row(
        InlineKeyboardButton(
            text=SubjectPasses.EACH_EVEN_WEEK.description,
            callback_data=SubjectPasses.EACH_EVEN_WEEK.value,
        ),
    )
    return keyboard

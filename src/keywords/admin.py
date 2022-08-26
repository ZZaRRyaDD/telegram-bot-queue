import enum

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .client import get_list_keys


class DaysOfWeekEnum(enum.Enum):
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


class GroupActionsEnum(enum.Enum):
    """Class choices of group actions."""

    CREATE = ("Create", "Создать группу")
    UPDATE = ("Update", "Обновить группу")
    DELETE = ("Delete", "Удалить группу")

    def __init__(self, action: str, description: str) -> None:
        self.action = action
        self.description = description


class SubjectPassesEnum(enum.Enum):
    """Class choices for time of subject."""

    EACH_WEEK = ("None", "Каждую неделю")
    EACH_ODD_WEEK = ("False", "По нечетным неделям")
    EACH_EVEN_WEEK = ("True", "По четным неделям")

    def __init__(self, value: str, description: str) -> None:
        self.value = value
        self.description = description


class SubjectActionsEnum(enum.Enum):
    """Class choices of subject actions."""

    CREATE = ("Create", "Добавить предмет")
    UPDATE = ("Update", "Обновить предмет")
    DELETE = ("Delete", "Удалить предмет")

    def __init__(self, action: str, description: str) -> None:
        self.action = action
        self.description = description


class ScheduleActionsEnum(enum.Enum):
    """Class choices of schedule actions."""

    ADD = ("Add", "Добавить расписание")
    DELETE = ("Delete", "Удалить расписание")
    NEXT_ACTION = ("Next", "Продолжить создание предмета")

    def __init__(self, action: str, description: str) -> None:
        self.action = action
        self.description = description


def select_days() -> InlineKeyboardMarkup:
    """Create keys for select days of week."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.row(
        InlineKeyboardButton(
            text=DaysOfWeekEnum.MONDAY.weekday,
            callback_data=DaysOfWeekEnum.MONDAY.number,
        ),
        InlineKeyboardButton(
            text=DaysOfWeekEnum.TUESDAY.weekday,
            callback_data=DaysOfWeekEnum.TUESDAY.number,
        ),
    ).row(
        InlineKeyboardButton(
            text=DaysOfWeekEnum.WEDNESDAY.weekday,
            callback_data=DaysOfWeekEnum.WEDNESDAY.number,
        ),
        InlineKeyboardButton(
            text=DaysOfWeekEnum.THURSDAY.weekday,
            callback_data=DaysOfWeekEnum.THURSDAY.number,
        ),
    ).row(
        InlineKeyboardButton(
            text=DaysOfWeekEnum.FRIDAY.weekday,
            callback_data=DaysOfWeekEnum.FRIDAY.number,
        ),
        InlineKeyboardButton(
            text=DaysOfWeekEnum.SATURDAY.weekday,
            callback_data=DaysOfWeekEnum.SATURDAY.number,
        ),
    ).row(
        InlineKeyboardButton(
            text=DaysOfWeekEnum.STOP.weekday,
            callback_data=DaysOfWeekEnum.STOP.number,
        ),
    )
    return keyboard


def subject_action() -> InlineKeyboardMarkup:
    """Create keyboard for create/update/delete subject."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.row(
        InlineKeyboardButton(
            text=SubjectActionsEnum.CREATE.description,
            callback_data=SubjectActionsEnum.CREATE.action,
        ),
    ).row(
        InlineKeyboardButton(
            text=SubjectActionsEnum.UPDATE.description,
            callback_data=SubjectActionsEnum.UPDATE.action,
        ),
    ).row(
        InlineKeyboardButton(
            text=SubjectActionsEnum.DELETE.description,
            callback_data=SubjectActionsEnum.DELETE.action,
        ),
    )
    return keyboard


def choice_schedule(schedule: list) -> InlineKeyboardMarkup:
    """Create keyboard for choice schedule."""
    return get_list_keys(schedule)


def group_action() -> InlineKeyboardMarkup:
    """Create keyboard for create/update/delete group."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.row(
        InlineKeyboardButton(
            text=GroupActionsEnum.CREATE.description,
            callback_data=GroupActionsEnum.CREATE.action,
        ),
    ).row(
        InlineKeyboardButton(
            text=GroupActionsEnum.UPDATE.description,
            callback_data=GroupActionsEnum.UPDATE.action,
        ),
    ).row(
        InlineKeyboardButton(
            text=GroupActionsEnum.DELETE.description,
            callback_data=GroupActionsEnum.DELETE.action,
        ),
    )
    return keyboard


def schedule_action(next_action: bool = False) -> InlineKeyboardMarkup:
    """Create keyboard for schedule of subject."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.row(
        InlineKeyboardButton(
            text=ScheduleActionsEnum.ADD.description,
            callback_data=ScheduleActionsEnum.ADD.action,
        ),
        InlineKeyboardButton(
            text=ScheduleActionsEnum.DELETE.description,
            callback_data=ScheduleActionsEnum.DELETE.action,
        )
    )
    if next_action:
        keyboard.row(
            InlineKeyboardButton(
                text=ScheduleActionsEnum.NEXT_ACTION.description,
                callback_data=ScheduleActionsEnum.NEXT_ACTION.action,
            ),
        )
    return keyboard


def select_subject_passes() -> InlineKeyboardMarkup:
    """Create keyboard for select when subject passes."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.row(
        InlineKeyboardButton(
            text=SubjectPassesEnum.EACH_WEEK.description,
            callback_data=SubjectPassesEnum.EACH_WEEK.value,
        ),
    ).row(
        InlineKeyboardButton(
            text=SubjectPassesEnum.EACH_ODD_WEEK.description,
            callback_data=SubjectPassesEnum.EACH_ODD_WEEK.value,
        ),
    ).row(
        InlineKeyboardButton(
            text=SubjectPassesEnum.EACH_EVEN_WEEK.description,
            callback_data=SubjectPassesEnum.EACH_EVEN_WEEK.value,
        ),
    )
    return keyboard

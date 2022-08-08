import enum

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class DaysOfWeek(enum.Enum):
    """Class choices."""

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5


def select_days() -> InlineKeyboardMarkup:
    """Create keys for select days of week."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.row(
        InlineKeyboardButton(
            text="Понедельник",
            callback_data=DaysOfWeek.MONDAY.value,
        ),
        InlineKeyboardButton(
            text="Вторник",
            callback_data=DaysOfWeek.TUESDAY.value,
        ),
    ).row(
        InlineKeyboardButton(
            text="Среда",
            callback_data=DaysOfWeek.WEDNESDAY.value,
        ),
        InlineKeyboardButton(
            text="Четверг",
            callback_data=DaysOfWeek.THURSDAY.value,
        ),
    ).row(
        InlineKeyboardButton(
            text="Пятница",
            callback_data=DaysOfWeek.FRIDAY.value,
        ),
        InlineKeyboardButton(
            text="Суббота",
            callback_data=DaysOfWeek.SATURDAY.value,
        ),
    ).row(
        InlineKeyboardButton(text="Завершить выбор", callback_data="Stop"),
    )
    return keyboard

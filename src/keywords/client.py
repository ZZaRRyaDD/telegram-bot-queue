import enum

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class UserActionEnum(enum.Enum):
    """Class choices of user actions."""

    UPDATE = ("Update", "Редактирование профиля")
    DELETE = ("Delete", "Удаление профиля")

    def __init__(self, action: str, description: str) -> None:
        self.action = action
        self.description = description


def user_actions() -> InlineKeyboardMarkup:
    """Create keys for update/delete user."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.row(
        InlineKeyboardButton(
            text=UserActionEnum.UPDATE.description,
            callback_data=UserActionEnum.UPDATE.action,
        ),
    ).row(
        InlineKeyboardButton(
            text=UserActionEnum.DELETE.description,
            callback_data=UserActionEnum.DELETE.action,
        ),
    )
    return keyboard


def get_list_keys(collection: list) -> InlineKeyboardMarkup:
    """Create keys for select something."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    buttons = []
    if len(collection) >= 2:
        buttons = [
            [collection[i], collection[i+1]]
            for i in range(0, len(collection)-1, 2)
        ]
        if len(buttons) * 2 < len(collection):
            buttons += [collection[len(buttons)*2:]]
    else:
        buttons += [[*collection]]
    for row in buttons:
        if len(row) == 2:
            keyboard.row(
                InlineKeyboardButton(
                    text=row[0].name,
                    callback_data=row[0].id,
                ),
                InlineKeyboardButton(
                    text=row[1].name,
                    callback_data=row[1].id,
                ),
            )
        else:
            keyboard.row(
                InlineKeyboardButton(
                    text=row[0].name,
                    callback_data=row[0].id,
                ),
            )
    return keyboard


def get_list_of_groups(groups: list) -> InlineKeyboardMarkup:
    """Create keys for select groups."""
    return get_list_keys(groups)


def get_list_of_subjects(subjects: list) -> InlineKeyboardMarkup:
    """Create keys for select subjects."""
    return get_list_keys(subjects)


def get_list_of_numbers(numbers: list) -> InlineKeyboardMarkup:
    """Create keys for select number of lab of subject."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    buttons = []
    if len(numbers) >= 2:
        buttons = [
            [numbers[i], numbers[i+1]]
            for i in range(0, len(numbers)-1, 2)
        ]
        if len(buttons) * 2 < len(numbers):
            buttons += [numbers[len(buttons)*2:]]
    else:
        buttons += [[*numbers]]
    for row in buttons:
        if len(row) == 2:
            keyboard.row(
                InlineKeyboardButton(
                    text=row[0],
                    callback_data=row[0],
                ),
                InlineKeyboardButton(
                    text=row[1],
                    callback_data=row[1],
                ),
            )
        else:
            keyboard.row(
                InlineKeyboardButton(
                    text=row[0],
                    callback_data=row[0],
                ),
            )
    keyboard.row(
        InlineKeyboardButton(
            text="Остановить выбор",
            callback_data="Stop",
        ),
    )
    return keyboard

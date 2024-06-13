from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.enums import OtherCommands, UserRepositoryEnum


def user_actions() -> InlineKeyboardMarkup:
    """Create keys for update/delete user."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.row(
        InlineKeyboardButton(
            text=UserRepositoryEnum.UPDATE.description,
            callback_data=UserRepositoryEnum.UPDATE.action,
        ),
    ).row(
        InlineKeyboardButton(
            text=UserRepositoryEnum.DELETE.description,
            callback_data=UserRepositoryEnum.DELETE.action,
        ),
    ).row(
        InlineKeyboardButton(
            text=UserRepositoryEnum.CANCEL.description,
            callback_data=UserRepositoryEnum.CANCEL.action,
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


def get_keyboard_with_cancel(collection: list) -> InlineKeyboardMarkup:
    """Button for add `cancel` button in keyboard."""
    keyboard = get_list_keys(collection)
    keyboard.row(
        InlineKeyboardButton(
            text=OtherCommands.CANCEL.description,
            callback_data=OtherCommands.CANCEL.command,
        ),
    )
    return keyboard


def get_list_of_groups(groups: list) -> InlineKeyboardMarkup:
    """Create keys for select groups."""
    return get_keyboard_with_cancel(groups)


def get_list_of_subjects(subjects: list) -> InlineKeyboardMarkup:
    """Create keys for select subjects."""
    return get_keyboard_with_cancel(subjects)


def get_list_of_numbers(numbers: list) -> InlineKeyboardMarkup:
    """Create keys for select number of lab of subject."""
    return get_keyboard_with_cancel(numbers)

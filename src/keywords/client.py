from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_list_keys(collection) -> InlineKeyboardMarkup:
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


def get_list_of_groups(groups) -> InlineKeyboardMarkup:
    """Create keys for select groups."""
    return get_list_keys(groups)


def get_list_of_subjects(subjects) -> InlineKeyboardMarkup:
    """Create keys for select subjects."""
    return get_list_keys(subjects)


def get_list_of_numbers(numbers) -> InlineKeyboardMarkup:
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
    return keyboard

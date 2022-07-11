from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_list_of_groups(groups):
    """Create keys for select groups."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    buttons = []
    if len(groups) < 2:
        buttons = [
            [groups[i], groups[i+1]] for i in range(0, len(groups)-1, 2)
        ]
        if len(buttons) * 2 < len(groups):
            buttons += [groups[len(buttons)*2:]]
    else:
        buttons += [[*groups]]
    for row in buttons:
        if len(row) == 2:
            keyboard.row(
                InlineKeyboardButton(
                    text=row[0].name,
                    callback_data=row[0].id,
                ),
                InlineKeyboardButton(
                    text=row[1].name,
                    callback_data=row[0].id,
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


def get_list_of_subjects(subjects):
    """Create keys for select subjects."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    buttons = []
    if len(subjects) < 2:
        buttons = [
            [subjects[i], subjects[i+1]] for i in range(0, len(subjects)-1, 2)
        ]
        if len(buttons) * 2 < len(subjects):
            buttons += [subjects[len(buttons)*2:]]
    else:
        buttons += [[*subjects]]
    for row in buttons:
        if len(row) == 2:
            keyboard.row(
                InlineKeyboardButton(
                    text=row[0].name,
                    callback_data=row[0].id,
                ),
                InlineKeyboardButton(
                    text=row[1].name,
                    callback_data=row[0].id,
                ),
            )
        else:
            keyboard.row(
                InlineKeyboardButton(
                    text=row[0].name,
                    callback_data=row[0].id,
                ),
            )
    keyboard.row(
        InlineKeyboardButton(
            text="Остановить выбор",
            callback_data="Stop",
        ),
    )
    return keyboard

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from enums import OtherCommands


def select_cancel() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup()
    keyboard.add(
        KeyboardButton(OtherCommands.CANCEL.command.capitalize())
    )
    return keyboard.as_markup(resize_keyboard=True)

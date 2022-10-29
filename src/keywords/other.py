from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from enums import OtherCommands


def select_cancel() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    keyboard.add(KeyboardButton(OtherCommands.CANCEL.command))
    return keyboard

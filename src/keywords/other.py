from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def select_cancel() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Cancel'))
    return keyboard

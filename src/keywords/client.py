from enum import Enum

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


class Choices(Enum):
    """Button names."""

    INFO_PROFILE = "Информация о профиле"
    CHANGE_PROFILE = "Изменение информации о профиле"
    CHOICE_GROUP = "Изменить группу"
    STAY_QUEUE = "Встать в очередь"


def create_buttons() -> ReplyKeyboardMarkup:
    """Create buttons for."""
    info_profile_btn: KeyboardButton = KeyboardButton(Choices.INFO_PROFILE)
    change_profile_btn: KeyboardButton = KeyboardButton(Choices.CHANGE_PROFILE)
    choice_group_btn: KeyboardButton = KeyboardButton(Choices.CHOICE_GROUP)
    stay_in_queue_btn: KeyboardButton = KeyboardButton(Choices.STAY_QUEUE)

    buttons_client: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    buttons_client.row(
        choice_group_btn,
        stay_in_queue_btn,
    ).row(info_profile_btn, change_profile_btn)
    return buttons_client

from enum import Enum

from aiogram import Dispatcher, types

from database import UserActions
from database.repository import GroupActions
from services import check_user
from state import register_handlers_change_account


class Choices(Enum):
    """Button names."""

    START_UP = "Создание аккаунт"
    INFO_PROFILE = "Информация о профиле"
    CHANGE_PROFILE = "Изменение информации о профиле"
    CHOICE_GROUP = "Изменить группу"
    STAY_QUEUE = "Встать в очередь"


async def set_commands_client(dispatcher: Dispatcher):
    """Set commands for client actions."""
    await dispatcher.bot.set_my_commands([
        types.BotCommand("start", Choices.START_UP.value),
        types.BotCommand("info", Choices.INFO_PROFILE.value),
        types.BotCommand("change_profile", Choices.CHANGE_PROFILE.value),
        types.BotCommand("choice_group", Choices.CHOICE_GROUP.value),
        types.BotCommand("stay_queue", Choices.STAY_QUEUE.value),
    ])


def print_info(id: int) -> str:
    """Return info about user."""
    info = ""
    user = UserActions.get_user(id)
    info += f"ID: {user.id}\n"
    info += f"Фамилия Имя: {user.full_name}\n"
    info += f"Email: {user.email}\n"
    if user.is_headman:
        group = (
            GroupActions.get_group(user.group).name
            if user.group is not None
            else ""
        )
        info += f"Вы являетесь старостой {group}\n"
    return info


async def start_command(message: types.Message) -> None:
    """Handler for start command."""
    if not check_user(message.from_user.id):
        await message.answer(
            "Смотрю ты еще не с нами. Давай это исправим!",
        )
        full_name = (
            f"{message.from_user.first_name} {message.from_user.last_name}"
        )
        new_user = {
            "id": message.from_user.id,
            "full_name": full_name,
            "email": "",
        }
        UserActions.create_user(new_user)
    await message.answer(
        "Хай",
    )


async def info_user(message: types.Message) -> None:
    """Print info about user."""
    await message.answer(
        print_info(message.from_user.id),
    )


def register_handlers_client(dispatcher: Dispatcher) -> None:
    """Register handler for different types commands of user."""
    dispatcher.register_message_handler(start_command, commands=["start"])
    dispatcher.register_message_handler(
        info_user,
        lambda message: check_user(message.from_user.id),
        commands=["info"],
    )
    register_handlers_change_account(dispatcher)

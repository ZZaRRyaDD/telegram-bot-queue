import os
from enum import Enum

from aiogram import Dispatcher, types

from database import GroupActions, UserActions
from services import check_user
from state import (register_handlers_change_account,
                   register_handlers_delete_account,
                   register_handlers_select_group,
                   register_handlers_stay_queue)

HELLO_TEXT = """
Хай
Этот бот поможет тебе безболезненно встать в очередь на предмет и сдать лабу.
От бота приходит четыре уведомления:
- в 12:00, 17:00, 21:00 напоминание о записи на сдачу лабы;
- в 22:00 итоги рандома (полный список и твоя позиция)
Твои возможности:
Как студента:
- войти в группу;
- записаться/отписаться на сдачу предмета
- удалить аккаунт
- редактировать аккаунт
Как старосты:
- CRUD операции с группой, предметами (кроме обновления);
- записаться/отписаться на сдачу предмета
По дефолту вы студент.
Чтобы стать старостой, напишите админу. Его контактики найдете в меню
"""


class Choices(Enum):
    """Button names."""

    START_UP = "Создание аккаунта"
    INFO_PROFILE = "Информация о профиле"
    CHANGE_PROFILE = "Изменение информации о профиле"
    CHOICE_GROUP = "Изменить группу"
    STAY_QUEUE = "Встать/уйти из очереди"
    TO_ADMIN = "Написать админу"
    DELETE_ACCOUNT = "Удалить аккаунт"
    INFO_PREACTICE = "Информация о сданных лабораторных работах"


async def set_commands_client(dispatcher: Dispatcher):
    """Set commands for client actions."""
    await dispatcher.bot.set_my_commands([
        types.BotCommand("start", Choices.START_UP.value),
        types.BotCommand("info", Choices.INFO_PROFILE.value),
        types.BotCommand("change_profile", Choices.CHANGE_PROFILE.value),
        types.BotCommand("select_group", Choices.CHOICE_GROUP.value),
        types.BotCommand("stay_queue", Choices.STAY_QUEUE.value),
        types.BotCommand("to_admin", Choices.TO_ADMIN.value),
        types.BotCommand("delete_account", Choices.DELETE_ACCOUNT.value),
        types.BotCommand("info_practice", Choices.INFO_PREACTICE.value),
    ])


def print_info(id: int) -> str:
    """Return info about user."""
    info = ""
    user = UserActions.get_user(id, subjects=False)
    info += f"ID: {user.id}\n"
    info += f"Фамилия Имя: {user.full_name}\n"
    group = (
        GroupActions.get_group(user.group).name
        if user.group is not None
        else ""
    )
    status = 'старостой' if user.is_headman else 'студентом'
    info += f"Вы являетесь {status} {group}\n"
    return info


async def start_command(message: types.Message) -> None:
    """Handler for start command."""
    if not UserActions.get_user(message.from_user.id):
        await message.answer(
            "Смотрю, ты еще не с нами. Давай это исправим!",
        )
        full_name = (
            f"{message.from_user.first_name} {message.from_user.last_name}"
        )
        new_user = {
            "id": message.from_user.id,
            "full_name": full_name,
        }
        UserActions.create_user(new_user)
    await message.answer(
        HELLO_TEXT,
    )


async def info_user(message: types.Message) -> None:
    """Print info about user."""
    await message.answer(
        print_info(message.from_user.id),
    )


async def to_admin(message: types.Message) -> None:
    """Print info about user."""
    await message.answer(
        f"Контакты господина: {os.getenv('ADMIN_URL')}",
    )


async def pass_info_practice(message: types.Message) -> None:
    await message.answer("Находится в разработке")


def register_handlers_client(dispatcher: Dispatcher) -> None:
    """Register handler for different types commands of user."""
    dispatcher.register_message_handler(
        start_command,
        commands=["start"],
    )
    register_handlers_change_account(dispatcher)
    register_handlers_select_group(dispatcher)
    register_handlers_stay_queue(dispatcher)
    register_handlers_delete_account(dispatcher)
    dispatcher.register_message_handler(
        info_user,
        lambda message: check_user(message.from_user.id),
        commands=["info"],
    )
    dispatcher.register_message_handler(
        to_admin,
        lambda message: check_user(message.from_user.id),
        commands=["to_admin"],
    )
    dispatcher.register_message_handler(
        pass_info_practice,
        commands=["info_practice"]
    )

from aiogram import Dispatcher, types

from database import GroupActions
from database.repository import UserActions
from services import check_admin, check_headman_of_group, is_headman
from state import (register_handlers_delete_group,
                   register_handlers_delete_subject, register_handlers_group,
                   register_handlers_set_headman, register_handlers_subject)


async def print_commands(message: types.Message) -> None:
    """Print commands of headman and admin."""
    admin_commands = {
        "/set_headman": "Добавление/удаление старосты\n"
    }
    headman_commands = {
        "/group_info": "Информация о группе\n",
        "/create_group": "Создание группы\n",
        "/edit_group": "Редактирование группы\n",
        "/delete_group": "Удаление группы\n",
        "/add_subject": "Добавление предмета\n",
        "/delete_subject": "Удаление предмета\n",
    }
    list_commands_headman = [
        f"{key}: {value}"
        for key, value in headman_commands.items()
    ]
    list_commands_admin = [
        f"{key}: {value}"
        for key, value in admin_commands.items()
    ]
    list_commands = (
        list_commands_admin + list_commands_headman
        if check_admin(message.from_user.id)
        else list_commands_headman
    )
    await message.answer(
        "".join(list_commands)
    )


def print_info(id: int) -> str:
    """Return info about user."""
    info = ""
    group = GroupActions.get_group_with_subjects(
        UserActions.get_user(id).group
    )
    info += f"ID: {group.id}\n"
    info += f"Название: {group.name}\n"
    for subject in group.subjects:
        days = ' '.join([str(day.number) for day in subject.days])
        info += f"{subject.name}: {days}\n"
    return info


async def print_group_info(message: types.Message):
    """Print group info."""
    await message.answer(
        print_info(message.from_user.id)
    )


def register_handlers_admin(dispatcher: Dispatcher) -> None:
    """Register handler for different types commands of admin."""
    register_handlers_set_headman(dispatcher)
    register_handlers_group(dispatcher)
    register_handlers_delete_group(dispatcher)
    register_handlers_subject(dispatcher)
    register_handlers_delete_subject(dispatcher)
    dispatcher.register_message_handler(
        print_commands,
        lambda message: any([
            check_admin(message.from_user.id),
            is_headman(message.from_user.id),
        ]),
        commands=["commands"],
    )
    dispatcher.register_message_handler(
        print_group_info,
        lambda message: check_headman_of_group(message.from_user.id),
        commands=["group_info"]
    )

from aiogram import Dispatcher, types

from services import check_admin, is_headman
from state import (register_handlers_delete_group, register_handlers_group,
                   register_handlers_set_headman)


async def print_commands(message: types.Message) -> None:
    """Print commands of headman and admin."""
    admin_commands = {
        "set_headman": "Добавление/удаление старосты\n"
    }
    headman_commands = {
        "delete_group": "Удаление группы\n",
        "create_group": "Создание группы\n",
        "edit_group": "Редактирование группы\n",
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


def register_handlers_admin(dispatcher: Dispatcher) -> None:
    """Register handler for different types commands of admin."""
    register_handlers_set_headman(dispatcher)
    register_handlers_group(dispatcher)
    register_handlers_delete_group(dispatcher)
    dispatcher.register_message_handler(
        print_commands,
        lambda message: any([
            check_admin(message.from_user.id),
            is_headman(message.from_user.id),
        ]),
        commands=["commands"],
    )

from aiogram import Dispatcher, types

from database import GroupActions, UserActions
from enums import AdminCommands, HeadmanCommands
from services import (
    check_admin,
    check_headman_of_group,
    get_all_info,
    get_info_group,
    is_headman,
)
from state import (
    register_handlers_group,
    register_handlers_message,
    register_handlers_set_headman,
    register_handlers_subject,
)


async def print_commands(message: types.Message) -> None:
    """Print commands of headman and admin."""
    list_commands_headman = [
        f"/{command.command}: {command.description}"
        for command in HeadmanCommands
    ]
    list_commands_admin = [
        f"/{command.command}: {command.description}"
        for command in AdminCommands
    ]
    list_commands = (
        list_commands_admin + list_commands_headman
        if check_admin(message.from_user.id)
        else list_commands_headman
    )
    await message.answer(
        "".join(list_commands)
    )


async def print_group_info(message: types.Message) -> None:
    """Print group info."""
    await message.answer(
        get_info_group(
            GroupActions.get_group(
                UserActions.get_user(message.from_user.id).group,
                subjects=True,
                students=True,
            ),
        )
    )


async def print_all_info(message: types.Message) -> None:
    """Print all info."""
    await message.answer(get_all_info())


async def download_json_data(message: types.Message) -> None:
    """Download data from db in JSON."""


async def upload_json_data(message: types.Message) -> None:
    """Upload data in db from JSON."""


def register_handlers_admin(dispatcher: Dispatcher) -> None:
    """Register handler for different types commands of admin."""
    register_handlers_message(dispatcher)
    register_handlers_set_headman(dispatcher)
    register_handlers_group(dispatcher)
    register_handlers_subject(dispatcher)
    dispatcher.register_message_handler(
        print_commands,
        lambda message: any([
            check_admin(message.from_user.id),
            is_headman(message.from_user.id),
        ]),
        commands=[AdminCommands.COMMANDS.command],
    )
    dispatcher.register_message_handler(
        print_group_info,
        lambda message: check_headman_of_group(message.from_user.id),
        commands=[HeadmanCommands.INFO_GROUP.command]
    )
    dispatcher.register_message_handler(
        print_all_info,
        lambda message: check_admin(message.from_user.id),
        commands=[AdminCommands.ALL_INFO.command]
    )
    dispatcher.register_message_handler(
        download_json_data,
        lambda message: check_admin(message.from_user.id),
        commands=[AdminCommands.DOWNLOAD_DATA.command]
    )
    dispatcher.register_message_handler(
        upload_json_data,
        lambda message: check_admin(message.from_user.id),
        commands=[AdminCommands.UPLOAD_DATA.command]
    )

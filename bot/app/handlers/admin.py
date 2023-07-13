from aiogram import Dispatcher, types

from app.database import GroupActions
from app.enums import AdminCommands, HeadmanCommands
from app.services import (
    check_admin,
    check_headman_of_group,
    get_all_info,
    get_info_group,
    is_headman,
)
from app.state import (
    register_handlers_event,
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
            GroupActions.get_group_by_user_id(
                message.from_user.id,
                subjects=True,
                students=True,
            ),
        )
    )


async def print_all_info(message: types.Message) -> None:
    """Print all info."""
    await message.answer(get_all_info())


def register_handlers_admin(dispatcher: Dispatcher) -> None:
    """Register handler for different types commands of admin."""
    register_handlers_message(dispatcher)
    register_handlers_set_headman(dispatcher)
    register_handlers_group(dispatcher)
    register_handlers_subject(dispatcher)
    register_handlers_event(dispatcher)
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
        commands=[HeadmanCommands.INFO_GROUP.command],
    )
    dispatcher.register_message_handler(
        print_all_info,
        lambda message: check_admin(message.from_user.id),
        commands=[AdminCommands.ALL_INFO.command],
    )

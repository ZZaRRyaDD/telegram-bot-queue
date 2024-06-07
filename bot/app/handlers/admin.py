from aiogram import Dispatcher, types

from app.database.repositories import GroupActions
from app.enums import AdminCommands, HeadmanCommands
from app.filters import HasUser, IsAdmin, IsHeadman, IsMemberOfGroup
from app.services import check_admin, get_all_info, get_info_group
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
        if await check_admin(message.from_user.id)
        else list_commands_headman
    )
    await message.answer(
        "".join(list_commands)
    )


async def print_group_info(message: types.Message) -> None:
    """Print group info."""
    await message.answer(
        await get_info_group(
            await GroupActions.get_group_by_user_id(
                message.from_user.id,
                subjects=True,
                students=True,
            ),
        )
    )


async def print_all_info(message: types.Message) -> None:
    """Print all info."""
    await message.answer(await get_all_info())


def register_handlers_admin(dispatcher: Dispatcher) -> None:
    """Register handler for different types commands of admin."""
    register_handlers_message(dispatcher)
    register_handlers_set_headman(dispatcher)
    register_handlers_group(dispatcher)
    register_handlers_subject(dispatcher)
    register_handlers_event(dispatcher)
    dispatcher.register_message_handler(
        print_commands,
        IsAdmin() | (HasUser() & IsHeadman() & IsMemberOfGroup()),
        commands=[AdminCommands.COMMANDS.command],
    )
    dispatcher.register_message_handler(
        print_group_info,
        HasUser(),
        IsHeadman(),
        IsMemberOfGroup(),
        commands=[HeadmanCommands.INFO_GROUP.command],
    )
    dispatcher.register_message_handler(
        print_all_info,
        IsAdmin(),
        commands=[AdminCommands.ALL_INFO.command],
    )

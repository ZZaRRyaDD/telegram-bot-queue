from aiogram import Dispatcher, types

from database import GroupActions, UserActions, models
from services import check_admin, check_headman_of_group, is_headman
from state import (register_handlers_delete_group,
                   register_handlers_delete_subject, register_handlers_group,
                   register_handlers_set_headman, register_handlers_subject)


async def print_commands(message: types.Message) -> None:
    """Print commands of headman and admin."""
    admin_commands = {
        "/set_headman": "Добавление/удаление старосты\n",
        "/all_info": "Вывод всей информации о всех группах\n",
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


def get_info_group(group: models.Group) -> str:
    """Return info about user."""
    info = ""
    info += f"ID: {group.id}\n"
    info += f"Название: {group.name}\n"
    for subject in group.subjects:
        days = ' '.join([str(day.number) for day in subject.days])
        name, can_select = subject.name, subject.can_select
        info += f"\t\t{name}; days: {days}; can_select: {can_select}\n"
    info += "Состав группы:\n"
    info += "".join(
        [
            f"\t\t{index + 1}. {user.full_name}\n"
            for index, user in enumerate(group.students)
        ]
    )
    return info


def get_all_info():
    """Get info about groups, subjects."""
    info = ""
    groups = GroupActions.get_groups(subjects=True, students=True)
    if groups:
        for group in groups:
            info += f"{get_info_group(group)}\n"
        return info
    return "Ничего нет"


async def print_group_info(message: types.Message):
    """Print group info."""
    await message.answer(
        get_info_group(
            GroupActions.get_group(
                UserActions.get_user(
                    message.from_user.id,
                    subjects=False,
                ).group,
                subjects=True,
                students=True,
            )
        )
    )


async def print_all_info(message: types.Message):
    """Print all info."""
    await message.answer(
        get_all_info()
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
    dispatcher.register_message_handler(
        print_all_info,
        lambda message: check_admin(message.from_user.id),
        commands=["all_info"]
    )

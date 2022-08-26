import os

import emoji
from aiogram import Dispatcher, types

from database import (
    CompletedPracticesActions,
    GroupActions,
    SubjectActions,
    UserActions,
)
from services import check_user, print_info
from state import (
    register_handlers_change_account,
    register_handlers_select_group,
    register_handlers_stay_queue,
)

from .commands import ClientCommands

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


async def set_commands_client(dispatcher: Dispatcher) -> None:
    """Set commands for client actions."""
    await dispatcher.bot.set_my_commands([
        types.BotCommand(
            ClientCommands.START.command,
            ClientCommands.START.description,
        ),
        types.BotCommand(
            ClientCommands.INFO_PROFILE.command,
            ClientCommands.INFO_PROFILE.description,
        ),
        types.BotCommand(
            ClientCommands.EDIT_PROFILE.command,
            ClientCommands.EDIT_PROFILE.description,
        ),
        types.BotCommand(
            ClientCommands.CHOICE_GROUP.command,
            ClientCommands.CHOICE_GROUP.description,
        ),
        types.BotCommand(
            ClientCommands.STAY_QUEUE.command,
            ClientCommands.STAY_QUEUE.description,
        ),
        types.BotCommand(
            ClientCommands.TO_ADMIN.command,
            ClientCommands.TO_ADMIN.description,
        ),
        types.BotCommand(
            ClientCommands.PASS_PRACTICES.command,
            ClientCommands.PASS_PRACTICES.description,
        ),
    ])


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
    await message.answer(print_info(message.from_user.id))


async def to_admin(message: types.Message) -> None:
    """Print info about user."""
    await message.answer(f"Контакты господина: {os.getenv('ADMIN_URL')}")


async def info_practice(message: types.Message) -> None:
    """Get info about practices."""
    pass_practices = set(
        practice.subject_id
        for practice in CompletedPracticesActions.get_completed_practices_info(
            message.from_user.id,
        )
    )
    all_subjects = set(map(lambda x: x.id, GroupActions.get_group(
            id=UserActions(message.from_user.id).group,
            subjects=True,
        ).subjects,
    ))
    status_subjects = {}
    for subject_id in all_subjects:
        subject = SubjectActions.get_subject(id=subject_id)
        if subject_id in pass_practices:
            completed = map(lambda x: x.number, filter(
                lambda x: x.subject_id == subject_id,
                pass_practices,
            ))
            status_subjects[subject.id] = []
            for number in range(1, subject.count + 1):
                status_subjects[subject.name][number] = [
                    int(number in completed)
                ]
        else:
            status_subjects[subject.name] = [0*subject.count]
        info = ""
        for subject, practices in status_subjects.items():
            info += f"{subject}:\n"
            if any(practices):
                for index, status in enumerate(practices, start=1):
                    emojie_type = (
                        emoji.emojize(':white_check_mark:')
                        if status
                        else emoji.emojize(':x:')
                    )
                    info += f"\t\t{emojie_type} {index}\n"
            else:
                info += "\t\tНе сдано ни одной лабы"
        await message.answer(info)


def register_handlers_client(dispatcher: Dispatcher) -> None:
    """Register handler for different types commands of user."""
    dispatcher.register_message_handler(
        start_command,
        commands=[ClientCommands.START.command],
    )
    register_handlers_change_account(dispatcher)
    register_handlers_select_group(dispatcher)
    register_handlers_stay_queue(dispatcher)
    dispatcher.register_message_handler(
        info_user,
        lambda message: check_user(message.from_user.id),
        commands=[ClientCommands.INFO_PROFILE.command],
    )
    dispatcher.register_message_handler(
        to_admin,
        lambda message: check_user(message.from_user.id),
        commands=[ClientCommands.TO_ADMIN.command],
    )
    dispatcher.register_message_handler(
        info_practice,
        commands=[ClientCommands.PASS_PRACTICES.command]
    )

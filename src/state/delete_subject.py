from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import (DateActions, GroupActions, QueueActions, SubjectActions,
                      UserActions)
from services import check_count_subject_group, check_headman_of_group


class DeleteSubject(StatesGroup):
    """FSM for delete group."""

    name = State()


def get_list_subjects(id: int) -> str:
    subjects = GroupActions.get_group(
        UserActions.get_user(id, subjects=False).group,
        subjects=True,
    ).subjects
    return "".join([
        f"{index + 1}. {subject.name}\n"
        for index, subject in enumerate(subjects)
    ])


async def start_subject(message: types.Message) -> None:
    """Entrypoint for subject."""
    await message.answer(
        get_list_subjects(message.from_user.id)
    )
    await DeleteSubject.name.set()
    await message.answer("Введите название дисциплины, либо 'cancel'")


async def input_name_subject(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Input name of subject."""
    group = GroupActions.get_group(
        UserActions.get_user(message.from_user.id, subjects=False).group,
        subjects=True,
    )
    subject = list(filter(lambda x: x.name == message.text, group.subjects))
    if subject:
        QueueActions.cleaning_subject(subject[0].id)
        DateActions.delete_date_by_subject(subject[0].id)
        SubjectActions.delete_subject(subject[0].id)
        await message.answer(
            "Предмет успешно удален"
        )
        await state.finish()
    else:
        await message.answer(
            (
                "Предмета с таким названием не найдено. "
                "Введите название заново, либо 'cancel'"
            )
        )


def register_handlers_delete_subject(dispatcher: Dispatcher) -> None:
    """Register handlers for delete subject."""
    dispatcher.register_message_handler(
        start_subject,
        lambda message: all([
            check_headman_of_group(message.from_user.id),
            check_count_subject_group(message.from_user.id),
        ]),
        commands=["delete_subject"],
        state=None,
    )
    dispatcher.register_message_handler(
        input_name_subject,
        state=DeleteSubject.name,
    )

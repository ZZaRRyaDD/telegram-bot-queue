from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import (
    CompletedPracticesActions,
    GroupActions,
    QueueActions,
    SubjectActions,
    ScheduleActions,
)
from services import check_headman_of_group, polynomial_hash


class DeleteGroup(StatesGroup):
    """FSM for delete group."""

    name = State()
    secret_word = State()


async def start_delete_group(message: types.Message) -> None:
    """Entrypoint for group."""
    await DeleteGroup.name.set()
    await message.answer("Введите название группы, либо 'cancel'")


async def input_name_group(message: types.Message, state: FSMContext) -> None:
    """Input name of group."""
    if GroupActions.get_group(message.text):
        async with state.proxy() as data:
            data["name"] = message.text
        await DeleteGroup.next()
        await message.answer(
            "Введите секретное слово для входа в группу, либо 'cancel'"
        )
    else:
        await message.answer(
            "Группы с таким названием нет. Введите название, либо 'cancel'"
        )


async def input_secret_word(message: types.Message, state: FSMContext) -> None:
    """Input secret word."""
    new_group = {}
    async with state.proxy() as data:
        new_group = {
            "secret_word": polynomial_hash(message.text),
            "name": data["name"],
        }
    group = GroupActions.get_group(new_group["name"], subjects=True)
    if int(group.secret_word) == int(new_group["secret_word"]):
        for subject in group.subjects:
            QueueActions.cleaning_subject(subject[0].id)
            CompletedPracticesActions.cleaning_subject(subject[0].id)
            ScheduleActions.delete_schedule_by_subject(subject[0].id)
            SubjectActions.delete_subject(subject[0].id)
        GroupActions.delete_group(group.id)
        await message.answer(f"Группа {new_group['name']} успешно удалена")
        await state.finish()
    else:
        await message.answer(
            "Ошибка удаления группы. Введите слово, либо 'cancel'"
        )


def register_handlers_delete_group(dispatcher: Dispatcher) -> None:
    """Register handlers for group."""
    dispatcher.register_message_handler(
        start_delete_group,
        lambda message: check_headman_of_group(message.from_user.id),
        commands=["delete_group"],
        state=None,
    )
    dispatcher.register_message_handler(
        input_name_group,
        lambda message: check_headman_of_group(message.from_user.id),
        state=DeleteGroup.name,
    )
    dispatcher.register_message_handler(
        input_secret_word,
        lambda message: check_headman_of_group(message.from_user.id),
        state=DeleteGroup.secret_word,
    )

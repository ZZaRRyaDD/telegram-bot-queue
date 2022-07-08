from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database.repository import GroupActions
from services import check_headman_of_group, polynomial_hash


class DeleteGroup(StatesGroup):
    """FSM for create and edit group."""

    name = State()
    secret_word = State()


async def start_delete_group(message: types.Message) -> None:
    """Entrypoint for group."""
    await DeleteGroup.name.set()
    await message.answer("Введите название группы")


async def input_name_group(message: types.Message, state: FSMContext) -> None:
    """Input name of group."""
    async with state.proxy() as data:
        data["name"] = message.text
    await DeleteGroup.next()
    await message.answer("Введите секретное слово для входа в группу")


async def input_secret_word(message: types.Message, state: FSMContext) -> None:
    """Input secret word."""
    async with state.proxy() as data:
        data["secret_word"] = polynomial_hash(message.text)
    group = GroupActions.get_group_by_name(data["name"])
    if int(group.secret_word) == int(data["secret_word"]):
        GroupActions.delete_group(group.id)
        await message.answer(f"Группа {data['name']} успешно удалена")
    else:
        await message.answer("Ошибка удаления группы")
    await state.finish()


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

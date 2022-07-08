from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import GroupActions, UserActions
from services import (check_empty_headman, check_headman_of_group,
                      polynomial_hash)


class Group(StatesGroup):
    """FSM for create and edit group."""

    name = State()
    secret_word = State()


async def start_group(message: types.Message) -> None:
    """Entrypoint for group."""
    await Group.name.set()
    await message.answer("Введите название группы")


async def input_name_group(message: types.Message, state: FSMContext) -> None:
    """Input name of group."""
    group = GroupActions.get_group_by_name(message.text)
    name = (
        all([
            UserActions.get_user(message.from_user.id).is_headman,
            UserActions.get_user(message.from_user.id).group == group.id,
        ])
        if group is not None
        else True
    )
    if name:
        async with state.proxy() as data:
            data["name"] = message.text
        await Group.next()
        await message.answer("Введите секретное слово для входа в группу")
    else:
        await message.answer("Группа с таким названием уже есть")


async def input_secret_word(message: types.Message, state: FSMContext) -> None:
    """Input secret word."""
    async with state.proxy() as data:
        data["secret_word"] = polynomial_hash(message.text)
    new_group = {
        "name": data["name"],
        "secret_word": data["secret_word"],
    }
    group = GroupActions.get_group_by_name(data["name"])
    status = 'создана' if group is None else 'обновлена'
    if group is not None:
        GroupActions.edit_group(group.id, new_group)
    else:
        group = GroupActions.create_group(new_group)
        UserActions.edit_user(message.from_user.id, {"group": group.id})
    await message.answer(f"Группа {new_group['name']} успешно {status}")
    await state.finish()


def register_handlers_group(dispatcher: Dispatcher) -> None:
    """Register handlers for group."""
    dispatcher.register_message_handler(
        start_group,
        lambda message: check_empty_headman(message.from_user.id),
        commands=["create_group"],
        state=None,
    )
    dispatcher.register_message_handler(
        start_group,
        lambda message: check_headman_of_group(message.from_user.id),
        commands=["edit_group"],
        state=None,
    )
    dispatcher.register_message_handler(
        input_name_group,
        state=Group.name,
    )
    dispatcher.register_message_handler(
        input_secret_word,
        state=Group.secret_word,
    )

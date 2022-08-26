from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import GroupActions, UserActions
from handlers import HeadmanCommands
from keywords import GroupActionsEnum, group_action
from services import (
    check_empty_headman,
    check_headman_of_group,
    polynomial_hash,
)


class Group(StatesGroup):
    """FSM for create and edit group."""

    action = State()
    name = State()
    secret_word = State()


async def start_group(message: types.Message) -> None:
    """Entrypoint for group."""
    await Group.action.set()
    await message.answer(
        "Выберите действие, либо введите 'cancel'",
        reply_markup=group_action(),
    )


async def input_action_group(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input action for group."""
    async with state.proxy() as data:
        data["action"] = callback.data
    await Group.name.set()
    await callback.message.answer(
        "Введите название группы, либо введите 'cancel'",
    )


async def input_name_group(message: types.Message, state: FSMContext) -> None:
    """Input name of group."""
    group = GroupActions.get_group(message.text)
    user = UserActions.get_user(message.from_user.id, subjects=False)
    name = (
        all([user.is_headman, user.group == group.id])
        if group is not None
        else True
    )
    if message.text and name:
        async with state.proxy() as data:
            data["name"] = message.text
        await Group.next()
        await message.answer(
            (
                "Введите секретное слово для входа в группу, "
                "либо введите 'cancel'"
            ),
        )
    else:
        await message.answer(
            (
                "Группа с таким названием уже есть, "
                "либо название не корректно.\n"
                "Введите другое название, либо введите 'cancel'."
            ),
        )


async def input_secret_word(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Input secret word."""
    action = ""
    async with state.proxy() as data:
        action = data["action"]
        new_group = {
            "name": data["name"],
            "secret_word": polynomial_hash(message.text),
        }
    group_id = UserActions.get_user(
        message.from_user.id,
        subjects=False,
    ).group
    status = (
        "создана"
        if group_id is None else "обновлена"
        if action == GroupActionsEnum.UPDATE.action else "удалена"
    )
    match action:
        case GroupActionsEnum.CREATE.action:
            GroupActions.edit_group(group_id, new_group)
        case GroupActionsEnum.UPDATE.action:
            group = GroupActions.create_group(new_group)
            UserActions.edit_user(message.from_user.id, {"group": group.id})
        case GroupActionsEnum.DELETE.action:
            GroupActions.delete_group(group_id)
    await message.answer(f"Группа {new_group['name']} успешно {status}")
    await state.finish()


def register_handlers_group(dispatcher: Dispatcher) -> None:
    """Register handlers for group."""
    dispatcher.register_message_handler(
        start_group,
        lambda message: (
            check_empty_headman(message.from_user.id) |
            check_headman_of_group(message.from_user.id)
        ),
        commands=[HeadmanCommands.EDIT_GROUP.command],
        state=None,
    )
    dispatcher.register_callback_query_handler(
        input_action_group,
        state=Group.action,
    )
    dispatcher.register_message_handler(
        input_name_group,
        state=Group.name,
    )
    dispatcher.register_message_handler(
        input_secret_word,
        state=Group.secret_word,
    )

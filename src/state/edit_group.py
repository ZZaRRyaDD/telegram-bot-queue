from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import GroupActions, UserActions
from enums import HeadmanCommands
from keywords import GroupActionsEnum, group_action, select_cancel
from services import (
    check_empty_headman,
    check_headman_of_group,
    get_info_group,
    polynomial_hash,
)


class Group(StatesGroup):
    """FSM for CRUD operrations with group."""

    action = State()
    name = State()
    secret_word = State()


async def start_group(message: types.Message) -> None:
    """Entrypoint for group."""
    group = UserActions.get_user(message.from_user.id).group
    if group is not None:
        await message.answer(
            get_info_group(
                GroupActions.get_group(group, subjects=True, students=True),
            ),
        )
    else:
        await message.answer("У вас нет группы")
    await Group.action.set()
    await message.answer(
        "Выберите действие",
        reply_markup=group_action(),
    )


async def input_action_group(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input action for group."""
    async with state.proxy() as data:
        data["action"] = callback.data
    group = UserActions.get_user(callback.from_user.id).group
    await Group.name.set()
    match callback.data:
        case GroupActionsEnum.CREATE.action:
            if group is None:
                await callback.message.answer(
                    "Введите название группы",
                    reply_markup=select_cancel(),
                )
            else:
                await callback.message.answer(
                    "У вас уже есть группа",
                )
                await state.finish()
        case GroupActionsEnum.UPDATE.action | GroupActionsEnum.DELETE.action:
            if group is not None:
                await callback.message.answer(
                    "Введите название группы",
                    reply_markup=select_cancel(),
                )
            else:
                await callback.message.answer(
                    "У вас еще нет группы",
                )
                await state.finish()
        case GroupActionsEnum.CANCEL.action:
            await callback.message.answer("Действие отменено")
            await state.finish()


async def input_name_group(message: types.Message, state: FSMContext) -> None:
    """Input name of group."""
    group = GroupActions.get_group(message.text)
    user = UserActions.get_user(message.from_user.id)
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
            "Введите секретное слово для входа в группу",
            reply_markup=select_cancel(),
        )
    else:
        await message.answer(
            (
                "Группа с таким названием уже есть, "
                "либо название не корректно.\n"
                "Введите другое название."
            ),
            reply_markup=select_cancel(),
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
    group_id = UserActions.get_user(message.from_user.id).group
    status = (
        "создана"
        if group_id is None else "обновлена"
        if action == GroupActionsEnum.UPDATE.action else "удалена"
    )
    match action:
        case GroupActionsEnum.CREATE.action:
            group = GroupActions.create_group(new_group)
            UserActions.edit_user(message.from_user.id, {"group": group.id})
        case GroupActionsEnum.UPDATE.action:
            GroupActions.edit_group(group_id, new_group)
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

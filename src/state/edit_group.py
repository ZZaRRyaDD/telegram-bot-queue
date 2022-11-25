from typing import Optional

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import (
    CompletedPracticesActions,
    GroupActions,
    QueueActions,
    ScheduleActions,
    SubjectActions,
    UserActions,
)
from enums import HeadmanCommands
from keywords import (
    GroupActionsEnum,
    group_action,
    remove_cancel,
    select_cancel,
)
from services import (
    check_empty_headman,
    check_headman_of_group,
    get_info_group,
    polynomial_hash,
)


def get_status_group(group_id: Optional[int], action: str) -> str:
    """Return status of group."""
    return (
        "создана"
        if group_id is None else "обновлена"
        if action == GroupActionsEnum.UPDATE.action else "удалена"
    )


class Group(StatesGroup):
    """FSM for CRUD operrations with group."""

    action = State()
    name = State()
    secret_word = State()


async def start_group(message: types.Message) -> None:
    """Entrypoint for group."""
    group = UserActions.get_user(message.from_user.id).group
    if group is None:
        await message.answer("У вас нет группы")
    else:
        await message.answer(
            get_info_group(
                GroupActions.get_group(group, subjects=True, students=True),
            ),
        )
    await Group.action.set()
    await message.answer("Выберите действие", reply_markup=group_action())


async def input_action_group_create(
    callback: types.CallbackQuery,
    state: FSMContext,
    group,
) -> None:
    """Take name of group or finish proccess."""
    if group is None:
        await callback.message.answer(
            "Введите название группы",
            reply_markup=select_cancel(),
        )
        return
    await callback.message.answer("У вас уже есть группа")
    await state.finish()


async def input_action_group_update_delete(
    callback: types.CallbackQuery,
    state: FSMContext,
    group,
) -> None:
    """Take second name and first name for update profile."""
    if group is not None:
        await callback.message.answer(
            "Введите название группы",
            reply_markup=select_cancel(),
        )
        return
    await callback.message.answer("У вас еще нет группы")
    await state.finish()


async def input_action_group(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input action for group."""
    await callback.answer()
    await state.update_data(action=callback.data)
    group = UserActions.get_user(callback.from_user.id).group
    await Group.name.set()
    match callback.data:
        case GroupActionsEnum.CREATE.action:
            await input_action_group_create(callback, state, group)
        case GroupActionsEnum.UPDATE.action | GroupActionsEnum.DELETE.action:
            await input_action_group_update_delete(callback, state, group)
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
    if not name:
        await message.answer(
            (
                "Группа с таким названием уже есть, "
                "либо название не корректно.\n"
                "Введите другое название."
            ),
            reply_markup=select_cancel(),
        )
        return
    await state.update_data(name=message.text)
    await Group.next()
    await message.answer(
        "Введите секретное слово для входа в группу",
        reply_markup=select_cancel(),
    )


async def input_secret_word_create(
    message: types.Message,
    new_group: dict,
) -> None:
    """Create new group."""
    group = GroupActions.create_group(new_group).id
    UserActions.edit_user(message.from_user.id, {"group": group})


async def input_secret_word_update(group_id: int, new_group: dict) -> None:
    """Update group."""
    GroupActions.edit_group(group_id, new_group)


async def input_secret_word_delete(group_id: int) -> int:
    """Delete group and subjects."""
    subjects = GroupActions.get_group(
        group_id=group_id,
        subjects=True,
    ).subjects
    for subject in subjects:
        QueueActions.cleaning_subject(subject.id)
        CompletedPracticesActions.cleaning_subject(subject.id)
        ScheduleActions.delete_schedule_by_subject(subject.id)
        SubjectActions.delete_subject(subject.id)
    GroupActions.delete_group(group_id)


async def input_secret_word(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Input secret word."""
    data = await state.get_data()
    name, action = data["name"], data["action"]
    new_group = {
        "name": name,
        "secret_word": polynomial_hash(message.text),
    }
    group_id = UserActions.get_user(message.from_user.id).group
    status = get_status_group(group_id, action)
    match action:
        case GroupActionsEnum.CREATE.action:
            await input_secret_word_create(message, new_group)
        case GroupActionsEnum.UPDATE.action:
            await input_secret_word_update(group_id, new_group)
        case GroupActionsEnum.DELETE.action:
            await input_secret_word_delete(group_id)
    await message.answer(
        f"Группа {name} успешно {status}",
        reply_markup=remove_cancel(),
    )
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

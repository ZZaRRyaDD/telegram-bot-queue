from typing import Optional

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.database.repositories import GroupRepository, UserRepository
from app.enums import HeadmanCommands
from app.filters import HasUser, IsHeadman
from app.keywords import (
    GroupRepositoryEnum,
    group_action,
    remove_cancel,
    select_cancel,
    select_random_queue_group,
)
from app.services import get_info_group, polynomial_hash


def get_status_group(group_id: Optional[int], action: str) -> str:
    """Return status of group."""
    return (
        "создана"
        if group_id is None else "обновлена"
        if action == GroupRepositoryEnum.UPDATE.action else "удалена"
    )


class Group(StatesGroup):
    """FSM for CRUD operations with group."""

    action = State()
    name = State()
    random_queue = State()
    secret_word = State()


async def start_group(message: types.Message) -> None:
    """Entrypoint for group."""
    group = await UserRepository.get_user(message.from_user.id, group=True).group
    if group is None:
        await message.answer("У вас нет группы")
    else:
        await message.answer(
            get_info_group(
                await GroupRepository.get_group(
                    group_name=group.name,
                    subjects=True,
                    students=True,
                ),
            ),
        )
    await Group.action.set()
    await message.answer("Выберите действие", reply_markup=group_action())


async def input_action_group_create(
    callback: types.CallbackQuery,
    state: FSMContext,
    group,
) -> None:
    """Take name of group or finish process."""
    if group is None:
        await callback.message.delete()
        await callback.message.answer(
            "Введите название группы",
            reply_markup=select_cancel(),
        )
        return
    await callback.message.edit_text("У вас уже есть группа")
    await state.finish()


async def input_action_group_update_delete(
    callback: types.CallbackQuery,
    state: FSMContext,
    group,
) -> None:
    """Take second name and first name for update profile."""
    if group is not None:
        await callback.message.delete()
        await callback.message.answer(
            "Введите название группы",
            reply_markup=select_cancel(),
        )
        return
    await callback.message.edit_text("У вас еще нет группы")
    await state.finish()


async def input_action_group(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input action for group."""
    await state.update_data(action=callback.data)
    group = await UserRepository.get_user(callback.from_user.id, group=True).group
    await Group.name.set()
    match callback.data:
        case GroupRepositoryEnum.CREATE.action:
            await input_action_group_create(callback, state, group)
        case GroupRepositoryEnum.UPDATE.action | GroupRepositoryEnum.DELETE.action:
            await input_action_group_update_delete(callback, state, group)
        case GroupRepositoryEnum.CANCEL.action:
            await callback.message.delete()
            await state.finish()


async def input_name_group(message: types.Message, state: FSMContext) -> None:
    """Input name of group."""
    group = await GroupRepository.get_group(group_name=message.text)
    user = await UserRepository.get_user(message.from_user.id)
    action = (await state.get_data())["action"]
    if action == GroupRepositoryEnum.CREATE.action:
        if group is not None:
            await message.answer(
                (
                    "Группа с таким названием уже есть. "
                    "Введите другое название."
                ),
                reply_markup=select_cancel(),
            )
            return
    elif action == GroupRepositoryEnum.UPDATE.action:
        if group is not None and user.group_id != group.id:
            await message.answer(
                (
                    "Группа с таким названием уже есть. "
                    "Введите другое название."
                ),
                reply_markup=select_cancel(),
            )
            return
    else:
        if group is None or user.group_id != group.id:
            await message.answer(
                "Введите корректное название.",
                reply_markup=select_cancel(),
            )
            return
    await state.update_data(name=message.text)
    if action == GroupRepositoryEnum.DELETE.action:
        await Group.secret_word.set()
        await state.update_data(random_queue=None)
        await message.answer(
            "Введите секретное слово для входа в группу",
            reply_markup=select_cancel(),
        )
    else:
        await Group.next()
        await message.answer(
            "Выберите способ формирования очереди в группе",
            reply_markup=select_random_queue_group(),
        )


async def input_random_queue(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input random_queue for group."""
    await state.update_data(random_queue=callback.data)
    await Group.next()
    await callback.message.delete()
    await callback.message.answer(
        "Введите секретное слово для входа в группу",
        reply_markup=select_cancel(),
    )


async def input_secret_word_create(
    message: types.Message,
    new_group: dict,
) -> None:
    """Create new group."""
    group = await GroupRepository.create(new_group).id
    user = await UserRepository.get(message.from_user.id)
    await UserRepository.update(db_obj=user, obj_in={"group_id": group})


async def input_secret_word_update(group, new_group: dict) -> None:
    """Update group."""
    await GroupRepository.update(db_obj=group, obj_in=new_group)


async def input_secret_word_delete(group) -> int:
    """Delete group and subjects."""
    await GroupRepository.remove(group.id)


async def input_secret_word(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Input secret word."""
    data = await state.get_data()
    name, action, random_queue = data["name"], data["action"], data["random_queue"]
    new_group = {
        "name": name,
        "secret_word": polynomial_hash(message.text),
        "random_queue": random_queue == "True",
    }
    group = await UserRepository.get_user(message.from_user.id).group
    status = get_status_group(group.id, action)
    match action:
        case GroupRepositoryEnum.CREATE.action:
            await input_secret_word_create(message, new_group)
        case GroupRepositoryEnum.UPDATE.action:
            await input_secret_word_update(group, new_group)
        case GroupRepositoryEnum.DELETE.action:
            await input_secret_word_delete(group)
    await message.answer(
        f"Группа {name} успешно {status}",
        reply_markup=remove_cancel(),
    )
    await state.finish()


def register_handlers_group(dispatcher: Dispatcher) -> None:
    """Register handlers for group."""
    dispatcher.register_message_handler(
        start_group,
        HasUser(),
        IsHeadman(),
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
    dispatcher.register_callback_query_handler(
        input_random_queue,
        state=Group.random_queue,
    )
    dispatcher.register_message_handler(
        input_secret_word,
        state=Group.secret_word,
    )

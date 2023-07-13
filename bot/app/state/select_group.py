from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.database import GroupActions, QueueActions, UserActions
from app.enums import ClientCommands, OtherCommands
from app.keywords import get_list_of_groups, remove_cancel, select_cancel
from app.services import check_user, is_headman, polynomial_hash


class SelectGroup(StatesGroup):
    """FSM for select group."""

    name = State()
    secret_word = State()


async def start_select_group(message: types.Message) -> None:
    """Entrypoint for select group."""
    if is_headman(message.from_user.id):
        await message.answer("Староста не может выбирать, ибо он держит ее")
        return
    groups = GroupActions.get_groups()
    if not groups:
        await message.answer("Пока нет ни одной группы")
        return
    await SelectGroup.name.set()
    await message.answer(
        "Выберите группу",
        reply_markup=get_list_of_groups(groups),
    )


async def get_select_group(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input select of group."""
    await callback.answer()
    if callback.data == OtherCommands.CANCEL.command:
        await callback.message.delete()
        await state.finish()
        return
    await state.update_data(group=callback.data)
    user = UserActions.get_user(callback.from_user.id, group=True)
    if int(callback.data) == user.group_id:
        await callback.message.answer(
            "На данный момент вы уже состоите в данной группе",
        )
        await state.finish()
        return
    await SelectGroup.next()
    await callback.message.delete()
    await callback.message.answer(
        "Введите секретное слово",
        reply_markup=select_cancel(),
    )


async def get_secret_word(message: types.Message, state: FSMContext) -> None:
    """Input secret word."""
    group = GroupActions.get_group(
        group_id=int((await state.get_data())["group"]),
    )
    if int(group.secret_word) != int(polynomial_hash(message.text)):
        await message.answer(
            "Секретное слово не верно. Введите его заново.",
            reply_markup=select_cancel(),
        )
        return
    UserActions.edit_user(message.from_user.id, {"group_id": group.id})
    QueueActions.cleaning_user(message.from_user.id)
    await message.answer(
        f"Теперь вы в группе {group.name}",
        reply_markup=remove_cancel(),
    )
    await state.finish()


def register_handlers_select_group(dispatcher: Dispatcher) -> None:
    """Register handlers for select group."""
    dispatcher.register_message_handler(
        start_select_group,
        lambda message: check_user(message.from_user.id),
        commands=[ClientCommands.CHOICE_GROUP.command],
        state=None,
    )
    dispatcher.register_callback_query_handler(
        get_select_group,
        state=SelectGroup.name,
    )
    dispatcher.register_message_handler(
        get_secret_word,
        state=SelectGroup.secret_word,
    )

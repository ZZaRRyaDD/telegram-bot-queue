from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import GroupActions, QueueActions, UserActions
from keywords import get_list_of_groups
from services import check_user, is_headman, polynomial_hash


class SelectGroup(StatesGroup):
    """FSM for select group."""

    name = State()
    secret_word = State()


async def start_select_group(message: types.Message) -> None:
    """Entrypoint for select group."""
    if not is_headman(message.from_user.id):
        groups = GroupActions.get_groups()
        if groups:
            await SelectGroup.name.set()
            await message.answer(
                """Выберите группу""",
                reply_markup=get_list_of_groups(groups),
            )
        else:
            await message.answer(
                "Пока нет ни одной группы",
            )
    else:
        await message.answer(
            "Староста не может выбирать, ибо он держит ее",
        )


async def get_select_group(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input select of group."""
    async with state.proxy() as data:
        data["name"] = callback.data
    await SelectGroup.next()
    await callback.message.answer(
        """Введите секретное слово, либо 'cancel'"""
    )


async def get_secret_word(message: types.Message, state: FSMContext) -> None:
    """Input secret word."""
    group_info = {}
    async with state.proxy() as data:
        group_info["group"] = data["name"]
    group = GroupActions.get_group(int(group_info["group"]))
    if int(group.secret_word) == int(polynomial_hash(message.text)):
        UserActions.edit_user(
            message.from_user.id,
            {"group": group.id},
        )
        QueueActions.cleaning_user(message.from_user.id)
        await message.answer(
            f"Теперь вы в группе {group.name}"
        )
        await state.finish()
    else:
        await message.answer(
            "Секретное слово не верно. Введите его заново, либо 'cancel'"
        )


def register_handlers_select_group(dispatcher: Dispatcher) -> None:
    """Register handlers for select group."""
    dispatcher.register_message_handler(
        start_select_group,
        lambda message: check_user(message.from_user.id),
        commands=["select_group"],
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

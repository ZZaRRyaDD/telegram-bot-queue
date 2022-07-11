from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import UserActions
from services import check_user


class EditAccountInfo(StatesGroup):
    """FSM for edit account."""

    full_name = State()


async def start_get_info(message: types.Message) -> None:
    """Entrypoint for edit account."""
    await EditAccountInfo.full_name.next()
    await message.answer(
        "Введи свое фамилию и имя, либо 'cancel'"
    )


async def input_full_name(message: types.Message, state: FSMContext) -> None:
    """Get info about first and last name."""
    new_info = {
        "id": message.from_user.id,
        "full_name": message.text,
    }
    UserActions.edit_user(message.from_user.id, new_info)
    await message.answer("Ваши данные успешно заменены")
    await state.finish()


def register_handlers_change_account(dispatcher: Dispatcher) -> None:
    """Register handlers for change account."""
    dispatcher.register_message_handler(
        start_get_info,
        lambda message: check_user(message.from_user.id),
        commands=["change_profile"],
        state=None,
    )
    dispatcher.register_message_handler(
        input_full_name,
        lambda message: check_user(message.from_user.id),
        state=EditAccountInfo.full_name,
    )

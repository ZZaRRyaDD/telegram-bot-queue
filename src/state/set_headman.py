from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import UserActions
from services import check_admin


class SetHeadman(StatesGroup):
    """FSM for set headman."""

    is_headman = State()


async def start_set_headman(message: types.Message) -> None:
    """Entrypoint for set headman."""
    await SetHeadman.is_headman.set()
    await message.answer(
        "Введите id пользователя, которого нужно назначить старостой"
    )


async def input_id_headman(message: types.Message, state: FSMContext) -> None:
    """Input id of future headman."""
    async with state.proxy() as data:
        data["id"] = int(message.text)
    user = UserActions.get_user(data["id"])
    if user:
        new_status = not user.is_headman
        new_info = {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "is_headman": new_status,
        }
        UserActions.edit_user(user.id, new_info)
        situation = (
            'назначен старостой'
            if new_status
            else 'удален с поста старосты'
        )
        await message.answer(
            f"Пользователь {user.full_name} {situation}"
        )
    else:
        await message.answer(
            "Такого пользователя нет"
        )
    await state.finish()


def register_handlers_set_headman(dispatcher: Dispatcher) -> None:
    """Register handlers for set headman."""
    dispatcher.register_message_handler(
        start_set_headman,
        lambda message: check_admin(message.from_user.id),
        commands=["set_headman"],
        state=None,
    )
    dispatcher.register_message_handler(
        input_id_headman,
        lambda message: check_admin(message.from_user.id),
        state=SetHeadman.is_headman,
    )

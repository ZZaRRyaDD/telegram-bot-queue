from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import UserActions
from handlers import AdminCommands
from main import bot
from services import check_admin


class SetHeadman(StatesGroup):
    """FSM for set headman."""

    is_headman = State()


async def start_set_headman(message: types.Message) -> None:
    """Entrypoint for set headman."""
    await SetHeadman.is_headman.set()
    await message.answer(
        (
            "Введите id пользователя, у которого нужно изменить статус, "
            "либо 'cancel'"
        )
    )


async def input_id_headman(message: types.Message, state: FSMContext) -> None:
    """Input id of future headman."""
    user = UserActions.get_user(int(message.text), subjects=False)
    if user:
        new_status = not user.is_headman
        new_info = {
            "id": user.id,
            "full_name": user.full_name,
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
        status = (
            'стали старостой и теперь вам доступна команда /commands'
            if new_status
            else 'больше не староста'
        )
        await bot.send_message(
            user.id,
            f"Вы {status}",
        )
        await state.finish()
    else:
        await message.answer(
            "Такого пользователя нет. Введите id, либо введите 'cancel'"
        )


def register_handlers_set_headman(dispatcher: Dispatcher) -> None:
    """Register handlers for set headman."""
    dispatcher.register_message_handler(
        start_set_headman,
        lambda message: check_admin(message.from_user.id),
        commands=[AdminCommands.SET_HEADMAN.command],
        state=None,
    )
    dispatcher.register_message_handler(
        input_id_headman,
        lambda message: check_admin(message.from_user.id),
        state=SetHeadman.is_headman,
    )

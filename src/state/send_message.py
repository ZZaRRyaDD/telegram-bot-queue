from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import UserActions
from enums import AdminCommands
from keywords import remove_cancel, select_cancel
from main import bot
from services import check_admin


class Message(StatesGroup):
    """FSM for message of admin."""

    message = State()


async def get_message(message: types.Message) -> None:
    """Entrypoint for message."""
    await Message.message.set()
    await message.answer(
        "Введите сообщение для отправки всем",
        reply_markup=select_cancel(),
    )


async def send_messages(message: types.Message, state: FSMContext) -> None:
    """Input message and send it."""
    users = UserActions.get_users(without_admin=True)
    if users is None:
        await message.answer(
            "Пользователей нет",
            reply_markup=remove_cancel(),
        )
        await state.finish()
        return
    for user in users:
        await bot.send_message(
            user.id,
            f"Сообщение от админа: \n{message.text}",
            reply_markup=remove_cancel(),
        )
    await state.finish()


def register_handlers_message(dispatcher: Dispatcher) -> None:
    """Register handlers for message."""
    dispatcher.register_message_handler(
        get_message,
        lambda message: check_admin(message.from_user.id),
        commands=[AdminCommands.SEND_MESSAGE.command],
        state=None,
    )
    dispatcher.register_message_handler(
        send_messages,
        state=Message.message,
    )

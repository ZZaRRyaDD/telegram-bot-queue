from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import UserActions
from main import bot
from services import check_admin


class Message(StatesGroup):
    """FSM for message of admin."""

    message = State()


async def get_message(message: types.Message) -> None:
    """Entrypoint for message."""
    await Message.message.set()
    await message.answer("Введите сообщение для отпаравки всем")


async def send_messages(message: types.Message, state: FSMContext) -> None:
    """Input message for send it."""
    users = UserActions.get_users()
    if users:
        for user in users:
            await bot.send_message(
                user.id,
                f"Сообщение от админа: \n{message.text}"
            )
    await state.finish()


def register_handlers_message(dispatcher: Dispatcher) -> None:
    """Register handlers for message."""
    dispatcher.register_message_handler(
        get_message,
        lambda message: check_admin(message.from_user.id),
        commands=["send_message"],
        state=None,
    )
    dispatcher.register_message_handler(
        send_messages,
        state=Message.message,
    )

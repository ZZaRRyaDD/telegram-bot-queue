from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import QueueActions, UserActions
from services import check_user, is_headman

ANSWER = "Да"


class DeleteAccount(StatesGroup):
    """FSM for delete account."""

    answer = State()


async def start_delete_account(message: types.Message) -> None:
    """Entrypoint for delete account."""
    await DeleteAccount.answer.set()
    await message.answer("Введите 'Да' без ковычек, либо cancel для отмены")


async def delete_account(message: types.Message, state: FSMContext) -> None:
    """Delete account."""
    if not is_headman(message.from_user.id):
        if message.text == ANSWER:
            QueueActions.cleaning_user(message.from_user.id)
            UserActions.delete_user(message.from_user.id)
            await message.answer("Успехов! Удачи! Спокойной ночи!")
            await state.finish()
        else:
            await message.answer("Ответ не верный")
    else:
        await message.answer(
            (
                "Чтобы удалиться старосте - напишите админу. "
                "После этого можете спокойно удаляться"
            )
        )
        await state.finish()


def register_handlers_delete_account(dispatcher: Dispatcher) -> None:
    """Register handlers for delete account."""
    dispatcher.register_message_handler(
        start_delete_account,
        lambda message: all([
            check_user(message.from_user.id),
        ]),
        commands=["delete_account"],
        state=None,
    )
    dispatcher.register_message_handler(
        delete_account,
        state=DeleteAccount.answer,
    )

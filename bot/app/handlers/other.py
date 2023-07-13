from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.enums import OtherCommands
from app.keywords import remove_cancel
from app.services import check_user


async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    """Handler for cancel action."""
    current_state = await state.get_state()
    if current_state is None:
        return
    await message.answer(
        "Действие отменено",
        reply_markup=remove_cancel(),
    )
    await state.finish()


def register_handlers_cancel_action(dispatcher: Dispatcher) -> None:
    """Register handlers for cancel action."""
    dispatcher.register_message_handler(
        cancel_handler,
        lambda message: check_user(message.from_user.id),
        state="*",
        commands=[OtherCommands.CANCEL.command],
    )
    dispatcher.register_message_handler(
        cancel_handler,
        lambda message: check_user(message.from_user.id),
        Text(equals="Cancel", ignore_case=True),
        state="*",
    )

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import QueueActions, UserActions
from handlers import ClientCommands
from keywords import UserActionEnum, user_actions
from services import check_user, is_headman


class User(StatesGroup):
    """FSM for edit account."""

    action = State()
    full_name = State()


async def start_user(message: types.Message) -> None:
    """Entrypoint for user."""
    await User.action.set()
    await message.answer(
        "Выберите действие, либо введите 'cancel'",
        reply_markup=user_actions(),
    )


async def input_action(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Entrypoint for edit account."""
    user = UserActions.get_user(callback.from_user.id)
    async with state.proxy() as data:
        data["action"] = callback.data
        data["full_name"] = user.full_name
    message = ""
    match callback.data:
        case UserActionEnum.UPDATE.action:
            message = "Введи свое фамилию и имя, либо введите 'cancel'"
        case UserActionEnum.DELETE.action:
            message = (
                f"Введи свое фамилию и имя '{user.full_name}' без ковычек, "
                "либо введите 'cancel'"
            )
    await User.full_name.set()
    await callback.message.answer(message)


async def input_full_name(message: types.Message, state: FSMContext) -> None:
    """Get info about first and last name."""
    action = ""
    full_name = ""
    async with state.proxy() as data:
        action = data["action"]
        full_name = data["full_name"]
    if message.text:
        match action:
            case UserActionEnum.UPDATE.action:
                new_info = {
                    "id": message.from_user.id,
                    "full_name": message.text,
                }
                UserActions.edit_user(message.from_user.id, new_info)
                await message.answer("Ваши данные успешно заменены")
            case UserActionEnum.DELETE.action:
                if not is_headman(message.from_user.id):
                    if message.text == full_name:
                        QueueActions.cleaning_user(message.from_user.id)
                        UserActions.delete_user(message.from_user.id)
                        await message.answer(
                            "Успехов! Удачи! Спокойной ночи!",
                        )
                        await state.finish()
                    else:
                        await message.answer("Ответ не верный")
                else:
                    await message.answer(
                        (
                            "Чтобы удалиться старосте - напишите админу. "
                            "После этого можете спокойно удаляться"
                        ),
                    )
                    await state.finish()
    else:
        await message.answer(
            "Введите корректное имя и фамилию, либо введите 'cancel'"
        )


def register_handlers_change_account(dispatcher: Dispatcher) -> None:
    """Register handlers for change account."""
    dispatcher.register_message_handler(
        start_user,
        lambda message: check_user(message.from_user.id),
        commands=[ClientCommands.EDIT_PROFILE.command],
        state=None,
    )
    dispatcher.register_callback_query_handler(
        input_action,
        lambda message: check_user(message.from_user.id),
        state=User.action,
    )
    dispatcher.register_message_handler(
        input_full_name,
        lambda message: check_user(message.from_user.id),
        state=User.full_name,
    )

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import QueueActions, UserActions
from enums import ClientCommands, UserActionsEnum
from keywords import select_cancel, user_actions
from services import check_user, is_headman, print_info


class User(StatesGroup):
    """FSM for edit account."""

    action = State()
    full_name = State()


async def start_user(message: types.Message) -> None:
    """Entrypoint for user."""
    await message.answer(print_info(message.from_user.id))
    await User.action.set()
    await message.answer("Выберите действие", reply_markup=user_actions())


async def input_action_update(callback: types.CallbackQuery) -> None:
    """Take second name and first name for update profile."""
    await callback.message.answer(
        "Введи свое фамилию и имя",
        reply_markup=select_cancel(),
    )


async def input_action_delete(callback: types.CallbackQuery, user) -> None:
    """Take second name and first name for delete profile."""
    await callback.message.answer(
        f"Введи свое фамилию и имя '{user.full_name}' без ковычек",
        reply_markup=select_cancel(),
    )


async def input_action(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Entrypoint for edit account."""
    user = UserActions.get_user(callback.from_user.id)
    await state.update_data(
        action=callback.data,
        full_name=user.full_name,
    )
    await User.full_name.set()
    match callback.data:
        case UserActionsEnum.UPDATE.action:
            await input_action_update(callback)
        case UserActionsEnum.DELETE.action:
            await input_action_delete(callback, user)
        case UserActionsEnum.CANCEL.action:
            await callback.message.answer("Действие отменено")
            await state.finish()


async def input_full_name_update(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Update profile."""
    new_info = {
        "id": message.from_user.id,
        "full_name": message.text,
    }
    UserActions.edit_user(message.from_user.id, new_info)
    await message.answer("Ваши данные успешно заменены")
    await state.finish()


async def input_full_name_delete(
    message: types.Message,
    state: FSMContext,
    full_name: str,
) -> None:
    """Delete profile."""
    if is_headman(message.from_user.id):
        await message.answer(
            (
                "Чтобы удалиться старосте - напишите админу. "
                "После этого можете спокойно удаляться"
            ),
        )
        await state.finish()
        return
    if message.text == full_name:
        QueueActions.cleaning_user(message.from_user.id)
        UserActions.delete_user(message.from_user.id)
        await message.answer("Успехов! Удачи! Спокойной ночи!")
        await state.finish()
        return
    await message.answer(
        "Введите корректное имя и фамилию",
        reply_markup=select_cancel(),
    )


async def input_full_name(message: types.Message, state: FSMContext) -> None:
    """Get info about first and last name."""
    data = await state.get_data()
    match data["action"]:
        case UserActionsEnum.UPDATE.action:
            await input_full_name_update(message, state)
        case UserActionsEnum.DELETE.action:
            await input_full_name_delete(
                message,
                state,
                data["full_name"],
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

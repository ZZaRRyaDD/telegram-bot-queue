from aiogram import Dispatcher, types

from database import UserActions
from keywords import Choices, create_buttons


def print_info(id: int) -> str:
    """Return info about user."""
    info = ""
    user = UserActions.get_user(id)
    info += f"ID: {user.id}\n"
    info += f"Username: {user.username}\n"
    info += f"Фамилия Имя: {user.full_name}\n"
    info += f"Email: {user.email}\n"
    info += f"Отправлять email: {user.send_email}"
    return info


def check_user(id: int) -> bool:
    """Check register user or not."""
    return UserActions.get_user(id) is None


async def start_command(message: types.Message) -> None:
    """Handler for start command."""
    if check_user(message.from_user.id):
        await message.answer(
            "Смотрю ты еще не с нами. Давай это исправим!",
        )
        full_name = (
            f"{message.from_user.first_name} {message.from_user.last_name}"
        )
        new_user = {
            "id": message.from_user.id,
            "username": message.from_user.username,
            "full_name": full_name,
            "email": "",
        }
        UserActions.create_user(new_user)
    await message.answer(
        "Хай",
        reply_markup=create_buttons(),
    )


async def choices(message: types.Message) -> None:
    """Handler for buttons."""
    match message.text:
        case Choices.INFO_PROFILE:
            await message.answer(
                print_info(message.from_user.id),
                reply_markup=create_buttons(),
            )
        case Choices.CHANGE_PROFILE:
            pass
        case Choices.CHOICE_GROUP:
            pass
        case Choices.STAY_QUEUE:
            pass


def register_handlers_client(dispatcher: Dispatcher) -> None:
    """Register handler for different types commands of user."""
    dispatcher.register_message_handler(start_command, commands=["start"])
    dispatcher.register_message_handler(choices, content_types=["text"])

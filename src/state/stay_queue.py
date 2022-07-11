from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import GroupActions, UserActions
from database.repository import SubjectActions
from keywords import get_list_of_subjects
from services import check_user, member_group


class StayQueue(StatesGroup):
    """FSM for stay in queue."""

    name = State()


async def start_stay_queue(message: types.Message) -> None:
    """Entrypoint for stay in queue."""
    if member_group(message.from_user.id):
        subjects = GroupActions.get_group_with_subjects(
            UserActions.get_user(message.from_user.id).group
        ).subjects
        access_subjects = list(filter(
            lambda subject: subject.can_select, subjects
        ))
        if access_subjects:
            await StayQueue.name.set()
            await message.answer(
                """Выберите предмет""",
                reply_markup=get_list_of_subjects(access_subjects),
            )
        else:
            await message.answer(
                "Нет предметов, на которые можно записаться",
            )
    else:
        await message.answer(
            "Чтобы выбрать предмет, нужно выбрать группу",
        )


def get_subject_info(user) -> str:
    """Get info about subscribe subjects."""
    if not user.subjects:
        return "Вы не записаны ни на один предмет"
    info = "Вы записаны на следующие предметы:\n"
    for subject in user.subjects:
        info += f"{subject.name}"
    return info


async def get_subject_name(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input select of subjects."""
    call_data = callback.data
    subjects = []
    async with state.proxy() as data:
        if call_data != "Stop":
            if data.get("subjects") is None:
                data["subjects"] = [call_data]
            else:
                data["subjects"].append(call_data)
        subjects = data["subjects"] if data.get("subjects") else []
    if call_data == "Stop":
        user = UserActions.get_user_with_subject(callback.from_user.id)
        for subject in subjects:
            SubjectActions.action_user(
                user,
                SubjectActions.get_subject(subject),
            )
        await callback.message.answer(
            get_subject_info(user)
        )
        await state.finish()


def register_handlers_stay_queue(dispatcher: Dispatcher) -> None:
    """Register handlers for select subjects."""
    dispatcher.register_message_handler(
        start_stay_queue,
        lambda message: check_user(message.from_user.id),
        commands=["stay_queue"],
        state=None,
    )
    dispatcher.register_callback_query_handler(
        get_subject_name,
        state=StayQueue.name,
    )

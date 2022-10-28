import emoji
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import (
    CompletedPracticesActions,
    GroupActions,
    SubjectActions,
    UserActions,
)
from enums import ClientCommands
from keywords import get_list_of_numbers, get_list_of_subjects
from services import check_user, member_group


class CompletePractice(StatesGroup):
    """FSM for stay in queue."""

    name = State()
    number = State()


def info_practice(message: types.Message) -> str:
    """Get info about practices."""
    pass_practices = set(
        practice.subject_id
        for practice in CompletedPracticesActions.get_completed_practices_info(
            message.from_user.id,
        )
    )
    all_subjects = set(map(lambda x: x.id, GroupActions.get_group(
            id=UserActions(message.from_user.id).group,
            subjects=True,
        ).subjects,
    ))
    status_subjects = {}
    infos = []
    for subject_id in all_subjects:
        subject = SubjectActions.get_subject(id=subject_id)
        if subject_id in pass_practices:
            completed = map(lambda x: x.number, filter(
                lambda x: x.subject_id == subject_id,
                pass_practices,
            ))
            status_subjects[subject.id] = []
            for number in range(1, subject.count + 1):
                status_subjects[subject.name][number] = [
                    int(number in completed)
                ]
        else:
            status_subjects[subject.name] = [0*subject.count]
        info = ""
        for subject, practices in status_subjects.items():
            info += f"{subject}:\n"
            if any(practices):
                for index, status in enumerate(practices, start=1):
                    emojie_type = (
                        emoji.emojize(':white_check_mark:')
                        if status
                        else emoji.emojize(':x:')
                    )
                    info += f"\t\t{emojie_type} {index}\n"
            infos.append(info)
    return infos


async def start_complete_practice(message: types.Message) -> None:
    """Entrypoint for complete practices."""
    if member_group(message.from_user.id):
        subjects = GroupActions.get_group(
            UserActions.get_user(message.from_user.id, subjects=False).group,
            subjects=True,
        ).subjects
        if subjects:
            await message.answer(
                info_practice(
                    message.from_user.id,
                ),
            )
            await CompletePractice.name.set()
            subjects = [
                SubjectActions.get_subject(subject_id=subject_id)
                for subject_id in subjects
            ]
            await message.answer(
                "Выберите предмет, либо введите 'cancel'",
                reply_markup=get_list_of_subjects(subjects),
            )
        else:
            await message.answer(
                "В группе нет предметов",
            )
    else:
        await message.answer(
            "Чтобы выбрать предмет, нужно выбрать группу",
        )


async def get_subject_name(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input select of subjects."""
    call_data = callback.data
    async with state.proxy() as data:
        data["subject"] = call_data
        await callback.answer()
    subject = SubjectActions.get_subject(int(call_data))
    await CompletePractice.next()
    await callback.message.answer(
        "Выберите номера лабораторных работ, либо введите 'cancel'",
        reply_markup=get_list_of_numbers(list(range(1, subject.count + 1)))
    )


async def get_numbers_lab_subject(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Get numbers of lab of subject."""
    numbers = []
    params = {
        "user_id": callback.from_user.id,
    }
    call_data = callback.data
    async with state.proxy() as data:
        message = "Вы завершили выбор"
        if call_data != "Stop":
            if data.get("numbers") is None:
                data["numbers"] = [call_data]
                message = f"Добавлена {call_data} лаба"
            else:
                if call_data in data["numbers"]:
                    data["numbers"].remove(call_data)
                    message = f"Удалена {call_data} лаба"
                else:
                    data["numbers"].append(call_data)
                    message = f"Добавлена {call_data} лаба"
        params["subject_id"] = int(data["subject"])
        numbers = (
            list(map(int, data["numbers"]))
            if data.get("numbers")
            else []
        )
        await callback.message.answer(message)
    await callback.answer()
    if call_data == "Stop":
        if numbers:
            for number in numbers:
                params["number"] = number
                CompletedPracticesActions.action_user(params)
        await state.finish()
        await message.answer(
            info_practice(
                message.from_user.id,
            ),
        )


def register_handlers_complete_practice(dispatcher: Dispatcher) -> None:
    """Register handlers for select subjects."""
    dispatcher.register_message_handler(
        start_complete_practice,
        lambda message: check_user(message.from_user.id),
        commands=[ClientCommands.PASS_PRACTICES.command],
        state=None,
    )
    dispatcher.register_callback_query_handler(
        get_subject_name,
        state=CompletePractice.name,
    )
    dispatcher.register_callback_query_handler(
        get_numbers_lab_subject,
        state=CompletePractice.number,
    )

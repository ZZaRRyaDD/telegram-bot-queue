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
from enums import ClientCommands, OtherCommands, SubjectCompact
from keywords import get_list_of_numbers, get_list_of_subjects
from services import check_user, member_group


class CompletePractice(StatesGroup):
    """FSM for stay in queue."""

    name = State()
    number = State()


def info_practice(user_id: int) -> str:
    """Get info about practices."""
    pass_practices = [
        practice
        for practice in CompletedPracticesActions.get_completed_practices_info(
            user_id,
        )
    ]
    all_subjects = set(map(lambda x: x.id, GroupActions.get_group(
            group_id=UserActions.get_user(user_id).group,
        ).subjects,
    ))
    status_subjects = {}
    for subject_id in all_subjects:
        subject = SubjectActions.get_subject(subject_id=subject_id)
        status_subjects[subject.name] = [False]*subject.count
        if subject_id in [item.subject_id for item in pass_practices]:
            completed = list(map(lambda x: x.number, filter(
                lambda x: x.subject_id == subject_id,
                pass_practices,
            )))
            for number in range(subject.count):
                status_subjects[subject.name][number] = (
                    (number + 1) in completed
                )
    info = ""
    for subject, practices in status_subjects.items():
        info += f"{subject}:\n"
        for index, status in enumerate(practices, start=1):
            emojize_type = ':white_check_mark:' if status else ':x:'
            info += emoji.emojize(
                f"\t\t{emojize_type} {index}\n",
                language='alias',
            )
    return "".join(info)


async def start_complete_practice(message: types.Message) -> None:
    """Entrypoint for complete practices."""
    if not member_group(message.from_user.id):
        await message.answer("Чтобы выбрать предмет, нужно выбрать группу")
        return
    subjects = GroupActions.get_group(
        UserActions.get_user(message.from_user.id).group,
    ).subjects
    if not subjects:
        await message.answer("В группе нет предметов")
        return
    await message.answer(info_practice(message.from_user.id))
    await CompletePractice.name.set()
    await message.answer(
        "Выберите предмет",
        reply_markup=get_list_of_subjects(subjects),
    )


async def get_subject_name(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input select of subjects."""
    await callback.answer()
    if callback.data == OtherCommands.CANCEL.command:
        await callback.message.answer("Действие отменено")
        await state.finish()
        return
    await state.update_data(subject=callback.data)
    subject = SubjectActions.get_subject(int(callback.data))
    await CompletePractice.next()
    lab_works = [
        SubjectCompact(id=i, name=i) for i in range(1, subject.count + 1)
    ]
    await callback.message.answer(
        "Выберите номера лабораторных работ",
        reply_markup=get_list_of_numbers(lab_works),
    )


async def get_numbers_lab_subject(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Get numbers of lab of subject."""
    await callback.answer()
    if callback.data == OtherCommands.CANCEL.command:
        await callback.message.answer("Действие отменено")
        await state.finish()
        return
    params = {
        "user_id": callback.from_user.id,
        "number": callback.data,
        "subject_id": int((await state.get_data())["subject"])
    }
    result = CompletedPracticesActions.action_user(params)
    status = 'Добавлена' if result else 'Удалена'
    message = f"{status} {params['number']} лабораторная работа"
    await callback.message.answer(message)
    await state.finish()
    await callback.message.answer(info_practice(callback.from_user.id))


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

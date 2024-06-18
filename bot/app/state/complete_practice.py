import emoji
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.database.repositories import (
    CompletedPracticesRepository,
    GroupRepository,
    SubjectRepository,
)
from app.enums import ClientCommands, OtherCommands, SubjectCompact
from app.filters import HasUser, IsMemberOfGroup
from app.keywords import get_list_of_numbers, get_list_of_subjects
from app.services import member_group


class CompletePractice(StatesGroup):
    """FSM for stay in queue."""

    name = State()
    number = State()


async def info_practice(user_id: int) -> str:
    """Get info about practices."""
    pass_practices = [
        practice
        for practice in (await CompletedPracticesRepository.get_completed_practices_info(
            user_id,
        ))
    ]
    all_subjects = set(map(lambda x: x.id, (await GroupRepository.get_group_by_user_id(
            user_id,
            subjects=True,
        )).subjects,
    ))
    status_subjects = {}
    for subject_id in all_subjects:
        subject = await SubjectRepository.get_subject(subject_id=subject_id)
        status_subjects[subject.name] = [False]*subject.count_practices
        if subject_id in [item.subject_id for item in pass_practices]:
            completed = list(map(lambda x: x.number_practice, filter(
                lambda x: x.subject_id == subject_id,
                pass_practices,
            )))
            for number in range(subject.count_practices):
                status_subjects[subject.name][number] = (
                    (number + 1) in completed
                )
    info = ""
    for subject, practices in status_subjects.items():
        info += f"{subject}:\n"
        for index, status in enumerate(practices, start=1):
            emoji_type = ':white_check_mark:' if status else ':x:'
            info += emoji.emojize(
                f"\t\t{emoji_type} {index}\n",
                language='alias',
            )
    return "".join(info)


async def start_complete_practice(message: types.Message) -> None:
    """Entrypoint for complete practices."""
    if not member_group(message.from_user.id):
        await message.answer("Чтобы выбрать предмет, нужно выбрать группу")
        return
    group = await GroupRepository.get_group_by_user_id(
        message.from_user.id,
        subjects=True,
    )
    if not subjects:
        await message.answer("В группе нет предметов")
        return
    await message.answer(await info_practice(message.from_user.id))
    await CompletePractice.name.set()
    await message.answer(
        "Выберите предмет",
        reply_markup=get_list_of_subjects(group.subjects),
    )


async def get_subject_name(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input select of subjects."""
    await callback.answer()
    if callback.data == OtherCommands.CANCEL.command:
        await callback.message.delete()
        await state.finish()
        return
    await state.update_data(subject=callback.data)
    subject = await SubjectRepository.get_subject(int(callback.data))
    await CompletePractice.next()
    lab_works = [
        SubjectCompact(id=i, name=i)
        for i in range(1, subject.count_practices + 1)
    ]
    await callback.message.edit_text(
        "Выберите номер лабораторной работы",
        reply_markup=get_list_of_numbers(lab_works),
    )


async def get_numbers_lab_subject(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Get number of lab of subject."""
    await callback.answer()
    if callback.data == OtherCommands.CANCEL.command:
        await callback.message.delete()
        await state.finish()
        return
    params = {
        "user_id": callback.from_user.id,
        "number_practice": callback.data,
        "subject_id": int((await state.get_data())["subject"])
    }
    result = await CompletedPracticesRepository.action_user(params)
    status = 'Добавлена' if result else 'Удалена'
    message = f"{status} {params['number_practice']} лабораторная работа"
    await callback.message.delete()
    await callback.message.answer(message)
    await state.finish()
    await callback.message.answer(
        await info_practice(callback.from_user.id),
    )


def register_handlers_complete_practice(dispatcher: Dispatcher) -> None:
    """Register handlers for select subjects."""
    dispatcher.register_message_handler(
        start_complete_practice,
        HasUser(),
        IsMemberOfGroup(),
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

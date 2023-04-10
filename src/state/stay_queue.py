from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import (
    GroupActions,
    QueueActions,
    ScheduleActions,
    SubjectActions,
    UserActions,
)
from enums import ClientCommands, OtherCommands, SubjectCompact
from keywords import get_list_of_numbers, get_list_of_subjects
from services import check_user, member_group

QUEUE_TEXT = """
Выберите предмет.
Если вы еще не вставали в очередь:
- при нажатии на номер лабораторной работы вы встаете в очередь на нее
- при повторном нажатии вы выходите из очереди по данной лабораторной работе
Если вы уже вставали в очередь:
- нажмите на номер лабораторной работы, чтобы уйти с очереди на нее
(если работа была выбрана ранее)
- нажмите на номер лабораторной работы, чтобы встать в очередь на нее
(если работа не была выбрана ранее)
Для того, чтобы встать в очередь на другую лабораторную работу нужно проделать
все выше изложенные действия
"""


class StayQueue(StatesGroup):
    """FSM for stay in queue."""

    name = State()
    number = State()


def get_subject_info(user_id: int) -> str:
    """Get info about subscribe subjects."""
    positions = QueueActions.get_queue_info(user_id)
    if not positions:
        return "Вы не записаны ни на один предмет"
    info = "Вы записаны на следующие предметы:\n\n"
    subjects = set(position.subject_id for position in positions)
    for subject_id in subjects:
        subject = SubjectActions.get_subject(subject_id)
        numbers = sorted(
            filter(lambda x: x.subject_id == subject_id, positions),
            key=lambda x: x.number,
        )
        numbers = list(map(lambda x: str(x.number), numbers))
        info += f"Дисциплина: {subject.name}\n"
        info += f"Номера лабораторных работ: {' '.join(numbers)}\n\n"
    return info


async def start_stay_queue(message: types.Message) -> None:
    """Entrypoint for stay in queue."""
    if not member_group(message.from_user.id):
        await message.answer("Чтобы выбрать предмет, нужно выбрать группу")
        return
    subjects = set(subject.id for subject in GroupActions.get_group(
        UserActions.get_user(message.from_user.id).group,
        subjects=True,
    ).subjects)
    schedule = set(
        schedule.subject_id
        for schedule in ScheduleActions.get_schedule(can_select=True)
    )
    access_subjects = subjects.intersection(schedule)
    if not access_subjects:
        await message.answer("Нет предметов, на которые можно записаться")
        return
    await message.answer(
        get_subject_info(message.from_user.id),
    )
    await StayQueue.name.set()
    access_subjects_list = [
        SubjectActions.get_subject(subject_id=subject_id)
        for subject_id in access_subjects
    ]
    await message.answer(
        QUEUE_TEXT,
        reply_markup=get_list_of_subjects(access_subjects_list),
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
    subject = SubjectActions.get_subject(int(callback.data))
    await StayQueue.next()
    lab_works = [
        SubjectCompact(id=i, name=i) for i in range(1, subject.count + 1)
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
        "number": callback.data,
        "subject_id": int((await state.get_data())["subject"]),
    }
    result = QueueActions.action_user(params)
    status = 'Добавлена' if result else 'Удалена'
    message = f"{status} {params['number']} лабораторная работа"
    await callback.message.answer(message)
    await state.finish()
    await callback.message.edit_text(
        get_subject_info(callback.from_user.id),
    )


def register_handlers_stay_queue(dispatcher: Dispatcher) -> None:
    """Register handlers for select subjects."""
    dispatcher.register_message_handler(
        start_stay_queue,
        lambda message: check_user(message.from_user.id),
        commands=[ClientCommands.STAY_QUEUE.command],
        state=None,
    )
    dispatcher.register_callback_query_handler(
        get_subject_name,
        state=StayQueue.name,
    )
    dispatcher.register_callback_query_handler(
        get_numbers_lab_subject,
        state=StayQueue.number,
    )

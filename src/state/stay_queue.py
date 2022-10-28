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
from enums import ClientCommands
from keywords import get_list_of_numbers, get_list_of_subjects
from services import check_user, member_group

QUEUE_TEXT = """
Выберите предмет, либо введите 'cancel'.
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
В любом момент вы можете напечатать 'cancel', чтобы отменить процедуру
"""


class StayQueue(StatesGroup):
    """FSM for stay in queue."""

    name = State()
    number = State()


def get_subject_info(positions: list) -> str:
    """Get info about subscribe subjects."""
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
    if member_group(message.from_user.id):
        subjects = set(GroupActions.get_group(
            UserActions.get_user(message.from_user.id, subjects=False).group,
            subjects=True,
        ).subjects)
        schedule = set(
            schedule.subject_id
            for schedule in ScheduleActions.get_schedule(can_select=True)
        )
        access_subjects = subjects.intersection(schedule)
        if access_subjects:
            await message.answer(
                get_subject_info(
                    QueueActions.get_queue_info(message.from_user.id)
                )
            )
            await StayQueue.name.set()
            access_subjects = [
                SubjectActions.get_subject(subject_id=subject_id)
                for subject_id in access_subjects
            ]
            await message.answer(
                QUEUE_TEXT,
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
    await StayQueue.next()
    await callback.message.answer(
        "Выберите номера лабораторных работ, либо введите 'cancel'",
        reply_markup=get_list_of_numbers(list(range(1, subject.count + 1)))
    )


async def get_numbers_lab_subject(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Get numbers of lab of subject."""
    params = {
        "user_id": callback.from_user.id,
        "number": callback.data,
    }
    async with state.proxy() as data:
        params["subject_id"] = int(data["subject"])
    result = QueueActions.action_user(params)
    status = 'Добавлена' if result else 'Удалена'
    message = f"{status} {params['number']} лабораторная работа"
    await callback.message.answer(message)
    await state.finish()
    await callback.message.answer(
        get_subject_info(
            QueueActions.get_queue_info(callback.from_user.id)
        )
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

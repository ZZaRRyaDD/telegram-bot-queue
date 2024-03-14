from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.database import (
    GroupActions,
    QueueActions,
    ScheduleActions,
    SubjectActions,
)
from app.enums import ClientCommands, OtherCommands, SubjectCompact
from app.keywords import get_list_of_numbers, get_list_of_subjects
from app.services import check_user, member_group

QUEUE_TEXT = """
Выберите предмет.
При нажатии на номер работы вы встаете в очередь на нее.
При повторном нажатии вы выходите из очереди по данной работе.
"""


class StayQueue(StatesGroup):
    """FSM for stay in queue."""

    name = State()
    number = State()


async def get_subject_info(user_id: int) -> str:
    """Get info about subscribe subjects."""
    positions = await QueueActions.get_queue_info(user_id)
    if not positions:
        return "Вы не записаны ни на один предмет"
    info = "Вы записаны на следующие предметы:\n\n"
    processes = set()
    for position in positions:
        subject_id = position.subject_id
        if subject_id in processes:
            continue
        subject = await SubjectActions.get_subject(subject_id)
        numbers = sorted(
            filter(lambda x: x.subject_id == subject_id, positions),
            key=lambda x: x.number_practice,
        )
        in_queue, not_in_queue = list(), list()
        for item in numbers:
            if item.number_in_list is not None:
                in_queue.append(item)
            else:
                not_in_queue.append(item)
        in_queue.sort(key=lambda x: x.number_practice)
        not_in_queue.sort(key=lambda x: x.number_practice)
        numbers = list(map(lambda x: str(x.number_practice), not_in_queue))
        info += f"Дисциплина: {subject.name}\n"
        if numbers:
            info += f"Номера работ: {' '.join(numbers)}\n"
        if in_queue:
            list_labs = []
            template = "\tРабота №{0} - {1}"
            for item in in_queue:
                list_labs.append(template.format(
                    item.number_practice,
                    item.number_in_list,
                ))
            places = '\n'.join(list_labs)
            info += f"Текущая очередь:\n{places}\n"
        info += "\n"
        processes.add(subject_id)
    return info


async def start_stay_queue(message: types.Message) -> None:
    """Entrypoint for stay in queue."""
    if not member_group(message.from_user.id):
        await message.answer("Чтобы выбрать предмет, нужно выбрать группу")
        return
    subjects = set(
        subject.id for subject in (await GroupActions.get_group_by_user_id(
            message.from_user.id,
            subjects=True,
        )).subjects
    )
    schedule = set(
        schedule.subject_id
        for schedule in (await ScheduleActions.get_schedule(can_select=True))
    )
    access_subjects = subjects.intersection(schedule)
    if not access_subjects:
        await message.answer("Нет предметов, на которые можно записаться")
        return
    await message.answer(await get_subject_info(message.from_user.id))
    await StayQueue.name.set()
    access_subjects_list = [
        (await SubjectActions.get_subject(subject_id=subject_id))
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
    subject_id = callback.data
    await state.update_data(subject=subject_id)
    subject = await SubjectActions.get_subject(int(subject_id))
    await StayQueue.next()
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
        "subject_id": int((await state.get_data())["subject"]),
    }
    result = await QueueActions.action_user(params)
    message = ""
    if result is None:
        message = "В данный момент вы уже записаны в очередь на данную работу"
    else:
        status = 'Добавлена' if result else 'Удалена'
        message = f"{status} {params['number_practice']} работа"
    await callback.message.delete()
    await callback.message.answer(message)
    await state.finish()
    await callback.message.answer(
        await get_subject_info(callback.from_user.id),
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

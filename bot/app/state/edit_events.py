from datetime import date, timedelta

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.database import (
    GroupActions,
    ScheduleActions,
    SubjectActions,
    SubjectType,
    UserActions,
)
from app.enums import EventActionsEnum, HeadmanCommands, SubjectActionsEnum
from app.keywords import (
    event_action,
    get_list_of_subjects,
    remove_cancel,
    select_cancel,
    select_subject_type,
)
from app.services import check_headman_of_group

START_MESSAGE = """
Учтите, что при создании летней практики/курсовой работы/диплома
возможность его выбора появляется после 8:00 за день до проведения защиты.
Необходимо создать события заранее. В случае чего пишите админу.
"""


class Event(StatesGroup):
    """FSM for edit event."""

    action = State()
    name_update_delete = State()
    name_create = State()
    type_event = State()
    day_passage = State()


async def start_event(message: types.Message) -> None:
    """Entrypoint for subject."""
    await message.answer(START_MESSAGE)
    await Event.action.set()
    await message.answer(
        "Выберите действие",
        reply_markup=event_action(),
    )


async def input_action_event_create(callback: types.CallbackQuery) -> None:
    """Take name for new event."""
    await Event.name_create.set()
    await callback.message.delete()
    await callback.message.answer(
        "Введите название события",
        reply_markup=select_cancel(),
    )


async def input_action_event_update_delete(
    callback: types.CallbackQuery,
) -> None:
    """Get info for update/delete event."""
    subject_types = [
        SubjectType.COURSE_WORK,
        SubjectType.GRADUATE_WORK,
        SubjectType.SUMMER_PRACTICE,
    ]
    subjects = GroupActions.get_group_by_user_id(
        callback.from_user.id,
        subjects=True,
    ).subjects
    subjects = list(filter(
        lambda x: x.subject_type in subject_types,
        subjects,
    ))
    if not subjects:
        await callback.message.delete()
        await callback.message.answer("Изменять нечего.")
        await Event.action.set()
        await callback.message.answer(
            "Выберите действие",
            reply_markup=event_action(),
        )
        return
    await Event.name_update_delete.set()
    await callback.message.edit_text(
        "Выберите дисциплину",
        reply_markup=get_list_of_subjects(subjects),
    )


async def input_action_event(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input action for event."""
    await callback.answer()
    await state.update_data(action=callback.data)
    match callback.data:
        case EventActionsEnum.CREATE.action:
            await input_action_event_create(callback)
        case (
            EventActionsEnum.DELETE.action |
            EventActionsEnum.UPDATE.action
        ):
            await input_action_event_update_delete(callback)
        case EventActionsEnum.CANCEL.action:
            await callback.message.delete()
            await state.finish()


async def input_name_event(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Get name of new event."""
    group = GroupActions.get_group_by_user_id(
        message.from_user.id,
        subjects=True,
    )
    subject = list(filter(
        lambda x: x.name == message.text,
        group.subjects,
    ))
    if subject:
        await message.answer(
            (
                "Событие с таким названием уже есть в группе. "
                "Введите другое название."
            ),
            reply_markup=select_cancel(),
        )
        return
    await state.update_data({"name": message.text})
    await Event.type_event.set()
    await message.answer(
        "Выберите тип события",
        reply_markup=select_subject_type(),
    )


async def input_name_update_delete_event_update(callback: types.CallbackQuery) -> None:
    """Print schedule for subject and get action for it."""
    await callback.message.delete()
    await Event.type_event.set()
    await callback.message.answer(
        "Выберите тип события",
        reply_markup=select_subject_type(),
    )


async def input_name_update_delete_event_delete(
    callback: types.CallbackQuery,
    state: FSMContext,
    subject_id: int,
) -> None:
    """Delete event and bounded this it items."""
    SubjectActions.delete_subject(subject_id)
    await callback.message.edit_text("Событие успешно удалено")
    await state.finish()


async def input_name_update_delete_event(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input name of event."""
    await callback.answer()
    if callback.data == SubjectActionsEnum.CANCEL.action:
        await callback.message.delete()
        await state.finish()
        return
    group = GroupActions.get_group_by_user_id(
        callback.from_user.id,
        subjects=True,
    )
    subject = list(filter(
        lambda x: x.id == int(callback.data),
        group.subjects,
    ))[0]
    schedule = ScheduleActions.get_schedule(subject_id=subject.id)
    await state.update_data(
        name=subject.name,
        subject_id=subject.id,
        to_update=True,
        date_protection=schedule[-1].date_protection,
    )
    match (await state.get_data())["action"]:
        case EventActionsEnum.UPDATE.action:
            await input_name_update_delete_event_update(callback)
        case EventActionsEnum.DELETE.action:
            await input_name_update_delete_event_delete(
                callback,
                state,
                subject.id,
            )


def check_date_protection(date_protection: date) -> bool:
    return date.today() > date_protection - timedelta(days=2)


async def event_create(data, user, date_protection) -> None:
    subject_info = {
        "name": data['name'],
        "group_id": user.group_id,
        "count_practices": 1,
        "subject_type": data['subject_type'],
    }
    subject = SubjectActions.create_subject(subject_info)
    day = {
        "subject_id": subject.id,
        "date_protection": date_protection,
    }
    ScheduleActions.create_schedule(day)


async def event_update(data, user, date_protection) -> None:
    subject_info = {
        "name": data['name'],
        "group_id": user.group_id,
        "subject_type": data['subject_type'],
    }
    SubjectActions.update_subject(data.get("subject_id"), subject_info)
    subject = SubjectActions.get_subject(data.get("subject_id"))
    schedule = ScheduleActions.get_schedule(
        subject_id=data.get("subject_id"),
        date_protection=date_protection,
    )
    if not schedule:
        day = {
            "subject_id": subject.id,
            "date_protection": date_protection,
        }
        ScheduleActions.create_schedule(day)


async def input_type_event(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    await state.update_data(subject_type=callback.data)
    await callback.message.delete()
    data = await state.get_data()
    date_protection = data.get('date_protection')
    if date_protection is not None and check_date_protection(date_protection):
        await callback.message.answer(
            (
                "Поменять дату проведения нельзя из-за "
                "невозможности проведения очереди по данному "
                "событию из-за отсутствия времени."
            ),
        )
        user = UserActions.get_user(callback.from_user.id)
        await event_update(data, user, date_protection)
        action = "обновлен"
        await state.finish()
        await callback.message.answer(
            f"Событие {data['name']} успешно {action}.",
            reply_markup=remove_cancel(),
        )
        return
    await Event.day_passage.set()
    await callback.message.answer(
        "Введите дату проведения мероприятия в формате: дд.мм.гггг",
    )


async def input_day_passage(
    message: types.Message,
    state: FSMContext,
) -> None:
    input_date = message.text.split(".")
    try:
        date_protection = date(*list(map(int, input_date[::-1])))
    except Exception:
        await message.answer(
            "Дата введена не корректно. Введите корректную дату",
        )
        return
    if check_date_protection(date_protection):
        await message.answer(
            (
                "Дата проведения не может быть позже текущей даты. "
                "Введите корректную дату"
            ),
        )
        return
    user = UserActions.get_user(message.from_user.id)
    action, data = "", await state.get_data()
    match data.get("action"):
        case SubjectActionsEnum.CREATE.action:
            await event_create(data, user, date_protection)
            action = "создан"
        case SubjectActionsEnum.UPDATE.action:
            await event_update(data, user, date_protection)
            action = "обновлен"
    await state.finish()
    await message.answer(
        f"Событие {data['name']} успешно {action}.",
        reply_markup=remove_cancel(),
    )


def register_handlers_event(dispatcher: Dispatcher) -> None:
    """Register handlers for event."""
    dispatcher.register_message_handler(
        start_event,
        lambda message: check_headman_of_group(message.from_user.id),
        commands=[HeadmanCommands.EDIT_EVENT.command],
        state=None,
    )
    dispatcher.register_callback_query_handler(
        input_action_event,
        state=Event.action,
    )
    dispatcher.register_callback_query_handler(
        input_name_update_delete_event,
        state=Event.name_update_delete,
    )
    dispatcher.register_message_handler(
        input_name_event,
        state=Event.name_create,
    )
    dispatcher.register_callback_query_handler(
        input_type_event,
        state=Event.type_event,
    )
    dispatcher.register_message_handler(
        input_day_passage,
        state=Event.day_passage,
    )

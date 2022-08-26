import datetime
from dataclasses import dataclass

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import (
    CompletedPracticesActions,
    GroupActions,
    QueueActions,
    ScheduleActions,
    SubjectActions,
    UserActions,
)
from handlers import HeadmanCommands
from keywords import (
    ScheduleActionsEnum,
    SubjectActionsEnum,
    choice_schedule,
    schedule_action,
    select_days,
    select_subject_passes,
    subject_action,
)
from services import (
    check_headman_of_group,
    get_info_schedule,
    get_schedule_name,
)

FIRST_DAY = datetime.datetime(1970, 1, 1)
START_MESSAGE = """
Учтите, что при создании предмета возможность его выбора
появляется после 22:00 текущего дня (если еще нет 22:00),
либо следующего дня (если предмет создали после 22:00).
"""


@dataclass
class ScheduleCompact:
    """Class for send schedule in keyboard."""

    name: str
    id: int


class Subject(StatesGroup):
    """FSM for edit subject."""

    action = State()
    name = State()
    schedule_action = State()
    schedule_delete = State()
    week = State()
    days = State()
    count = State()


async def start_subject(message: types.Message) -> None:
    """Entrypoint for subject."""
    await message.answer(START_MESSAGE)
    await message.answer(
        "Выберите действие, либо введите 'cancel'",
        reply_markup=subject_action(),
    )


async def input_action_subject(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input action for subject."""
    async with state.proxy() as data:
        data["action"] = callback.data
    await Subject.name.set()
    await callback.message.answer(
        "Введите название дисциплины, либо введите 'cancel'",
    )


async def input_name_subject(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Input name of subject."""
    group = GroupActions.get_group(
        UserActions.get_user(message.from_user.id, subjects=False).group,
        subjects=True,
    )
    action = ""
    async with state.proxy() as data:
        action = data["action"]
    if message.text:
        match action:
            case SubjectActionsEnum.CREATE.action:
                if not list(filter(
                    lambda x: x.name.lower() == message.text.lower(),
                    group.subjects,
                )):
                    async with state.proxy() as data:
                        data["name"] = message.text
                        data["schedule"] = []
                    await Subject.next()
                    await message.answer(
                        (
                            "Выберите действие для расписания, "
                            "либо введите 'cancel'"
                        ),
                        reply_markup=schedule_action(),
                    )
                else:
                    await message.answer(
                        (
                            "Предмет с таким названием уже есть в группе."
                            "Введите другое название, либо введите 'cancel'"
                        ),
                    )
            case SubjectActionsEnum.UPDATE.action:
                subject = list(filter(
                    lambda x: x.name == message.text,
                    group.subjects,
                ))
                if subject:
                    schedule = list(map(
                        lambda x: x.__dict__,
                        ScheduleActions.get_schedule(subject[0].id)
                    ))
                    async with state.proxy() as data:
                        data["name"] = message.text
                        data["subject_id"] = subject[0].id
                        data["schedule"] = schedule
                    await Subject.next()
                    await message.answer(get_info_schedule(subject[0].id))
                    await message.answer(
                        (
                            "Выберите действие для расписания, "
                            "либо введите 'cancel'"
                        ),
                        reply_markup=schedule_action(
                            next_action=bool(schedule),
                        ),
                    )
                else:
                    await message.answer(
                        (
                            "Предмета с таким названием нет в группе. "
                            "Введите другое название, либо введите 'cancel'"
                        ),
                    )
            case SubjectActionsEnum.DELETE.action:
                subject = list(filter(
                    lambda x: x.name == message.text,
                    group.subjects,
                ))
                if subject:
                    QueueActions.cleaning_subject(subject[0].id)
                    CompletedPracticesActions.cleaning_subject(subject[0].id)
                    ScheduleActions.delete_schedule_by_subject(subject[0].id)
                    SubjectActions.delete_subject(subject[0].id)
                    await message.answer("Предмет успешно удален")
                    await state.finish()
                else:
                    await message.answer(
                        (
                            "Предмета с таким названием нет в группе. "
                            "Введите другое название, либо введите 'cancel'"
                        ),
                    )
    else:
        await message.answer(
            (
                "Название не корректно. "
                "Введите другое название, либо введите 'cancel'"
            ),
        )


async def input_schedule_action(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input action of schedule."""
    schedule = []
    async with state.proxy() as data:
        schedule = data["schedule"]
    match callback.data:
        case ScheduleActionsEnum.ADD.action:
            await Subject.week.set()
            await callback.message.answer(
                "Выберите, как будет проходить предмет, либо введите 'cancel'",
                reply_markup=select_subject_passes(),
            )
        case ScheduleActionsEnum.DELETE.action:
            if schedule:
                schedule_list = [
                    ScheduleCompact(name=get_schedule_name(item), id=item.id)
                    for item in schedule
                ]
                await Subject.schedule_delete.set()
                await callback.message.answer(
                    (
                        "Выберите расписание, которое нужно удалить, "
                        "либо введите 'cancel'"
                    ),
                    reply_markup=choice_schedule(schedule_list),
                )
            else:
                await callback.message.answer("Удалять нечего.")
                await Subject.schedule_action.set()
                await callback.message.answer(
                    "Выберите действие для расписания, либо введите 'cancel'",
                    reply_markup=schedule_action(),
                )
        case ScheduleActionsEnum.NEXT_ACTION.action:
            await Subject.count.set()
            await callback.message.answer(
                (
                    "Введите количество лабораторных работ, "
                    "либо введите 'cancel'"
                ),
            )


async def delete_schedule_action(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Delete schedule."""
    schedule = []
    async with state.proxy() as data:
        match data["action"]:
            case SubjectActionsEnum.UPDATE.action:
                ScheduleActions.delete_schedule_by_id(int(callback.data))
        data["schedule"] = list(filter(
            lambda x: x["id"] != int(callback.data),
            data["schedule"]
        ))
        schedule = data["schedule"]
    await Subject.schedule_action.set()
    await callback.message.answer(
        "Выберите действие для расписания, либо введите 'cancel'",
        reply_markup=schedule_action(bool(schedule)),
    )


async def input_week_subject(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input type of week of subject."""
    async with state.proxy() as data:
        data["on_even_week"] = (
            True
            if callback.data == "True"
            else False if callback.data == "False" else None
        )
    await Subject.next()
    await callback.message.answer(
        "Выберите дни, в которые будет проходить предмет с выбранной неделей",
        reply_markup=select_days(),
    )


async def input_date_subject(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input date of subject."""
    call_data = callback.data
    days = []
    schedule, new_schedules = [], []
    on_even_week = None
    async with state.proxy() as data:
        message = "Вы завершили выбор"
        if call_data != "Stop":
            if data.get("days") is None:
                data["days"] = [call_data]
                message = f"Добавлен {call_data} день"
            else:
                if call_data not in data["days"]:
                    data["days"].append(call_data)
                    message = f"Добавлен {call_data} день"
                else:
                    data["days"].remove(call_data)
                    message = f"Удален {call_data} день"
        days = data["days"] if data.get("days") else []
        await callback.message.answer(message)
        if call_data == "Stop":
            on_even_week = data["on_even_week"]
            for day in days:
                match data["action"]:
                    case SubjectActionsEnum.CREATE.action:
                        new_schedules.append(
                            {
                                "id": (
                                    datetime.datetime.now() - FIRST_DAY
                                ).total_seconds(),
                                "date_number": day,
                                "on_even_week": on_even_week,
                            }
                        )
                    case SubjectActionsEnum.UPDATE.action:
                        item = {
                            "date_number": day,
                            "on_even_week": on_even_week,
                            "subject_id": data["subject_id"],
                        }
                        new_schedules.append(
                            ScheduleActions.create_schedule(item)
                        )
            data["schedule"].extend(new_schedules)
            schedule = data["schedule"]
    await callback.answer()
    if call_data == "Stop":
        if days:
            await Subject.schedule_action.set()
            await message.answer(
                "Выберите действие для расписания, либо введите 'cancel'",
                reply_markup=schedule_action(next_action=bool(schedule)),
            )
        else:
            await callback.message.answer(
                (
                    "Выберите дни недели, в которые проходит дисциплина,"
                    " либо введите 'cancel'"
                ),
            )


async def input_count_lab_subject(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Input count of lab of subject."""
    count = message.text
    if count.isdigit():
        count = int(count)
        if count > 0:
            group = UserActions.get_user(
                message.from_user.id,
                subjects=False,
            ).group
            subject_name = ""
            action = ""
            async with state.proxy() as data:
                match data["action"]:
                    case SubjectActionsEnum.CREATE.action:
                        subject_info = {
                            "name": data["name"],
                            "group": group,
                            "count": count,
                        }
                        subject = SubjectActions.create_subject(subject_info)
                        for day in data["schedule"]:
                            day.pop("id")
                            day["subject_id"] = subject.id
                            ScheduleActions.create_schedule(day)
                        action = "создан"
                    case SubjectActionsEnum.UPDATE.action:
                        subject_info = {
                            "name": data["name"],
                            "group": group,
                            "count": count,
                        }
                        subject = SubjectActions.update_subject(subject_info)
                        action = "обновлен"
                subject_name = data["name"]
            await state.finish()
            await message.answer(
                f"Предмет {subject_name} успешно {action}.",
            )
        else:
            await message.answer(
                "Введите количество лабораторных работ, либо введите 'cancel'"
            )
    else:
        await message.answer(
            "Введите количество лабораторных работ, либо введите 'cancel'"
        )


def register_handlers_subject(dispatcher: Dispatcher) -> None:
    """Register handlers for subject."""
    dispatcher.register_message_handler(
        start_subject,
        lambda message: check_headman_of_group(message.from_user.id),
        commands=[HeadmanCommands.EDIT_SUBJECT.command],
        state=None,
    )
    dispatcher.register_callback_query_handler(
        input_action_subject,
        state=Subject.action,
    )
    dispatcher.register_message_handler(
        input_name_subject,
        state=Subject.name,
    )
    dispatcher.register_callback_query_handler(
        input_schedule_action,
        state=Subject.schedule_action,
    )
    dispatcher.register_callback_query_handler(
        delete_schedule_action,
        state=Subject.schedule_delete,
    )
    dispatcher.register_callback_query_handler(
        input_week_subject,
        state=Subject.week,
    )
    dispatcher.register_callback_query_handler(
        input_date_subject,
        state=Subject.days,
    )
    dispatcher.register_message_handler(
        input_count_lab_subject,
        state=Subject.count,
    )

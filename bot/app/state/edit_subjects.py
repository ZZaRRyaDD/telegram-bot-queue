import datetime
from typing import Optional, Union

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.database import (
    CompletedPracticesActions,
    GroupActions,
    ScheduleActions,
    SubjectActions,
    SubjectType,
    UserActions,
)
from app.enums import (
    HeadmanCommands,
    ScheduleActionsEnum,
    ScheduleCompact,
    SubjectActionsEnum,
)
from app.keywords import (
    choice_schedule,
    get_list_of_subjects,
    remove_cancel,
    schedule_action,
    select_cancel,
    select_days,
    select_subject_passes,
    subject_action,
)
from app.services import (
    check_headman_of_group,
    get_info_schedule,
    get_schedule_name,
)

FIRST_DAY = datetime.datetime(1970, 1, 1)
DAY_WEEKS_NUMBERS = list(range(0, 7))
START_MESSAGE = """
Учтите, что при создании предмета возможность его выбора
появляется после 8:00 текущего дня (если еще нет 8:00),
либо следующего дня (если предмет создали после 8:00).
"""


def nice_schedule(
    schedule: list,
    day: int,
    on_even_week: Optional[bool],
) -> bool:
    """Check schedule to exists."""
    return not bool(list(filter(
        lambda x: (
            int(x["date_number"]) == int(day) and
            x["on_even_week"] == on_even_week
        ),
        schedule,
    )))


def is_true_value(value: Union[int, str]) -> bool:
    """Check value of day."""
    if not value.isdigit():
        return False
    if int(value) not in DAY_WEEKS_NUMBERS:
        return False
    return True


class Subject(StatesGroup):
    """FSM for edit subject."""

    action = State()
    name_update_delete = State()
    name_create = State()
    schedule_action = State()
    schedule_delete = State()
    week = State()
    days = State()
    count = State()


async def start_subject(message: types.Message) -> None:
    """Entrypoint for subject."""
    await message.answer(START_MESSAGE)
    await Subject.action.set()
    await message.answer(
        "Выберите действие",
        reply_markup=subject_action(),
    )


async def input_action_subject_create(callback: types.CallbackQuery) -> None:
    """Take name for new subject."""
    await Subject.name_create.set()
    await callback.message.delete()
    await callback.message.answer(
        "Введите название дисциплины",
        reply_markup=select_cancel(),
    )


async def input_action_subject_update_delete(
    callback: types.CallbackQuery,
) -> None:
    """Get info for update/delete subject."""
    subject_types = [
        SubjectType.LABORATORY_WORK,
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
        await Subject.action.set()
        await callback.message.answer(
            "Выберите действие",
            reply_markup=subject_action(),
        )
        return
    await Subject.name_update_delete.set()
    await callback.message.edit_text(
        "Выберите дисциплину",
        reply_markup=get_list_of_subjects(subjects),
    )


async def input_action_subject(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input action for subject."""
    await state.update_data(action=callback.data)
    match callback.data:
        case SubjectActionsEnum.CREATE.action:
            await input_action_subject_create(callback)
        case (
            SubjectActionsEnum.DELETE.action |
            SubjectActionsEnum.UPDATE.action
        ):
            await input_action_subject_update_delete(callback)
        case SubjectActionsEnum.CANCEL.action:
            await callback.message.delete()
            await state.finish()


async def input_name_update_delete_subject_update(
    callback: types.CallbackQuery,
    subject: Subject,
) -> None:
    """Print schedule for subject and get action for it."""
    await callback.message.delete()
    await callback.message.answer(
        get_info_schedule(subject),
    )
    await Subject.schedule_action.set()
    await callback.message.answer(
        "Выберите действие для предмета",
        reply_markup=schedule_action(),
    )


async def input_name_update_delete_subject_delete(
    callback: types.CallbackQuery,
    state: FSMContext,
    subject_id: int,
) -> None:
    """Delete subject and bounded this it items."""
    SubjectActions.delete_subject(subject_id)
    await callback.message.edit_text("Предмет успешно удален")
    await state.finish()


async def input_name_update_delete_subject(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input name of subject."""
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
    schedule = list(map(
        lambda x: x.__dict__,
        ScheduleActions.get_schedule(subject_id=subject.id),
    ))
    for item in schedule:
        item.pop("_sa_instance_state")
        item.pop("subject")
    await state.update_data(
        name=subject.name,
        schedule=schedule,
        subject_id=subject.id,
        to_update=True,
    )
    match (await state.get_data())["action"]:
        case SubjectActionsEnum.UPDATE.action:
            await input_name_update_delete_subject_update(
                callback,
                subject,
            )
        case SubjectActionsEnum.DELETE.action:
            await input_name_update_delete_subject_delete(
                callback,
                state,
                subject.id,
            )


async def input_name_subject(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Get name of new or exists subject."""
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
                "Предмет с таким названием уже есть в группе. "
                "Введите другое название."
            ),
            reply_markup=select_cancel(),
        )
        return
    data = await state.get_data()
    if data.get("to_update", False) is not True:
        await state.update_data({"schedule": []})
    await state.update_data({"name": message.text})
    subject_id = data.get("subject_id", None)
    if subject_id is not None:
        subject = SubjectActions.get_subject(subject_id=subject_id)
        await message.answer(get_info_schedule(subject))
    await Subject.schedule_action.set()
    await message.answer(
        "Выберите действие для предмета",
        reply_markup=schedule_action(),
    )


async def input_action_schedule_add(
    callback: types.CallbackQuery,
) -> None:
    """Take type of week."""
    await Subject.week.set()
    await callback.message.edit_text(
        "Выберите, как будет проходить предмет",
        reply_markup=select_subject_passes(),
    )


async def input_action_schedule_delete(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Get schedule for delete."""
    schedule = (await state.get_data())["schedule"]
    if schedule:
        schedule_list = [
            ScheduleCompact(
                name=get_schedule_name(item),
                id=item["id"],
            )
            for item in schedule
        ]
        await Subject.schedule_delete.set()
        await callback.message.edit_text(
            "Выберите расписание, которое нужно удалить",
            reply_markup=choice_schedule(schedule_list),
        )
        return
    await callback.message.delete()
    await callback.message.answer(
        "Удалять нечего.",
    )
    await Subject.schedule_action.set()
    await callback.message.answer(
        "Выберите действие для предмета",
        reply_markup=schedule_action(),
    )


async def input_action_schedule_next_action(
    callback: types.CallbackQuery,
) -> None:
    """Take count lab work."""
    await Subject.count.set()
    await callback.message.delete()
    await callback.message.answer(
        "Введите количество лабораторных работ",
        reply_markup=select_cancel(),
    )


async def input_action_schedule(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input action of schedule."""
    await callback.answer()
    match callback.data:
        case ScheduleActionsEnum.ADD.action:
            await input_action_schedule_add(callback)
        case ScheduleActionsEnum.DELETE.action:
            await input_action_schedule_delete(callback, state)
        case ScheduleActionsEnum.NEXT_ACTION.action:
            await input_action_schedule_next_action(callback)
        case ScheduleActionsEnum.CANCEL.action:
            await callback.message.edit_text("Действие отменено")
            await state.finish()


async def delete_schedule_action(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Delete schedule."""
    await callback.message.delete()
    if callback.data != SubjectActionsEnum.CANCEL.action:
        data = await state.get_data()
        subject_id = data.get("subject_id", None)
        new_schedule = data["schedule"][::]
        for index, day in enumerate(data.get("schedule")):
            if str(day['id']) == str(callback.data):
                new_schedule.pop(index)
                break
        await state.update_data({"schedule": new_schedule})
        if subject_id is not None:
            ScheduleActions.delete_schedule_by_id(int(callback.data))
            subject = SubjectActions.get_subject(subject_id=subject_id)
            await callback.message.answer(get_info_schedule(subject))
    await Subject.schedule_action.set()
    await callback.message.answer(
        "Выберите действие для предмета",
        reply_markup=schedule_action(),
    )


async def input_week_subject(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input type of week of subject."""
    await callback.answer()
    on_even_week = (
        True
        if callback.data == "True"
        else False if callback.data == "False" else None
    )
    await state.update_data({"on_even_week": on_even_week})
    data = await state.get_data()
    if data.get("to_update", False):
        schedule = data["schedule"]
        this_week = list(filter(
            lambda x: x["on_even_week"] is on_even_week,
            schedule,
        ))
        if this_week:
            days = list(map(lambda x: int(x["date_number"]), this_week))
            await state.update_data(days=days)
    await Subject.days.set()
    await callback.message.edit_text(
        "Выберите дни, в которые будет проходить предмет с выбранной неделей",
        reply_markup=select_days(),
    )


async def input_date_subject(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input date of subject."""
    await callback.answer()
    new_schedules, days, data = [], [], await state.get_data()
    message = "Вы завершили выбор"
    if callback.data != "Stop":
        if is_true_value(callback.data):
            day = int(callback.data)
            exists_days = data.get("days", None)
            if exists_days is None:
                await state.update_data({"days": [day]})
                message = f"Добавлен {day} день"
            else:
                if nice_schedule(
                    data.get("schedule"),
                    day,
                    data.get("on_even_week"),
                ):
                    if day not in exists_days:
                        await state.update_data(
                            {"days": exists_days + [day]}
                        )
                        message = f"Добавлен {day} день"
                    else:
                        exists_days.remove(day)
                        await state.update_data({"days": exists_days})
                        message = f"Удален {day} день"
                else:
                    message = "Расписание с такими параметрами уже существует"
        else:
            message = "Попробуйте выбрать другое значение"
    days = data.get("days", [])
    await callback.message.answer(message)
    if callback.data == "Stop":
        subject_id = data.get("subject_id", None)
        on_even_week = data.get("on_even_week")
        schedule = data.get("schedule")
        for day in days:
            match data.get("action"):
                case SubjectActionsEnum.CREATE.action:
                    schedule_id = str((
                        datetime.datetime.now() - FIRST_DAY
                    ).total_seconds())
                    new_schedules.append(
                        {
                            "id": schedule_id,
                            "date_number": int(day),
                            "on_even_week": on_even_week,
                        }
                    )
                case SubjectActionsEnum.UPDATE.action:
                    item = {
                        "date_number": int(day),
                        "on_even_week": on_even_week,
                        "subject_id": subject_id,
                    }
                    if nice_schedule(
                        schedule,
                        day,
                        on_even_week,
                    ):
                        new_schedule = ScheduleActions.create_schedule(item).__dict__
                        new_schedule.pop("_sa_instance_state")
                        new_schedule.pop("subject")
                        new_schedules.append(new_schedule)
        await state.update_data(
            schedule=schedule + new_schedules,
            days=[],
        )
        if subject_id is not None:
            subject = SubjectActions.get_subject(subject_id=subject_id)
            await callback.message.answer(get_info_schedule(subject))
        await Subject.schedule_action.set()
        await callback.message.delete()
        await callback.message.answer(
            "Выберите действие для расписания",
            reply_markup=schedule_action(),
        )
        return


async def input_count_lab_subject_create(
    name: str,
    group: int,
    count: int,
    schedule: list,
) -> None:
    """Add schedule when create subject."""
    subject_info = {
        "name": name,
        "group_id": group,
        "count_practices": count,
        "subject_type": SubjectType.LABORATORY_WORK,
    }
    subject = SubjectActions.create_subject(subject_info)
    for day in schedule:
        day.pop("id")
        day["subject_id"] = subject.id
        ScheduleActions.create_schedule(day)


async def input_count_lab_subject_update(
    name: str,
    group: int,
    count: int,
    subject_id: int,
) -> None:
    """Add schedule when update subject."""
    subject_info = {
        "name": name,
        "group_id": group,
        "count_practices": count,
        "subject_type": SubjectType.LABORATORY_WORK,
    }
    SubjectActions.update_subject(subject_id, subject_info)


async def input_count_lab_subject(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Input count of lab of subject."""
    if not message.text.isdigit():
        await message.answer(
            "Введите количество лабораторных работ",
            reply_markup=select_cancel(),
        )
        return
    if int(message.text) <= 0:
        await message.answer(
            "Введите количество лабораторных работ",
            reply_markup=select_cancel(),
        )
        return
    group = UserActions.get_user(message.from_user.id).group_id
    action, data = "", await state.get_data()
    name = data['name']
    count = int(message.text)
    match data.get("action"):
        case SubjectActionsEnum.CREATE.action:
            await input_count_lab_subject_create(
                name,
                group,
                count,
                data.get("schedule"),
            )
            action = "создан"
        case SubjectActionsEnum.UPDATE.action:
            old_count = SubjectActions.get_subject(
                data.get("subject_id")
            ).count_practices
            await input_count_lab_subject_update(
                name,
                group,
                count,
                data.get("subject_id"),
            )
            if old_count > count:
                for lab in range(count + 1, old_count + 1):
                    CompletedPracticesActions.remove_completed_practices_labs(
                        {
                            "subject_id": data.get("subject_id"),
                            "number_practice": lab,
                        },
                    )
            action = "обновлен"
    await state.finish()
    await message.answer(
        f"Предмет {name} успешно {action}.",
        reply_markup=remove_cancel(),
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
    dispatcher.register_callback_query_handler(
        input_name_update_delete_subject,
        state=Subject.name_update_delete,
    )
    dispatcher.register_message_handler(
        input_name_subject,
        state=Subject.name_create,
    )
    dispatcher.register_callback_query_handler(
        input_action_schedule,
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

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import DateActions, GroupActions, SubjectActions, UserActions
from keywords import select_days, select_subject_passes
from services import check_headman_of_group

START_MESSAGE = """
Учтите, что при создании предмета возможность его выбора
появляется после 22:00 текущего дня (если еще нет 22:00),
либо следующего дня (если предмет создали после 22:00).

Если у предмета сложное расписание, типа:
каждую неделю в пн и ср и в пт и сб по четным неделям, то лучше сделать так:
название_предмета_1 поставить на каждую неделю по пн и ср
и название_предмета_2 поставить по четным неделям в пт и сб
"""


class Subject(StatesGroup):
    """FSM for create and edit group."""

    name = State()
    days = State()
    count = State()
    week = State()


async def start_subject(message: types.Message) -> None:
    """Entrypoint for subject."""
    await message.answer(START_MESSAGE)
    await Subject.name.set()
    await message.answer("Введите название дисциплины, либо 'cancel'")


async def input_name_subject(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Input name of subject."""
    group = GroupActions.get_group(
        UserActions.get_user(message.from_user.id, subjects=False).group,
        subjects=True,
    )
    if not list(filter(
        lambda x: x.name.lower() == message.text.lower(), group.subjects
    )) and message.text:
        async with state.proxy() as data:
            data["name"] = message.text
        await Subject.next()
        await message.answer(
            (
                "Выберите дни недели, в которые проходит дисциплина, "
                "либо введите 'cancel'"
            ),
            reply_markup=select_days(),
        )
    else:
        await message.answer(
            (
                "Предмет с аналогичным названием уже есть в группе, "
                "либо название не корректно. "
                "Введите другое название, либо введите 'cancel'"
            )
        )


async def input_date_subject(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input date of subject."""
    call_data = callback.data
    new_days = {"days": []}
    async with state.proxy() as data:
        message = "Завершили выбор"
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
        new_days["days"] = data["days"] if data.get("days") else []
        await callback.message.answer(message)
    await callback.answer()
    if call_data == "Stop":
        if new_days["days"]:
            await Subject.next()
            await callback.message.answer(
                "Введите количество лабораторных работ, либо введите 'cancel'"
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
            async with state.proxy() as data:
                data["count"] = count
            await Subject.next()
            await message.answer(
                "Выберите, как будет проходить предмет, либо введите 'cancel'",
                reply_markup=select_subject_passes(),
            )
        else:
            await message.answer(
                "Введите количество лабораторных работ, либо введите 'cancel'"
            )
    else:
        await message.answer(
            "Введите количество лабораторных работ, либо введите 'cancel'"
        )


async def input_week_subject(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """Input type of week of subject."""
    data = callback.data
    new_subject = {
        "on_even_week": (
            True
            if data == "True"
            else False if data == "False" else None
        ),
    }
    days = []
    async with state.proxy() as data:
        new_subject["name"] = data["name"]
        new_subject["count"] = data["count"]
        days = data["days"] if data.get("days") else []
    new_subject["group"] = UserActions.get_user(
        callback.from_user.id,
        subjects=False,
    ).group
    subject = SubjectActions.create_subject(new_subject)
    for day in days:
        DateActions.create_date(
            {
                "number": int(day),
                "subject": subject.id,
            },
        )
    await state.finish()
    await callback.message.answer(
        f"Предмет {new_subject['name']} успешно добавлен в группу.",
    )


def register_handlers_subject(dispatcher: Dispatcher) -> None:
    """Register handlers for subject."""
    dispatcher.register_message_handler(
        start_subject,
        lambda message: check_headman_of_group(message.from_user.id),
        commands=["add_subject"],
        state=None,
    )
    dispatcher.register_message_handler(
        input_name_subject,
        state=Subject.name,
    )
    dispatcher.register_callback_query_handler(
        input_date_subject,
        state=Subject.days,
    )
    dispatcher.register_message_handler(
        input_count_lab_subject,
        state=Subject.count,
    )
    dispatcher.register_callback_query_handler(
        input_week_subject,
        state=Subject.week,
    )

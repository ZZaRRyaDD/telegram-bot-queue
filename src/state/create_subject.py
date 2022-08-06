from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import DateActions, GroupActions, SubjectActions, UserActions
from keywords import select_days
from services import check_headman_of_group

START_MESSAGE = """
Учтите, что при создании предмета возможность его выбора
появляется после 22:00 текущего дня (если еще нет 22:00), либо
следующего дня (если предмет создали после 22:00)
"""


class Subject(StatesGroup):
    """FSM for create and edit group."""

    name = State()
    days = State()
    count = State()


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
        if call_data != "Stop":
            if data.get("days") is None:
                data["days"] = [call_data]
            else:
                if call_data not in data["days"]:
                    data["days"].append(call_data)
                else:
                    data["days"].remove(call_data)
        new_days["days"] = data["days"] if data.get("days") else []
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
    new_subject = {}
    new_days = {"days": []}
    count = message.text
    async with state.proxy() as data:
        new_subject["name"] = data["name"]
        new_days["days"] = data["days"] if data.get("days") else []
    if count.isdigit():
        count = int(count)
        if count > 0:
            new_subject["count"] = count
            new_subject["group"] = UserActions.get_user(
                message.from_user.id,
                subjects=False,
            ).group
            subject = SubjectActions.create_subject(new_subject)
            for day in new_days["days"]:
                DateActions.create_date(
                    {
                        "number": int(day),
                        "subject": subject.id,
                    },
                )
            await message.answer(
                "Предмет успешно добавлен в группу.",
            )
            await state.finish()
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

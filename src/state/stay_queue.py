from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import GroupActions, QueueActions, UserActions
from keywords import get_list_of_subjects
from services import check_user, member_group

QUEUE_TEXT = """
Выберите предмет.
Если вы еще не вставали в очередь:
- при нажатии на предмет вы встаете в очередь на него
- при повторном нажатии вы отменяется поставку в очередь
- по окончании действий нажмите кнопку 'Остановить выбор'
Если вы уже вставали в очередь:
- нажмите на предмет, чтобы уйти с очереди по нему
(если предмет был выбран ранее)
- нажмите на предмет, чтобы встать в очередь по нему
(если предмет не был выбран ранее)
- по окончании действий нажмите кнопку 'Остановить выбор'
В любом момент вы можете напечатать 'cancel', чтобы отменить процедуру
"""


class StayQueue(StatesGroup):
    """FSM for stay in queue."""

    name = State()


def get_subject_info(user) -> str:
    """Get info about subscribe subjects."""
    if not user.subjects:
        return "Вы не записаны ни на один предмет"
    info = "Вы записаны на следующие предметы:\n"
    for subject in user.subjects:
        info += f"{subject.name}\n"
    return info


async def start_stay_queue(message: types.Message) -> None:
    """Entrypoint for stay in queue."""
    if member_group(message.from_user.id):
        subjects = GroupActions.get_group(
            UserActions.get_user(message.from_user.id, subjects=False).group,
            subjects=True,
        ).subjects
        access_subjects = list(filter(
            lambda subject: subject.can_select, subjects
        ))
        if access_subjects:
            await message.answer(
                get_subject_info(
                    UserActions.get_user(message.from_user.id, subjects=True)
                )
            )
            await StayQueue.name.set()
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
    subjects = []
    async with state.proxy() as data:
        if call_data != "Stop":
            if data.get("subjects") is None:
                data["subjects"] = [call_data]
            else:
                if call_data in data["subjects"]:
                    data["subjects"].remove(call_data)
                else:
                    data["subjects"].append(call_data)
        subjects = data["subjects"] if data.get("subjects") else []
        await callback.answer()
    if call_data == "Stop":
        for subject in subjects:
            params = {
                "user_id": callback.from_user.id,
                "subject_id": int(subject),
            }
            QueueActions.action_user(params)
        await callback.message.answer(
            get_subject_info(
                UserActions.get_user(callback.from_user.id, subjects=True)
            )
        )
        await state.finish()


def register_handlers_stay_queue(dispatcher: Dispatcher) -> None:
    """Register handlers for select subjects."""
    dispatcher.register_message_handler(
        start_stay_queue,
        lambda message: check_user(message.from_user.id),
        commands=["stay_queue"],
        state=None,
    )
    dispatcher.register_callback_query_handler(
        get_subject_name,
        state=StayQueue.name,
    )

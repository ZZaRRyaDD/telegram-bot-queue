import datetime
import random

from aiogram import Bot
from aiogram.utils.exceptions import BotBlocked

from app.database import (
    GroupActions,
    QueueActions,
    ScheduleActions,
    SubjectActions,
    SubjectType,
    UserActions,
)

from .services import is_event_week

SATURDAY = 5
DAYS_BEFORE_SUBJECT = 1


async def send_message_users(message: str, bot: Bot) -> None:
    """Function for send message for users with group."""
    schedules = ScheduleActions.get_schedule(can_select=True)
    if schedules:
        groups = []
        for schedule in schedules:
            groups.append(
                SubjectActions.get_subject(schedule.subject_id).group_id
            )
        groups = set(groups)
        if groups:
            for group_id in groups:
                group = GroupActions.get_group(
                    group_id=group_id,
                    students=True,
                )
                for student in group.students:
                    try:
                        await bot.send_message(
                            student.id,
                            message,
                        )
                    except BotBlocked:
                        pass


async def activate_after_tomorrow_subjects() -> None:
    """Function for activate next subjects."""
    after_tomorrow = datetime.date.today() + datetime.timedelta(
        days=DAYS_BEFORE_SUBJECT,
    )
    dates = set([
        date.id
        for date in ScheduleActions.get_schedule(
            date_number=after_tomorrow.weekday(),
        )
    ])
    dates_protection = set([
        date.id
        for date in ScheduleActions.get_schedule(
            date_protection=after_tomorrow,
        )
    ])
    dates |= dates_protection
    for date in dates:
        ScheduleActions.change_status_subjects(True, schedule_id=date)
    ScheduleActions.change_status_subjects(
        False,
        on_even_week=str(not bool(is_event_week(after_tomorrow))),
    )


async def send_reminder(bot: Bot) -> None:
    """Send remind for stay in queue."""
    await send_message_users(
        "Не забудь записаться на сдачу лабораторной работы. В 8:00 будут результаты",
        bot,
    )


async def send_top(bot: Bot) -> None:
    """Send result queue."""
    QueueActions.cleaning_subject()
    schedule = ScheduleActions.get_schedule(can_select=True)
    subject_template = "Очередь по дисциплине {0}\n{1}"
    lab_template = "Лабораторная работа №{0}\n{1}\n\n"
    event_template = "{0} {1}\n{2}\n\n"
    if schedule:
        for subject_id in [item.subject_id for item in schedule]:
            subject = SubjectActions.get_subject(
                subject_id=subject_id,
                users_practice=True,
            )
            if not subject.users_practice:
                continue
            group = GroupActions.get_group(
                group_id=subject.group_id,
                students=True,
            )
            all_users = group.students
            list_labs = []
            for number in range(1, subject.count_practices + 1):
                params = {
                    "subject_id": subject.id,
                    "number_practice": number,
                }
                users = QueueActions.get_users_by_number(params)
                if users:
                    if group.random_queue:
                        random.shuffle(users)
                    list_queue = "".join([
                        f"{index + 1}. {UserActions.get_user(id).full_name}\n"
                        for index, id in enumerate(users)
                    ])
                    if subject.subject_type == SubjectType.LABORATORY_WORK:
                        list_labs.append(
                            lab_template.format(number, list_queue)
                        )
                    else:
                        list_labs.append(
                            event_template.format(
                                subject.subject_type,
                                subject.name,
                                list_queue,
                            )
                        )
                for index, user in enumerate(users, 1):
                    params["number_in_list"] = index
                    params["user_id"] = user
                    QueueActions.update_queue_info(params)
            for student in all_users:
                try:
                    await bot.send_message(
                        student.id,
                        subject_template.format(
                            subject.name,
                            "".join(list_labs),
                        )
                    )
                except BotBlocked:
                    pass
    ScheduleActions.change_status_subjects(False, can_select_to_change=True)
    await activate_after_tomorrow_subjects()
    await send_message_users(
        "Запись на следующие лабораторные работы доступна",
        bot,
    )

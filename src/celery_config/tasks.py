import asyncio
import datetime
import random

from ..database import (
    GroupActions,
    QueueActions,
    ScheduleActions,
    SubjectActions,
    UserActions,
)
from ..main import bot
from .celery_app import app
from .services import is_event_week

SATURDAY = 5


def send_message_users(message: str) -> None:
    """Function for send message for users with group."""
    schedules = ScheduleActions.get_schedule(can_select=True)
    if schedules:
        groups = []
        for schedule in schedules:
            groups.append(
                SubjectActions.get_subject(schedule.subject_id).group
            )
        groups = set(groups)
        if groups:
            for group_id in groups:
                group = GroupActions.get_group(id=group_id, students=True)
                for student in group.students:
                    asyncio.run(bot.send_message(
                        student.id,
                        message,
                    ))


def activate_after_tomorrow_subjects() -> None:
    """Function for activate next subjects."""
    after_tomorrow = datetime.date.today() + datetime.timedelta(days=2)
    dates = ScheduleActions.get_schedule(date_number=after_tomorrow.weekday())
    if dates:
        for date in dates:
            ScheduleActions.change_status_subjects(
                date.subject_id,
                True,
            )
        ScheduleActions.change_status_subjects(
            str(not bool(is_event_week(after_tomorrow))),
            False,
        )


@app.task(task_ignore_result=True)
def send_reminder() -> None:
    """Send remind for stay in queue."""
    if datetime.date.today().weekday() != SATURDAY:
        send_message_users(
            "Не забудь записаться на сдачу лабы. В 22:00 будут результаты",
        )


@app.task(task_ignore_result=True)
def send_top() -> None:
    """Send result queue."""
    subjects = ScheduleActions.get_schedule(can_select=True)
    subject_template = "Очередь по дисциплине {0}\n{1}"
    lab_template = "Лабораторная работа №{0}\n{1}\n\n"
    if subjects:
        for subject_id in subjects:
            subject = SubjectActions.get_subject(
                subject_id,
                users_practice=True,
            )
            if not subject.users_practice:
                continue
            all_users = []
            list_labs = []
            for number in range(1, subject.count + 1):
                params = {
                    "subject_id": subject.id,
                    "number": number,
                }
                users = QueueActions.get_users_by_number(params)
                if users:
                    all_users.extend(users)
                    random.shuffle(users)
                    list_queue = "".join([
                        f"{index + 1}. {UserActions.get_user(id).full_name}\n"
                        for index, id in enumerate(users)
                    ])
                    list_labs.append(
                        lab_template.format(number, list_queue)
                    )
            all_users = set(all_users)
            for user in all_users:
                asyncio.run(bot.send_message(
                    user,
                    subject_template.format(
                        subject.name,
                        "".join(list_labs),
                    )
                ))
            QueueActions.cleaning_subject(subject.id)
    ScheduleActions.change_status_subjects(True, False)
    activate_after_tomorrow_subjects()
    if datetime.date.today().weekday() + 1 != SATURDAY:
        send_message_users("Запись на следующие лабораторные работы доступна")

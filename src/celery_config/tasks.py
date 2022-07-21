import asyncio
import datetime
import random

from ..database import DateActions, QueueActions, SubjectActions, UserActions
from ..main import bot
from .celery_app import app


@app.task(task_ignore_result=True)
def send_reminder():
    """Send remind for stay in queue."""
    users = UserActions.get_users_with_group()
    if users:
        for user in users:
            asyncio.run(bot.send_message(
                user.id,
                "Не забудь записаться на сдачу лабы. В 22:00 будут результаты"
            ))


@app.task(task_ignore_result=True)
def send_top():
    """Send result queue."""
    subjects = SubjectActions.get_subjects(True, users=True)
    subject_template = "Очередь по дисциплине {0}\n{1}"
    lab_template = (
        "Лабораторная работа №{0}\n{1}\n\n"
    )
    if subjects:
        for subject in subjects:
            if not subject.users:
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
    SubjectActions.change_status_subjects(True, False)
    dates = DateActions.get_dates(
        (datetime.date.today() + datetime.timedelta(days=1)).weekday()
    )
    if dates:
        for date in dates:
            SubjectActions.change_status_subjects(
                date.subject,
                True,
            )

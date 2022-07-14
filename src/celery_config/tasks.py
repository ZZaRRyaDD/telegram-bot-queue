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
    template = (
        "Очередь по дисциплине {0}\n"
        "Ваша позиция в очереди: {1}\n\nВся очередь: {2}"
    )
    if subjects:
        for subject in subjects:
            if not subject.users:
                continue
            users = subject.users[::]
            random.shuffle(users)
            list_queue = "".join([
                f"{index + 1}. {user.full_name}\n"
                for index, user in enumerate(users)
            ])
            for index, user in enumerate(users):
                asyncio.run(bot.send_message(
                    user.id,
                    template.format(subject.name, index + 1, list_queue)
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

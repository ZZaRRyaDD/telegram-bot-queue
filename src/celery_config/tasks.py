import asyncio
import random

from ..database import SubjectActions, UserActions
from ..main import bot
from .celery_app import app


@app.task(task_ignore_result=True)
def send_reminder():
    """Send remind for stay in queue."""
    users = UserActions.get_users()
    if users:
        users = list(filter(lambda user: user.group is not None, users))
        for user in users:
            asyncio.run(bot.send_message(
                user.id,
                "Не забудь записаться на сдачу лабы. В 22:00 будут результаты"
            ))


@app.task(task_ignore_result=True)
def send_top():
    """Send result queue."""
    subjects = SubjectActions.get_subjects()
    if subjects:
        for subject in subjects:
            if not subjects.users:
                continue
            users = subject.users[::]
            random.shuffle(users)
            list_queue = "".join([
                f"{index + 1}. {user.full_name}\n"
                for index, user in enumerate(users)
            ])
            template = """
            Очередь по дисциплине {0}\n
            Ваша позиция в очереди: {1}\n\n
            Вся очередь:\n{2}
            """
            for index, user in enumerate(users):
                asyncio.run(bot.send_message(
                    user.id,
                    template.format(subject.name, index + 1, list_queue)
                ))
            SubjectActions.clear_subject_queue(subject.id)

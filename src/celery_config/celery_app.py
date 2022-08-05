import os

from celery import Celery
from celery.schedules import crontab

app = Celery(
    'celery_config',
    broker=(
        os.getenv("REDIS_URL")
    ),
    include=["src.celery_config.tasks"],
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Krasnoyarsk',
    enable_utc=True,
)

app.conf.beat_schedule = {
   'send-reminder': {
        'task': 'src.celery_config.tasks.send_reminder',
        'schedule': crontab(minute=0, hour="12, 17, 21"),
    },
   'send-top': {
        'task': 'src.celery_config.tasks.send_top',
        'schedule': crontab(minute=0, hour=22),
    },
}

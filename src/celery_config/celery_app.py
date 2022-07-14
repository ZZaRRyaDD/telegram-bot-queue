import os

from celery import Celery
from celery.schedules import crontab

app = Celery(
    'celery_config',
    broker=(
        f'redis://{os.getenv("REDIS_HOST")}:{int(os.getenv("REDIS_PORT"))}/0'
    ),
    backend=(
        f'redis://{os.getenv("REDIS_HOST")}:{int(os.getenv("REDIS_PORT"))}/1'
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
        # 'schedule': crontab(minute=0, hour=17),
        'schedule': crontab(minute='*/3'),
    },
   'send-top': {
        'task': 'src.celery_config.tasks.send_top',
        # 'schedule': crontab(minute=0, hour=22),
        'schedule': crontab(minute='*/5'),
    },
}

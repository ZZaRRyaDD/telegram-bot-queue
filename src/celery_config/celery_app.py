import os

from celery import Celery

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
        'schedule': 30.0,
    },
   'send-top': {
        'task': 'src.celery_config.tasks.send_top',
        'schedule': 30.0,
    },
}

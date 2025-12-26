import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo_project.settings')

app = Celery('demo_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['task'])

app.conf.beat_schedule = {
    'daily-task-reminder': {
        'task': 'task.tasks.daily_task_reminder',
        'schedule': crontab(hour=9, minute=10),
    },
}
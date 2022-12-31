import os
import logging

from celery import Celery
from celery.schedules import crontab

logger = logging.getLogger(__name__)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djuix.settings')

app = Celery('djuix')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    logger.error('Request: {0!r}'.format(self.request))
    
    
app.conf.beat_schedule = {
    'run-every-2-minutes': {
        'task': 'djuix.tasks.backup_project',
        'schedule': crontab(minute="*/2"),
    }
}

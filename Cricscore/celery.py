import os
from celery import Celery
from celery.schedules import crontab
from match import tasks

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Cricscore.settings')

app = Celery('Cricscore')

app.config_from_object('django.conf:settings', namespace='CELERY')




#celery_beat setting

app.conf.beat_schedule = {
    'fetch-matches-every-2hours': {
        'task': 'match.tasks.fetch_matches_from_api',
        'schedule': crontab(minute='*/2'),
    },
    
    'fetch_oversummary-every-2minute': {
        'task': 'match.tasks.fetch_oversummary',
        'schedule': crontab(minute='*/1'),
    },
}


app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request:{self.request}')
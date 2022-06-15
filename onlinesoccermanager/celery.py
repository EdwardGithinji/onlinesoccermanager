import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlinesoccermanager.settings')
app = Celery('onlinesoccermanager')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.timezone = 'Africa/Nairobi'
app.autodiscover_tasks()
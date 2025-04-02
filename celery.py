import os
from celery import Celery

# Django의 settings 모듈을 Celery의 기본 설정으로 사용하도록 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Django settings.py에서 'CELERY_' 접두사를 가진 모든 설정을 로드
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django 앱 설정에서 task들을 자동으로 로드
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
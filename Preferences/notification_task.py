from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging # 로깅 추가 

logger = logging.getLogger(__name__)

@shared_task(bind=True) # bind=True는 재시도 등을 위해 self 인자를 사용 가능하게 함
def send_email_task(self, subject, message, recipient):
    """Celery를 사용하여 단일 이메일을 비동기적으로 발송합니다."""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_SENDER, # settings.py에 정의된 발신자 사용
            recipient_list=[recipient],
            fail_silently=False,
        )
        logger.info(f"Celery 이메일 발송 성공: {recipient}")
        return True
    except Exception as e:
        logger.error(f"Celery 이메일 발송 실패 ({recipient}): {str(e)}")
        # 예: 5번까지 60초 간격으로 재시도 (최대 재시도 횟수는 기본 3번)
        try:
            # countdown: 재시도 전 대기 시간(초)
            # max_retries: 최대 재시도 횟수
            self.retry(exc=e, countdown=60, max_retries=5)
        except self.MaxRetriesExceededError:
            logger.error(f"최대 재시도 횟수 초과 ({recipient}): {str(e)}")
            return False
        return False # 재시도 중에는 False 반환 (선택적)
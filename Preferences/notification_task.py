from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# html_message 인자를 추가로 받도록 수정 (기본값 None)
@shared_task(bind=True)
def send_email_task(self, subject, message, recipient, html_message=None):
    """Celery를 사용하여 단일 이메일을 비동기적으로 발송합니다 (HTML 포함 가능)."""
    try:
        send_mail(
            subject=subject,
            message=message,                 # 일반 텍스트 메시지 (HTML 미지원 시 보여짐)
            from_email=settings.EMAIL_SENDER,
            recipient_list=[recipient],
            fail_silently=False,
            html_message=html_message      # HTML 버전 메시지
        )
        logger.info(f"Celery HTML 이메일 발송 성공: {recipient}")
        return True
    except Exception as e:
        logger.error(f"Celery HTML 이메일 발송 실패 ({recipient}): {str(e)}")
        try:
            self.retry(exc=e, countdown=60, max_retries=5)
        except self.MaxRetriesExceededError:
            logger.error(f"최대 재시도 횟수 초과 ({recipient}): {str(e)}")
            return False
        return False
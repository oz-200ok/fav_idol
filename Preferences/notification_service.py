from django.template.loader import render_to_string # 템플릿 렌더링 함수 임포트
from django.utils.html import strip_tags # HTML 태그 제거 함수 임포트 (텍스트 버전용)

from .models import UserGroupSubscribe
from .notification_task import send_email_task
# ... (다른 import 구문들) ...

class NotificationService:
    @staticmethod
    def notify_schedule_creation(schedule):
        subscribers = UserGroupSubscribe.objects.filter(
            group_id=schedule.group_id, notification=True
        ).select_related("user")

        if not subscribers:
            return False

        subject = f"[ILOG] {schedule.group.name} 새 일정 알림"
        template_name = "../templates/schedule_notification.html" # 사용할 템플릿 경로

        for subscriber in subscribers:
            if subscriber.user.email:
                # 템플릿에 전달할 컨텍스트 데이터 (딕셔너리 형태)
                context = {
                    'subject': subject,
                    'username': subscriber.user.username,
                    'group_name': schedule.group.name,
                    'schedule': schedule,
                }

                # HTML 템플릿 렌더링
                html_message = render_to_string(template_name, context)

                # HTML에서 태그를 제거하여 간단한 텍스트 버전 생성 (Fallback 용)
                plain_message = strip_tags(html_message)

                # Celery task 호출 시 HTML 메시지와 일반 텍스트 메시지를 함께 전달
                send_email_task.delay(subject, plain_message, subscriber.user.email, html_message=html_message)

        return True
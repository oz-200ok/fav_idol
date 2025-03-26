from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.core.mail import send_mail

from .models import UserGroupSubscribe


class NotificationService:
    @staticmethod
    def send_email_async(subject, message, recipient):
        """단일 이메일을 비동기적으로 발송합니다."""
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_SENDER,
                recipient_list=[recipient],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"이메일 발송 실패 ({recipient}): {str(e)}")
            return False

    @staticmethod
    def notify_schedule_creation(schedule):
        """새로운 일정이 생성되면 구독자들에게 이메일 알림을 발송합니다."""
        # 해당 그룹을 구독하고 알림 설정이 활성화된 사용자 조회
        subscribers = UserGroupSubscribe.objects.filter(
            group_id=schedule.group_id, notification=True
        ).select_related("user")

        if not subscribers:
            return False

        # 이메일 제목과 내용 구성
        subject = f"[ILOG] {schedule.group.name} 새 일정 알림"

        # 이메일을 비동기적으로 발송
        with ThreadPoolExecutor(max_workers=5) as executor:
            for subscriber in subscribers:
                if subscriber.user.email:
                    message = f"""
안녕하세요, {subscriber.user.username}님!

구독하신 {schedule.group.name}의 새로운 일정이 등록되었습니다.

일정 제목: {schedule.title}
일정 장소: {schedule.location or '미정'}
시작 시간: {schedule.start_time.strftime('%Y년 %m월 %d일 %H:%M')}
종료 시간: {schedule.end_time.strftime('%Y년 %m월 %d일 %H:%M') if schedule.end_time else '미정'}

자세한 내용은 ILOG 웹에서 확인해주세요.
감사합니다.
"""
                    executor.submit(
                        NotificationService.send_email_async,
                        subject,
                        message,
                        subscriber.user.email,
                    )

        return True

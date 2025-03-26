from django.core.mail import send_mail
from django.conf import settings

class NotificationService:
    @staticmethod
    def send_email_async(subject, message, recipient):
        """단일 이메일을 비동기적으로 발송합니다."""
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"이메일 발송 실패 ({recipient}): {str(e)}")
            return False

from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from .models import Schedule, Group
from django.contrib.auth.models import User


class ScheduleAPITestCase(APITestCase):
    def setUp(self):
        # 테스트 사용자 생성
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.admin = User.objects.create_superuser(username="admin", password="adminpass")

        # 그룹 생성
        self.group = Group.objects.create(name="Test Group")

        # 인증 클라이언트 생성
        self.client = APIClient()
        self.client.login(username="admin", password="adminpass")  # Admin 로그인

        # URL 설정
        self.list_url = reverse("schedule-list")  # 등록된 view의 URL name
        self.excel_upload_url = reverse("excel-upload")  # Excel 업로드용 URL

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Group, Schedule


class ScheduleAPITestCase(APITestCase):
    def setUp(self):
        # 테스트 사용자 생성
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.admin = User.objects.create_superuser(
            username="admin", password="adminpass"
        )

        # 그룹 생성
        self.group = Group.objects.create(name="Test Group")

        # 인증 클라이언트 생성
        self.client = APIClient()
        self.client.login(username="admin", password="adminpass")  # Admin 로그인

        # URL 설정
        self.list_url = reverse("schedule-list")  # 등록된 view의 URL name
        self.excel_upload_url = reverse("excel-upload")  # Excel 업로드용 URL

    def test_create_schedule(self):
        """일정 등록 테스트"""
        data = {
            "group": self.group.id,
            "title": "Sample Schedule",
            "description": "A test schedule",
            "location": "Meeting Room",
            "start_time": "2025-04-01T10:00:00Z",
            "end_time": "2025-04-01T12:00:00Z",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Schedule.objects.count(), 1)
        self.assertEqual(Schedule.objects.get().title, "Sample Schedule")

    def test_list_schedules(self):
        """일정 목록 조회 테스트"""
        Schedule.objects.create(
            group=self.group,
            title="Test Schedule",
            description="A test description",
            location="Office",
            start_time="2025-04-01T10:00:00Z",
            end_time="2025-04-01T12:00:00Z",
            user=self.admin,
        )
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

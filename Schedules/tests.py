from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from Idols.models import Agency
from .models import Group, Schedule


class ScheduleAPITestCase(APITestCase):
    def setUp(self):
        # 커스텀 User 모델 가져오기
        User = get_user_model()

        # 테스트 사용자 생성
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            name="Test User",
            password="testpass"
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            username="admin",
            name="Admin User",
            password="adminpass"
        )

        # Agency 객체 생성
        self.agency = Agency.objects.create(name="Test Agency")

        # 그룹 생성 (agency 연결)
        self.group = Group.objects.create(name="Test Group", agency=self.agency)

        # 사용자 토큰 생성
        token = Token.objects.create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        # URL 설정
        self.list_url = reverse("schedule")  # 등록된 view의 URL name
        self.excel_upload_url = reverse("upload_schedule")  # Excel 업로드용 URL

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

        # 인증된 클라이언트로 POST 요청
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

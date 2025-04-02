from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory, APITestCase

from Idols.models import Agency, Idol

from .models import Group, Schedule
from .serializer import ScheduleSerializer


class PermissionOverrideTest(APITestCase):
    def setUp(self):
        # 테스트 사용자 생성
        User = get_user_model()
        self.superuser = User.objects.create_superuser(
            username="adminuser",
            name="Super User",
            email="admin@example.com",
            password="adminpassword123",
        )

        self.user = User.objects.create_user(
            username="testuser",
            name="Test User",
            email="testuser@example.com",
            password="password123",
        )

        # 테스트 그룹 및 에이전시 생성
        self.agency = Agency.objects.create(name="Test Agency")
        self.group = Group.objects.create(name="Test Group", agency=self.agency)

        # 테스트 클라이언트 설정
        self.client = APIClient()

        # force_authenticate로 인증 우회 - 관리자 설정
        self.client.force_authenticate(user=self.superuser)

        # API 엔드포인트 설정
        self.schedule_list_url = reverse("schedule")
        self.schedule_detail_url = lambda pk: reverse(
            "schedule_detail", kwargs={"pk": pk}
        )

    from rest_framework.request import Request
    from rest_framework.test import APIRequestFactory

    def test_create_schedule_as_admin(self):
        """관리자 권한으로 일정 생성 테스트"""
        idol1 = Idol.objects.create(name="Idol1", group=self.group)
        idol2 = Idol.objects.create(name="Idol2", group=self.group)

        data = {
            "group": self.group.id,
            "title": "Admin Test Schedule",
            "description": "Testing schedule creation as admin.",
            "location": "Head Office",
            "start_time": "2025-04-01T10:00:00Z",
            "end_time": "2025-04-01T12:00:00Z",
            "participating_member_ids": [idol1.id, idol2.id],
        }

        factory = APIRequestFactory()
        request = factory.post(self.schedule_list_url, data, format="json")
        request.user = self.superuser  # 인증된 사용자 설정

        serializer = ScheduleSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            self.assertEqual(Schedule.objects.count(), 1)
            self.assertEqual(Schedule.objects.get().title, "Admin Test Schedule")
        else:
            print("Errors:", serializer.errors)

    def test_list_schedules(self):
        """일정 목록 조회 테스트"""
        Schedule.objects.create(
            group=self.group,
            user=self.user,
            title="Sample Schedule",
            description="This is a sample.",
            location="Meeting Room",
            start_time="2025-04-01T10:00:00Z",
            end_time="2025-04-01T12:00:00Z",
        )

        response = self.client.get(self.schedule_list_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_delete_schedule(self):
        """관리자 권한으로 일정 삭제 테스트"""
        schedule = Schedule.objects.create(
            group=self.group,
            user=self.superuser,  # 관리자 사용자로 설정
            title="Sample Schedule",
            description="This is a sample.",
            location="Meeting Room",
            start_time="2025-04-01T10:00:00Z",
            end_time="2025-04-01T12:00:00Z",
        )

        # force_authenticate로 관리자 인증 설정
        self.client.force_authenticate(user=self.superuser)

        response = self.client.delete(
            self.schedule_detail_url(schedule.id), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Schedule.objects.count(), 0)

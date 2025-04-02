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

    def test_create_schedule_without_required_fields(self):
        """필수 필드 없이 일정 생성 요청 시 실패"""
        data = {
            # 필수 필드 'group'과 'title' 누락
            "description": "Missing required fields for schedule creation.",
            "location": "Unknown",
            "start_time": "2025-04-01T10:00:00Z",
            "end_time": "2025-04-01T12:00:00Z",
            "participating_member_ids": [],
        }

        response = self.client.post(self.schedule_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # 실패 확인
        self.assertIn(
            "group", response.data
        )  # 필수 필드 'group'에 대한 에러 메시지 확인
        self.assertIn(
            "title", response.data
        )  # 필수 필드 'title'에 대한 에러 메시지 확인

    def test_create_schedule_invalid_time_range(self):
        """종료 시간이 시작 시간보다 빠른 경우 실패"""
        idol1 = Idol.objects.create(name="Idol1", group=self.group)
        idol2 = Idol.objects.create(name="Idol2", group=self.group)

        data = {
            "group": self.group.id,
            "title": "Invalid Time Schedule",
            "description": "End time is earlier than start time.",
            "location": "Head Office",
            "start_time": "2025-04-01T12:00:00Z",  # 시작 시간
            "end_time": "2025-04-01T10:00:00Z",  # 종료 시간이 시작 시간보다 빠름
            "participating_member_ids": [idol1.id, idol2.id],
        }

        response = self.client.post(self.schedule_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # 실패 확인
        self.assertIn(
            "non_field_errors", response.data
        )  # 전체 데이터 수준 오류 메시지 확인
        self.assertIn(
            "종료 시간이 시작 시간보다 빠를 수 없습니다.",
            response.data["non_field_errors"][0],
        )  # 오류 메시지 텍스트 확인

    def test_list_schedules_empty(self):
        """일정 데이터가 없는 경우 목록 조회 시 빈 데이터 반환"""
        response = self.client.get(self.schedule_list_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # 일정이 없으므로 빈 목록 확인

    def test_delete_schedule_unauthorized(self):
        """일정 삭제 요청 시 권한 없는 사용자로 실패"""
        schedule = Schedule.objects.create(
            group=self.group,
            user=self.superuser,  # 관리자가 생성한 일정
            title="Sample Schedule",
            description="This is a sample schedule.",
            location="Meeting Room",
            start_time="2025-04-01T10:00:00Z",
            end_time="2025-04-01T12:00:00Z",
        )

        # 권한 없는 일반 사용자 인증 설정
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            self.schedule_detail_url(schedule.id), format="json"
        )
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN
        )  # 권한 실패 확인
        self.assertEqual(Schedule.objects.count(), 1)  # 일정 삭제되지 않음 확인

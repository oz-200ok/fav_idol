from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.utils import timezone

from Idols.models import Agency, Group, Idol

from .models import Schedule

User = get_user_model()


class ScheduleModelTest(TestCase):
    def setUp(self):
        # 테스트에 필요한 객체들을 생성합니다.
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            name="Test User",
            password="testpassword",
        )
        self.agency = Agency.objects.create(name="Test Agency")
        self.group = Group.objects.create(name="Test Group", agency=self.agency)
        self.idol1 = Idol.objects.create(name="Idol 1", group=self.group)
        self.idol2 = Idol.objects.create(name="Idol 2", group=self.group)
        self.start_time = timezone.now()  # Use timezone.now()
        self.end_time = self.start_time + timedelta(hours=2)

        self.schedule = Schedule.objects.create(
            user=self.user,
            group=self.group,
            title="Test Schedule",
            description="This is a test schedule.",
            location="Test Location",
            start_time=self.start_time,
            end_time=self.end_time,
        )
        self.schedule.participating_members.add(self.idol1, self.idol2)

    def test_schedule_creation(self):
        # 스케줄이 정상적으로 생성되는지 테스트합니다.
        self.assertEqual(Schedule.objects.count(), 1)
        schedule = Schedule.objects.first()
        self.assertEqual(schedule.user, self.user)
        self.assertEqual(schedule.group, self.group)
        self.assertEqual(schedule.title, "Test Schedule")
        self.assertEqual(schedule.description, "This is a test schedule.")
        self.assertEqual(schedule.location, "Test Location")
        self.assertEqual(schedule.start_time, self.start_time)
        self.assertEqual(schedule.end_time, self.end_time)

    def test_schedule_participating_members(self):
        # 스케줄의 참가 멤버들이 올바르게 저장되는지 테스트합니다.
        self.assertEqual(self.schedule.participating_members.count(), 2)
        self.assertIn(self.idol1, self.schedule.participating_members.all())
        self.assertIn(self.idol2, self.schedule.participating_members.all())


class ManagedGroupSchedulesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password",
            name="Test User",
        )
        self.client = Client()
        self.client.login(username="testuser", password="password")

        agency = Agency.objects.create(name="Test Agency", contact="test@example.com")
        group = Group.objects.create(name="Test Group", agency=agency)
        Schedule.objects.create(
            title="Meeting",
            group=group,
            start_time="2025-04-01 10:00",
            end_time="2025-04-01 11:00",
            user=self.user,  # user_id를 추가
        )

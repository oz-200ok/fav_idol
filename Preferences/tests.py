from django.urls import reverse
from rest_framework.test import APITestCase
from Accounts.models import User
from Idols.models import Group
from Schedules.models import Schedule
from .models import UserGroupSubscribe


class PreferenceAPITests(APITestCase):
    """
    Preferences 앱의 API 뷰들에 대한 테스트 클래스
    (SubscribeViewSet, UserSubscribedSchedulesView, UserScheduleDetailView)
    """

    @classmethod
    def setUpTestData(cls):
        """테스트 전체에서 사용할 초기 데이터 설정 (DB에 한 번만 생성)"""
        # 1. 테스트용 사용자 생성
        cls.user = User.objects.create_user(username='testuser', password='password123', email='test@example.com')

        # 2. 테스트용 그룹 생성
        cls.group1 = Group.objects.create(name='Test Group 1')
        cls.group2 = Group.objects.create(name='Test Group 2') # 구독하지 않을 그룹

        # 3. 테스트용 일정 생성 (그룹1에 속함)
        cls.schedule1 = Schedule.objects.create(
            group=cls.group1,
            title='Test Schedule 1 for Group 1',
            start_time='2025-04-10T10:00:00Z', # UTC 시간으로 예시
            location='Test Location'
        )
        # 4. 테스트용 일정 생성 (그룹2에 속함)
        cls.schedule2 = Schedule.objects.create(
            group=cls.group2,
            title='Test Schedule 2 for Group 2',
            start_time='2025-04-11T10:00:00Z',
        )

        # 5. 초기 구독 상태 생성 (user가 group1을 구독)
        cls.initial_subscription = UserGroupSubscribe.objects.create(
            user=cls.user,
            group=cls.group1,
            notification=True
        )

        # API 엔드포인트 URL 미리 정의
        cls.subscribe_list_create_url = reverse('subscribe-list') # ViewSet의 list, create 액션
        cls.subscribe_detail_url = lambda pk: reverse('subscribe-detail', kwargs={'pk': pk}) # ViewSet의 destroy 액션 (pk 필요)
        cls.subscribed_schedules_url = reverse('user-subscribed-schedules')
        cls.schedule_detail_url = lambda pk: reverse('user-schedule-detail', kwargs={'schedule_id': pk})
        
    def setUp(self):
        """ 각 테스트 메소드 실행 전에 호출됨 """
        # 모든 API 요청에 대해 인증된 사용자 설정
        self.client.force_authenticate(user=self.user)
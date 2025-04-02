from django.urls import reverse
from rest_framework.test import APITestCase
from Accounts.models import User
from Idols.models import Group,Agency
from Schedules.models import Schedule
from .models import UserGroupSubscribe
from rest_framework import status



class PreferenceAPITests(APITestCase):
    """
    Preferences 앱의 API 뷰들에 대한 테스트 클래스
    (SubscribeViewSet, UserSubscribedSchedulesView, UserScheduleDetailView)
    """

    @classmethod
    def setUpTestData(cls):
        """테스트 전체에서 사용할 초기 데이터 설정"""
        # 1. 테스트용 사용자 생성
        cls.user = User.objects.create_user(
            username='testuser',
            password='password123',
            email='test@example.com',
            name='Test User' # <- name 인자 추가! 원하는 테스트용 이름으로 설정해
        )

        # 1.5. 테스트용 Agency 생성 (Group을 만들기 전에 필요)
        cls.agency = Agency.objects.create(name='Test Agency') 

        # 2. 테스트용 그룹 생성 
        cls.group1 = Group.objects.create(name='Test Group 1', agency=cls.agency)
        cls.group2 = Group.objects.create(name='Test Group 2', agency=cls.agency) 

        # 3. 테스트용 일정 생성
        cls.schedule1 = Schedule.objects.create(
            group=cls.group1,
            user=cls.user, 
            title='Test Schedule 1 for Group 1',
            start_time='2025-04-10T10:00:00Z',
            location='Test Location'
        )
        # 4. 테스트용 일정 생성 
        cls.schedule2 = Schedule.objects.create(
            group=cls.group2,
            user=cls.user,
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
        cls.subscribe_list_create_url = reverse('subscribe-list')
        cls.subscribe_detail_url = lambda pk: reverse('subscribe-detail', kwargs={'pk': pk})
        cls.subscribed_schedules_url = reverse('user-subscribed-schedules')
        cls.schedule_detail_url = lambda pk: reverse('user-schedule-detail', kwargs={'schedule_id': pk})
        
    def setUp(self):
        """ 각 테스트 메소드 실행 전에 호출됨 """
        # 모든 API 요청에 대해 인증된 사용자 설정
        self.client.force_authenticate(user=self.user)
        
    def test_list_subscriptions_success(self):
        """GET /subscriptions/ - 사용자의 구독 목록 조회 성공 테스트"""
        response = self.client.get(self.subscribe_list_create_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK) # 성공 상태 코드 확인
        self.assertEqual(len(response.data['data']), 1) # setUpTestData에서 만든 구독 1개가 보이는지 확인
        self.assertEqual(response.data['data'][0]['group_id'], self.group1.id) # 반환된 데이터의 그룹 ID 확인
        self.assertEqual(response.data['data'][0]['group_name'], self.group1.name) # 반환된 데이터의 그룹 이름 확인
        self.assertTrue(response.data['data'][0]['notification']) # 알림 설정 확인
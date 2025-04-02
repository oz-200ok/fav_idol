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
        # 사용자
        cls.user = User.objects.create_user(username='testuser', password='password123', email='test@example.com', name='Test User')
        # 에이전시
        cls.agency = Agency.objects.create(name='Test Agency')
        # 그룹 (group1은 초기 구독용, group2는 CRUD 테스트용)
        cls.group1 = Group.objects.create(name='Test Group 1', agency=cls.agency)
        cls.group2 = Group.objects.create(name='Test Group 2', agency=cls.agency)
        # 일정 (group1 소속)
        cls.schedule1 = Schedule.objects.create(group=cls.group1, user=cls.user, title='Test Schedule 1', start_time='2025-04-10T10:00:00Z')
        # 초기 구독 (group1) - 일정 목록 테스트에 필요
        cls.initial_subscription = UserGroupSubscribe.objects.create(user=cls.user, group=cls.group1, notification=True)
        # URL 정의
        cls.subscribe_list_create_url = reverse('subscribe-list')
        cls.subscribe_detail_url = lambda pk: reverse('subscribe-detail', kwargs={'pk': pk})
        cls.subscribed_schedules_url = reverse('user-subscribed-schedules')
        cls.schedule_detail_url = lambda pk: reverse('user-schedule-detail', kwargs={'schedule_id': pk})
        
    def setUp(self):
        """ 각 테스트 메소드 실행 전에 호출됨 """
        # 모든 API 요청에 대해 인증된 사용자 설정
        self.client.force_authenticate(user=self.user)
        
    def test_subscription_crud_flow(self):
        """ 구독 생성(POST) -> 목록 조회(GET) -> 삭제(DELETE) 흐름 테스트 """
        # 1. 구독 생성 (group2 구독)
        create_data = {'group_id': self.group2.id, 'notification': True}
        create_response = self.client.post(self.subscribe_list_create_url, data=create_data)
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_response.data['data']['group_id'], self.group2.id)
        new_subscription_id_from_response = create_response.data['data']['id'] # 응답에서 id 확인 (삭제 시 사용 가능)

        # 2. 구독 목록 조회 (초기 구독 group1 + 방금 만든 group2 = 총 2개 확인)
        list_response = self.client.get(self.subscribe_list_create_url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data['data']), 2)
        group_ids_in_list = {item['group_id'] for item in list_response.data['data']}
        self.assertIn(self.group1.id, group_ids_in_list)
        self.assertIn(self.group2.id, group_ids_in_list)

        # 3. 구독 삭제 (방금 만든 group2 구독 삭제)
        delete_url = self.subscribe_detail_url(self.group2.id) # pk는 group_id 사용
        delete_response = self.client.delete(delete_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        # 4. 구독 목록 다시 조회 (group1만 남았는지 확인)
        list_response_after_delete = self.client.get(self.subscribe_list_create_url)
        self.assertEqual(list_response_after_delete.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response_after_delete.data['data']), 1)
        self.assertEqual(list_response_after_delete.data['data'][0]['group_id'], self.group1.id)

    def test_create_subscription_invalid_group(self):
        """존재하지 않는 그룹 ID 구독 시 실패 (400 에러 확인)"""
        invalid_group_id = 9999
        data = {'group_id': invalid_group_id}
        response = self.client.post(self.subscribe_list_create_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error_code', response.data) # 커스텀 에러 형식 확인
        
    def test_list_subscribed_schedules_success(self):
        """구독한 그룹의 일정 목록 조회 성공 (GET /schedules/)"""
        response = self.client.get(self.subscribed_schedules_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 초기 구독(group1)의 일정(schedule1)만 포함하는지 확인
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['title'], self.schedule1.title)
        
    def test_retrieve_schedule_detail_success(self):
        """특정 일정 상세 조회 성공 (GET /schedules/{id}/)"""
        url = self.schedule_detail_url(self.schedule1.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['title'], self.schedule1.title)
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Agency, Group, Idol


class AgencyViewTests(APITestCase):
    def setUp(self):
        # 테스트 클라이언트 생성
        self.client = APIClient()

        # 테스트 데이터 생성
        self.agency = Agency.objects.create(name="Test Agency", contact="123456789")
        self.agency_list_url = reverse("agency_list")  # 소속사 목록 URL 설정
        self.agency_detail_url = reverse("agency_detail", kwargs={"pk": self.agency.id})

        # 그룹 생성 및 URL 설정
        self.group = Group.objects.create(name="Test Group", agency=self.agency)
        self.group_list_url = reverse("group_list")
        self.group_detail_url = reverse("group_detail", kwargs={"pk": self.group.id})

        # 아이돌 관련 URL 설정
        self.idol_list_url = reverse("idol_list")
        self.idol_detail_url = lambda pk: reverse("idol_detail", kwargs={"pk": pk})

    def test_get_agency_list(self):
        """소속사 목록 조회 테스트"""
        response = self.client.get(self.agency_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"]
        }
    )
    def test_create_agency_with_auth(self):
        """소속사 생성 테스트 - 인증된 사용자"""
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="admin",
            name="Super User",
            email="admin@example.com",
            password="adminpassword",
        )

        # 관리자 인증 설정
        self.client.force_authenticate(user=admin_user)

        data = {
            "name": "New Agency",
            "contact": "987654321",
        }
        response = self.client.post(self.agency_list_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Agency.objects.count(), 2)

    def test_create_agency_without_auth(self):
        """소속사 생성 테스트 - 인증되지 않은 사용자"""
        # 인증 비활성화
        self.client.force_authenticate(user=None)

        # 데이터를 multipart/form-data 형식으로 전송
        data = {
            "name": "Unauthorized Agency",
            "contact": "123456789",
        }
        response = self.client.post(self.agency_list_url, data, format="multipart")
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED
        )  # 인증 실패 확인
        self.assertEqual(Agency.objects.count(), 1)  # 데이터 추가되지 않음 확인

    def test_create_agency_missing_fields(self):
        """필수 필드 없이 소속사 생성 요청 시 실패"""
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="admin",
            name="Super User",
            email="admin@example.com",
            password="adminpassword",
        )

        # 관리자 인증 설정
        self.client.force_authenticate(user=admin_user)

        # 필수 필드 누락
        data = {
            "contact": "987654321",  # 'name' 필드 누락
        }
        response = self.client.post(self.agency_list_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # 실패 확인
        self.assertIn("name", response.data)  # 'name' 필드 오류 메시지 확인

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"]
        }
    )
    def test_create_duplicate_agency(self):
        """중복된 이름의 소속사 생성 실패"""
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="admin",
            name="Super User",
            email="admin@example.com",
            password="adminpassword",
        )

        # 관리자 인증 설정
        self.client.force_authenticate(user=admin_user)

        # 동일한 이름의 소속사 데이터 전송
        data = {
            "name": "Test Agency",  # 이미 존재하는 이름
            "contact": "987654321",
        }
        response = self.client.post(self.agency_list_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)  # 'name' 필드 오류 확인

    def test_delete_nonexistent_agency(self):
        """존재하지 않는 소속사 ID로 삭제 실패"""
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="admin",
            name="Super User",
            email="admin@example.com",
            password="adminpassword",
        )

        # 관리자 인증 설정
        self.client.force_authenticate(user=admin_user)

        nonexistent_id = 9999  # 존재하지 않는 ID
        response = self.client.delete(
            reverse("agency_detail", kwargs={"pk": nonexistent_id}), format="json"
        )
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )  # 404 오류 확인

    def test_get_empty_agency_list(self):
        """소속사 목록 데이터 없음"""
        Agency.objects.all().delete()  # 모든 소속사 삭제

        response = self.client.get(self.agency_list_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 성공 상태 확인
        self.assertEqual(len(response.data["data"]), 0)  # 빈 목록 확인

    def test_group_member_count(self):
        """그룹 멤버 수 반환 확인"""
        Idol.objects.create(name="Idol1", group=self.group)
        Idol.objects.create(name="Idol2", group=self.group)

        response = self.client.get(self.group_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"][0]["member_count"], 2)

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"]
        }
    )
    def test_update_group(self):
        """그룹 데이터 업데이트 테스트"""
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="admin",
            name="Super User",
            email="admin@example.com",
            password="adminpassword",
        )
        self.client.force_authenticate(user=admin_user)

        data = {
            "name": "Updated Group",
            "agency": self.agency.id,
        }
        response = self.client.put(self.group_detail_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Group.objects.get(id=self.group.id).name, "Updated Group")

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"]
        }
    )
    def test_create_idol_with_missing_fields(self):
        """아이돌 필수 필드 누락 테스트"""
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="admin",
            name="Super User",
            email="admin@example.com",
            password="adminpassword",
        )
        self.client.force_authenticate(user=admin_user)

        data = {
            "name": "",  # 누락된 필드
            "group": self.group.id,
        }
        response = self.client.post(self.idol_list_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"]
        }
    )
    def test_delete_idol_preserve_group(self):
        """아이돌 삭제 후 그룹 무결성 테스트"""
        idol = Idol.objects.create(name="Idol1", group=self.group)

        response = self.client.delete(
            reverse("idol_detail", kwargs={"pk": idol.id}), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Idol.objects.filter(group=self.group).count(), 0)
        self.assertEqual(Group.objects.filter(id=self.group.id).count(), 1)

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"]
        }
    )
    def test_delete_group_with_related_idols(self):
        """그룹 삭제 시 관련 아이돌 삭제 확인"""
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="admin",
            name="Super User",
            email="admin@example.com",
            password="adminpassword",
        )
        self.client.force_authenticate(user=admin_user)

        Idol.objects.create(name="Idol1", group=self.group)
        Idol.objects.create(name="Idol2", group=self.group)

        response = self.client.delete(self.group_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)  # 수정
        self.assertEqual(
            Idol.objects.filter(group=self.group).count(), 0
        )  # 아이돌도 삭제 확인

    def test_get_idol_detail(self):
        """아이돌 상세 정보 조회"""
        idol = Idol.objects.create(name="Idol1", group=self.group)

        response = self.client.get(reverse("idol_detail", kwargs={"pk": idol.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "Idol1")
        self.assertEqual(response.data["data"]["group"], self.group.id)

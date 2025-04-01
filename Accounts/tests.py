from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APITestCase


# Django's 기본 User 모델 가져오기
User = get_user_model()


# 테스트를 위한 기본 사용자 데이터 (클래스 상수로 정의)
class TestUserData:
    TEST_USER = {
        "email": "test@example.com",
        "username": "testuser",
        "name": "Test Name",
        "phone": "01012345678",
        "password": "StrongPassword123!",
    }
    OTHER_USER = {
        "email": "other@example.com",
        "username": "otheruser",
        "name": "Other Name",
        "phone": "01087654321",
        "password": "OtherPassword123!",
    }
    INACTIVE_USER = {
        "email": "inactive@example.com",
        "username": "inactiveuser",
        "name": "Inactive Name",
        "password": "InactivePassword123!",
        "is_active": False,
    }
    NEW_USER = {
        "email": "newuser@example.com",
        "username": "newuser",
        "name": "New Name",
        "phone": "01011112222",
        "password": "NewPassword123!",
    }
    WRONG_PASSWORD = "WrongPassword!"
    INVALID_TOKEN = "invalidtoken123"

class AccountAPITests(APITestCase):
    """
    계정 관련 API 엔드포인트 테스트 클래스
    APITestCase를 사용하여 각 테스트 후 데이터베이스 롤백
    """

    @classmethod
    def setUpTestData(cls):
        """클래스 전체에서 공유할 테스트 데이터 설정 (한 번만 실행)"""
        cls.user = User.objects.create_user(**TestUserData.TEST_USER, is_active=True)
        cls.other_user = User.objects.create_user(
            **TestUserData.OTHER_USER, is_active=True
        )
        cls.inactive_user = User.objects.create_user(**TestUserData.INACTIVE_USER)

    def setUp(self):
        """각 테스트 메소드 실행 전 설정 (매번 실행)"""
        self.client.credentials()  # 모든 요청 전에 인증 초기화

    # ==============================
    # 회원가입 (Register) 테스트
    # ==============================
    @patch("Accounts.services.EmailService.send_verification_email")
    def test_register_success(self, mock_send_email):
        """회원가입 성공 테스트"""
        url = reverse("register")
        response = self.client.post(url, TestUserData.NEW_USER, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            User.objects.filter(email=TestUserData.NEW_USER["email"]).exists()
        )
        created_user = User.objects.get(email=TestUserData.NEW_USER["email"])
        self.assertFalse(created_user.is_active)
        mock_send_email.assert_called_once()
        self.assertIn("user_id", response.data["data"])
        self.assertEqual(response.data["data"]["email"], TestUserData.NEW_USER["email"])

    def test_register_duplicate_email(self):
        """중복 이메일 회원가입 실패 테스트"""
        url = reverse("register")
        data = TestUserData.NEW_USER.copy()
        data["email"] = TestUserData.TEST_USER["email"]
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        """필수 필드 누락 회원가입 실패 테스트"""
        url = reverse("register")
        data = {
            k: v for k, v in TestUserData.NEW_USER.items() if k != "username"
        }  # username 필드 제외
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.tokens import default_token_generator


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

    # ==============================
    # 이메일 인증 (Verify Email) 테스트
    # ==============================
    def test_verify_email_success(self):
        """이메일 인증 성공 테스트"""
        user = self.inactive_user
        token = default_token_generator.make_token(user)
        import urllib.parse

        email_encoded = urllib.parse.quote(user.email)
        url = reverse("verify_email") + f"?token={token}&email={email_encoded}"

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["email"], user.email)

    def test_verify_email_invalid_token(self):
        """잘못된 토큰으로 이메일 인증 실패 테스트"""
        user = self.inactive_user
        import urllib.parse

        email_encoded = urllib.parse.quote(user.email)
        url = (
            reverse("verify_email")
            + f"?token={TestUserData.INVALID_TOKEN}&email={email_encoded}"
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("유효하지 않은 인증 토큰", str(response.data))
        user.refresh_from_db()
        self.assertFalse(user.is_active)
        
    # ==============================
    # 로그인 (Login) 테스트
    # ==============================
    def test_login_success(self):
        """로그인 성공 테스트 (활성화된 사용자)"""
        url = reverse("login")
        response = self.client.post(
            url,
            {
                "email": TestUserData.TEST_USER["email"],
                "password": TestUserData.TEST_USER["password"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data["data"])
        self.assertIn("refresh_token", response.data["data"])
        self.assertEqual(response.data["data"]["user"]["email"], self.user.email)

    def test_login_inactive_user(self):
        """비활성화된 사용자 로그인 실패 테스트"""
        url = reverse("login")
        response = self.client.post(
            url,
            {
                "email": TestUserData.INACTIVE_USER["email"],
                "password": TestUserData.INACTIVE_USER["password"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_wrong_password(self):
        """잘못된 비밀번호 로그인 실패 테스트"""
        url = reverse("login")
        response = self.client.post(
            url,
            {
                "email": TestUserData.TEST_USER["email"],
                "password": TestUserData.WRONG_PASSWORD,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ==============================
    # 로그아웃 (Logout) 테스트
    # ==============================
    def test_logout_success(self):
        """로그아웃 성공 테스트"""
        login_url = reverse("login")
        login_response = self.client.post(
            login_url,
            {
                "email": TestUserData.TEST_USER["email"],
                "password": TestUserData.TEST_USER["password"],
            },
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        refresh_token = login_response.data["data"]["refresh_token"]
        access_token = login_response.data["data"]["access_token"]

        logout_url = reverse("logout")
        response = self.client.post(
            logout_url,
            {"refresh_token": refresh_token},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_unauthenticated(self):
        """미인증 상태 로그아웃 실패 테스트"""
        logout_url = reverse("logout")
        response = self.client.post(
            logout_url, {"refresh_token": "fakerefreshtoken"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

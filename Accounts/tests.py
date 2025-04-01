from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
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

    # ==============================
    # 프로필 조회 (User Profile) 테스트
    # ==============================
    def test_get_user_profile_success(self):
        """인증된 사용자 프로필 조회 성공 테스트"""
        url = reverse("user_profile")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["email"], self.user.email)
        self.assertEqual(response.data["data"]["username"], self.user.username)

    def test_get_user_profile_unauthenticated(self):
        """미인증 사용자 프로필 조회 실패 테스트"""
        url = reverse("user_profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ==============================
    # 프로필 수정 (User Profile Update) 테스트
    # ==============================
    def test_update_user_profile_success(self):
        """프로필 수정 성공 테스트 (닉네임, 전화번호 변경)"""
        url = reverse("user-profile-update")
        self.client.force_authenticate(user=self.user)
        new_username = "updatedusername"
        new_phone = "01099998888"
        response = self.client.patch(
            url, {"username": new_username, "phone": new_phone}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, new_username)
        self.assertEqual(self.user.phone, new_phone)
        self.assertEqual(response.data["data"]["username"], new_username)

    def test_update_user_profile_password_success(self):
        """프로필 수정 성공 테스트 (비밀번호 변경)"""
        url = reverse("user-profile-update")
        self.client.force_authenticate(user=self.user)
        new_password = "NewStrongPassword456!"
        response = self.client.patch(
            url,
            {
                "current_password": TestUserData.TEST_USER["password"],
                "password": new_password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))

    def test_update_user_profile_password_wrong_current(self):
        """프로필 수정 실패 테스트 (현재 비밀번호 불일치)"""
        url = reverse("user-profile-update")
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            url,
            {
                "current_password": TestUserData.WRONG_PASSWORD,
                "password": "NewStrongPassword456!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_profile_duplicate_username(self):
        """프로필 수정 실패 테스트 (닉네임 중복)"""
        url = reverse("user-profile-update")
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            url, {"username": self.other_user.username}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ==============================
    # 중복 확인 (Check Duplicate) 테스트
    # ==============================
    def test_check_duplicate_username_exists(self):
        """중복 닉네임 확인 테스트 (존재하는 경우)"""
        url = reverse("check-duplicate") + f"?type=username&value={self.user.username}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_duplicate_username_not_exists(self):
        """중복 닉네임 확인 테스트 (존재하지 않는 경우)"""
        unique_username = "uniqueusername"
        url = reverse("check-duplicate") + f"?type=username&value={unique_username}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("username", response.data["data"])
        self.assertEqual(response.data["data"]["username"], unique_username)

    def test_check_duplicate_email_exists(self):
        """중복 이메일 확인 테스트 (존재하는 경우)"""
        url = reverse("check-duplicate") + f"?type=email&value={self.user.email}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_duplicate_phone_exists(self):
        """중복 전화번호 확인 테스트 (존재하는 경우)"""
        url = reverse("check-duplicate") + f"?type=phone&value={self.user.phone}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_duplicate_invalid_type(self):
        """중복 확인 실패 테스트 (잘못된 타입)"""
        url = reverse("check-duplicate") + "?type=invalidtype&value=somevalue"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ==============================
    # 이메일 찾기 (Find Email) 테스트
    # ==============================
    def test_find_email_success(self):
        """이메일 찾기 성공 테스트"""
        url = reverse("find_email")
        response = self.client.post(
            url,
            {
                "name": TestUserData.TEST_USER["name"],
                "phone": TestUserData.TEST_USER["phone"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["email"], self.user.email)

    def test_find_email_not_found(self):
        """이메일 찾기 실패 테스트 (정보 불일치)"""
        url = reverse("find_email")
        response = self.client.post(
            url,
            {"name": "Wrong Name", "phone": TestUserData.TEST_USER["phone"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("입력하신 정보와 일치하는 회원이 없습니다", str(response.data))

    # ==============================
    # 비밀번호 찾기 (Find Password) 테스트
    # ==============================
    @patch("Accounts.services.EmailService.send_password_reset_email")
    def test_find_password_success(self, mock_send_email):
        """비밀번호 찾기(재설정 이메일 발송) 성공 테스트"""
        url = reverse("find_password")
        response = self.client.post(
            url, {"email": TestUserData.TEST_USER["email"]}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_email.assert_called_once_with(self.user)

    def test_find_password_user_not_found(self):
        """비밀번호 찾기 실패 테스트 (존재하지 않는 이메일)"""
        url = reverse("find_password")
        response = self.client.post(
            url, {"email": "nonexistent@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("입력하신 이메일로 등록된 계정이 없습니다", str(response.data))

    # ==============================
    # 비밀번호 재설정 (Reset Password) 테스트
    # ==============================
    def test_reset_password_success(self):
        """비밀번호 재설정 성공 테스트"""
        user = self.user
        token = default_token_generator.make_token(user)
        new_password = "ResetPassword789!"
        url = reverse("reset_password")
        response = self.client.post(
            url,
            {"token": token, "email": user.email, "new_password": new_password},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user.refresh_from_db()
        self.assertTrue(user.check_password(new_password))

    def test_reset_password_invalid_token(self):
        """비밀번호 재설정 실패 테스트 (잘못된 토큰)"""
        user = self.user
        new_password = "ResetPassword789!"
        url = reverse("reset_password")
        response = self.client.post(
            url,
            {
                "token": TestUserData.INVALID_TOKEN,
                "email": user.email,
                "new_password": new_password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("유효하지 않은 토큰입니다", str(response.data))

    # ==============================
    # 회원 탈퇴 (Delete Account) 테스트
    # ==============================
    def test_delete_account_success(self):
        """회원 탈퇴 성공 테스트"""
        user_id_to_delete = self.user.id
        url = reverse("account-delete")
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=user_id_to_delete).exists())

    def test_delete_account_unauthenticated(self):
        """미인증 상태 회원 탈퇴 실패 테스트"""
        url = reverse("account-delete")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ==============================
    # 소셜 로그인 (Social Login) 테스트
    # ==============================
    @patch("Accounts.services.SocialLoginService.get_access_token")
    def test_social_login_missing_code(self, mock_get_access_token):
        """소셜 로그인 실패 테스트 (인가 코드 누락)"""
        url = reverse("social-login")
        response = self.client.post(url, {"social_type": "kakao"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_get_access_token.assert_not_called()

    @patch("Accounts.services.SocialLoginService.get_access_token")
    def test_social_login_invalid_type(self, mock_get_access_token):
        """소셜 로그인 실패 테스트 (지원하지 않는 타입)"""
        url = reverse("social-login")
        response = self.client.post(
            url, {"social_type": "google", "code": "somecode"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_get_access_token.assert_not_called()

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

User = get_user_model()


# Create your tests here.
class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "name": "Test User",
            "password": "testpassword",
        }

    def test_create_user(self):
        # 일반 유저 생성 테스트
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.name, "Test User")
        self.assertTrue(user.check_password("testpassword"))
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_social)
        self.assertIsNone(user.social_login)

    def test_create_superuser(self):
        # 슈퍼 유저 생성 테스트
        superuser = User.objects.create_superuser(
            email="admin@example.com",
            username="adminuser",
            name="Admin User",
            password="adminpassword",
        )
        self.assertEqual(superuser.email, "admin@example.com")
        self.assertEqual(superuser.username, "adminuser")
        self.assertEqual(superuser.name, "Admin User")
        self.assertTrue(superuser.check_password("adminpassword"))
        self.assertTrue(superuser.is_admin)
        self.assertTrue(superuser.is_staff)
        self.assertFalse(superuser.is_social)
        self.assertIsNone(superuser.social_login)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)

    def test_create_user_without_email(self):
        # 이메일 없이 유저 생성 시 에러 발생 테스트
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="",
                username="testuser2",
                name="Test User2",
                password="testpassword",
            )

    def test_create_user_without_username(self):
        # 유저네임 없이 유저 생성 시 에러 발생 테스트
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="test2@example.com",
                username="",
                name="Test User2",
                password="testpassword",
            )

    def test_create_user_without_name(self):
        # 이름 없이 유저 생성 시 에러 발생 테스트
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="test2@example.com",
                username="testuser2",
                name="",
                password="testpassword",
            )

    def test_duplicate_email(self):
        # 중복된 이메일로 유저 생성 시 에러 발생 테스트
        User.objects.create_user(**self.user_data)
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**self.user_data)

    def test_duplicate_username(self):
        # 중복된 유저네임으로 유저 생성 시 에러 발생 테스트
        User.objects.create_user(**self.user_data)
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email="test2@example.com",
                username="testuser",
                name="Test User2",
                password="testpassword",
            )

    def test_social_user(self):
        # 소셜 로그인 유저 생성 테스트
        social_user = User.objects.create_user(
            email="social@example.com",
            username="socialuser",
            name="Social User",
            is_social=True,
            social_login="google",
        )
        self.assertEqual(social_user.email, "social@example.com")
        self.assertEqual(social_user.username, "socialuser")
        self.assertEqual(social_user.name, "Social User")
        self.assertFalse(social_user.has_usable_password())
        self.assertTrue(social_user.is_social)
        self.assertEqual(social_user.social_login, "google")

    def test_invalid_email_format(self):
        # 유효하지 않은 이메일 형식으로 유저 생성 시 에러 발생 테스트
        invalid_emails = [
            "invalid-email",
            "another.invalid",
            "invalid@",
            "@invalid.com",
            "test@.com",
            "test@@example.com",
            "test@com.",
        ]
        for email in invalid_emails:
            with self.assertRaises(ValueError):
                User.objects.create_user(
                    email=email,
                    username="testuser",
                    name="Test User",
                    password="testpassword",
                )

    def test_valid_email_format(self):
        # 유효한 이메일 형식으로 유저 생성 테스트
        valid_emails = [
            "test@example.com",
            "test.user@example.com",
            "test_user@example.co.kr",
            "test1234@example.com",
            "test-user@example.com",
        ]
        for i, email in enumerate(valid_emails):
            username = f"testuser{i}"
            user = User.objects.create_user(
                email=email,
                username=username,
                name="Test User",
                password="testpassword",
            )
            self.assertEqual(user.email, email)

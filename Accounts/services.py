import requests
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount, SocialToken
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.naver.views import NaverOAuth2Adapter
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class AuthService:
    @staticmethod
    def authenticate_user(email, password):
        user = authenticate(email=email, password=password)
        if not user:
            return None, "이메일 또는 비밀번호가 올바르지 않습니다."
        if not user.is_active:
            return None, "이메일 인증이 필요합니다."
        return user, None

    @staticmethod
    def generate_tokens(user):
        refresh = RefreshToken.for_user(user)
        return {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "expires_in": settings.JWT_EXPIRES_IN,
        }

    @staticmethod
    def blacklist_token(token):
        try:
            RefreshToken(token).blacklist()
            return True, None
        except Exception as e:
            return False, str(e)


class SocialLoginService:
    @staticmethod
    def get_adapter_config(social_type):
        if social_type == "naver":
            return {
                "adapter_class": NaverOAuth2Adapter,
                "callback_url": settings.NAVER_CALLBACK_URL,
                "client_id": settings.NAVER_CLIENT_ID,
                "client_secret": settings.NAVER_CLIENT_SECRET,
            }
        elif social_type == "kakao":
            return {
                "adapter_class": KakaoOAuth2Adapter,
                "callback_url": settings.KAKAO_CALLBACK_URL,
                "client_id": settings.KAKAO_CLIENT_ID,
                "client_secret": settings.KAKAO_CLIENT_SECRET,
            }
        return None

    @staticmethod
    def get_access_token(adapter_config, code):
        token_url = adapter_config["adapter_class"].access_token_url
        token_params = {
            "grant_type": "authorization_code",
            "client_id": adapter_config["client_id"],
            "client_secret": adapter_config["client_secret"],
            "code": code,
            "redirect_uri": adapter_config["callback_url"],
        }

        try:
            token_response = requests.post(token_url, data=token_params)
            token_response.raise_for_status()
            token_data = token_response.json()

            if "access_token" not in token_data:
                return None, "액세스 토큰을 얻는데 실패했습니다."

            return token_data["access_token"], None
        except requests.RequestException as e:
            error_detail = str(e)
            if hasattr(e, "response") and e.response:
                error_detail += f" 응답: {e.response.text}"
            return None, f"액세스 토큰을 얻는 데 실패했습니다: {error_detail}"

    @staticmethod
    def get_user_info(adapter_class, request, access_token):
        adapter = adapter_class(request)
        token = SocialToken(token=access_token)

        try:
            social_info = adapter.complete_login(request, None, token=token)
            return social_info, None
        except Exception as e:
            return None, f"사용자 정보를 가져오는 데 실패했습니다: {e}"

    @staticmethod
    def get_or_create_social_user(social_type, social_info):
        email = social_info.user.email
        try:
            social_account = SocialAccount.objects.get(
                provider=social_type, uid=social_info.account.uid
            )
            user = social_account.user
        except SocialAccount.DoesNotExist:
            try:
                user = User.objects.get(email=email)
                SocialAccount.objects.create(
                    user=user,
                    provider=social_type,
                    uid=social_info.account.uid,
                    extra_data=social_info.account.extra_data,
                )
                user.is_social = True
                user.social_login = social_type
                user.save()
            except User.DoesNotExist:
                username = f"{social_type}_{email.split('@')[0]}"
                name = email.split("@")[0]
                user = User.objects.create_user(
                    email=email,
                    username=username,
                    name=name,
                    is_active=True,
                    is_social=True,
                    social_login=social_type,
                )
                SocialAccount.objects.create(
                    user=user,
                    provider=social_type,
                    uid=social_info.account.uid,
                    extra_data=social_info.account.extra_data,
                )
                EmailAddress.objects.get_or_create(
                    user=user, email=email, verified=True, primary=True
                )
        return user


class EmailService:
    @staticmethod
    def send_verification_email(user):
        token = default_token_generator.make_token(user)
        verification_url = (
            f"{settings.FRONTEND_URL}/verify-email?token={token}&email={user.email}"
        )

        subject = "ILOG 회원가입 인증 메일입니다."
        message = render_to_string(
            "email_verification.html",
            {"user": user, "verification_url": verification_url},
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
            html_message=message,
        )

        return token

    @staticmethod
    def send_password_reset_email(user):
        token = default_token_generator.make_token(user)
        reset_url = (
            f"{settings.FRONTEND_URL}/reset-password?token={token}&email={user.email}"
        )

        subject = "ILOG 비밀번호 재설정 안내"
        message = render_to_string(
            "password_reset_email.html", {"user": user, "reset_url": reset_url}
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
            html_message=message,
        )

        return token

    @staticmethod
    def verify_token(user, token):
        return default_token_generator.check_token(user, token)


class UserService:
    @staticmethod
    def find_user_by_email(email):
        try:
            return User.objects.get(email=email), None
        except User.DoesNotExist:
            return None, "입력하신 이메일로 등록된 계정이 없습니다."

    @staticmethod
    def find_user_by_name_and_phone(name, phone):
        try:
            user = User.objects.get(name=name, phone=phone)
            return user, None
        except User.DoesNotExist:
            return None, "입력하신 정보와 일치하는 회원이 없습니다."

    @staticmethod
    def reset_password(user, new_password):
        user.set_password(new_password)
        user.save()
        return True

    @staticmethod
    def activate_user(user):
        user.is_active = True
        user.save()
        EmailAddress.objects.filter(user=user, email=user.email).update(
            verified=True, primary=True
        )
        return user

    @staticmethod
    def check_email_uniqueness(email):
        if User.objects.filter(email=email).exists():
            return False, "이미 사용 중인 이메일입니다."
        return True, None

    @staticmethod
    def check_username_uniqueness(username, user_id=None):
        query = User.objects.filter(username=username)
        if user_id:
            query = query.exclude(id=user_id)
        if query.exists():
            return False, "이미 사용 중인 닉네임입니다."
        return True, None

    @staticmethod
    def check_phone_uniqueness(phone, user_id=None):
        if not phone:
            return True, None
        query = User.objects.filter(phone=phone)
        if user_id:
            query = query.exclude(id=user_id)
        if query.exists():
            return False, "이미 사용 중인 전화번호입니다."
        return True, None

    @staticmethod
    def verify_current_password(user, current_password):
        if not user.check_password(current_password):
            return False, "현재 비밀번호가 일치하지 않습니다."
        return True, None

    @staticmethod
    def update_user_profile(user, username=None, phone=None):
        if username:
            user.username = username
        if phone:
            user.phone = phone
        user.save()
        return user

    @staticmethod
    def update_password(user, new_password):
        user.set_password(new_password)
        user.save()
        return user

    @staticmethod
    def delete_user_account(user):
        user.delete()
        return True
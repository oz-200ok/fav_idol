import requests
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount, SocialToken
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.naver.views import NaverOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=50)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        email = data.get("email", "")
        password = data.get("password", "")

        if email and password:
            user = authenticate(email=email, password=password)

            if not user:
                raise serializers.ValidationError(
                    "이메일 또는 비밀번호가 올바르지 않습니다."
                )

            if not user.is_active:
                raise serializers.ValidationError("이메일 인증이 필요합니다.")

            refresh = RefreshToken.for_user(user)

            return {
                "user": user,
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "expires_in": settings.JWT_EXPIRES_IN,  # settings 파일에서 가져오기
            }
        else:
            raise serializers.ValidationError("이메일과 비밀번호를 모두 입력해주세요.")


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


class SocialLoginSerializer(serializers.Serializer):
    social_type = serializers.CharField(required=True)
    code = serializers.CharField(required=True)

    def validate(self, attrs):
        social_type = attrs.get("social_type")
        code = attrs.get("code")

        if not social_type or not code:
            raise serializers.ValidationError("소셜 타입과 인가 코드는 필수입니다.")

        if social_type not in ["naver", "kakao"]:
            raise serializers.ValidationError("지원하지 않는 소셜 로그인 타입입니다.")

        # 소셜 로그인 타입에 따라 어댑터 선택
        if social_type == "naver":
            adapter_class = NaverOAuth2Adapter
            callback_url = settings.NAVER_CALLBACK_URL
            client_id = settings.NAVER_CLIENT_ID
            client_secret = settings.NAVER_CLIENT_SECRET
        elif social_type == "kakao":
            adapter_class = KakaoOAuth2Adapter
            callback_url = settings.KAKAO_CALLBACK_URL
            client_id = settings.KAKAO_CLIENT_ID
            client_secret = settings.KAKAO_CLIENT_SECRET

        # 인가 코드로 액세스 토큰 요청
        token_url = adapter_class.access_token_url
        token_params = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": callback_url,
        }

        try:
            token_response = requests.post(token_url, data=token_params)
            token_response.raise_for_status()
            print(f"토큰 응답: {token_response.text}")
        except requests.RequestException as e:
            error_detail = str(e)
            if hasattr(e, "response") and e.response:
                error_detail += f" 응답: {e.response.text}"
            raise serializers.ValidationError(
                f"액세스 토큰을 얻는 데 실패했습니다: {error_detail}"
            )

        token_data = token_response.json()

        if "access_token" not in token_data:
            raise serializers.ValidationError("액세스 토큰을 얻는데 실패했습니다.")

        access_token = token_data["access_token"]
        token = SocialToken(token=access_token)

        # 액세스 토큰으로 사용자 정보 요청
        adapter = adapter_class(self.context["request"])
        try:
            social_info = adapter.complete_login(
                self.context["request"], None, token=token
            )
        except OAuth2Error as e:
            raise serializers.ValidationError(
                f"사용자 정보를 가져오는 데 실패했습니다: {e}"
            )
        except Exception as e:
            raise serializers.ValidationError(
                f"사용자 정보를 가져오는 데 실패했습니다: {e}"
            )

        # 소셜 계정으로 사용자 찾기 또는 생성
        extra_data = social_info.account.extra_data
        uid = extra_data["id"]
        social_info.uid = uid
        user = get_or_create_social_user(social_type, social_info)

        # JWT 토큰 생성
        refresh = RefreshToken.for_user(user)

        return {
            "user": user,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "expires_in": settings.JWT_EXPIRES_IN,  # settings 파일에서 가져오기
        }


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh_token"]
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except Exception as e:
            raise serializers.ValidationError(str(e))

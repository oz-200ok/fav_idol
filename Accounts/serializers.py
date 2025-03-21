from rest_framework import serializers

from .services import AuthService, SocialLoginService


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=50)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        email = data.get("email", "")
        password = data.get("password", "")

        if not email or not password:
            raise serializers.ValidationError("이메일과 비밀번호를 모두 입력해주세요.")

        user, error = AuthService.authenticate_user(email, password)
        if error:
            raise serializers.ValidationError(error)

        tokens = AuthService.generate_tokens(user)
        return {
            "user": user,
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "expires_in": tokens["expires_in"],
        }


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

        # 어댑터 설정 가져오기
        adapter_config = SocialLoginService.get_adapter_config(social_type)
        if not adapter_config:
            raise serializers.ValidationError("지원하지 않는 소셜 로그인 타입입니다.")

        # 액세스 토큰 요청
        access_token, error = SocialLoginService.get_access_token(adapter_config, code)
        if error:
            raise serializers.ValidationError(error)

        # 사용자 정보 요청
        social_info, error = SocialLoginService.get_user_info(
            adapter_config["adapter_class"], self.context["request"], access_token
        )
        if error:
            raise serializers.ValidationError(error)

        # 소셜 계정으로 사용자 찾기 또는 생성
        social_info.account.uid = social_info.account.extra_data["id"]
        user = SocialLoginService.get_or_create_social_user(social_type, social_info)

        # JWT 토큰 생성
        tokens = AuthService.generate_tokens(user)
        return {
            "user": user,
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "expires_in": tokens["expires_in"],
        }

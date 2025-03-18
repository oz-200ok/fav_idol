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
                "expires_in": 86400,  # 24시간
            }
        else:
            raise serializers.ValidationError("이메일과 비밀번호를 모두 입력해주세요.")

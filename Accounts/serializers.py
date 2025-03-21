from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User
from .services import AuthService, EmailService, SocialLoginService, UserService


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


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh_token"]
        return attrs

    def save(self, **kwargs):
        success, error = AuthService.blacklist_token(self.token)
        if not success:
            raise serializers.ValidationError(error)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ("email", "password", "username", "name", "phone")
        extra_kwargs = {
            "email": {"required": True},
            "username": {"required": True},
            "name": {"required": True},
            "phone": {"required": True},
        }

    def validate(self, attrs):
        # 이메일 중복 검사
        email = attrs.get("email")
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "이미 사용 중인 이메일입니다."})

        # 닉네임 중복 검사
        username = attrs.get("username")
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {"username": "이미 사용 중인 닉네임입니다."}
            )

        # 전화번호 중복 검사
        phone = attrs.get("phone")
        if phone and User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError(
                {"phone": "이미 사용 중인 전화번호입니다."}
            )

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            name=validated_data["name"],
            phone=validated_data["phone"],
            password=validated_data["password"],
            is_active=False,  # 이메일 인증 전까지는 비활성화
        )
        return user


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        token = attrs.get("token")
        email = attrs.get("email")

        if not token or not email:
            raise serializers.ValidationError("토큰과 이메일은 필수 파라미터입니다.")

        user, error = UserService.find_user_by_email(email)
        if error:
            raise serializers.ValidationError(error)

        # 토큰 검증
        if EmailService.verify_token(user, token):
            # 사용자 활성화
            user = UserService.activate_user(user)

            return {
                "user": user,
                "message": "회원가입이 완료되었습니다",
                "data": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "phone": user.phone,
                },
            }
        else:
            raise serializers.ValidationError("유효하지 않은 인증 토큰입니다.")


class FindEmailSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)

    def validate(self, attrs):
        name = attrs.get("name")
        phone = attrs.get("phone")

        if not name or not phone:
            raise serializers.ValidationError("이름과 전화번호는 필수 입력 항목입니다.")

        user, error = UserService.find_user_by_name_and_phone(name, phone)
        if error:
            raise serializers.ValidationError(error)

        return {
            "email": user.email,
            "message": "회원님의 정보와 일치하는 이메일을 찾았습니다.",
        }


class FindPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")
        user, error = UserService.find_user_by_email(email)
        if error:
            raise serializers.ValidationError(error)

        # 비밀번호 재설정 이메일 발송
        EmailService.send_password_reset_email(user)
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        token = attrs.get("token")
        email = attrs.get("email")
        new_password = attrs.get("new_password")

        user, error = UserService.find_user_by_email(email)
        if error:
            raise serializers.ValidationError(error)

        # 토큰 검증
        if EmailService.verify_token(user, token):
            # 비밀번호 변경
            UserService.reset_password(user, new_password)
            return attrs
        else:
            raise serializers.ValidationError("유효하지 않은 토큰입니다.")

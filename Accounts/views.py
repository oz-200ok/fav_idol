from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    CheckDuplicateSerializer,
    FindEmailSerializer,
    FindPasswordSerializer,
    LoginSerializer,
    LogoutSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    SocialLoginSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    VerifyEmailSerializer,
)
from .services import EmailService, UserService


def custom_response(data=None, status_code=status.HTTP_200_OK):
    if data is None:
        return Response(status=status_code)
    return Response({"data": data}, status=status_code)


class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer

    def perform_create(self, serializer):
        return serializer.validated_data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.perform_create(serializer)
        return custom_response(
            {
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "expires_in": data["expires_in"],
                "user": {"id": data["user"].id, "email": data["user"].email},
            }
        )


class SocialLoginView(generics.CreateAPIView):
    serializer_class = SocialLoginSerializer

    def perform_create(self, serializer):
        return serializer.validated_data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.perform_create(serializer)
        return custom_response(
            {
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "expires_in": data["expires_in"],
                "user": {"id": data["user"].id, "email": data["user"].email},
            }
        )


class LogoutView(generics.CreateAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return custom_response(status_code=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        EmailService.send_verification_email(user)
        return user

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        return custom_response(
            {
                "user_id": user.id,
                "email": user.email,
                "is_verified": user.is_active,
                "resend_available_in": 600,  # 10분 후 재발송 가능
            },
            status_code=status.HTTP_201_CREATED,
        )


class VerifyEmailView(generics.RetrieveAPIView):
    serializer_class = VerifyEmailSerializer

    def get_object(self):
        return None

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "token",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description="이메일 인증 토큰",
            ),
            openapi.Parameter(
                "email",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description="사용자 이메일",
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return custom_response(serializer.validated_data["data"])


class FindEmailView(generics.CreateAPIView):
    serializer_class = FindEmailSerializer

    def perform_create(self, serializer):
        return serializer.validated_data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.perform_create(serializer)
        return custom_response({"email": data["email"]})


class FindPasswordView(generics.CreateAPIView):
    serializer_class = FindPasswordSerializer

    def perform_create(self, serializer):
        return serializer.validated_data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return custom_response()


class ResetPasswordView(generics.CreateAPIView):
    serializer_class = ResetPasswordSerializer

    def perform_create(self, serializer):
        return serializer.validated_data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return custom_response(status_code=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return custom_response(serializer.data)


class UserProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        return serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return custom_response(
            {
                "username": instance.username,
                "phone": instance.phone,
            },
            status_code=status.HTTP_201_CREATED,
        )


class CheckDuplicateView(generics.GenericAPIView):
    serializer_class = CheckDuplicateSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "type",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description="확인할 항목 (username, email, phone)",
            ),
            openapi.Parameter(
                "value",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description="확인할 값",
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        return custom_response(serializer.validated_data)


class UserDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_destroy(self, instance):
        UserService.delete_user_account(instance)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return custom_response(status_code=status.HTTP_204_NO_CONTENT)

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    FindEmailSerializer,
    FindPasswordSerializer,
    LoginSerializer,
    LogoutSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    SocialLoginSerializer,
    UserProfileSerializer,
    VerifyEmailSerializer,
)
from .services import EmailService


class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        access_token = serializer.validated_data["access_token"]
        refresh_token = serializer.validated_data["refresh_token"]
        expires_in = serializer.validated_data["expires_in"]

        return Response(
            {
                "data": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_in": expires_in,
                    "user": {"id": user.id, "email": user.email},
                }
            },
            status=status.HTTP_200_OK,
        )


class SocialLoginView(generics.CreateAPIView):
    serializer_class = SocialLoginSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        access_token = serializer.validated_data["access_token"]
        refresh_token = serializer.validated_data["refresh_token"]
        expires_in = serializer.validated_data["expires_in"]

        return Response(
            {
                "data": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_in": expires_in,
                    "user": {"id": user.id, "email": user.email},
                }
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(generics.CreateAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        token = EmailService.send_verification_email(user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user = serializer.instance

        return Response(
            {
                "data": {
                    "user_id": user.id,
                    "email": user.email,
                    "is_verified": user.is_active,
                    "resend_available_in": 600,  # 10분 후 재발송 가능
                }
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(generics.RetrieveAPIView):
    serializer_class = VerifyEmailSerializer

    def get_object(self):
        return None

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                "data": {
                    **serializer.validated_data["data"],
                }
            },
            status=status.HTTP_200_OK,
        )


class FindEmailView(generics.CreateAPIView):
    serializer_class = FindEmailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"data": {"email": serializer.validated_data["email"]}},
            status=status.HTTP_200_OK,
        )


class FindPasswordView(generics.CreateAPIView):
    serializer_class = FindPasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_200_OK)


class ResetPasswordView(generics.CreateAPIView):
    serializer_class = ResetPasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user    
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {"data": serializer.data},
            status=status.HTTP_200_OK
        )
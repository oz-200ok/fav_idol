from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    RegisterSerializer,
    SocialLoginSerializer,
    VerifyEmailSerializer,
)


class LoginView(APIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            access_token = serializer.validated_data["access_token"]
            refresh_token = serializer.validated_data["refresh_token"]
            expires_in = serializer.validated_data["expires_in"]

            return Response(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_in": expires_in,
                    "user": {"id": user.id, "email": user.email},
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SocialLoginView(APIView):
    def post(self, request):
        serializer = SocialLoginSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            access_token = serializer.validated_data["access_token"]
            refresh_token = serializer.validated_data["refresh_token"]
            expires_in = serializer.validated_data["expires_in"]

            return Response(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_in": expires_in,
                    "user": {"id": user.id, "email": user.email},
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "로그아웃 되었습니다."}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # 이메일 인증 토큰 생성
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # 인증 이메일 발송
            verification_url = (
                f"{settings.FRONTEND_URL}/verify-email?token={token}&email={user.email}"
            )
            subject = "I-LOG 회원가입 인증 메일입니다."
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

            return Response(
                {
                    "message": "회원 가입이 완료되었으며, 인증 이메일이 발송되었습니다.",
                    "data": {
                        "user_id": user.id,
                        "email": user.email,
                        "is_verified": user.is_active,
                        "resend_available_in": 600,  # 10분 후 재발송 가능
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    def get(self, request):
        serializer = VerifyEmailSerializer(data=request.query_params)
        if serializer.is_valid():
            return Response(
                {
                    "message": serializer.validated_data["message"],
                    "data": serializer.validated_data["data"],
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

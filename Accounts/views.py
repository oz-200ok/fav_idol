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
    return Response({"data": data}, status=status_code)

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
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)


class UserProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {
                "data": {
                    "username": instance.username,
                    "phone": instance.phone,
                }
            },
            status=status.HTTP_201_CREATED,
        )


class CheckDuplicateView(generics.GenericAPIView):
    serializer_class = CheckDuplicateSerializer

    def get(self, request):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # 중복이 없으면 여기까지 실행됨 (중복 있으면 ValidationError 발생)
        return Response({"data": serializer.validated_data}, status=status.HTTP_200_OK)


class UserDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()

        UserService.delete_user_account(user)

        return Response(status=status.HTTP_200_OK)

from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import LoginSerializer, SocialLoginSerializer


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

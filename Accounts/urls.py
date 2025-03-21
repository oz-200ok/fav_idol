from django.urls import path

from .views import (
    FindEmailView,
    FindPasswordView,
    LoginView,
    LogoutView,
    RegisterView,
    ResetPasswordView,
    SocialLoginView,
    UserProfileUpdateView,
    UserProfileView,
    VerifyEmailView,
)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("social-login/", SocialLoginView.as_view(), name="social-login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify_email"),
    path("find-email/", FindEmailView.as_view(), name="find_email"),
    path("find-password/", FindPasswordView.as_view(), name="find_password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
    path("me/", UserProfileView.as_view(), name="user_profile"),
    path('profile/', UserProfileUpdateView.as_view(), name='user-profile-update'),
]

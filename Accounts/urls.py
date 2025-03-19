from django.urls import path

from .views import LoginView, LogoutView, SocialLoginView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("social-login/", SocialLoginView.as_view(), name="social-login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]

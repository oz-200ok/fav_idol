from django.urls import path

from .views import LoginView, SocialLoginView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("social-login/", SocialLoginView.as_view(), name="social-login"),
]

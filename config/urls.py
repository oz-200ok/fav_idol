"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ilog/account/", include("Accounts.urls")),
    path("ilog/schedule/", include("Schedules.urls")),
    path("ilog/idol/", include("Idols.urls")),
    path("ilog/service/", include("Preferences.urls")),
    path("ilog/accounts/", include("allauth.urls")),
]

if settings.DEBUG:
    schema_view = get_schema_view(
        openapi.Info(
            title="I-LOG API",
            default_version="v1",
            description="아이돌 스케줄 관리 API 문서",
            contact=openapi.Contact(email="contact@example.com"),
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )

    urlpatterns += [
        path(
            "swagger/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
    ]
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin  # UserAdmin을 임포트

from .models import User  # Accounts 앱의 User 모델을 임포트


# User 모델을 관리자 페이지에 등록
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "id",
        "email",
        "username",
        "name",
        "password",
        "is_admin",
        "is_staff",
        "is_superuser",
        "is_active",
        "is_social",
        "social_login",
        "created_at",
    )  # 관리자 페이지에 표시할 필드 목록
    list_filter = (
        "is_admin",
        "is_superuser",
        "is_active",
        "is_social",
    )  # 필터링에 사용할 필드 목록
    search_fields = ("email", "username", "name")  # 검색에 사용할 필드 목록
    ordering = ("email",)  # 정렬 기준

from django.contrib import admin
from .models import UserGroupSubscribe

@admin.register(UserGroupSubscribe)
class UserGroupSubscribeAdmin(admin.ModelAdmin):
    # 관리자 페이지 목록에 표시할 필드
    list_display = ('user', 'group', 'notification')
    # 검색 가능한 필드
    search_fields = ('user__username', 'group__name')
    # 필터 옵션 추가
    list_filter = ('notification',)

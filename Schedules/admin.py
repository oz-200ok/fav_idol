from django.contrib import admin

from .models import Schedule  # Schedule 모델 임포트


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "user",
        "group",
        "start_time",
        "end_time",
        "location",
        "display_participating_members",  # 참가 멤버를 표시하는 메서드를 추가합니다.
        "created_at",
        "updated_at",
    )  # 관리자 페이지의 스케줄 목록에 표시할 필드들을 지정합니다.
    # id, title, user, group, start_time, end_time, location, created_at, updated_at 필드를 표시합니다.

    list_filter = (
        "user",
        "group",
        "start_time",
    )  # 관리자 페이지의 스케줄 목록에서 필터링에 사용할 필드들을 지정합니다.
    # user, group, start_time 필드를 기준으로 필터링할 수 있습니다.

    search_fields = (
        "title",
        "description",
        "location",
    )  # 관리자 페이지의 스케줄 목록에서 검색에 사용할 필드들을 지정합니다.
    # title, description, location 필드를 기준으로 검색할 수 있습니다.

    ordering = (
        "start_time",
    )  # 관리자 페이지의 스케줄 목록을 정렬할 때 사용할 필드를 지정합니다.
    # start_time 필드를 기준으로 오름차순으로 정렬합니다.

    fieldsets = (
        (
            None,
            {"fields": ("title", "user", "group")},
        ),  # 제목 없이 title, user, group 필드를 표시합니다.
        (
            "Schedule Details",
            {"fields": ("description", "location", "start_time", "end_time")},
        ),  # "Schedule Details"라는 제목으로 description, location, start_time, end_time 필드를 그룹화하여 표시합니다.
        (
            "Participating Members",
            {"fields": ("participating_members",)},
        ),  # "Participating Members"라는 제목으로 participating_members 필드를 그룹화하여 표시합니다.
        (
            "Important dates",
            {"fields": ("created_at", "updated_at")},
        ),  # "Important dates"라는 제목으로 created_at, updated_at 필드를 그룹화하여 표시합니다.
    )  # 관리자 페이지에서 스케줄 정보를 수정할 때 보여줄 필드들을 그룹화하여 정의합니다.
    # 각 튜플은 (그룹 제목, {'fields': (필드 목록)}) 형태로 구성됩니다.

    readonly_fields = (
        "created_at",
        "updated_at",
    )  # 관리자 페이지에서 수정할 수 없도록 읽기 전용으로 설정할 필드들을 지정합니다.
    # created_at, updated_at 필드는 읽기 전용으로 표시됩니다.

    def display_participating_members(self, obj):
        """
        참가 멤버들을 쉼표로 구분된 문자열로 표시합니다.
        """
        return ", ".join([member.name for member in obj.participating_members.all()])

    display_participating_members.short_description = (
        "Participating Members"  # 메서드의 컬럼 이름을 설정합니다.
    )

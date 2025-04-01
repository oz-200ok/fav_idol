from django.contrib import admin
from django.utils.html import format_html

from .models import Agency, Group, Idol


# Group을 Agency에 테이븛 형식 Inline으로 추가
class GroupInline(admin.TabularInline):
    model = Group
    extra = 0


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "contact", "image_preview")

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 100px;" />', obj.image)
        return None


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "agency", "image_preview")

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 100px;" />', obj.image)
        return None

    search_fields = ("name",)


class IdolInline(admin.TabularInline):
    model = Idol
    extra = 0


@admin.register(Idol)
class IdolAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "group")
    search_fields = ("name",)
    list_filter = ("group",)

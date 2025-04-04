from django.urls import path

from .views import *

urlpatterns = [
    path("", ScheduleListView.as_view(), name="schedule"),
    path("<int:pk>/", ScheduleDetailView.as_view(), name="schedule_detail"),
    path(
        "group/<int:group_id>/", GroupScheduleListView.as_view(), name="group_schedule"
    ),
    path("myschedules/", UserScheduleListView.as_view(), name="my_schedules"),
    path("uploadschedule/", ExcelUploadview.as_view(), name="upload_schedule"),
]

from django.urls import path

from .views import *


class ExcelUploadView:
    pass


urlpatterns = [
    path("", ScheduleListView.as_view(), name="schedule"),
    path("<int:pk>/", ScheduleDetailView.as_view(), name="schedule_detail"),
    path(
        "group/<int:group_id>/", GroupScheduleListView.as_view(), name="group_schedule"
    ),
    path("myschedules/", UserScheduleListView.as_view(), name="my_schedules"),
    path('uploadschedule/', ExcelUploadView.as_view(), name='upload_schedule'),
]

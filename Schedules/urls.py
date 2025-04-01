from django.urls import path

from .views import *

urlpatterns = [
    path("", ScheduleListView.as_view(), name="schedule"),
    path("<int:pk>/", ScheduleDetailView.as_view(), name="schedule_detail"),
    path(
        "group/<int:group_id>/", GroupScheduleListView.as_view(), name="group_schedule"
    ),
    path('my-schedules/', UserScheduleListView.as_view(), name='my_schedules'),
]

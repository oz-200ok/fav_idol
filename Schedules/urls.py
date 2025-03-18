from django.urls import path

from .views import *

urlpatterns = [
    path("", ScheduleListView.as_view(), name="schedule"),
    path("<int:pk>/", ScheduleDetailView.as_view(), name="schedule_detail"),
    path("create/", ScheduleCreateView.as_view(), name="schedule_create"),
    path("<int:pk>/update/", ScheduleUpdateView.as_view(), name="schedule_update"),
    path("group/<int:group_id>/", GroupScheduleListView.as_view(), name="group_schedule"),
]
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import SubscribeViewSet, UserScheduleDetailView, UserSubscribedSchedulesView

router = DefaultRouter()
router.register(r"subscriptions", SubscribeViewSet, basename="subscribe")


urlpatterns = [
    *router.urls,
    path(
        "schedules/",
        UserSubscribedSchedulesView.as_view(),
        name="user-subscribed-schedules",
    ),
    path(
        "schedules/<int:schedule_id>/",
        UserScheduleDetailView.as_view(),
        name="user-schedule-detail",
    ),
]

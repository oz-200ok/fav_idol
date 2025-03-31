from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import SubscribeViewSet, UserSubscribedSchedulesView

router = DefaultRouter()
router.register(r"subscriptions", SubscribeViewSet, basename="subscribe")


urlpatterns = [
    *router.urls,
    path('schedules/', UserSubscribedSchedulesView.as_view(), name='user-subscribed-schedules'),
]

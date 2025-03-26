from rest_framework.routers import DefaultRouter

from .views import SubscribeViewSet

router = DefaultRouter()
router.register(r"subscriptions", SubscribeViewSet, basename="subscribe")


urlpatterns = [
    *router.urls,
]

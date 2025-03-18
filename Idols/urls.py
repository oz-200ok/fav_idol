from django.urls import path

from .views import AgencyListView, GroupListView, IdolListView

urlpatterns = [
    # 에이전시 리스트
    path("agencies/", AgencyListView.as_view(), name="agency_list"),
    path("agencies/<str:name>/", AgencyListView.as_view(), name="agency_list_name"),
    # 그룹 리스트
    path("groups/", GroupListView.as_view(), name="group_list"),
    # 아이돌 리스트
    path("idols/", IdolListView.as_view(), name="idol_list"),
]

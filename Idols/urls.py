from django.urls import path

from .views import (
    AgencyDetailView,
    AgencyListView,
    GroupByNameView,
    GroupDetailView,
    GroupListView,
    IdolDetailView,
    IdolListView,
)

urlpatterns = [
    # 에이전시 리스트
    path("agencies/", AgencyListView.as_view(), name="agency_list"),
    path("agencies/<int:pk>/", AgencyDetailView.as_view(), name="agency_detail"),
    # 그룹 리스트
    path("groups/", GroupListView.as_view(), name="group_list"),
    path(
        "groups/<int:pk>/", GroupDetailView.as_view(), name="group_detail"
    ),  # 그룹 디테일
    path(
        "groups/<str:name>/", GroupByNameView.as_view(), name="group_by_name"
    ),
    # 그룹 이름으로 검색
    # 아이돌 리스트
    path("idols/", IdolListView.as_view(), name="idol_list"),
    path(
        "idols/<int:pk>/", IdolDetailView.as_view(), name="idol_detail"
    ),  # 디테일 확인
]

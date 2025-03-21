from django.urls import path

from .views import AgencyListView, GroupListView, IdolListView

urlpatterns = [
    # 에이전시 리스트
    path("agencies/", AgencyListView.as_view(), name="agency_list"),
    path("agencies/<int:pk>/", AgencyListView.as_view(), name="agency_detail"),
    # 그룹 리스트
    path("groups/", GroupListView.as_view(), name="group_list"),
    path(
        "groups/<int:pk>/", GroupListView.as_view(), name="group_detail"
    ),  # 삭제 요청을 위한 pk 추가
    # 아이돌 리스트
    path("idols/", IdolListView.as_view(), name="idol_list"),
    path(
        "idols/<int:pk>/", IdolListView.as_view(), name="idol_detail"
    ),  # 삭제 요청을 위한 pk 추가
]

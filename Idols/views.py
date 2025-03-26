from django.db.models import Count
from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    get_object_or_404,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from config.permissions import IsAdminOrReadOnly, IsSuperUser

from .models import Agency, Group, Idol
from .serializers import AgencySerializer, GroupSerializer, IdolSerializer


# 에이전시 리스트
class AgencyListView(ListCreateAPIView):

    queryset = Agency.objects.all()
    serializer_class = AgencySerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]  # 읽기 요청은 모든 사용자 허용
        return super().get_permissions()  # 기본 권한(관리자 쓰기)


class AgencyDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Agency.objects.all()
    serializer_class = AgencySerializer
    permission_classes = [IsSuperUser]


# 그룹 리스트
class GroupListView(ListCreateAPIView):
    queryset = Group.objects.select_related("agency").annotate(
        member_count=Count("idol")
    )
    serializer_class = GroupSerializer
    permission_classes = [IsAdminOrReadOnly]


class GroupDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.select_related("agency")
    serializer_class = GroupSerializer
    permission_classes = [IsSuperUser]


# 아이돌 리스트
class IdolListView(ListCreateAPIView):
    queryset = Idol.objects.select_related("group")
    serializer_class = IdolSerializer
    permission_classes = [IsAdminOrReadOnly]


class IdolDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Idol.objects.select_related("group")
    serializer_class = IdolSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        deleted_idol_data = {
            "idol.id": instance.id,
            "group_id": instance.group_id,
            "name": instance.name,
        }
        self.perform_destroy(instance)

        return Response(
            {"data": deleted_idol_data},
        )

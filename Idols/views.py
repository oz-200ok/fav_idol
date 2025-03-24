from django.db.models import Count
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .models import Agency, Group, Idol
from config.permissions import IsAdminOrReadOnly, IsSuperUser
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
    permission_classes = [IsAdminOrReadOnly]

    def delete(self, request, pk):
        # 해당 ID의 객체를 가져오고, 없으면 404 반환
        idol = get_object_or_404(Idol, pk=pk)

        # 삭제된 데이터를 반환할 정보 구성
        deleted_data = {
            "id": idol.id,
            "name": idol.name,
            "group_id": idol.group_id,
        }

        # 객체 삭제
        idol.delete()

        # 응답 반환
        return Response(
            {"message": "삭제 완료", "data": deleted_data},
            status=status.HTTP_200_OK,
        )
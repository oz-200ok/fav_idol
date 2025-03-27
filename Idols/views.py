from django.db.models import Count
from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    get_object_or_404,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from config.permissions import IsAdminOrReadOnly, IsSuperUser

from .models import Agency, Group, Idol
from .serializers import AgencySerializer, GroupSerializer, IdolSerializer


# 에이전시 리스트
class AgencyListView(ListCreateAPIView):
    queryset = Agency.objects.all()
    serializer_class = AgencySerializer
    permission_classes = [IsAdminOrReadOnly]

    @swagger_auto_schema(
        operation_description="에이전시 목록을 가져옵니다.",
        responses={200: AgencySerializer(many=True)}  # 목록 반환
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="새 에이전시를 생성합니다.",
        request_body=AgencySerializer,  # POST 요청 시 필요한 데이터 정의
        responses={
            201: AgencySerializer,  # 생성 성공 시 반환될 데이터
            400: "유효하지 않은 요청 데이터입니다.",  # 유효성 오류
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]  # 읽기 요청은 모든 사용자 허용
        return super().get_permissions()  # 관리자만 쓰기 허용


class AgencyDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Agency.objects.all()
    serializer_class = AgencySerializer
    permission_classes = [IsSuperUser]

    @swagger_auto_schema(
        operation_description="특정 에이전시 데이터를 조회합니다.",
        responses={200: AgencySerializer},  # 성공 시 반환할 데이터 스키마
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="특정 에이전시 데이터를 업데이트합니다.",
        request_body=AgencySerializer,  # 요청 시 필요한 데이터 스키마
        responses={
            200: AgencySerializer,  # 성공 시 반환할 데이터 스키마
            400: "요청 데이터 유효성 검사 실패",
        },
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="특정 에이전시 데이터를 삭제합니다.",
        responses={
            204: "데이터 삭제 성공",  # No Content 응답
            404: "에이전시를 찾을 수 없습니다.",
        },
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


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

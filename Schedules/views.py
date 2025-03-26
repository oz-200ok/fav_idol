from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.response import Response

from .models import Schedule
from .permissions import IsAdminOrReadOnly
from .serializer import ScheduleSerializer


class ScheduleListView(ListCreateAPIView):
    """
    일정 목록 조회 및 등록
    """

    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAdminOrReadOnly]

    @swagger_auto_schema(request_body=ScheduleSerializer)
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request  # request 객체를 context에 추가
        return context


class ScheduleDetailView(RetrieveUpdateDestroyAPIView):
    """
    특정 일정 상세 조회, 수정 및 삭제
    """

    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAdminOrReadOnly]

    @swagger_auto_schema(
        request_body=ScheduleSerializer,
        responses={
            200: openapi.Response(
                description="일정 삭제 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "schedule.id": openapi.Schema(type=openapi.TYPE_INTEGER, description="일정 ID"),
                        "group_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="그룹 ID"),
                        "title": openapi.Schema(type=openapi.TYPE_STRING, description="일정 제목"),
                    },
                ),
            ),
            404: openapi.Response(
                description="일정을 찾을 수 없음",
            ),
        },
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        deleted_schedule_data = {
            "schedule.id": instance.id,
            "group_id": instance.group_id,
            "title": instance.title,
        }
        self.perform_destroy(instance)
        return Response(deleted_schedule_data, status=200)

    @swagger_auto_schema(
        request_body=ScheduleSerializer,
        responses={
            200: openapi.Response(
                description="일정 수정 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "group_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="그룹 ID"),
                        "schedule_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="일정 ID"),
                    },
                ),
            ),
            201: openapi.Response(
                description="일정 등록 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "group_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="그룹 ID"),
                        "schedule_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="일정 ID"),
                    },
                ),
            ),
        },
    )
    def update(self, request, *args, **kwargs):
        # 일정 수정 처리 로직...
        updated_data = {
            "group_id": request.data.get("group_id"),
            "schedule_id": self.kwargs["pk"],
        }
        return Response(updated_data, status=200)

    @swagger_auto_schema(
        request_body=ScheduleSerializer,
        responses={
            201: openapi.Response(
                description="일정 등록 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "group_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="그룹 ID"),
                        "schedule_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="일정 ID"),
                    },
                ),
            ),
        },
    )
    def create(self, request, *args, **kwargs):
        # 일정 등록 처리 로직...
        created_data = {
            "group_id": request.data.get("group_id"),
            "schedule_id": 123,  # 새로 생성된 ID를 반환
        }
        return Response(created_data, status=201)


class GroupScheduleListView(ListAPIView):
    """
    특정 그룹의 일정 필터링
    """

    serializer_class = ScheduleSerializer

    def get_queryset(self):
        group_id = self.kwargs["group_id"]
        return Schedule.objects.filter(group_id=group_id).prefetch_related(
            "participating_members"
        )

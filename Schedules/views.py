from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.permissions import IsAdminOrReadOnly
from Idols.models import Group
from Preferences.notification_service import NotificationService

from .models import Schedule
from .serializer import MinimalScheduleSerializer, ScheduleSerializer


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
        return {"data": context}

    def perform_create(self, serializer):
        # 일정 생성
        schedule = serializer.save()
        manager = group.manager
        serializer.save(manager=manager)
        # 일정 생성 후 알림 발송 (비동기적으로 처리됨)
        NotificationService.notify_schedule_creation(schedule)


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
                        "schedule.id": openapi.Schema(
                            type=openapi.TYPE_INTEGER, description="일정 ID"
                        ),
                        "group_id": openapi.Schema(
                            type=openapi.TYPE_INTEGER, description="그룹 ID"
                        ),
                        "title": openapi.Schema(
                            type=openapi.TYPE_STRING, description="일정 제목"
                        ),
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
        return Response({"data": deleted_schedule_data}, status=200)

    @swagger_auto_schema(
        request_body=ScheduleSerializer,
        responses={
            200: openapi.Response(
                description="일정 수정 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "group_id": openapi.Schema(
                            type=openapi.TYPE_INTEGER, description="그룹 ID"
                        ),
                        "schedule_id": openapi.Schema(
                            type=openapi.TYPE_INTEGER, description="일정 ID"
                        ),
                    },
                ),
            ),
            201: openapi.Response(
                description="일정 등록 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "group_id": openapi.Schema(
                            type=openapi.TYPE_INTEGER, description="그룹 ID"
                        ),
                        "schedule_id": openapi.Schema(
                            type=openapi.TYPE_INTEGER, description="일정 ID"
                        ),
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
        return Response({"data": updated_data}, status=200)

    @swagger_auto_schema(
        request_body=ScheduleSerializer,
        responses={
            201: openapi.Response(
                description="일정 등록 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "group_id": openapi.Schema(
                            type=openapi.TYPE_INTEGER, description="그룹 ID"
                        ),
                        "schedule_id": openapi.Schema(
                            type=openapi.TYPE_INTEGER, description="일정 ID"
                        ),
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
        return Response({"data": created_data}, status=201)


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

    def list(self, request, *args, **kwargs):
        # 기존의 queryset 가져오기
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        # {"data": ...} 형식으로 리스폰스 반환
        return Response({"data": serializer.data})


class UserScheduleListView(ListAPIView):
    """
    본인이 작성한 일정 목록 조회
    """

    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 현재 사용자가 작성한 일정만 반환
        return Schedule.objects.filter(user=self.request.user).select_related("group")

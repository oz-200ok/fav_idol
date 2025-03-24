from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
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

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        deleted_schedule_data = {
            "schedule.id": instance.id,
            "group_id": instance.group_id,
            "title": instance.title,
        }
        self.perform_destroy(instance)

        return Response(
            {"data": deleted_schedule_data},
        )

class GroupScheduleListView(ListAPIView):
    """
    특정 그룹의 일정 필터링
    """
    serializer_class = ScheduleSerializer

    def get_queryset(self):
        group_id = self.kwargs["group_id"]
        return Schedule.objects.filter(group_id=group_id).prefetch_related("participating_members")


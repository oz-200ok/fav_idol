from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Schedule
from .permissions import IsAdminOrReadOnly
from .serializer import ScheduleSerializer


class ScheduleListView(APIView):
    """
    일정 목록 조회
    """

    def get(self, request):
        schedules = Schedule.objects.all()
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ScheduleDetailView(APIView):
    """
    특정 일정 상세 조회 및 삭제
    """

    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, pk):
        schedule = get_object_or_404(Schedule, pk=pk)
        serializer = ScheduleSerializer(schedule)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        schedule = get_object_or_404(Schedule, pk=pk)
        deleted_schedule_data = {
            "schedule.id": schedule.id,
            "group_id": schedule.group_id,
            "title": schedule.title,
        }

        schedule.delete()
        return Response(
            {
                "message": "일정이 삭제되었습니다.",
                "deleted_schedule_data": deleted_schedule_data,
            },
            status=status.HTTP_200_OK,
        )


class ScheduleCreateView(APIView):
    """
    새 일정 생성
    """

    permission_classes = [IsAdminOrReadOnly]

    def post(self, request):
        serializer = ScheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScheduleUpdateView(APIView):
    """
    일정 업데이트
    """

    permission_classes = [IsAdminOrReadOnly]

    def post(self, request, pk):
        schedule = get_object_or_404(Schedule, pk=pk)

        # 기존 객체 업데이트를 위해 instance 전달
        serializer = ScheduleSerializer(instance=schedule, data=request.data)
        if serializer.is_valid():
            # 데이터 저장
            serializer.save()

            # 업데이트 된 데이터를 반환
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupScheduleListView(APIView):
    """
    특정 그룹의 일정 필터링
    """

    def get(self, request, group_id):
        # 특정 그룹의 일정 필터링
        schedules = Schedule.objects.filter(group_id=group_id)
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

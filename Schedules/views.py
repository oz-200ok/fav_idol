from django.db.models import prefetch_related_objects
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Schedule
from .permissions import IsAdminOrReadOnly
from .serializer import ScheduleSerializer


class ScheduleListView(APIView):
    """
    일정 목록 조회 및 등록
    """

    def get(self, request):
        schedules = Schedule.objects.all()
        serializer = ScheduleSerializer(schedules, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        # 일정 등록
        serializer = ScheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )


class ScheduleDetailView(APIView):
    """
    특정 일정 상세 조회, 수정 및 삭제
    """

    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, pk):
        # 일정 상세 조회
        schedule = get_object_or_404(Schedule, pk=pk)
        serializer = ScheduleSerializer(schedule)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        # 일정 부분 수정
        schedule = get_object_or_404(Schedule, pk=pk)
        serializer = ScheduleSerializer(schedule, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        # 일정 삭제
        schedule = get_object_or_404(Schedule, pk=pk)
        deleted_schedule_data = {
            "schedule.id": schedule.id,
            "group_id": schedule.group_id,
            "title": schedule.title,
        }

        schedule.delete()
        return Response(
            {"data": deleted_schedule_data},
            status=status.HTTP_200_OK,
        )


class GroupScheduleListView(APIView):
    """
    특정 그룹의 일정 필터링
    """

    def get(self, request, group_id):
        # 특정 그룹의 일정 필터링
        schedules = (Schedule.objects.filter(group_id=group_id).prefetch_related("participating_members"))

        serializer = ScheduleSerializer(schedules, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)


from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views import View
from .models import Schedule
from Idols.models import Group, Idol

class ScheduleListView(View):
    def get(self, request):
        schedules = Schedule.objects.all()
        data = [
            {
                "id": schedule.id,
                "user": schedule.user.username,
                "group": schedule.group.name,
                "title": schedule.title,
                "description": schedule.description,
                "location": schedule.location,
                "start_time": schedule.start_time,
                "end_time": schedule.end_time,
                "created_at": schedule.created_at,
                "updated_at": schedule.updated_at,
                "participating_members": [
                    member.name for member in schedule.participating_members.all()
                ]
            } for schedule in schedules
        ]
        return JsonResponse(data, safe=False)


class ScheduleDetailView(View):
    def get(self, request, pk):
        schedule = get_object_or_404(Schedule, pk=pk)
        data = {
            "id": schedule.id,
            "user": schedule.user.username,
            "group": schedule.group.name,
            "title": schedule.title,
            "description": schedule.description,
            "location": schedule.location,
            "start_time": schedule.start_time,
            "end_time": schedule.end_time,
            "created_at": schedule.created_at,
            "updated_at": schedule.updated_at,
            "participating_members": [
                member.name for member in schedule.participating_members.all()
            ]
        }
        return JsonResponse(data)

    def delete(self, request, pk):
        schedule = get_object_or_404(Schedule, pk=pk)
        schedule.delete()
        return JsonResponse({"message": "일정이 삭제되었습니다."})

class ScheduleCreateView(View):
    def post(self, request):
        data = request.POST
        user_id = data.get("user_id")
        group_id = data.get("group_id")
        title = data.get("title")
        description = data.get("description")
        location = data.get("location")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        participating_member_ids = data.getlist("participating_members")

        user = get_object_or_404(User, id=user_id)
        group = get_object_or_404(Group, id=group_id)
        schedule = Schedule.objects.create(
            user=user,
            group=group,
            title=title,
            description=description,
            location=location,
            start_time=start_time,
            end_time=end_time,
        )

        if participating_member_ids:
            schedule.participating_members.set(
                Idol.objects.filter(id__in=participating_member_ids)
            )

        return JsonResponse({"message": "일정 등록이 완료되었습니다.", "id": schedule.id})


class ScheduleUpdateView(View):
    def post(self, request, pk):
        schedule = get_object_or_404(Schedule, pk=pk)
        data = request.POST

        schedule.title = data.get("title", schedule.title)
        schedule.description = data.get("description", schedule.description)
        schedule.location = data.get("location", schedule.location)
        schedule.start_time = data.get("start_time", schedule.start_time)
        schedule.end_time = data.get("end_time", schedule.end_time)

        if "participating_members" in data:
            participating_member_ids = data.getlist("participating_members")
            schedule.participating_members.set(
                Idol.objects.filter(id__in=participating_member_ids)
            )

        schedule.save()
        return JsonResponse({"message": "일정 수정이 완료되었습니다."})

class GroupScheduleListView(View):
    def get(self, request, group_id):
        # 특정 그룹의 일정 필터링
        schedules = Schedule.objects.filter(group_id=group_id)
        data = [
            {
                "id": schedule.id,
                "title": schedule.title,
                "description": schedule.description,
                "location": schedule.location,
                "start_time": schedule.start_time,
                "end_time": schedule.end_time,
                "created_at": schedule.created_at,
                "updated_at": schedule.updated_at,
                "participating_members": [member.name for member in schedule.participating_members.all()]
            }
            for schedule in schedules
        ]
        return JsonResponse(data, safe=False)
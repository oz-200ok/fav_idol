from rest_framework import serializers

from Idols.models import Group, Idol
from Idols.serializers import IdolSerializer

from .models import Schedule


class ScheduleSerializer(serializers.ModelSerializer):
    participating_members = IdolSerializer(many=True, read_only=True)

    class Meta:
        model = Schedule
        fields = ["group", "title", "description", "location", "start_time", "end_time", "participating_members"]


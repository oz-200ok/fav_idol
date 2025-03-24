from rest_framework import serializers

from Idols.models import Group, Idol
from Idols.serializers import IdolSerializer

from .models import Schedule


class ScheduleSerializer(serializers.ModelSerializer):
    participating_members = serializers.PrimaryKeyRelatedField(many=True, queryset=Idol.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = Schedule
        fields = ["group", "title", "description", "location", "start_time", "end_time", "participating_members"]

    def validate(self,data):
        if data ['end_time'] <= data['start_time']:
            raise serializers.ValidationError("end_time은 start_time 이후여야 합니다.")
        return data


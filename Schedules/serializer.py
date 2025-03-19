from rest_framework import serializers

from Idols.models import Group, Idol

from .models import Schedule


class ScheduleSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    participating_members = serializers.SlugRelatedField(
        many=True, slug_field="name", queryset=Idol.objects.all()
    )

    class Meta:
        model = Schedule
        fields = "__all__"

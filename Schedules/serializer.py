from rest_framework import serializers

from Idols.models import Group, Idol

from .models import Schedule


class ScheduleSerializer(serializers.ModelSerializer):
    # 참여 멤버를 이름 반환
    participating_members = serializers.SerializerMethodField()
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    participating_member_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Idol.objects.all(), write_only=True
    )  # 저장 시 사용할 ID 필드

    class Meta:
        model = Schedule
        fields = [
            "group",
            "title",
            "description",
            "location",
            "start_time",
            "end_time",
            "participating_members",
            "participating_member_ids",
        ]

    def create(self, validated_data):
        # 요청하는 사용자 가져오기
        request = self.context.get("request")
        if not request or not hasattr(request, "user"):
            raise serializers.ValidationError("User context is missing.")

        participating_members = validated_data.pop("participating_member_ids", [])
        validated_data["user"] = request.user  # 사용자 설정
        schedule = Schedule.objects.create(**validated_data)
        schedule.participating_members.set(
            participating_members
        )  # ManyToMany 관계 설정
        return schedule

    def get_participating_members(self, obj):
        # 참여 멤버의 이름만 반환
        return [member.name for member in obj.participating_members.all()]

    def validate(self, data):
        # start_time과 end_time 검증
        if data["end_time"] <= data["start_time"]:
            raise serializers.ValidationError("end_time은 start_time 이후여야 합니다.")
        return data


class MinimalScheduleSerializer(serializers.ModelSerializer):
    # 관리 중인 그룹 일정 반환용 시리얼라이저
    schedule_id = serializers.IntegerField(source="id")
    group_id = serializers.IntegerField(source="group.id")

    class Meta:
        model = Schedule
        fields = ["schedule_id", "group_id"]

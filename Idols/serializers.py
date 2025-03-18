from rest_framework import serializers

from .models import Agency, Group, Idol


# Agency Serializer
class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ["id", "name", "contact"]  # 필요한 필드 정의

    # 이름 중복 검증
    def validate_name(self, value):
        if Agency.objects.filter(name=value).exists():
            raise serializers.ValidationError("같은 이름의 소속사가 존재합니다.")
        return value


# Group Serializer
class GroupSerializer(serializers.ModelSerializer):
    agency_name = serializers.CharField(
        source="agency.name", read_only=True
    )  # 관련 소속사 이름 추가 (읽기 전용)

    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "agency",
            "agency_name",
            "sns",
            "color",
        ]  # 사용 필드 정의

    # 이름 중복 검증
    def validate_name(self, value):
        if Group.objects.filter(name=value).exists():
            raise serializers.ValidationError("같은 이름의 그룹이 존재합니다.")
        return value


# Idol Serializer
class IdolSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(
        source="group.name", read_only=True
    )  # 관련 그룹 이름 추가 (읽기 전용)

    class Meta:
        model = Idol
        fields = ["id", "name", "group", "group_name"]  # 사용 필드 정의

    # 이름 중복 검증
    def validate_name(self, value):
        if Idol.objects.filter(name=value).exists():
            raise serializers.ValidationError("같은 이름의 아이돌이 존재합니다.")
        return value

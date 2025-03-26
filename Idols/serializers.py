from rest_framework import serializers

from .models import Agency, Group, Idol


# Agency Serializer
class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ["name", "contact"]  # 필요한 필드 정의

    # 이름 중복 검증
    def validate_name(self, value):
        if Agency.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("같은 이름의 소속사가 존재합니다.")
        return value


# Group Serializer
class GroupSerializer(serializers.ModelSerializer):
    agency_name = serializers.CharField(
        source="agency.name", read_only=True
    )  # 관련 소속사 이름 추가 (읽기 전용)
    member_count = serializers.IntegerField(read_only=True)  # 그룹 멤버 수 추가

    class Meta:
        model = Group
        fields = [
            "agency_name",
            "id",
            "name",
            "sns",
            "color",
            "image",
            "member_count",
        ]  # 사용 필드 정의

    # 이름 중복 검증
    def validate_name(self, value):
        if Group.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("같은 이름의 그룹이 존재합니다.")
        return value



# Idol Serializer
class IdolSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(
        source="group.name", read_only=True
    )  # 관련 그룹 이름 추가 (읽기 전용)

    class Meta:
        model = Idol
        fields = ["name", "group", "group_name"]  # 사용 필드 정의

    def validate(self, data):
        name = data.get("name")
        group = data.get("group")

        # 데이터 유효성 검사
        if not name or not group:
            raise serializers.ValidationError("이름과 그룹은 필수 입력 항목입니다.")

        if Idol.objects.filter(name=name, group=group).exists():
            raise serializers.ValidationError(
                "같은 그룹에 동일한 이름의 아이돌이 존재합니다."
            )
        return data
from rest_framework import serializers

from Idols.s3_utils import upload_image_to_s3

from .models import Agency, Group, Idol

class IdolNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idol
        fields = ['id', 'name', 'image'] # 그룹 정보에 포함시킬 아이돌 필드 (id, 이름, 이미지 URL)


# Agency Serializer
class AgencySerializer(serializers.ModelSerializer):
    image_file = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Agency
        fields = ["id", "name", "contact", "image", "image_file"]  # 필요한 필드 정의
        read_only_fields = ["image"]  # image 필드는 읽기 전용으로 설정

    # 이름 중복 검증
    def validate_name(self, value):
        if Agency.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("같은 이름의 소속사가 존재합니다.")
        return value

    def create(self, validated_data):
        image_file = validated_data.pop("image_file", None)
        instance = super().create(validated_data)
        if image_file:
            image_url = upload_image_to_s3(image_file, "agencies", instance.id)
            if image_url:
                instance.image = image_url
                instance.save()
        return instance

    def update(self, instance, validated_data):
        image_file = validated_data.pop("image_file", None)
        instance = super().update(instance, validated_data)
        if image_file:
            image_url = upload_image_to_s3(image_file, "agencies", instance.id)
            if image_url:
                instance.image = image_url
                instance.save()
        return instance


# Group Serializer
class GroupSerializer(serializers.ModelSerializer):
    agency_name = serializers.CharField(
        source="agency.name", read_only=True
    )  # 관련 소속사 이름 추가 (읽기 전용)
    idol_set = IdolNestedSerializer(many=True, read_only=True)
    member_count = serializers.SerializerMethodField()
    image_file = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Group
        fields = [
            "id",           # ID 필드 추가 
            "name",
            "agency",       # 소속사 ID (ForeignKey)
            "agency_name",  # 소속사 이름
            "color",
            "sns",
            "image",        # 그룹 이미지 URL
            "idol_set",     # 중첩된 아이돌 정보 리스트
            "member_count", # 계산된 멤버 수
            "image_file",   # 이미지 업로드용 (write_only)
        ]  # 사용 필드 정의

        read_only_fields = ["image"]  # image 필드는 읽기 전용으로 설정

    # member_count 계산 메서드
    def get_member_count(self, obj):
        # obj는 Group 인스턴스. 연관된 idol_set의 개수를 센다.
        return obj.idol_set.count()


    # 이름 중복 검증
    def validate_name(self, value):
        if Group.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("같은 이름의 그룹이 존재합니다.")
        return value

    def create(self, validated_data):
        image_file = validated_data.pop("image_file", None)
        instance = super().create(validated_data)
        if image_file:
            image_url = upload_image_to_s3(image_file, "groups", instance.id)
            if image_url:
                instance.image = image_url
                instance.save()
        return instance

    def update(self, instance, validated_data):
        image_file = validated_data.pop("image_file", None)
        instance = super().update(instance, validated_data)
        if image_file:
            image_url = upload_image_to_s3(image_file, "groups", instance.id)
            if image_url:
                instance.image = image_url
                instance.save()
        return instance


# Idol Serializer
class IdolSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(
        source="group.name", read_only=True
    )  # 관련 그룹 이름 추가 (읽기 전용)
    image_file = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Idol
        fields = [
            "id",           # ID 필드 추가
            "name",
            "group",        # 생성/수정 시 필요
            "group_name",
            "image",        # 아이돌 이미지 URL 필드 추가
            "image_file",
        ]
        # group_name도 읽기 전용이므로 read_only_fields에 추가
        read_only_fields = ["image", "group_name"]

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

    def create(self, validated_data):
        image_file = validated_data.pop("image_file", None)
        instance = super().create(validated_data)
        if image_file:
            image_url = upload_image_to_s3(image_file, "idols", instance.id)
            if image_url:
                instance.image = image_url
                instance.save()
        return instance

    def update(self, instance, validated_data):
        image_file = validated_data.pop("image_file", None)
        instance = super().update(instance, validated_data)
        if image_file:
            image_url = upload_image_to_s3(image_file, "idols", instance.id)
            if image_url:
                instance.image = image_url
                instance.save()
        return instance

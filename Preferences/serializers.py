from rest_framework import serializers
from .models import UserGroupSubscribe
from Idols.models import Group

class SubscribeSerializer(serializers.ModelSerializer):
    # 그룹 구독을 위한 입력 데이터 검증 및 처리
    group_id = serializers.IntegerField(write_only=True)
    notification = serializers.BooleanField(default=True)
    
    class Meta:
        model = UserGroupSubscribe
        fields = ['id', 'group_id', 'notification']
        read_only_fields = ['id']
    
    def validate_group_id(self, value):
        # 그룹 존재 여부 검증
        if not Group.objects.filter(id=value).exists():
            raise serializers.ValidationError("존재하지 않는 그룹입니다.")
        return value

class SubscribeResponseSerializer(serializers.ModelSerializer):
    # 구독 응답을 위한 시리얼라이저
    group_id = serializers.IntegerField(source='group.id')
    group_name = serializers.CharField(source='group.name')
    notification = serializers.BooleanField()
    
    class Meta:
        model = UserGroupSubscribe
        fields = ['id', 'group_id', 'group_name', 'notification']
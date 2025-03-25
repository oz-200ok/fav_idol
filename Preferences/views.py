from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserGroupSubscribe
from .serializers import SubscribeSerializer, SubscribeResponseSerializer
from .services import SubscriptionService

class SubscribeViewSet(viewsets.GenericViewSet):
    # 그룹 구독을 관리하는 뷰셋
    permission_classes = [IsAuthenticated]
    serializer_class = SubscribeSerializer

    def get_serializer_class(self):
        # 메서드에 따른 시리얼라이저 동적 선택
        if self.action == 'list':
            return SubscribeResponseSerializer
        return SubscribeSerializer
    
    def custom_response(self, data=None, status=status.HTTP_200_OK):
        # 응답 형식 커스터마이징
        if data is None:
            return Response(status=status)
        return Response({"data": data}, status=status)


    def list(self, request):
        # 사용자의 구독 목록 조회
        subscriptions = SubscriptionService.get_user_subscriptions(request.user)
        serializer = self.get_serializer(subscriptions, many=True)
        return self.custom_response(serializer.data)

    def create(self, request):
        # 그룹 구독 생성 또는 업데이트
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        subscription = SubscriptionService.subscribe_to_group(
            user=request.user,
            group_id=serializer.validated_data['group_id'],
            notification=serializer.validated_data.get('notification', True)
        )
        
        response_serializer = SubscribeResponseSerializer(subscription)
        return self.custom_response(response_serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        # 그룹 구독 취소
        success = SubscriptionService.unsubscribe_from_group(
            user=request.user, 
            group_id=pk
        )
        
        if success:
            return self.custom_response(status=status.HTTP_204_NO_CONTENT)
        return self.custom_response(
            status=status.HTTP_404_NOT_FOUND
        )
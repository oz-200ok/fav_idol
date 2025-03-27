from Idols.models import Group

from .models import UserGroupSubscribe


class SubscriptionService:
    # 사용자 그룹 구독 서비스 로직 처리

    @staticmethod
    def subscribe_to_group(user, group_id, notification=True):
        # 사용자가 그룹을 구독하거나 구독 설정을 업데이트합니다
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            raise ValueError("존재하지 않는 그룹입니다.")

        subscription, created = UserGroupSubscribe.objects.update_or_create(
            user=user, group=group, defaults={"notification": notification}
        )

        return subscription

    @staticmethod
    def unsubscribe_from_group(user, group_id):
        # 사용자가 그룹 구독을 취소합니다
        try:
            subscription = UserGroupSubscribe.objects.get(user=user, group_id=group_id)
            subscription.delete()
            return True
        except UserGroupSubscribe.DoesNotExist:
            return False

    @staticmethod
    def get_user_subscriptions(user):
        # 사용자의 모든 구독 정보를 반환합니다
        return UserGroupSubscribe.objects.filter(user=user)

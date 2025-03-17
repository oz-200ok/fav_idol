from django.test import TestCase

from Accounts.models import User
from Idols.models import Agency, Group

from .models import UserGroupSubscribe


class UserGroupSubscribeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="test",
            username="tester",
            email="test@test.com",
            password="test@1234",
        )
        self.agency = Agency.objects.create(
            name="SM Entertainment",
            contact="010-1234-5678",
            image_name="sm_logo",
            image_url="http://example.com/sm_logo.png",
            image_ext="png",
        )

        self.group = Group.objects.create(
            agency=self.agency,
            name="Test Group",
            sns="http://twitter.com/testgroup",
            color="blue",
            image_name="test_group_logo",
            image_url="http://example.com/test_group_logo.png",
            image_ext="png",
        )
        self.subscription = UserGroupSubscribe.objects.create(
            user=self.user, group=self.group, notification=True
        )

    def test_subscription_creation(self):
        # UserGroupSubscribe 객체가 올바르게 생성되었는지 확인
        self.assertEqual(self.subscription.user, self.user)
        self.assertEqual(self.subscription.group, self.group)
        self.assertTrue(self.subscription.notification)

    def test_subscription_string_representation(self):
        expected_string = f"{self.user} subscribed to {self.group} (Notification: {self.subscription.notification})"
        self.assertEqual(str(self.subscription), expected_string)

    def test_notification_toggle(self):
        # Notification 값을 토글하여 변경 가능한지 테스트
        self.subscription.notification = not self.subscription.notification
        self.subscription.save()
        updated_subscription = UserGroupSubscribe.objects.get(id=self.subscription.id)
        self.assertFalse(
            updated_subscription.notification
        )  # 값이 False로 변경되었는지 확인

    def test_multiple_subscriptions(self):
        # 같은 사용자가 여러 그룹을 구독할 수 있는지 테스트
        another_group = Group.objects.create(
            agency=self.agency,
            name="Another Test Group",
            sns="http://twitter.com/anothergroup",
            color="red",
            image_name="another_group_logo",
            image_url="http://example.com/another_group_logo.png",
            image_ext="jpg",
        )
        another_subscription = UserGroupSubscribe.objects.create(
            user=self.user, group=another_group, notification=True
        )
        subscriptions = UserGroupSubscribe.objects.filter(user=self.user)
        self.assertEqual(subscriptions.count(), 2)  # 같은 사용자로 두 개의 구독 확인

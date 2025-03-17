from django.db import models

from Accounts.models import User
from Idols.models import Group


class UserGroupSubscribe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    notification = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} subscribed to {self.group} (Notification: {self.notification})"

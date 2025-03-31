from django.contrib.auth import get_user_model
from django.db import models

from Idols.models import Group, Idol

User = get_user_model()


class Schedule(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="schedules")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="schedules")
    title = models.CharField(max_length=30)
    description = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=50)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # manager = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    # 참가 멤버와의 다대다 관계를 위한 필드
    participating_members = models.ManyToManyField(
        Idol, related_name="schedules", blank=True
    )

    def __str__(self):
        return self.title

    class Meta:
        db_table = "schedule"

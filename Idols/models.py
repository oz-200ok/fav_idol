from django.core.validators import RegexValidator
from django.db import models

from Accounts.models import User


class Agency(models.Model):
    name = models.CharField(max_length=20)  # null 불가, 공백 불가
    contact = models.CharField(max_length=50, null=True)
    image = models.URLField(max_length=500, null=True)

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)  # 그룹 이름
    manager = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="managed_groups", null=False
    )
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)  # 소속사
    color = models.CharField(
        max_length=7,
        validators=[
            RegexValidator(
                regex="^#[0-9A-Fa-f]{6}$", message="유효한 HEX 색상을 입력하세요."
            )
        ],
        null=True,
        blank=True,
    )
    sns = models.URLField(blank=True, null=True)  # SNS 링크
    image = models.URLField(max_length=500, null=True, blank=True)  # 그룹 이미지

    def __str__(self):
        return f"{self.name} ({self.agency.name})"


class Idol(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    image = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.group.name})"

    class Meta:
        db_table = "idols"

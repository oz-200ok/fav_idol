from django.db import models


class Agency(models.Model):
    name = models.CharField(max_length=20)  # null 불가, 공백 불가
    contact = models.CharField(max_length=50, null=True)
    image = models.ImageField(upload_to="agencies/", blank=True, null=True)

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)  # 그룹 이름
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)  # 소속사
    color = models.CharField(max_length=7)  # HEX 색상 코드
    sns = models.URLField(blank=True, null=True)  # SNS 링크
    image = models.ImageField(upload_to="groups/", blank=True, null=True)  # 그룹 이미지


    def __str__(self):
        return f"{self.name} ({self.agency.name})"


class Idol(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    image = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.group.name})"

    class Meta:
        db_table = "idols"

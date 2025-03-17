from django.db import models


class Agency(models.Model):
    name = models.CharField(max_length=20)  # null 불가, 공백 불가
    contact = models.CharField(max_length=50, null=True)
    image_name = models.CharField(max_length=20, null=True, blank=True)
    image_url = models.CharField(max_length=50, null=True, blank=True)
    image_ext = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.name


class Group(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    sns = models.CharField(max_length=50, null=True)
    color = models.CharField(max_length=10)
    image_name = models.CharField(max_length=20, null=True, blank=True)
    image_url = models.CharField(max_length=50, null=True, blank=True)
    image_ext = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.agency.name})"


class Idol(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    image_name = models.CharField(max_length=20, null=True, blank=True)
    image_url = models.CharField(max_length=50, null=True, blank=True)
    image_ext = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.group.name})"

    class Meta:
        db_table = "idols"

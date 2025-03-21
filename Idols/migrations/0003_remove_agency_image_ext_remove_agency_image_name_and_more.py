# Generated by Django 5.1.7 on 2025-03-20 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Idols", "0002_alter_agency_image_ext_alter_agency_image_name_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="agency",
            name="image_ext",
        ),
        migrations.RemoveField(
            model_name="agency",
            name="image_name",
        ),
        migrations.RemoveField(
            model_name="agency",
            name="image_url",
        ),
        migrations.RemoveField(
            model_name="group",
            name="image_ext",
        ),
        migrations.RemoveField(
            model_name="group",
            name="image_name",
        ),
        migrations.RemoveField(
            model_name="group",
            name="image_url",
        ),
        migrations.RemoveField(
            model_name="idol",
            name="image_ext",
        ),
        migrations.RemoveField(
            model_name="idol",
            name="image_name",
        ),
        migrations.RemoveField(
            model_name="idol",
            name="image_url",
        ),
        migrations.AddField(
            model_name="agency",
            name="image",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="group",
            name="image",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="idol",
            name="image",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

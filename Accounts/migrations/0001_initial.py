# Generated by Django 5.1.7 on 2025-03-24 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions.py without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("is_admin", models.BooleanField(default=False)),
                ("is_staff", models.BooleanField(default=False)),
                ("email", models.EmailField(max_length=50, unique=True)),
                ("is_active", models.BooleanField(default=False)),
                ("name", models.CharField(max_length=20)),
                ("username", models.CharField(max_length=15, unique=True)),
                ("password", models.CharField(max_length=200)),
                (
                    "phone",
                    models.CharField(blank=True, max_length=15, null=True, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_social", models.BooleanField(default=False)),
                (
                    "social_login",
                    models.CharField(blank=True, max_length=15, null=True),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions.py granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions.py for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions.py",
                    ),
                ),
            ],
            options={
                "db_table": "user",
            },
        ),
    ]

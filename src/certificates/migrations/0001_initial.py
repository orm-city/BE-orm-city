# Generated by Django 5.1.2 on 2024-10-13 16:07

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Certificate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("object_id", models.PositiveIntegerField(verbose_name="객체 ID")),
                (
                    "issued_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="발급일"),
                ),
                (
                    "certificate_id",
                    models.UUIDField(
                        default=uuid.uuid4, unique=True, verbose_name="수료증 ID"
                    ),
                ),
                ("encrypted_data", models.TextField(verbose_name="암호화된 데이터")),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="certificates",
                        to="contenttypes.contenttype",
                        verbose_name="콘텐츠 타입",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="certificates",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="사용자",
                    ),
                ),
            ],
            options={
                "verbose_name": "수료증",
                "verbose_name_plural": "수료증들",
            },
        ),
    ]

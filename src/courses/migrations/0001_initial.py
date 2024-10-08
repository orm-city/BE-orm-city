# Generated by Django 5.1.1 on 2024-10-07 18:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MajorCategory",
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
                ("name", models.CharField(max_length=100, verbose_name="대분류명")),
                (
                    "price",
                    models.PositiveIntegerField(default=0, verbose_name="강의가격"),
                ),
            ],
            options={
                "verbose_name": "대분류",
                "verbose_name_plural": "대분류 목록",
            },
        ),
        migrations.CreateModel(
            name="MinorCategory",
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
                ("name", models.CharField(max_length=100, verbose_name="소분류명")),
                ("content", models.TextField(verbose_name="내용")),
                ("order", models.PositiveIntegerField(verbose_name="순서")),
                (
                    "major_category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="minor_categories",
                        to="courses.majorcategory",
                        verbose_name="대분류",
                    ),
                ),
            ],
            options={
                "verbose_name": "소분류",
                "verbose_name_plural": "소분류 목록",
                "ordering": ["order"],
            },
        ),
        migrations.CreateModel(
            name="Enrollment",
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
                (
                    "enrollment_date",
                    models.DateTimeField(auto_now_add=True, verbose_name="수강 신청일"),
                ),
                ("expiry_date", models.DateTimeField(verbose_name="수강 만료일")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "진행중"),
                            ("completed", "완료"),
                            ("expired", "만료"),
                        ],
                        default="active",
                        max_length=10,
                        verbose_name="상태",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="enrollments",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="사용자",
                    ),
                ),
                (
                    "major_category",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="enrollments",
                        to="courses.majorcategory",
                        verbose_name="수강 대분류",
                    ),
                ),
            ],
            options={
                "verbose_name": "수강 신청",
                "verbose_name_plural": "수강 신청 목록",
                "unique_together": {("user", "major_category")},
            },
        ),
    ]

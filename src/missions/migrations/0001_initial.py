# Generated by Django 5.1.2 on 2024-10-13 16:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("courses", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CodeSubmission",
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
                ("problem_statement", models.TextField(verbose_name="문제 설명")),
                ("example_input", models.TextField(verbose_name="입력 예시")),
                ("example_output", models.TextField(verbose_name="출력 예시")),
                (
                    "time_limit",
                    models.IntegerField(default=1, verbose_name="시간 제한(초)"),
                ),
                (
                    "memory_limit",
                    models.IntegerField(default=128, verbose_name="메모리 제한(MB)"),
                ),
                (
                    "language",
                    models.CharField(
                        choices=[("python", "Python"), ("javascript", "JavaScript")],
                        max_length=20,
                        verbose_name="프로그래밍 언어",
                    ),
                ),
            ],
            options={
                "verbose_name": "코드 제출형 문제",
                "verbose_name_plural": "코드 제출형 문제들",
            },
        ),
        migrations.CreateModel(
            name="CodeSubmissionRecord",
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
                ("submitted_code", models.TextField(verbose_name="제출된 코드")),
                (
                    "submission_time",
                    models.DateTimeField(auto_now_add=True, verbose_name="제출 시간"),
                ),
                (
                    "test_results",
                    models.TextField(blank=True, verbose_name="테스트 결과"),
                ),
                (
                    "result_summary",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="결과 요약"
                    ),
                ),
                (
                    "is_passed",
                    models.BooleanField(default=False, verbose_name="통과 여부"),
                ),
                (
                    "execution_time",
                    models.FloatField(
                        blank=True, null=True, verbose_name="실행 시간(초)"
                    ),
                ),
                (
                    "memory_usage",
                    models.IntegerField(
                        blank=True, null=True, verbose_name="메모리 사용량(KB)"
                    ),
                ),
                (
                    "code_submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submission_records",
                        to="missions.codesubmission",
                        verbose_name="코드 제출 문제",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="code_submission_records",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="사용자",
                    ),
                ),
            ],
            options={
                "verbose_name": "코드 제출 기록",
                "verbose_name_plural": "코드 제출 기록들",
            },
        ),
        migrations.CreateModel(
            name="Mission",
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
                ("title", models.CharField(max_length=255, verbose_name="제목")),
                ("description", models.TextField(verbose_name="설명")),
                (
                    "mission_type",
                    models.CharField(
                        choices=[
                            ("multiple_choice", "5지선다형"),
                            ("code_submission", "코드 제출형"),
                        ],
                        max_length=50,
                        verbose_name="미션 유형",
                    ),
                ),
                (
                    "is_midterm",
                    models.BooleanField(default=False, verbose_name="중간 미션 여부"),
                ),
                (
                    "is_final",
                    models.BooleanField(default=False, verbose_name="기말 미션 여부"),
                ),
                (
                    "minor_category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="missions",
                        to="courses.minorcategory",
                        verbose_name="소분류 카테고리",
                    ),
                ),
            ],
            options={
                "verbose_name": "미션",
                "verbose_name_plural": "미션들",
            },
        ),
        migrations.AddField(
            model_name="codesubmission",
            name="mission",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="code_submissions",
                to="missions.mission",
                verbose_name="미션",
            ),
        ),
        migrations.CreateModel(
            name="MultipleChoiceQuestion",
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
                ("question", models.TextField(verbose_name="문제")),
                ("option_1", models.CharField(max_length=255, verbose_name="선택지 1")),
                ("option_2", models.CharField(max_length=255, verbose_name="선택지 2")),
                ("option_3", models.CharField(max_length=255, verbose_name="선택지 3")),
                ("option_4", models.CharField(max_length=255, verbose_name="선택지 4")),
                ("option_5", models.CharField(max_length=255, verbose_name="선택지 5")),
                (
                    "correct_option",
                    models.IntegerField(
                        choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],
                        verbose_name="정답 선택지",
                    ),
                ),
                (
                    "mission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="multiple_choice_questions",
                        to="missions.mission",
                        verbose_name="미션",
                    ),
                ),
            ],
            options={
                "verbose_name": "5지선다형 문제",
                "verbose_name_plural": "5지선다형 문제들",
            },
        ),
        migrations.CreateModel(
            name="MultipleChoiceSubmission",
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
                    "selected_option",
                    models.IntegerField(
                        choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],
                        verbose_name="선택한 답안",
                    ),
                ),
                ("is_correct", models.BooleanField(verbose_name="정답 여부")),
                (
                    "submitted_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="제출 시간"),
                ),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submissions",
                        to="missions.multiplechoicequestion",
                        verbose_name="5지선다형 문제",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="multiple_choice_submissions",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="사용자",
                    ),
                ),
            ],
            options={
                "verbose_name": "5지선다형 제출 기록",
                "verbose_name_plural": "5지선다형 제출 기록들",
            },
        ),
        migrations.CreateModel(
            name="TestCase",
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
                ("input_data", models.TextField(verbose_name="입력 데이터")),
                ("expected_output", models.TextField(verbose_name="예상 출력")),
                (
                    "is_sample",
                    models.BooleanField(default=False, verbose_name="샘플 테스트 여부"),
                ),
                (
                    "code_submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="test_cases",
                        to="missions.codesubmission",
                        verbose_name="코드 제출 문제",
                    ),
                ),
            ],
            options={
                "verbose_name": "테스트 케이스",
                "verbose_name_plural": "테스트 케이스들",
            },
        ),
    ]

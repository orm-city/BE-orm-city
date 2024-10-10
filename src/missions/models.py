from django.db import models
from django.conf import settings
from courses.models import MinorCategory


class Mission(models.Model):
    """
    각 미션의 기본 정보를 저장하는 모델.
    중간 및 기말 미션 유형과 관련된 정보를 관리.
    """

    title = models.CharField(max_length=255, verbose_name="제목")
    description = models.TextField(verbose_name="설명")
    minor_category = models.ForeignKey(
        MinorCategory,
        on_delete=models.CASCADE,
        related_name="missions",
        verbose_name="소분류 카테고리",
    )
    mission_type = models.CharField(
        max_length=50,
        choices=[("multiple_choice", "5지선다형"), ("code_submission", "코드 제출형")],
        verbose_name="미션 유형",
    )
    is_midterm = models.BooleanField(default=False, verbose_name="중간 미션 여부")
    is_final = models.BooleanField(default=False, verbose_name="기말 미션 여부")

    class Meta:
        verbose_name = "미션"
        verbose_name_plural = "미션들"

    def __str__(self):
        return self.title


class MultipleChoiceQuestion(models.Model):
    """
    5지선다형 문제를 정의하는 모델.
    각 미션에 대한 문제와 선택지를 관리.
    """

    mission = models.ForeignKey(
        Mission,
        on_delete=models.CASCADE,
        related_name="multiple_choice_questions",
        verbose_name="미션",
    )
    question = models.TextField(verbose_name="문제")
    option_1 = models.CharField(max_length=255, verbose_name="선택지 1")
    option_2 = models.CharField(max_length=255, verbose_name="선택지 2")
    option_3 = models.CharField(max_length=255, verbose_name="선택지 3")
    option_4 = models.CharField(max_length=255, verbose_name="선택지 4")
    option_5 = models.CharField(max_length=255, verbose_name="선택지 5")
    correct_option = models.IntegerField(
        choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],
        verbose_name="정답 선택지",
    )

    class Meta:
        verbose_name = "5지선다형 문제"
        verbose_name_plural = "5지선다형 문제들"

    def __str__(self):
        return self.question


class CodeSubmission(models.Model):
    """
    코드 제출형 문제를 정의하는 모델.
    각 미션에 대한 문제 설명과 입출력 예시를 관리.
    """

    mission = models.ForeignKey(
        Mission,
        on_delete=models.CASCADE,
        related_name="code_submissions",
        verbose_name="미션",
    )
    problem_statement = models.TextField(verbose_name="문제 설명")
    example_input = models.TextField(verbose_name="입력 예시")
    example_output = models.TextField(verbose_name="출력 예시")
    time_limit = models.IntegerField(default=1, verbose_name="시간 제한(초)")
    memory_limit = models.IntegerField(default=128, verbose_name="메모리 제한(MB)")

    class Meta:
        verbose_name = "코드 제출형 문제"
        verbose_name_plural = "코드 제출형 문제들"

    def __str__(self):
        return self.problem_statement


class TestCase(models.Model):
    """
    코드 제출형 문제에 대한 테스트 케이스를 관리하는 모델.
    입력 값과 예상 출력 값을 저장.
    """

    code_submission = models.ForeignKey(
        CodeSubmission,
        on_delete=models.CASCADE,
        related_name="test_cases",
        verbose_name="코드 제출 문제",
    )
    input_data = models.TextField(verbose_name="입력 데이터")
    expected_output = models.TextField(verbose_name="예상 출력")
    is_sample = models.BooleanField(default=False, verbose_name="샘플 테스트 여부")

    class Meta:
        verbose_name = "테스트 케이스"
        verbose_name_plural = "테스트 케이스들"

    def __str__(self):
        return f"입력: {self.input_data} / 예상 출력: {self.expected_output}"


class MultipleChoiceSubmission(models.Model):
    """
    5지선다형 문제에 대한 학생의 제출 기록을 관리하는 모델.
    제출된 답안과 정답 여부를 저장.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="multiple_choice_submissions",
        verbose_name="사용자",
    )
    question = models.ForeignKey(
        MultipleChoiceQuestion,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="5지선다형 문제",
    )
    selected_option = models.IntegerField(
        choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],
        verbose_name="선택한 답안",
    )
    is_correct = models.BooleanField(verbose_name="정답 여부")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="제출 시간")

    class Meta:
        verbose_name = "5지선다형 제출 기록"
        verbose_name_plural = "5지선다형 제출 기록들"

    def __str__(self):
        return f"{self.user.username} - {self.question.question}"


class CodeSubmissionRecord(models.Model):
    """
    코드 제출형 문제에 대한 학생의 제출 기록을 관리하는 모델.
    제출된 코드와 테스트 결과를 저장.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="code_submission_records",
        verbose_name="사용자",
    )
    code_submission = models.ForeignKey(
        CodeSubmission,
        on_delete=models.CASCADE,
        related_name="submission_records",
        verbose_name="코드 제출 문제",
    )
    submitted_code = models.TextField(verbose_name="제출된 코드")
    submission_time = models.DateTimeField(auto_now_add=True, verbose_name="제출 시간")
    test_results = models.TextField(blank=True, verbose_name="테스트 결과")
    result_summary = models.CharField(
        max_length=255, blank=True, verbose_name="결과 요약"
    )
    is_passed = models.BooleanField(default=False, verbose_name="통과 여부")
    execution_time = models.FloatField(
        null=True, blank=True, verbose_name="실행 시간(초)"
    )
    memory_usage = models.IntegerField(
        null=True, blank=True, verbose_name="메모리 사용량(KB)"
    )

    class Meta:
        verbose_name = "코드 제출 기록"
        verbose_name_plural = "코드 제출 기록들"

    def __str__(self):
        return f"{self.user.username} - {self.code_submission.problem_statement}"

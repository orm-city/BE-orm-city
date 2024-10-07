from django.db import models
from django.conf import settings
from courses.models import MinorCategory
from itertools import chain


class Mission(models.Model):
    """
    미션 모델

    각 과목(소분류)에 대한 중간 및 기말 미션을 나타냅니다.
    """

    MISSION_TYPES = [
        ("MID", "중간 미션"),
        ("FINAL", "기말 미션"),
    ]

    minor_category = models.ForeignKey(
        MinorCategory,
        on_delete=models.CASCADE,
        related_name="missions",
        verbose_name="소분류",
    )
    title = models.CharField(max_length=100, verbose_name="미션 제목")
    description = models.TextField(verbose_name="미션 설명")
    mission_type = models.CharField(
        max_length=5, choices=MISSION_TYPES, verbose_name="미션 유형"
    )
    order = models.PositiveIntegerField(verbose_name="미션 순서")
    passing_score = models.PositiveIntegerField(default=60, verbose_name="합격 점수")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        ordering = ["order"]
        verbose_name = "미션"
        verbose_name_plural = "미션 목록"
        unique_together = ["minor_category", "order"]

    def __str__(self):
        return f"{self.minor_category.name} - {self.get_mission_type_display()} - {self.title}"


class Question(models.Model):
    """
    문제 모델

    각 미션에 포함된 개별 문제를 나타냅니다.
    """

    QUESTION_TYPES = [
        ("MCQ", "5지선다형"),
        ("CODE", "코드 제출형"),
    ]

    mission = models.ForeignKey(
        Mission,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="미션",
    )
    question_type = models.CharField(
        max_length=4, choices=QUESTION_TYPES, verbose_name="문제 유형"
    )
    content = models.TextField(verbose_name="문제 내용")
    order = models.PositiveIntegerField(verbose_name="문제 순서")
    points = models.PositiveIntegerField(default=1, verbose_name="배점")

    class Meta:
        ordering = ["order"]
        verbose_name = "문제"
        verbose_name_plural = "문제 목록"
        unique_together = ["mission", "order"]

    def __str__(self):
        return f"{self.mission.title} - 문제 {self.order}"


class MultipleChoiceOption(models.Model):
    """
    5지선다형 문제의 선택지 모델
    """

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="options",
        verbose_name="문제",
    )
    content = models.CharField(max_length=200, verbose_name="선택지 내용")
    is_correct = models.BooleanField(default=False, verbose_name="정답 여부")
    order = models.PositiveIntegerField(verbose_name="선택지 순서")

    class Meta:
        ordering = ["order"]
        verbose_name = "선택지"
        verbose_name_plural = "선택지 목록"
        unique_together = ["question", "order"]

    def __str__(self):
        return f"{self.question} - 선택지: {self.content[:20]}"


class CodeQuestion(models.Model):
    """
    코드 제출형 문제의 추가 정보 모델
    """

    question = models.OneToOneField(
        Question,
        on_delete=models.CASCADE,
        related_name="code_question",
        verbose_name="문제",
    )
    initial_code = models.TextField(blank=True, verbose_name="초기 코드")
    test_cases = models.JSONField(verbose_name="테스트 케이스")

    class Meta:
        verbose_name = "코드 제출 문제"
        verbose_name_plural = "코드 제출 문제 목록"

    def __str__(self):
        return f"코드 문제: {self.question}"


class MissionSubmission(models.Model):
    """
    미션 제출 모델

    사용자의 미션 제출 정보를 나타냅니다.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mission_submissions",
        verbose_name="사용자",
    )
    mission = models.ForeignKey(
        Mission,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="미션",
    )
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="제출 시간")
    total_score = models.FloatField(default=0, verbose_name="총점")
    is_passed = models.BooleanField(default=False, verbose_name="통과 여부")

    class Meta:
        verbose_name = "미션 제출"
        verbose_name_plural = "미션 제출 목록"
        unique_together = ["user", "mission"]

    def __str__(self):
        return f"{self.user.username}의 {self.mission.title} 제출"

    def calculate_total_score(self):
        """
        미션 제출의 총점을 계산하고 통과 여부를 업데이트합니다.
        """
        # 모든 문제 제출의 점수를 합산
        question_submissions = chain(
            self.code_submissions.all(), self.multiple_choice_submissions.all()
        )
        total_score = sum(
            qs.score for qs in question_submissions if qs.score is not None
        )
        self.total_score = total_score
        self.is_passed = self.total_score >= self.mission.passing_score
        self.save()


class QuestionSubmission(models.Model):
    """
    개별 문제 제출 모델 (추상 모델)

    사용자의 개별 문제에 대한 답변을 나타냅니다.
    """

    mission_submission = models.ForeignKey(
        MissionSubmission,
        on_delete=models.CASCADE,
        verbose_name="미션 제출",
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, verbose_name="문제"
    )
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="제출 시간")
    score = models.FloatField(null=True, blank=True, verbose_name="점수")

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.mission_submission.calculate_total_score()


class MultipleChoiceSubmission(QuestionSubmission):
    """
    5지선다형 문제 제출 모델
    """

    mission_submission = models.ForeignKey(
        MissionSubmission,
        on_delete=models.CASCADE,
        related_name="multiple_choice_submissions",
        verbose_name="미션 제출",
    )
    selected_option = models.ForeignKey(
        MultipleChoiceOption, on_delete=models.CASCADE, verbose_name="선택한 답변"
    )

    class Meta:
        verbose_name = "객관식 문제 제출"
        verbose_name_plural = "객관식 문제 제출 목록"
        unique_together = ["mission_submission", "question"]

    def __str__(self):
        return f"{self.mission_submission.user.username}의 {self.question} 답변"

    def save(self, *args, **kwargs):
        # 채점 로직: 정답 여부에 따라 점수 부여
        if self.selected_option.is_correct:
            self.score = self.question.points
        else:
            self.score = 0
        super().save(*args, **kwargs)


class CodeSubmission(QuestionSubmission):
    """
    코드 제출형 문제 제출 모델
    """

    mission_submission = models.ForeignKey(
        MissionSubmission,
        on_delete=models.CASCADE,
        related_name="code_submissions",
        verbose_name="미션 제출",
    )
    submitted_code = models.TextField(verbose_name="제출한 코드")

    class Meta:
        verbose_name = "코드 문제 제출"
        verbose_name_plural = "코드 문제 제출 목록"
        unique_together = ["mission_submission", "question"]

    def __str__(self):
        return f"{self.mission_submission.user.username}의 {self.question} 코드 제출"

    def save(self, *args, **kwargs):
        # 코드 채점 로직
        test_cases = self.question.code_question.test_cases
        self.score = evaluate_code(self.submitted_code, test_cases)
        super().save(*args, **kwargs)
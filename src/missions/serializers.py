from rest_framework import serializers

from .models import (
    CodeSubmission,
    CodeSubmissionRecord,
    MultipleChoiceQuestion,
    MultipleChoiceSubmission,
    Mission,
)


class MultipleChoiceQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleChoiceQuestion
        fields = (
            "id",
            "mission",
            "question",
            "option_1",
            "option_2",
            "option_3",
            "option_4",
            "option_5",
            "correct_option",
        )


class MultipleChoiceSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleChoiceSubmission
        fields = ["question", "selected_option"]

    def create(self, validated_data):
        """
        제출된 답안을 저장하고, 정답 여부를 확인하는 메서드.
        """
        question = validated_data["question"]
        selected_option = validated_data["selected_option"]

        is_correct = question.correct_option == selected_option

        submission = MultipleChoiceSubmission.objects.create(
            user=self.context["request"].user,  # 제출한 사용자
            question=question,
            selected_option=selected_option,
            is_correct=is_correct,
        )

        return submission


class DetailMultipleChoiceSubmissionSerializer(serializers.ModelSerializer):
    """
    MultipleChoiceSubmission 시리얼라이저.
    제출된 답안에 대한 필드를 정의합니다.
    question 필드는 실제 question의 내용을 반환합니다.
    """

    question = serializers.CharField(source="question.question", read_only=True)
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = MultipleChoiceSubmission
        fields = (
            "id",
            "user",
            "question",
            "selected_option",
            "is_correct",
            "submitted_at",
        )


class MissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = (
            "id",
            "title",
            "description",
            "minor_category",
            "mission_type",
            "is_midterm",
            "is_final",
        )


class CodeSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeSubmission
        fields = (
            "id",
            "mission",
            "problem_statement",
            "example_input",
            "example_output",
            "time_limit",
            "memory_limit",
            "language",
        )


class SimpleSubmissionSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)
    code_submission = serializers.CharField(source="code_submission.problem_statement")

    class Meta:
        model = CodeSubmissionRecord
        fields = (
            "id",
            "user",
            "code_submission",
            "submission_time",
            "is_passed",
        )

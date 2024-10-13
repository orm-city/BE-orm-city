from rest_framework import serializers

from .models import (
    CodeSubmission,
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

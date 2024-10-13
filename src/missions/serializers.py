from rest_framework import serializers

from .models import (
    CodeSubmission,
    MultipleChoiceQuestion,
    MultipleChoiceSubmission,
    Mission,
)


class MultipleChoiceQuestionSerializer(serializers.ModelSerializer):
    """
    MultipleChoiceQuestion 모델을 직렬화하는 클래스.

    이 클래스는 MultipleChoiceQuestion 모델의 필드를 직렬화 및 역직렬화합니다.
    """

    class Meta:
        model = MultipleChoiceQuestion
        fields = (
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
    """
    MultipleChoiceSubmission 모델을 직렬화하는 클래스.

    이 클래스는 MultipleChoiceSubmission 모델의 필드를 직렬화 및 역직렬화하며,
    정답 여부를 확인하고 저장하는 로직을 포함합니다.
    """

    class Meta:
        model = MultipleChoiceSubmission
        fields = ["question", "selected_option"]

    def create(self, validated_data):
        """
        MultipleChoiceSubmission 객체를 생성하고, 정답 여부를 확인하여 저장합니다.

        Args:
            validated_data (dict): 검증된 데이터.

        Returns:
            MultipleChoiceSubmission: 생성된 제출 기록.
        """
        question = validated_data["question"]
        selected_option = validated_data["selected_option"]

        # 정답 여부를 확인
        is_correct = question.correct_option == selected_option

        submission = MultipleChoiceSubmission.objects.create(
            user=self.context["request"].user,  # 제출한 사용자
            question=question,
            selected_option=selected_option,
            is_correct=is_correct,
        )

        return submission


class MissionSerializer(serializers.ModelSerializer):
    """
    Mission 모델을 직렬화하는 클래스.

    Mission 모델의 필드들을 직렬화/역직렬화하여 API 응답에서 사용됩니다.
    """

    class Meta:
        model = Mission
        fields = (
            "title",
            "description",
            "minor_category",
            "mission_type",
            "is_midterm",
            "is_final",
        )


class CodeSubmissionSerializer(serializers.ModelSerializer):
    """
    CodeSubmission 모델을 직렬화하는 클래스.

    CodeSubmission 모델의 필드들을 직렬화/역직렬화하여 API 응답에서 사용됩니다.
    """

    class Meta:
        model = CodeSubmission
        fields = (
            "mission",
            "problem_statement",
            "example_input",
            "example_output",
            "time_limit",
            "memory_limit",
            "language",
        )

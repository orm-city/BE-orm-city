from rest_framework import serializers
from .models import (
    Mission,
    Question,
    MultipleChoiceOption,
    CodeQuestion,
    MissionSubmission,
    MultipleChoiceSubmission,
    CodeSubmission,
)


class MissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = [
            "title",
            "description",
            "mission_type",
            "order",
            "passing_score",
            "minor_category",
        ]


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "mission", "question_type", "content", "order", "points"]


class MultipleChoiceOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleChoiceOption
        fields = ["id", "question", "content", "is_correct", "order"]


class CodeQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeQuestion
        fields = ["id", "question", "initial_code", "test_cases"]


class MissionSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissionSubmission
        fields = ["id", "user", "mission", "submitted_at", "total_score", "is_passed"]
        read_only_fields = ["submitted_at", "total_score", "is_passed"]


class MultipleChoiceSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleChoiceSubmission
        fields = [
            "id",
            "mission_submission",
            "question",
            "selected_option",
            "submitted_at",
            "score",
        ]
        read_only_fields = ["submitted_at", "score"]


class CodeSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeSubmission
        fields = [
            "id",
            "mission_submission",
            "question",
            "submitted_code",
            "submitted_at",
            "score",
        ]
        read_only_fields = ["submitted_at", "score"]

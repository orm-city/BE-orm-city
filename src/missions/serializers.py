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

class MultipleChoiceOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleChoiceOption
        fields = ['id', 'content', 'is_correct', 'order']

class CodeQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeQuestion
        fields = ['id', 'initial_code', 'test_cases']

class QuestionSerializer(serializers.ModelSerializer):
    options = MultipleChoiceOptionSerializer(many=True, required=False)
    code_question = CodeQuestionSerializer(required=False)

    class Meta:
        model = Question
        fields = ['id', 'mission', 'question_type', 'content', 'order', 'points', 'options', 'code_question']

class MissionSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Mission
        fields = ['id', 'minor_category', 'title', 'description', 'mission_type', 'order', 'passing_score', 'questions']

class MissionSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissionSubmission
        fields = ['id', 'user', 'mission', 'submitted_at', 'total_score', 'is_passed']

class MultipleChoiceSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleChoiceSubmission
        fields = ['id', 'mission_submission', 'question', 'submitted_at', 'score', 'selected_option']

class CodeSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeSubmission
        fields = ['id', 'mission_submission', 'question', 'submitted_at', 'score', 'submitted_code']

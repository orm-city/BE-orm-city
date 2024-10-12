from django.contrib import admin
from .models import (
    Mission,
    MultipleChoiceQuestion,
    CodeSubmission,
    TestCase,
    MultipleChoiceSubmission,
    CodeSubmissionRecord,
)


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ("title", "minor_category", "mission_type", "is_midterm", "is_final")
    search_fields = ("title", "description", "minor_category__name")
    list_filter = ("mission_type", "is_midterm", "is_final", "minor_category")


@admin.register(MultipleChoiceQuestion)
class MultipleChoiceQuestionAdmin(admin.ModelAdmin):
    list_display = ("mission", "question", "correct_option")
    search_fields = ("question",)
    list_filter = ("mission__title",)


@admin.register(CodeSubmission)
class CodeSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "mission",
        "problem_statement",
        "time_limit",
        "memory_limit",
        "language",
    )
    search_fields = ("problem_statement",)
    list_filter = ("mission__title", "language")


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ("code_submission", "input_data", "expected_output", "is_sample")
    search_fields = ("input_data", "expected_output")
    list_filter = ("code_submission__problem_statement", "is_sample")


@admin.register(MultipleChoiceSubmission)
class MultipleChoiceSubmissionAdmin(admin.ModelAdmin):
    list_display = ("user", "question", "selected_option", "is_correct", "submitted_at")
    search_fields = ("user__username", "question__question")
    list_filter = ("is_correct", "submitted_at")


@admin.register(CodeSubmissionRecord)
class CodeSubmissionRecordAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "code_submission",
        "is_passed",
        "submission_time",
        "execution_time",
        "memory_usage",
    )
    search_fields = ("user__username", "code_submission__problem_statement")
    list_filter = ("is_passed", "submission_time")

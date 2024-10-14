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
    """
    Admin 화면에서 Mission 모델을 관리하기 위한 클래스.
    
    Attributes:
        list_display (tuple): Mission 리스트에서 표시할 필드들.
        search_fields (tuple): 검색 가능 필드들.
        list_filter (tuple): 필터로 사용할 필드들.
    """
    list_display = ("title", "minor_category", "mission_type", "is_midterm", "is_final")
    search_fields = ("title", "description", "minor_category__name")
    list_filter = ("mission_type", "is_midterm", "is_final", "minor_category")


@admin.register(MultipleChoiceQuestion)
class MultipleChoiceQuestionAdmin(admin.ModelAdmin):
    """
    Admin 화면에서 MultipleChoiceQuestion 모델을 관리하기 위한 클래스.
    
    Attributes:
        list_display (tuple): MultipleChoiceQuestion 리스트에서 표시할 필드들.
        search_fields (tuple): 검색 가능 필드들.
        list_filter (tuple): 필터로 사용할 필드들.
    """
    list_display = ("mission", "question", "correct_option")
    search_fields = ("question",)
    list_filter = ("mission__title",)


@admin.register(CodeSubmission)
class CodeSubmissionAdmin(admin.ModelAdmin):
    """
    Admin 화면에서 CodeSubmission 모델을 관리하기 위한 클래스.
    
    Attributes:
        list_display (tuple): CodeSubmission 리스트에서 표시할 필드들.
        search_fields (tuple): 검색 가능 필드들.
        list_filter (tuple): 필터로 사용할 필드들.
    """
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
    """
    Admin 화면에서 TestCase 모델을 관리하기 위한 클래스.
    
    Attributes:
        list_display (tuple): TestCase 리스트에서 표시할 필드들.
        search_fields (tuple): 검색 가능 필드들.
        list_filter (tuple): 필터로 사용할 필드들.
    """
    list_display = ("code_submission", "input_data", "expected_output", "is_sample")
    search_fields = ("input_data", "expected_output")
    list_filter = ("code_submission__problem_statement", "is_sample")


@admin.register(MultipleChoiceSubmission)
class MultipleChoiceSubmissionAdmin(admin.ModelAdmin):
    """
    Admin 화면에서 MultipleChoiceSubmission 모델을 관리하기 위한 클래스.
    
    Attributes:
        list_display (tuple): MultipleChoiceSubmission 리스트에서 표시할 필드들.
        search_fields (tuple): 검색 가능 필드들.
        list_filter (tuple): 필터로 사용할 필드들.
    """
    list_display = ("user", "question", "selected_option", "is_correct", "submitted_at")
    search_fields = ("user__username", "question__question")
    list_filter = ("is_correct", "submitted_at")


@admin.register(CodeSubmissionRecord)
class CodeSubmissionRecordAdmin(admin.ModelAdmin):
    """
    Admin 화면에서 CodeSubmissionRecord 모델을 관리하기 위한 클래스.
    
    Attributes:
        list_display (tuple): CodeSubmissionRecord 리스트에서 표시할 필드들.
        search_fields (tuple): 검색 가능 필드들.
        list_filter (tuple): 필터로 사용할 필드들.
    """
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

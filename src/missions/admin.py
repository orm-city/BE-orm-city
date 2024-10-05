# missions/admin.py

from django.contrib import admin
from .models import (
    Mission,
    Question,
    MultipleChoiceOption,
    CodeQuestion,
    MissionSubmission,
    MultipleChoiceSubmission,
    CodeSubmission,
)

# 인라인 모델 설정
class MultipleChoiceOptionInline(admin.TabularInline):
    model = MultipleChoiceOption
    extra = 1

class CodeQuestionInline(admin.StackedInline):
    model = CodeQuestion
    extra = 0

# 문제 관리자 설정
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('content', 'mission', 'question_type', 'order', 'points')
    list_filter = ('mission', 'question_type')
    search_fields = ('content',)
    inlines = []

    def get_inlines(self, request, obj=None):
        if obj:
            if obj.question_type == 'MCQ':
                return [MultipleChoiceOptionInline]
            elif obj.question_type == 'CODE':
                return [CodeQuestionInline]
        return []

# 미션 관리자 설정
@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'minor_category', 'mission_type', 'order', 'passing_score')
    list_filter = ('minor_category', 'mission_type')
    search_fields = ('title', 'description')

# 미션 제출 관리자 설정
@admin.register(MissionSubmission)
class MissionSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'mission', 'submitted_at', 'total_score', 'is_passed')
    list_filter = ('is_passed', 'submitted_at')
    search_fields = ('user__username', 'mission__title')

# 객관식 문제 제출 관리자 설정
@admin.register(MultipleChoiceSubmission)
class MultipleChoiceSubmissionAdmin(admin.ModelAdmin):
    list_display = ('mission_submission', 'question', 'selected_option', 'score', 'submitted_at')
    search_fields = ('mission_submission__user__username', 'question__content')

# 코드 문제 제출 관리자 설정
@admin.register(CodeSubmission)
class CodeSubmissionAdmin(admin.ModelAdmin):
    list_display = ('mission_submission', 'question', 'score', 'submitted_at')
    search_fields = ('mission_submission__user__username', 'question__content')

# 모델 등록
admin.site.register(MultipleChoiceOption)
admin.site.register(CodeQuestion)

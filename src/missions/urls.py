from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MissionViewSet,
    QuestionViewSet,
    MultipleChoiceOptionViewSet,
    CodeQuestionViewSet,
    MissionSubmissionViewSet,
    MultipleChoiceSubmissionViewSet,
    CodeSubmissionViewSet,
)

# DefaultRouter를 사용하여 뷰셋 자동 라우팅
router = DefaultRouter()
router.register(r'missions', MissionViewSet, basename='mission')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'multiple-choice-options', MultipleChoiceOptionViewSet, basename='multiplechoiceoption')
router.register(r'code-questions', CodeQuestionViewSet, basename='codequestion')
router.register(r'mission-submissions', MissionSubmissionViewSet, basename='missionsubmission')
router.register(r'multiple-choice-submissions', MultipleChoiceSubmissionViewSet, basename='multiplechoicesubmission')
router.register(r'code-submissions', CodeSubmissionViewSet, basename='codesubmission')

# URL 패턴 정의
urlpatterns = [
    path('', include(router.urls)),
]

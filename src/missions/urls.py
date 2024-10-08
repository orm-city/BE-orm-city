from django.urls import path
from .views import (
    MissionListCreateView,
    MissionRetrieveUpdateDestroyView,
    QuestionListCreateView,
    QuestionRetrieveUpdateDestroyView,
    MultipleChoiceOptionListCreateView,
    MultipleChoiceOptionRetrieveUpdateDestroyView,
    CodeQuestionListCreateView,
    CodeQuestionRetrieveUpdateDestroyView,
    MissionSubmissionListCreateView,
    MissionSubmissionRetrieveView,
    MultipleChoiceSubmissionListCreateView,
    MultipleChoiceSubmissionRetrieveView,
    CodeSubmissionListCreateView,
    CodeSubmissionRetrieveView,
)

urlpatterns = [
    # 미션 엔드포인트
    path('missions/', MissionListCreateView.as_view(), name='mission-list-create'),
    path('missions/<int:pk>/', MissionRetrieveUpdateDestroyView.as_view(), name='mission-detail'),

    # 문제 엔드포인트
    path('questions/', QuestionListCreateView.as_view(), name='question-list-create'),
    path('questions/<int:pk>/', QuestionRetrieveUpdateDestroyView.as_view(), name='question-detail'),

    # 객관식 선택지 엔드포인트
    path('multiple-choice-options/', MultipleChoiceOptionListCreateView.as_view(), name='mc-option-list-create'),
    path('multiple-choice-options/<int:pk>/', MultipleChoiceOptionRetrieveUpdateDestroyView.as_view(), name='mc-option-detail'),

    # 코드 문제 추가 정보 엔드포인트
    path('code-questions/', CodeQuestionListCreateView.as_view(), name='code-question-list-create'),
    path('code-questions/<int:pk>/', CodeQuestionRetrieveUpdateDestroyView.as_view(), name='code-question-detail'),

    # 미션 제출 엔드포인트
    path('mission-submissions/', MissionSubmissionListCreateView.as_view(), name='mission-submission-list-create'),
    path('mission-submissions/<int:pk>/', MissionSubmissionRetrieveView.as_view(), name='mission-submission-detail'),

    # 객관식 문제 제출 엔드포인트
    path('multiple-choice-submissions/', MultipleChoiceSubmissionListCreateView.as_view(), name='mc-submission-list-create'),
    path('multiple-choice-submissions/<int:pk>/', MultipleChoiceSubmissionRetrieveView.as_view(), name='mc-submission-detail'),

    # 코드 문제 제출 엔드포인트
    path('code-submissions/', CodeSubmissionListCreateView.as_view(), name='code-submission-list-create'),
    path('code-submissions/<int:pk>/', CodeSubmissionRetrieveView.as_view(), name='code-submission-detail'),
]

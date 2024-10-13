from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MissionViewSet,
    MultipleChoiceQuestionViewSet,
    MultipleChoiceQuestionSubmissionAPIView,
    CodeSubmissionViewSet,
    CodeSubmissionEvaluationAPIView,
)

router = DefaultRouter()

router.register(
    r"multiple-choice-questions",
    MultipleChoiceQuestionViewSet,
    basename="multiple-choice-question",
)
router.register(
    r"code-submission-questions",
    CodeSubmissionViewSet,
    basename="code-submission-question",
)
router.register(r"code-submissions", CodeSubmissionViewSet, basename="code-submission")
router.register(r"", MissionViewSet, basename="mission")

urlpatterns = [
    # 중간 및 기말 미션 5지선다형 문제 목록 필터링 API
    path(
        "major/<int:major_id>/<int:minor_id>/<str:mid_or_final>/mcqs/",
        MultipleChoiceQuestionViewSet.as_view({"get": "list"}),
        name="multiple-choice-question-list",
    ),
    # 중간 및 기말 미션 코드 제출형 문제 목록 필터링 API
    path(
        "major/<int:major_id>/<int:minor_id>/<str:mid_or_final>/cs/",
        CodeSubmissionViewSet.as_view({"get": "list"}),
        name="code-submission-list",
    ),
    # 5지선다형 문제 제출 및 채점 API
    path(
        "multiple-choice-questions/submit/",
        MultipleChoiceQuestionSubmissionAPIView.as_view(),
        name="multiple-choice-question-submit",
    ),
    # 코드 제출형 문제 채점 API
    path(
        "code-submissions/<int:code_submission_id>/evaluate/",
        CodeSubmissionEvaluationAPIView.as_view(),
        name="code-submission-evaluate",
    ),
    path("", include(router.urls)),
]

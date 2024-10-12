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


router.register(r"missions", MissionViewSet, basename="mission")
router.register(
    r"multiple-choice-questions",
    MultipleChoiceQuestionViewSet,
    basename="multiple-choice-question",
)
router.register(r"code-submissions", CodeSubmissionViewSet, basename="code-submission")

urlpatterns = [
    path("", include(router.urls)),
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
]

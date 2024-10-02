# missions/urls.py
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

router = DefaultRouter()
router.register(r"missions", MissionViewSet)
router.register(r"questions", QuestionViewSet)
router.register(r"multiple-choice-options", MultipleChoiceOptionViewSet)
router.register(r"code-questions", CodeQuestionViewSet)
router.register(r"mission-submissions", MissionSubmissionViewSet)
router.register(r"multiple-choice-submissions", MultipleChoiceSubmissionViewSet)
router.register(r"code-submissions", CodeSubmissionViewSet)

# urlpatterns를 router.urls로 교체하여 자동으로 URL 라우팅을 설정
urlpatterns = router.urls

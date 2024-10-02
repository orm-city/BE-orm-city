# missions/views.py
from rest_framework import viewsets
from .models import (
    Mission,
    Question,
    MultipleChoiceOption,
    CodeQuestion,
    MissionSubmission,
    MultipleChoiceSubmission,
    CodeSubmission,
)

# from rest_framework.permissions import AllowAny  #인증 없이 사용 추가
from .serializers import (
    MissionSerializer,
    QuestionSerializer,
    MultipleChoiceOptionSerializer,
    CodeQuestionSerializer,
    MissionSubmissionSerializer,
    MultipleChoiceSubmissionSerializer,
    CodeSubmissionSerializer,
)


# 미션에 대한 모든 CRUD 작업을 처리하는 뷰셋
class MissionViewSet(viewsets.ModelViewSet):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
    # permission_classes = [AllowAny]  # 인증 없이 접근을 허용


# 문제에 대한 모든 CRUD 작업을 처리하는 뷰셋
class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


# 객관식 문제 선택지에 대한 모든 CRUD 작업을 처리하는 뷰셋
class MultipleChoiceOptionViewSet(viewsets.ModelViewSet):
    queryset = MultipleChoiceOption.objects.all()
    serializer_class = MultipleChoiceOptionSerializer


# 코드 제출형 문제에 대한 모든 CRUD 작업을 처리하는 뷰셋
class CodeQuestionViewSet(viewsets.ModelViewSet):
    queryset = CodeQuestion.objects.all()
    serializer_class = CodeQuestionSerializer


# 미션 제출에 대한 모든 CRUD 작업을 처리하는 뷰셋
class MissionSubmissionViewSet(viewsets.ModelViewSet):
    queryset = MissionSubmission.objects.all()
    serializer_class = MissionSubmissionSerializer


# 객관식 문제 제출에 대한 모든 CRUD 작업을 처리하는 뷰셋
class MultipleChoiceSubmissionViewSet(viewsets.ModelViewSet):
    queryset = MultipleChoiceSubmission.objects.all()
    serializer_class = MultipleChoiceSubmissionSerializer


# 코드 제출에 대한 모든 CRUD 작업을 처리하는 뷰셋
class CodeSubmissionViewSet(viewsets.ModelViewSet):
    queryset = CodeSubmission.objects.all()
    serializer_class = CodeSubmissionSerializer

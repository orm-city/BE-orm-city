from rest_framework import viewsets, permissions
from .models import (
    Mission,
    Question,
    MultipleChoiceOption,
    CodeQuestion,
    MissionSubmission,
    MultipleChoiceSubmission,
    CodeSubmission,
)
from .serializers import (
    MissionSerializer,
    QuestionSerializer,
    MultipleChoiceOptionSerializer,
    CodeQuestionSerializer,
    MissionSubmissionSerializer,
    MultipleChoiceSubmissionSerializer,
    CodeSubmissionSerializer,
)

class MissionViewSet(viewsets.ModelViewSet):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class MultipleChoiceOptionViewSet(viewsets.ModelViewSet):
    queryset = MultipleChoiceOption.objects.all()
    serializer_class = MultipleChoiceOptionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CodeQuestionViewSet(viewsets.ModelViewSet):
    queryset = CodeQuestion.objects.all()
    serializer_class = CodeQuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class MissionSubmissionViewSet(viewsets.ModelViewSet):
    queryset = MissionSubmission.objects.all()
    serializer_class = MissionSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MultipleChoiceSubmissionViewSet(viewsets.ModelViewSet):
    queryset = MultipleChoiceSubmission.objects.all()
    serializer_class = MultipleChoiceSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

class CodeSubmissionViewSet(viewsets.ModelViewSet):
    queryset = CodeSubmission.objects.all()
    serializer_class = CodeSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

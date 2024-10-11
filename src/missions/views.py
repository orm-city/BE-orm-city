from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets

from .models import (
    Mission,
    MultipleChoiceQuestion,
    CodeSubmission,
)
from .serializers import (
    MissionSerializer,
    MultipleChoiceQuestionSerializer,
    CodeSubmissionSerializer,
    MultipleChoiceSubmissionSerializer,
)
from .services import evaluate_code_submission


class MissionViewSet(viewsets.ModelViewSet):
    """
    모든 미션 목록 조회 및 특정 미션의 세부 정보 조회를 제공하는 ViewSet.
    """

    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
    http_method_names = ["get", "put", "patch"]


class MultipleChoiceQuestionViewSet(viewsets.ModelViewSet):
    """
    5지선다형 문제의 CRUD를 제공하는 ViewSet.
    ModelViewSet을 사용하여 기본적인 CRUD 기능을 제공.
    """

    queryset = MultipleChoiceQuestion.objects.all()
    serializer_class = MultipleChoiceQuestionSerializer

    def get_queryset(self):
        """
        특정 미션에 속한 5지선다형 문제 목록을 필터링하여 반환하는 메서드.
        URL에서 mission_id를 받아 해당 미션에 속한 문제만 반환.
        """
        mission_id = self.request.query_params.get("mission_id", None)
        if mission_id:
            try:
                mission = Mission.objects.get(pk=mission_id)
                return MultipleChoiceQuestion.objects.filter(mission=mission)
            except Mission.DoesNotExist:
                return MultipleChoiceQuestion.objects.none()
        return super().get_queryset()

    def destroy(self, request, *args, **kwargs):
        """
        삭제 시 커스터마이징: 삭제되었는지 확인 후 성공 메시지 반환.
        """
        try:
            question = self.get_object()
            question.delete()
            return Response(
                {"message": "문제가 성공적으로 삭제되었습니다."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except MultipleChoiceQuestion.DoesNotExist:
            return Response(
                {"error": "해당 문제가 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )


class MultipleChoiceQuestionSubmissionAPIView(APIView):
    """
    5지선다형 문제에 대한 답안을 제출하고 채점하는 API 뷰.
    """

    def post(self, request, *args, **kwargs):
        serializer = MultipleChoiceSubmissionSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            submission = serializer.save()
            return Response(
                {"message": "제출 완료", "is_correct": submission.is_correct},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CodeSubmissionViewSet(viewsets.ModelViewSet):
    """
    코드 제출형 문제에 대한 CRUD ViewSet.
    특정 미션에 속한 코드 제출형 문제들을 필터링하여 조회할 수 있음.
    """

    queryset = CodeSubmission.objects.all()
    serializer_class = CodeSubmissionSerializer

    def get_queryset(self):
        mission_id = self.request.query_params.get("mission_id", None)
        if mission_id:
            try:
                mission = Mission.objects.get(pk=mission_id)
                return CodeSubmission.objects.filter(mission=mission)
            except Mission.DoesNotExist:
                return CodeSubmission.objects.none()
        return super().get_queryset()

    def destroy(self, request, *args, **kwargs):
        """
        삭제 시 커스터마이징: 삭제되었는지 확인 후 성공 메시지 반환.
        """
        try:
            submission = self.get_object()
            submission.delete()
            return Response(
                {"message": "코드 제출형 문제가 성공적으로 삭제되었습니다."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except CodeSubmission.DoesNotExist:
            return Response(
                {"error": "해당 코드 제출형 문제가 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )


class CodeSubmissionEvaluationAPIView(APIView):
    """
    제출된 코드를 채점하고 결과를 반환하는 API.
    """

    def post(self, request, code_submission_id, *args, **kwargs):
        """
        POST 요청으로 제출된 코드를 채점하는 메서드.
        """

        try:
            code_submission = CodeSubmission.objects.get(pk=code_submission_id)
        except CodeSubmission.DoesNotExist:
            return Response(
                {"error": "해당 코드 제출형 문제가 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        submitted_code = request.data.get("submitted_code")
        if not submitted_code:
            return Response(
                {"error": "제출된 코드가 없습니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user

        time_limit = code_submission.time_limit
        memory_limit = code_submission.memory_limit
        result = evaluate_code_submission(
            code_submission=code_submission,
            submitted_code=submitted_code,
            user=user,
            time_limit=time_limit,
            memory_limit=memory_limit,
        )

        return Response(
            {
                "message": "채점 완료",
                "test_results": result["results"],
                "is_passed": result["all_passed"],
            },
            status=status.HTTP_200_OK,
        )

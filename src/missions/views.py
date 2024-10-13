from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .permissions import IsActiveOrCompletedEnrollmentOrManagerAdmin, IsManagerOrAdmin

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
    Mission 관련 모든 목록 조회 및 특정 Mission의 세부 정보 조회를 제공하는 ViewSet.

    이 ViewSet은 Mission 객체에 대한 list, retrieve, update, partial_update 등의 작업을 처리합니다.
    사용자 권한에 따라 접근이 제한됩니다.
    """

    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
    http_method_names = ["get", "put", "patch"]

    def get_permissions(self):
        """
        요청에 따라 필요한 권한을 반환합니다.

        사용자의 요청 action에 따라 다른 permission 클래스를 적용합니다.
        - list: 인증된 사용자만 접근 가능.
        - retrieve: 사용자가 해당 Mission에 대한 등록 상태가 active 또는 completed이거나,
                    사용자가 manager 또는 admin일 때 접근 가능.
        - update/partial_update: manager 또는 admin 권한이 있을 때 접근 가능.

        Returns:
            list: 요청 action에 맞는 permission 클래스의 인스턴스 목록.

        Raises:
            NotAuthenticated: 인증되지 않은 사용자가 접근할 경우 예외가 발생할 수 있습니다.
            PermissionDenied: 사용자가 적절한 권한을 갖지 않으면 접근이 거부됩니다.
        """
        if self.action == "list":
            permission_classes = [IsAuthenticated]
        elif self.action == "retrieve":
            permission_classes = [IsActiveOrCompletedEnrollmentOrManagerAdmin]
        elif self.action in ["update", "partial_update"]:
            permission_classes = [IsManagerOrAdmin]
        else:
            permission_classes = [IsManagerOrAdmin]

        return [permission() for permission in permission_classes]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="minor_category_id",
                description="필터링할 MinorCategory ID. 이 값을 제공하면 해당 minor_category에 속한 Mission만 반환됩니다.",
                required=False,
                type=int,
            ),
        ],
        responses={200: OpenApiResponse(MissionSerializer(many=True))},
    )
    def list(self, request, *args, **kwargs):
        """
        특정 MinorCategory에 속한 Mission만 반환하는 커스텀 list 메서드.

        요청 파라미터에 minor_category_id가 포함된 경우, 해당 minor_category에 속한 Mission만 필터링합니다.
        만약 파라미터가 제공되지 않으면, 모든 Mission 목록을 반환합니다.

        Args:
            request (Request): HTTP 요청 객체.

        Returns:
            Response: 직렬화된 Mission 데이터를 포함하는 응답 객체.

        Example:
            GET /multiplechoicequestions/?minor_category_id=5  # minor_category_id=5인 Mission만 반환.
            GET /multiplechoicequestions/                      # 모든 Mission 반환.
        """
        queryset = Mission.objects.all()

        # 쿼리 파라미터로 minor_category_id를 받음
        minor_category_id = self.request.query_params.get("minor_category_id", None)

        if minor_category_id:
            # 특정 MinorCategory에 속한 Mission만 필터링
            queryset = queryset.filter(minor_category_id=minor_category_id)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MultipleChoiceQuestionViewSet(viewsets.ModelViewSet):
    """
    5지선다형 문제에 대한 CRUD 기능을 제공하는 ViewSet.

    기본적인 CRUD(Create, Read, Update, Delete) 기능을 ModelViewSet을 통해 구현합니다.
    특정 미션에 속한 문제들을 필터링하여 목록을 제공하며, 문제의 생성, 수정, 삭제를 지원합니다.
    """

    queryset = MultipleChoiceQuestion.objects.all()
    serializer_class = MultipleChoiceQuestionSerializer

    def get_permissions(self):
        """
        요청에 따라 필요한 권한을 반환합니다.

        사용자의 요청 action에 따라 다른 permission 클래스를 적용합니다.
        - list: 인증된 사용자만 접근 가능.
        - retrieve: 사용자가 해당 미션에 대한 등록 상태가 active 또는 completed이거나,
                    사용자가 manager 또는 admin일 때 접근 가능.
        - update/partial_update: manager 또는 admin 권한이 있을 때 접근 가능.

        Returns:
            list: 요청 action에 맞는 permission 클래스의 인스턴스 목록.

        Raises:
            NotAuthenticated: 인증되지 않은 사용자가 접근할 경우 예외가 발생할 수 있습니다.
            PermissionDenied: 사용자가 적절한 권한을 갖지 않으면 접근이 거부됩니다.
        """
        if self.action == "list":
            permission_classes = [IsAuthenticated]
        elif self.action == "retrieve":
            permission_classes = [IsActiveOrCompletedEnrollmentOrManagerAdmin]
        elif self.action in ["update", "partial_update"]:
            permission_classes = [IsManagerOrAdmin]
        else:
            permission_classes = [IsManagerOrAdmin]

        return [permission() for permission in permission_classes]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="mission_id",
                description="필터링할 mission ID. 이 값을 제공하면 해당 mission 속한 multiplechoicequestions만 반환됩니다.",
                required=False,
                type=int,
            ),
        ],
        responses={200: OpenApiResponse(MissionSerializer(many=True))},
    )
    def list(self, request, *args, **kwargs):
        """
        특정 미션에 속한 5지선다형 문제 목록을 필터링하여 반환합니다.

        URL 쿼리 파라미터로 `mission_id`를 받아, 해당 미션에 속한 문제들을 필터링하여 반환합니다.
        또는, URL 경로 파라미터로 `minor_id`, `mid_or_final`을 받아 필터링할 수 있습니다.

        Args:
            request (Request): HTTP 요청 객체.
            minor_id (int): 소분류 카테고리 ID.
            mid_or_final (str): "mid" 또는 "final"로 미션 유형을 나타냅니다.

        Returns:
            Response: 직렬화된 MultipleChoiceQuestion 데이터를 포함하는 응답 객체.

        Example:
            GET /multiplechoicequestions/?mission_id=5  # mission_id=5인 문제만 반환.
            GET /major/1/2/mid/                        # minor_id=2인 중간 미션의 문제만 반환.

        Raises:
            Mission.DoesNotExist: 요청된 mission_id에 해당하는 미션이 존재하지 않으면 빈 결과를 반환합니다.
        """
        queryset = self.get_queryset()

        # URL 경로 파라미터로 minor_id와 mid_or_final을 받음
        minor_id = kwargs.get("minor_id")
        mid_or_final = kwargs.get("mid_or_final")

        # mission_id 쿼리 파라미터로 필터링
        mission_id = self.request.query_params.get("mission_id", None)
        if mission_id:
            queryset = queryset.filter(mission_id=mission_id)
        # minor_id와 mid_or_final 파라미터로 필터링
        elif minor_id and mid_or_final:
            mission_filter = {
                "minor_category_id": minor_id,
                "is_midterm": (mid_or_final == "mid"),
                "is_final": (mid_or_final == "final"),
            }
            missions = Mission.objects.filter(**mission_filter)
            queryset = queryset.filter(mission__in=missions)

        # 시리얼라이저를 사용해 데이터 반환
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        문제 삭제 기능을 제공하며, 삭제 완료 후 성공 메시지를 반환합니다.

        문제를 삭제할 때, 존재하지 않는 경우 404 에러를 반환하며,
        삭제가 성공한 경우 204 상태 코드를 반환합니다.

        Args:
            request (Request): HTTP 요청 객체.

        Returns:
            Response: 문제 삭제 성공 또는 실패 메시지를 포함하는 응답 객체.

        Raises:
            MultipleChoiceQuestion.DoesNotExist: 삭제하려는 문제가 존재하지 않을 때 404 에러를 반환합니다.
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

    사용자가 5지선다형 문제에 대한 답안을 제출하면, 이를 검증하고 채점 결과를 반환합니다.
    제출된 답안이 유효한 경우, 답안이 맞았는지 여부를 포함하여 응답을 반환합니다.
    """

    def post(self, request, *args, **kwargs):
        """
        5지선다형 문제의 답안을 제출하고 채점합니다.

        사용자가 제출한 데이터를 받아서 검증한 후, 답안이 올바른지 여부를 응답합니다.
        제출된 데이터가 유효하지 않을 경우, 오류 메시지를 반환합니다.

        Args:
            request (Request): HTTP 요청 객체, 제출된 데이터를 포함.

        Returns:
            Response: 제출 성공 시 채점 결과를 포함한 응답 객체를 반환합니다.
                      {"message": "제출 완료", "is_correct": bool} 형식의 JSON 응답.
                      제출 실패 시, 오류 메시지와 함께 400 상태 코드를 반환합니다.

        Raises:
            ValidationError: 제출된 데이터가 유효하지 않을 경우 발생하며,
                             400 상태 코드와 함께 에러 메시지를 반환합니다.
        """
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
    코드 제출형 문제에 대한 CRUD 기능을 제공하는 ViewSet.

    모든 미션 목록 조회 및 특정 미션의 세부 정보 조회를 제공하는 ViewSet.
    """

    queryset = Mission.objects.all()
    serializer_class = MissionSerializer

    """
    사용자는 특정 미션에 속한 코드 제출형 문제들을 필터링하여 조회할 수 있으며,
    문제의 생성, 수정, 삭제를 지원합니다.
    """

    queryset = CodeSubmission.objects.all()
    serializer_class = CodeSubmissionSerializer

    def get_permissions(self):
        """
        요청에 따라 필요한 권한을 반환합니다.

        사용자의 요청 action에 따라 다른 permission 클래스를 적용합니다.
        - list: 인증된 사용자만 접근 가능.
        - retrieve: 사용자가 해당 미션에 대한 등록 상태가 active 또는 completed이거나,
                    사용자가 manager 또는 admin일 때 접근 가능.
        - update/partial_update: manager 또는 admin 권한이 있을 때 접근 가능.

        Returns:
            list: 요청 action에 맞는 permission 클래스의 인스턴스 목록.

        Raises:
            NotAuthenticated: 인증되지 않은 사용자가 접근할 경우 예외가 발생할 수 있습니다.
            PermissionDenied: 사용자가 적절한 권한을 갖지 않으면 접근이 거부됩니다.
        """
        if self.action == "list":
            permission_classes = [IsAuthenticated]
        elif self.action == "retrieve":
            permission_classes = [IsActiveOrCompletedEnrollmentOrManagerAdmin]
        elif self.action in ["update", "partial_update"]:
            permission_classes = [IsManagerOrAdmin]
        else:
            permission_classes = [IsManagerOrAdmin]
        return [permission() for permission in permission_classes]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="mission_id",
                description="필터링할 mission ID. 이 값을 제공하면 해당 mission 속한 multiplechoicequestions만 반환됩니다.",
                required=False,
                type=int,
            ),
        ],
        responses={200: OpenApiResponse(MissionSerializer(many=True))},
    )
    def list(self, request, *args, **kwargs):
        """
        특정 미션에 속한 5지선다형 문제 목록을 필터링하여 반환합니다.

        URL 쿼리 파라미터로 `mission_id`를 받아, 해당 미션에 속한 문제들을 필터링하여 반환합니다.
        또는, URL 경로 파라미터로 `minor_id`, `mid_or_final`을 받아 필터링할 수 있습니다.

        Args:
            request (Request): HTTP 요청 객체.
            minor_id (int): 소분류 카테고리 ID.
            mid_or_final (str): "mid" 또는 "final"로 미션 유형을 나타냅니다.

        Returns:
            Response: 직렬화된 MultipleChoiceQuestion 데이터를 포함하는 응답 객체.

        Example:
            GET /multiplechoicequestions/?mission_id=5  # mission_id=5인 문제만 반환.
            GET /major/1/2/mid/                        # minor_id=2인 중간 미션의 문제만 반환.

        Raises:
            Mission.DoesNotExist: 요청된 mission_id에 해당하는 미션이 존재하지 않으면 빈 결과를 반환합니다.
        """
        queryset = self.get_queryset()

        # URL 경로 파라미터로 minor_id와 mid_or_final을 받음
        minor_id = kwargs.get("minor_id")
        mid_or_final = kwargs.get("mid_or_final")

        # mission_id 쿼리 파라미터로 필터링
        mission_id = self.request.query_params.get("mission_id", None)
        if mission_id:
            queryset = queryset.filter(mission_id=mission_id)
        # minor_id와 mid_or_final 파라미터로 필터링
        elif minor_id and mid_or_final:
            mission_filter = {
                "minor_category_id": minor_id,
                "is_midterm": (mid_or_final == "mid"),
                "is_final": (mid_or_final == "final"),
            }
            missions = Mission.objects.filter(**mission_filter)
            queryset = queryset.filter(mission__in=missions)

        # 시리얼라이저를 사용해 데이터 반환
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        코드 제출형 문제 삭제 기능을 제공하며, 삭제 완료 후 성공 메시지를 반환합니다.

        문제가 존재하지 않을 경우 404 에러를 반환하며,
        삭제가 성공한 경우 204 상태 코드를 반환합니다.

        Args:
            request (Request): HTTP 요청 객체.

        Returns:
            Response: 문제 삭제 성공 또는 실패 메시지를 포함한 응답 객체.

        Raises:
            CodeSubmission.DoesNotExist: 삭제하려는 코드 제출형 문제가 존재하지 않을 때 404 에러를 반환합니다.
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

    사용자가 제출한 코드를 받아서 미리 정의된 시간 및 메모리 제한 내에서 채점을 수행하고,
    채점 결과를 반환합니다.
    """

    def post(self, request, code_submission_id, *args, **kwargs):
        """
        제출된 코드를 채점하는 POST 메서드.

        사용자가 제출한 코드를 주어진 시간 및 메모리 제한 내에서 실행하고,
        테스트 결과와 함께 채점 통과 여부를 반환합니다.

        Args:
            request (Request): HTTP 요청 객체, 제출된 코드를 포함.
            code_submission_id (int): 채점할 코드 제출형 문제의 ID.

        Returns:
            Response: 채점 결과 및 통과 여부를 포함한 응답 객체.
                      {"message": "채점 완료", "test_results": list, "is_passed": bool} 형식의 JSON 응답.
                      제출된 코드가 없을 경우 400 상태 코드, 문제 ID가 잘못되었을 경우 404 상태 코드를 반환.

        Raises:
            CodeSubmission.DoesNotExist: 요청된 코드 제출형 문제 ID에 해당하는 문제가 존재하지 않을 때 404 에러를 반환.
            ValidationError: 제출된 코드가 없을 경우 400 상태 코드와 함께 에러 메시지를 반환.
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

        # 코드 실행 시 시간 및 메모리 제한
        time_limit = code_submission.time_limit
        memory_limit = code_submission.memory_limit

        # 제출된 코드를 채점하는 함수 호출
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

from rest_framework import mixins, generics, permissions, status
from rest_framework.response import Response
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

# 미션 리스트 및 생성 뷰
class MissionListCreateView(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            generics.GenericAPIView):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
  
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

# 미션 상세, 수정, 삭제 뷰
class MissionRetrieveUpdateDestroyView(mixins.RetrieveModelMixin,
                                       mixins.UpdateModelMixin,
                                       mixins.DestroyModelMixin,
                                       generics.GenericAPIView):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
  
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
  
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# 문제 리스트 및 생성 뷰
class QuestionListCreateView(mixins.ListModelMixin,
                             mixins.CreateModelMixin,
                             generics.GenericAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
  
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

# 문제 상세, 수정, 삭제 뷰
class QuestionRetrieveUpdateDestroyView(mixins.RetrieveModelMixin,
                                        mixins.UpdateModelMixin,
                                        mixins.DestroyModelMixin,
                                        generics.GenericAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
  
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
  
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# 객관식 선택지 리스트 및 생성 뷰
class MultipleChoiceOptionListCreateView(mixins.ListModelMixin,
                                         mixins.CreateModelMixin,
                                         generics.GenericAPIView):
    queryset = MultipleChoiceOption.objects.all()
    serializer_class = MultipleChoiceOptionSerializer
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
  
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

# 객관식 선택지 상세, 수정, 삭제 뷰
class MultipleChoiceOptionRetrieveUpdateDestroyView(mixins.RetrieveModelMixin,
                                                    mixins.UpdateModelMixin,
                                                    mixins.DestroyModelMixin,
                                                    generics.GenericAPIView):
    queryset = MultipleChoiceOption.objects.all()
    serializer_class = MultipleChoiceOptionSerializer
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
  
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
  
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# 코드 문제 추가 정보 리스트 및 생성 뷰
class CodeQuestionListCreateView(mixins.ListModelMixin,
                                 mixins.CreateModelMixin,
                                 generics.GenericAPIView):
    queryset = CodeQuestion.objects.all()
    serializer_class = CodeQuestionSerializer
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
  
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

# 코드 문제 추가 정보 상세, 수정, 삭제 뷰
class CodeQuestionRetrieveUpdateDestroyView(mixins.RetrieveModelMixin,
                                            mixins.UpdateModelMixin,
                                            mixins.DestroyModelMixin,
                                            generics.GenericAPIView):
    queryset = CodeQuestion.objects.all()
    serializer_class = CodeQuestionSerializer
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
  
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
  
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# 미션 제출 리스트 및 생성 뷰
class MissionSubmissionListCreateView(mixins.ListModelMixin,
                                      mixins.CreateModelMixin,
                                      generics.GenericAPIView):
    queryset = MissionSubmission.objects.all()
    serializer_class = MissionSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 로그인한 사용자의 제출만 조회하도록 쿼리셋 필터링
        return self.queryset.filter(user=self.request.user)
  
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
  
    def post(self, request, *args, **kwargs):
        # 미션 제출 시 현재 사용자를 설정
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

# 미션 제출 상세 뷰
class MissionSubmissionRetrieveView(mixins.RetrieveModelMixin,
                                    generics.GenericAPIView):
    queryset = MissionSubmission.objects.all()
    serializer_class = MissionSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        submission = self.get_object()
        if submission.user != request.user:
            return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        return self.retrieve(request, *args, **kwargs)

# 객관식 문제 제출 리스트 및 생성 뷰
class MultipleChoiceSubmissionListCreateView(mixins.ListModelMixin,
                                             mixins.CreateModelMixin,
                                             generics.GenericAPIView):
    queryset = MultipleChoiceSubmission.objects.all()
    serializer_class = MultipleChoiceSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 로그인한 사용자의 제출만 조회하도록 쿼리셋 필터링
        return self.queryset.filter(mission_submission__user=self.request.user)
  
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
  
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

# 객관식 문제 제출 상세 뷰
class MultipleChoiceSubmissionRetrieveView(mixins.RetrieveModelMixin,
                                           generics.GenericAPIView):
    queryset = MultipleChoiceSubmission.objects.all()
    serializer_class = MultipleChoiceSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        submission = self.get_object()
        if submission.mission_submission.user != request.user:
            return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        return self.retrieve(request, *args, **kwargs)

# 코드 문제 제출 리스트 및 생성 뷰
class CodeSubmissionListCreateView(mixins.ListModelMixin,
                                   mixins.CreateModelMixin,
                                   generics.GenericAPIView):
    queryset = CodeSubmission.objects.all()
    serializer_class = CodeSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 로그인한 사용자의 제출만 조회하도록 쿼리셋 필터링
        return self.queryset.filter(mission_submission__user=self.request.user)
  
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
  
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

# 코드 문제 제출 상세 뷰
class CodeSubmissionRetrieveView(mixins.RetrieveModelMixin,
                                 generics.GenericAPIView):
    queryset = CodeSubmission.objects.all()
    serializer_class = CodeSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        submission = self.get_object()
        if submission.mission_submission.user != request.user:
            return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        return self.retrieve(request, *args, **kwargs)

from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.response import Response

# from rest_framework.permissions import IsAuthenticated

from progress.models import UserProgress
from progress.serializers import UserProgressSerializer

from .models import Video
from .serializers import VideoSerializer


class VideoCreateAPIView(generics.CreateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer


class VideoRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def get_queryset(self):
        return Video.objects.filter(id=self.kwargs["pk"])


class VideoUpdateAPIView(generics.UpdateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def get_queryset(self):
        return Video.objects.filter(id=self.kwargs["pk"])


class VideoDeleteAPIView(generics.DestroyAPIView):
    queryset = Video.objects.all()

    def get_queryset(self):
        return Video.objects.filter(id=self.kwargs["pk"])


class UserProgressUpdateAPIView(generics.UpdateAPIView):
    serializer_class = UserProgressSerializer

    def put(self, request, *args, **kwargs):
        video_id = request.data.get("video_id")
        new_progress = request.data.get("progress_percent")
        additional_time = request.data.get("time_spent", 0)

        video = get_object_or_404(Video, id=video_id)
        user_progress, created = UserProgress.objects.get_or_create(
            user=request.user, video=video
        )

        user_progress.update_progress(
            new_progress, timezone.timedelta(seconds=additional_time)
        )

        return Response(
            UserProgressSerializer(user_progress).data, status=status.HTTP_200_OK
        )


class UserProgressDetailAPIView(generics.RetrieveAPIView):
    serializer_class = UserProgressSerializer

    def get(self, request, *args, **kwargs):
        video_id = self.kwargs.get("video_id")
        video = get_object_or_404(Video, id=video_id)
        user_progress = get_object_or_404(UserProgress, user=request.user, video=video)

        return Response(
            UserProgressSerializer(user_progress).data, status=status.HTTP_200_OK
        )

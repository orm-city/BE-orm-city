from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Video, VideoWatchProgress
from .serializers import VideoWatchProgressSerializer
from django.http import StreamingHttpResponse
import requests


class VideoViewSet(viewsets.ViewSet):
    """
    비디오 스트리밍 및 시청 기록 관리
    """

    def retrieve(self, request, pk=None):
        """
        비디오 스트리밍 기능 구현
        """
        video = get_object_or_404(Video, pk=pk)
        video_url = video.video_url

        # 비디오 URL을 통해 스트리밍 응답 생성
        def stream_video(video_url):
            r = requests.get(video_url, stream=True)
            for chunk in r.iter_content(chunk_size=8192):
                yield chunk

        response = StreamingHttpResponse(
            stream_video(video_url), content_type="video/mp4"
        )
        response["Accept-Ranges"] = "bytes"

        return response

    @action(detail=True, methods=["get"], url_path="watch-progress")
    def get_watch_progress(self, request, pk=None):
        """
        비디오의 시청 진행률을 반환
        """
        video = get_object_or_404(Video, pk=pk)
        watch_progress = VideoWatchProgress.objects.filter(
            user=request.user, video=video
        ).first()

        if watch_progress:
            serializer = VideoWatchProgressSerializer(watch_progress)
            return Response(serializer.data)
        return Response(
            {"message": "No watch progress found."}, status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=True, methods=["post"], url_path="watch-progress")
    def save_watch_progress(self, request, pk=None):
        """
        비디오 시청 시간 및 진행률을 기록
        """
        video = get_object_or_404(Video, pk=pk)
        serializer = VideoWatchProgressSerializer(data=request.data)
        if serializer.is_valid():
            watch_progress, created = VideoWatchProgress.objects.update_or_create(
                user=request.user,
                video=video,
                defaults={
                    "last_watched_time": serializer.validated_data["last_watched_time"],
                    "progress": serializer.validated_data["progress"],
                },
            )
            return Response(VideoWatchProgressSerializer(watch_progress).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path="resume")
    def resume_video(self, request, pk=None):
        """
        마지막 시청 지점을 가져와서 이어보기 기능을 구현
        """
        video = get_object_or_404(Video, pk=pk)
        watch_progress = VideoWatchProgress.objects.filter(
            user=request.user, video=video
        ).first()

        if watch_progress:
            return Response(
                {
                    "resume_time": watch_progress.last_watched_time,
                    "progress": watch_progress.progress,
                    "message": "You can resume the video from the last watched point.",
                }
            )
        return Response(
            {"message": "No resume point found."}, status=status.HTTP_404_NOT_FOUND
        )

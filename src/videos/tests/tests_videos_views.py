# 단순 import
from botocore.exceptions import ClientError
from django.conf import settings
from django.urls import reverse
import pytest

# Django 라이브러리

# DRF(Django Rest Framework) 라이브러리
from rest_framework import status

# 기능별로 만든 앱 모듈
from videos.models import Video

# 서드파티 라이브러리
from unittest.mock import patch


@pytest.mark.django_db
class TestVideoViewSet:
    @patch("videos.views.get_presigned_post")
    def test_admin_can_create_video(
        self, mock_presigned_post, api_client, admin_user, minor_category
    ):
        # Given: 관리자 권한을 가진 사용자가 인증된 상태이다.
        api_client.force_authenticate(user=admin_user)

        # Mock S3 presigned_post 메서드
        mock_presigned_post.return_value = {
            "url": "https://example.com",
            "fields": {"key": "test-video-key.mp4", "Content-Type": "video/mp4"},
        }

        # When: 관리자가 비디오 생성 요청을 보낸다.
        url = reverse("videos:video-list")
        response = api_client.post(
            url, {"name": "New Video", "description": "New Description"}, format="json"
        )

        # Then: 비디오가 성공적으로 생성되고 presigned URL이 반환된다.
        assert response.status_code == 201
        json_response = response.json()
        assert "presigned_post" in json_response
        assert "video_id" in json_response
        assert Video.objects.filter(id=json_response["video_id"]).exists()

    def test_normal_user_cannot_create_video(self, api_client, normal_user):
        # Given: 일반 사용자가 인증된 상태이다.
        api_client.force_authenticate(user=normal_user)

        # When: 일반 사용자가 비디오 생성 요청을 보낸다.
        url = reverse("videos:video-list")
        response = api_client.post(
            url,
            {"name": "Unauthorized Video", "description": "Unauthorized Description"},
            format="json",
        )

        # Then: 요청이 거부되고 403 Forbidden 응답이 반환된다.
        assert response.status_code == 403
        json_response = response.json()
        assert "detail" in json_response

    def test_unauthenticated_user_cannot_create_video(self, api_client):
        # Given: 인증되지 않은 상태이다.

        # When: 인증되지 않은 사용자가 비디오 생성 요청을 보낸다.
        url = reverse("videos:video-list")
        response = api_client.post(
            url,
            {"name": "No Auth Video", "description": "No Auth Description"},
            format="json",
        )

        # Then: 요청이 거부되고 401 Unauthorized 응답이 반환된다.
        assert response.status_code == 401
        json_response = response.json()
        assert "detail" in json_response

    @patch("videos.views.get_presigned_post")
    def test_s3_error_on_video_creation(
        self, mock_presigned_post, api_client, admin_user
    ):
        # Given: 관리자 권한을 가진 사용자가 인증된 상태이고, S3 ClientError가 발생한다.
        api_client.force_authenticate(user=admin_user)

        # S3 ClientError를 시뮬레이션
        mock_presigned_post.side_effect = ClientError(
            {"Error": {"Code": "500", "Message": "S3 Error"}}, "GeneratePresignedPost"
        )

        # When: 관리자가 비디오 생성 요청을 보내고 S3 오류가 발생한다.
        url = reverse("videos:video-list")
        response = api_client.post(
            url,
            {"name": "New Video with Error", "description": "Error Description"},
            format="json",
        )

        # Then: 서버 오류가 발생하고 적절한 에러 메시지가 반환된다.
        assert response.status_code == 500
        json_response = response.json()
        assert "detail" in json_response
        assert json_response["detail"].startswith("S3 URL 생성 중 오류 발생")

    @patch("boto3.client")
    def test_admin_can_delete_video(
        self, mock_boto3_client, api_client, admin_user, video
    ):
        # Given: 관리자 권한을 가진 사용자가 인증된 상태이다.
        api_client.force_authenticate(user=admin_user)

        # Mock S3 delete_object 메서드
        s3_mock = mock_boto3_client.return_value  # S3 클라이언트 모킹 객체 가져오기
        s3_mock.delete_object.return_value = {}  # delete_object 메서드의 반환 값 설정

        # When: 관리자가 비디오 삭제 요청을 보낸다.
        url = reverse("videos:video-detail", args=[video.id])
        response = api_client.delete(url)

        # Then: 비디오가 성공적으로 삭제된다.
        assert response.status_code == 204
        assert not Video.objects.filter(id=video.id).exists()

        # S3 delete_object 메서드가 호출되었는지 확인
        s3_mock.delete_object.assert_called_once_with(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key="test.mp4",  # 실제 객체 키 확인 필요
        )

    def test_normal_user_cannot_delete_video(self, api_client, normal_user, video):
        # Given: 일반 사용자가 인증된 상태이다.
        api_client.force_authenticate(user=normal_user)

        # When: 일반 사용자가 비디오 삭제 요청을 보낸다.
        url = reverse("videos:video-detail", args=[video.id])
        response = api_client.delete(url)

        # Then: 요청이 거부되고 403 Forbidden 응답이 반환된다.
        assert response.status_code == 403
        json_response = response.json()
        assert "detail" in json_response

    def test_unauthenticated_user_cannot_delete_video(self, api_client, video):
        # Given: 인증되지 않은 상태이다.

        # When: 인증되지 않은 사용자가 비디오 삭제 요청을 보낸다.
        url = reverse("videos:video-detail", args=[video.id])
        response = api_client.delete(url)

        # Then: 요청이 거부되고 401 Unauthorized 응답이 반환된다.
        assert response.status_code == 401
        json_response = response.json()
        assert "detail" in json_response

    @patch("boto3.client")
    def test_update_video_with_invalid_url(
        self, mock_boto3_client, api_client, admin_user, video
    ):
        # Given: 관리자 권한을 가진 사용자가 인증된 상태이다.
        api_client.force_authenticate(user=admin_user)
        video.video_url = (
            "https://csysungwons3.s3.amazonaws.com/invalid-url"  # 유효하지 않은 URL
        )
        video.save()

        # Mock S3 delete_object 메서드
        s3_mock = mock_boto3_client.return_value  # S3 클라이언트 모킹 객체
        s3_mock.delete_object.side_effect = ClientError(
            {
                "Error": {
                    "Code": "NoSuchKey",
                    "Message": "The specified key does not exist.",
                }
            },
            "delete_object",
        )  # delete_object 호출 시 예외 발생

        # When: 관리자가 비디오 업데이트 요청을 보낸다.
        url = reverse("videos:video-detail", args=[video.id])
        response = api_client.put(url, {"name": "Updated Video"}, format="json")

        # Then: 서버 오류가 발생하고 적절한 에러 메시지가 반환된다.
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "기존 비디오 삭제 중 오류 발생" in response.json()["detail"]
        assert "The specified key does not exist." in response.json()["detail"]

        # S3 delete_object 메서드가 호출되었는지 확인
        s3_mock.delete_object.assert_called_once_with(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,  # 버킷 이름을 명시적으로 설정
            Key="invalid-url",
        )

    def test_retrieve_nonexistent_video(self, api_client, normal_user):
        # Given: 일반 사용자가 인증된 상태이다.
        api_client.force_authenticate(user=normal_user)

        # When: 존재하지 않는 비디오에 대해 조회 요청을 보낸다.
        url = reverse("videos:video-detail", args=[9999])  # 존재하지 않는 ID 사용
        response = api_client.get(url)

        # Then: 비디오가 존재하지 않으며 404 Not Found가 반환된다.
        assert response.status_code == 404
        json_response = response.json()
        assert "detail" in json_response

    @pytest.mark.parametrize("num_requests", range(5))  # 여러 동시 요청 시뮬레이션
    @patch("videos.views.get_presigned_post")
    def test_concurrent_video_creation(
        self, mock_presigned_post, api_client, admin_user, minor_category, num_requests
    ):
        # Given: 관리자 권한을 가진 사용자가 인증된 상태이다.
        api_client.force_authenticate(user=admin_user)

        # Mock S3 presigned_post 메서드
        mock_presigned_post.return_value = {
            "url": "https://example.com",
            "fields": {"key": "test-video-key.mp4", "Content-Type": "video/mp4"},
        }

        # When: 동시에 여러 비디오 생성 요청을 보낸다.
        url = reverse("videos:video-list")
        response = api_client.post(
            url,
            {"name": f"New Video {num_requests}", "description": "New Description"},
            format="json",
        )

        # Then: 모든 요청이 성공적으로 처리되고 각각의 비디오가 생성된다.
        assert response.status_code == 201
        json_response = response.json()
        assert Video.objects.filter(id=json_response["video_id"]).exists()

    @patch("boto3.client")
    def test_s3_video_file_deleted_on_video_delete(
        self, mock_boto3_client, api_client, admin_user, video
    ):
        # Given: 관리자 권한을 가진 사용자가 인증된 상태이다.
        api_client.force_authenticate(user=admin_user)

        # Mock S3 delete_object 메서드
        s3_mock = mock_boto3_client.return_value
        s3_mock.delete_object.return_value = {}

        # When: 관리자가 비디오 삭제 요청을 보낸다.
        url = reverse("videos:video-detail", args=[video.id])
        response = api_client.delete(url)

        # Then: 비디오가 데이터베이스와 S3에서 성공적으로 삭제된다.
        assert response.status_code == 204
        assert not Video.objects.filter(id=video.id).exists()

        # S3 delete_object 메서드가 호출되었는지 확인
        s3_mock.delete_object.assert_called_once_with(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key="test.mp4",  # 실제로 삭제할 객체의 키
        )

    def test_video_list(self, api_client, normal_user, video_factory):
        # Given: 데이터베이스에 여러 개의 비디오가 존재한다.
        api_client.force_authenticate(user=normal_user)
        video_factory(10)

        # When: 사용자가 비디오 목록 조회 요청을 보낸다.
        url = reverse("videos:video-list")
        response = api_client.get(url)

        # Then: 비디오 목록이 정상적으로 반환된다.
        assert response.status_code == 200
        json_response = response.json()
        assert len(json_response) == 10

    @patch("videos.views.get_presigned_url")
    def test_normal_user_can_access_presigned_url(
        self, mock_presigned_url, api_client, normal_user, video, enrollment
    ):
        # Given: 일반 사용자가 인증된 상태이다.
        api_client.force_authenticate(user=normal_user)

        # Mock S3 presigned_url 메서드
        mock_presigned_url.return_value = "https://example.com/presigned-url"

        # When: 사용자가 비디오 다운로드 URL 요청을 보낸다.
        url = reverse("videos:video-detail", args=[video.id])
        response = api_client.get(url)

        # Then: 사용자는 presigned URL에 접근할 수 있다.
        assert response.status_code == 200

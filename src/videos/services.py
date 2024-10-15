from urllib.parse import urlparse
from uuid import uuid4

from django.conf import settings

import boto3
from botocore.exceptions import ClientError


def get_s3_client():
    """
    S3 클라이언트를 생성하여 반환하는 함수.

    Returns:
        client (boto3.client): S3 클라이언트 객체.
    """
    client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )
    return client


def initiate_multipart_upload():
    """
    멀티파트 업로드를 시작하는 함수. 새로운 파일명을 생성하고, S3에 멀티파트 업로드 요청을 보냅니다.

    Returns:
        upload_id (str): 업로드 식별자.
        filename (str): 업로드할 파일 이름.
    """
    s3_client = get_s3_client()
    filename = str(uuid4()) + ".mp4"
    try:
        response = s3_client.create_multipart_upload(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=filename,
            ContentType="video/mp4",
        )
        upload_id = response["UploadId"]
        return upload_id, filename
    except ClientError as e:
        raise e


def generate_presigned_urls_for_parts(upload_id, filename, total_parts):
    """
    각 파트에 대해 presigned URL을 생성하는 함수.

    Args:
        upload_id (str): 멀티파트 업로드 식별자.
        filename (str): 파일 이름.
        total_parts (int): 총 파트 수.

    Returns:
        presigned_urls (list): 각 파트의 presigned URL 리스트.
    """
    s3_client = get_s3_client()

    presigned_urls = []
    try:
        for part_number in range(1, total_parts + 1):
            presigned_url = s3_client.generate_presigned_url(
                "upload_part",
                Params={
                    "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                    "Key": filename,
                    "UploadId": upload_id,
                    "PartNumber": part_number,
                },
                ExpiresIn=3600,  # presigned URL 유효 시간
            )
            presigned_urls.append(
                {"part_number": part_number, "presigned_url": presigned_url}
            )
        return presigned_urls
    except ClientError as e:
        raise e


def check_multipart_upload_status(upload_id, filename):
    """
    멀티파트 업로드 상태를 확인하는 함수.

    Args:
        upload_id (str): 멀티파트 업로드 식별자.
        filename (str): 파일 이름.

    Returns:
        response (dict): 업로드된 파트에 대한 정보.
    """
    s3_client = get_s3_client()
    try:
        response = s3_client.list_parts(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=filename, UploadId=upload_id
        )
        return response["Parts"]
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchUpload":
            return None
        else:
            raise e


def complete_multipart_upload(upload_id, filename, parts):
    """
    멀티파트 업로드를 완료하는 함수.

    Args:
        upload_id (str): 멀티파트 업로드 식별자.
        filename (str): 파일 이름.
        parts (list): 각 파트에 대한 정보.

    Returns:
        response (dict): 업로드 완료 응답.
    """
    s3_client = get_s3_client()
    try:
        response = s3_client.complete_multipart_upload(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=filename,
            UploadId=upload_id,
            MultipartUpload={"Parts": parts},
        )
        return response
    except ClientError as e:
        raise e


def get_presigned_url(s3_url):
    """
    S3 객체에 대한 presigned URL을 생성하는 함수.

    Args:
        s3_url (str): S3 객체 URL.

    Returns:
        presigned_url (str): presigned URL.
    """
    s3_client = get_s3_client()

    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    parsed_url = urlparse(s3_url)
    object_key = parsed_url.path.lstrip("/")

    try:
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_key},
            ExpiresIn=3600,  # 1시간 동안 유효
        )
        return presigned_url
    except ClientError as e:
        raise e

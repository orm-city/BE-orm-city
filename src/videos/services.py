from uuid import uuid4
import boto3
from botocore.exceptions import ClientError

from django.conf import settings

from urllib.parse import urlparse


# S3 클라이언트 생성 함수
def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )


def get_presigned_post():
    s3_client = get_s3_client()  # 클라이언트 호출

    filename = str(uuid4()) + ".mp4"

    try:
        presigned_post = s3_client.generate_presigned_post(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=filename,
            Fields={"Content-Type": "video/mp4"},
            Conditions=[
                {"Content-Type": "video/mp4"},
                ["content-length-range", 1, 1024 * 1024 * 500],  # 최대 500MB
            ],
            ExpiresIn=120,  # 2분 동안 유효
        )
        return presigned_post
    except ClientError as e:
        raise e


def get_presigned_url(s3_url):
    s3_client = get_s3_client()  # 클라이언트 호출

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

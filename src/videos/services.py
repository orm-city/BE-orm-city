from urllib.parse import urlparse
from uuid import uuid4

from django.conf import settings

import boto3
from botocore.exceptions import ClientError


# service.py
# S3 클라이언트 생성 함수
def get_s3_client():
    client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )
    print(f"S3 client created with region: {settings.AWS_S3_REGION_NAME}")
    return client


def initiate_multipart_upload():
    s3_client = get_s3_client()
    filename = str(uuid4()) + ".mp4"
    print(f"Initiating multipart upload for file: {filename}")
    try:
        print(f"Initiating multipart upload for file: {filename}")
        response = s3_client.create_multipart_upload(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=filename,
            ContentType="video/mp4",
        )
        upload_id = response["UploadId"]
        print(f"Upload started with Upload ID: {upload_id}")
        return upload_id, filename
    except ClientError as e:
        print(f"Error initiating multipart upload: {str(e)}")
        raise e


def generate_presigned_urls_for_parts(upload_id, filename, total_parts):
    """
    각 파트에 대해 presigned URL을 생성합니다.
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
    s3_client = get_s3_client()
    try:
        print(f"Checking status for upload ID: {upload_id}, filename: {filename}")
        response = s3_client.list_parts(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=filename, UploadId=upload_id
        )
        print(f"Successfully retrieved parts for upload ID: {upload_id}")
        return response["Parts"]
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchUpload":
            print(f"Upload {upload_id} not found or expired. Error details: {str(e)}")
        else:
            print(f"Error checking multipart upload status: {str(e)}")
        return None


def complete_multipart_upload(upload_id, filename, parts):
    s3_client = get_s3_client()
    try:
        print(f"Completing upload for Upload ID: {upload_id}, Filename: {filename}")
        print(f"Parts: {parts}")
        response = s3_client.complete_multipart_upload(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=filename,
            UploadId=upload_id,
            MultipartUpload={"Parts": parts},
        )
        return response
    except ClientError as e:
        print(f"Error during complete multipart upload: {e}")
        print(f"Upload ID: {upload_id}, Filename: {filename}, Parts: {parts}")
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

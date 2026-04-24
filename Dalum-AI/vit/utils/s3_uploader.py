import boto3
import os
import cv2
import numpy as np
from botocore.exceptions import NoCredentialsError


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )


def upload_bytes_to_s3(file_bytes, bucket_name, s3_key, content_type=None):
    s3 = get_s3_client()

    try:
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        s3.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=file_bytes,
            **extra_args
        )

        print(f"S3 업로드 완료 (bytes): {s3_key}")

    except NoCredentialsError:
        print("AWS 자격 증명 오류")


def download_image_from_s3(bucket_name, s3_key):
    s3 = get_s3_client()

    try:
        response = s3.get_object(Bucket=bucket_name, Key=s3_key)
        image_bytes = response["Body"].read()

        np_array = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_UNCHANGED)

        return image

    except Exception as e:
        print(f"S3 다운로드 실패: {e}")
        return None
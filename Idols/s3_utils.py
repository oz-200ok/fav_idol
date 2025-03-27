import boto3
from django.conf import settings


def upload_image_to_s3(image_file, s3_key_prefix, instance_id):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION_NAME,
    )
    file_name = image_file.name
    s3_key = f"images/{s3_key_prefix}/{instance_id}/{file_name}"
    try:
        s3_client.upload_fileobj(
            image_file.file, settings.AWS_STORAGE_BUCKET_NAME, s3_key
        )
        image_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_REGION_NAME}.amazonaws.com/{s3_key}"
        return image_url
    except Exception as e:
        print(f"S3 업로드 실패 ({s3_key_prefix}): {e}")
        return None

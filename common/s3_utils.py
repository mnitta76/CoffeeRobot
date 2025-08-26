import boto3
import os

from django.conf import settings

def upload_file_to_s3(file_obj, user, filename_prefix="common"):
    """
    S3にファイルをアップロードし、公開URLを返す共通関数。
    """
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )

    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    file_key = f"{filename_prefix}/{user.username}/{file_obj.name}"

    s3.upload_fileobj(file_obj, bucket_name, file_key)

    response_data = {
        "status_code": 200,
        "status": "success",
        "message": "Uploaded File",
        "filename": file_obj.name,
        "url": f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}",
    }

    return response_data

def download_file_from_s3(file_obj, user, filename_prefix="common"):
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )

    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    file_key = f"{filename_prefix}/{user.username}/{file_obj.name}"
    download_path = os.path.join(settings.MEDIA_ROOT, file_obj.name)

    try:
        s3.download_file(bucket_name, file_key, download_path)
        print(f"✅ ダウンロード成功: {download_path}")
        return  {
            "status_code": 200,
            "status": "success",
            "message": "Downloaded File",
            "filename": file_obj.name,
            "s3_url": f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}",
            "download_path": download_path
        }
    except Exception as e:
        print(f"❌ S3 からのダウンロード失敗: {str(e)}")
        return {
            "status_code": 500,
            "status": "error",
            "message": "Download Error"
        }
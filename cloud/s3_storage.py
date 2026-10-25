from pathlib import Path
import boto3
from botocore.exceptions import ClientError

def upload_file(local_path: str, bucket: str, key: str, region: str | None = None):
    client = boto3.client('s3', region_name=region) if region else boto3.client('s3')
    extra = {'ContentType': 'application/octet-stream'}
    if str(local_path).lower().endswith('.parquet'):
        extra['ContentType'] = 'application/vnd.apache.parquet'
    client.upload_file(local_path, bucket, key, ExtraArgs=extra)

def download_file(bucket: str, key: str, local_path: str, region: str | None = None):
    Path(local_path).parent.mkdir(parents=True, exist_ok=True)
    client = boto3.client('s3', region_name=region) if region else boto3.client('s3')
    client.download_file(bucket, key, local_path)

def object_exists(bucket: str, key: str, region: str | None = None) -> bool:
    client = boto3.client('s3', region_name=region) if region else boto3.client('s3')
    try:
        client.head_object(Bucket=bucket, Key=key)
        return True
    except client.exceptions.ClientError as exc:
        if exc.response.get('Error', {}).get('Code') in {'404', 'NoSuchKey'}:
            return False
        raise


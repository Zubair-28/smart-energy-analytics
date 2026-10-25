from pathlib import Path
import boto3

def upload_file(local_path: str, bucket: str, key: str, region: str | None = None):
    client = boto3.client('s3', region_name=region) if region else boto3.client('s3')
    client.upload_file(local_path, bucket, key)

def download_file(bucket: str, key: str, local_path: str, region: str | None = None):
    Path(local_path).parent.mkdir(parents=True, exist_ok=True)
    client = boto3.client('s3', region_name=region) if region else boto3.client('s3')
    client.download_file(bucket, key, local_path)


import argparse, os, sys
from pathlib import Path
import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

def main():
    p = argparse.ArgumentParser(description='Verify AWS identity and SmartEnergy S3 access without printing secrets.')
    p.add_argument('--bucket', required=True)
    p.add_argument('--region', default=os.getenv('AWS_REGION', 'ap-south-1'))
    p.add_argument('--prefix', default=os.getenv('S3_PREFIX', 'smart-energy-analytics'))
    p.add_argument('--file', default='data/generated/energy_demo.csv')
    a = p.parse_args(); root = Path(__file__).resolve().parents[1]; local = root / a.file
    try:
        sts = boto3.client('sts', region_name=a.region)
        identity = sts.get_caller_identity()
        print(f"AWS identity verified: {identity.get('Arn', 'redacted')}")
        s3 = boto3.client('s3', region_name=a.region)
        s3.head_bucket(Bucket=a.bucket)
        key = f'{a.prefix}/raw/energy_demo.csv'
        s3.upload_file(str(local), a.bucket, key)
        s3.head_object(Bucket=a.bucket, Key=key)
        print(f'Upload verified: s3://{a.bucket}/{key}')
        print('Required permissions: sts:GetCallerIdentity, s3:HeadBucket, s3:PutObject, s3:HeadObject')
    except (NoCredentialsError, BotoCoreError, ClientError) as exc:
        print(f'AWS verification failed: {type(exc).__name__}: {exc}', file=sys.stderr); raise SystemExit(1)

if __name__ == '__main__': main()

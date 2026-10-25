import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse
from cloud.s3_storage import upload_file, download_file
from config.settings import AWS_REGION, S3_BUCKET, S3_PREFIX, ROOT
p=argparse.ArgumentParser(); p.add_argument('action', choices=['upload','download']); p.add_argument('--bucket', default=S3_BUCKET); p.add_argument('--key', default=f'{S3_PREFIX}/raw/energy_demo.csv'); p.add_argument('--file', default='data/generated/energy_demo.csv'); a=p.parse_args()
if not a.bucket: raise SystemExit('Set S3_BUCKET in .env or pass --bucket.')
if a.action == 'upload': upload_file(str(ROOT/a.file), a.bucket, a.key, AWS_REGION); print(f'Uploaded s3://{a.bucket}/{a.key}')
else: download_file(a.bucket, a.key, str(ROOT/a.file), AWS_REGION); print(f'Downloaded to {ROOT/a.file}')


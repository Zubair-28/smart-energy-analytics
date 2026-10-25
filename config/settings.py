from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')
DATA_PATH = Path(os.getenv('DATA_PATH', 'data/generated/energy_demo.csv'))
if not DATA_PATH.is_absolute(): DATA_PATH = ROOT / DATA_PATH
OUTPUT_DIR = ROOT / 'outputs'
AWS_REGION = os.getenv('AWS_REGION', 'ap-south-1')
S3_BUCKET = os.getenv('S3_BUCKET', '')
S3_PREFIX = os.getenv('S3_PREFIX', 'smart-energy-analytics')


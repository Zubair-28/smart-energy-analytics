import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse, json
from processing.pipeline import run_pipeline
parser = argparse.ArgumentParser(); parser.add_argument('--input', default='data/generated/energy_demo.csv'); parser.add_argument('--output', default='outputs'); args = parser.parse_args()
path = args.input
if path.startswith('s3://'): raise SystemExit('S3 input download should be performed with scripts/sync_s3.py first or use a mounted/local path.')
print(json.dumps(run_pipeline(path, args.output), indent=2))


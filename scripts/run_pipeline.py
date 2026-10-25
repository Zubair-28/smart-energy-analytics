import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse, json
import os
from processing.pipeline import run_pipeline
parser = argparse.ArgumentParser(); parser.add_argument('--input', default='data/generated/energy_demo.csv'); parser.add_argument('--output', default='outputs'); args = parser.parse_args()
path = args.input
if path.startswith('s3://'): raise SystemExit('S3 input download should be performed with scripts/sync_s3.py first or use a mounted/local path.')
# Prefer the verified Java 17 runtime bundled with Tableau when it exists.
java17 = Path(r'C:\Program Files\Tableau\Tableau Public 2026.2\bin\jre')
if java17.exists() and 'JAVA_HOME' not in os.environ:
    os.environ['JAVA_HOME'] = str(java17)
    os.environ['PATH'] = str(java17 / 'bin') + os.pathsep + os.environ.get('PATH', '')
print(json.dumps(run_pipeline(path, args.output), indent=2))


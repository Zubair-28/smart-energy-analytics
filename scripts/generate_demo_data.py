import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse
from processing.pipeline import generate_demo
parser = argparse.ArgumentParser(); parser.add_argument('--days', type=int, default=60); parser.add_argument('--entities', type=int, default=12); parser.add_argument('--output', default='data/generated/energy_demo.csv')
args = parser.parse_args(); print(generate_demo(Path(args.output), args.days, args.entities))


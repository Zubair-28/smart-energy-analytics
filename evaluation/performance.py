import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse, json, time
import pandas as pd
from processing.pipeline import generate_demo, run_pipeline

def benchmark(output: str, sizes=(1000, 10000, 100000)):
    root = Path(output); root.mkdir(parents=True, exist_ok=True); results=[]
    for rows in sizes:
        days = max(2, (rows // 24) + 1)
        path = root / f'benchmark_{rows}.csv'
        generate_demo(path, days=days, entities=max(1, rows // (days*24)))
        actual = len(pd.read_csv(path))
        start = time.perf_counter(); meta = run_pipeline(path, root / f'run_{rows}')
        elapsed = time.perf_counter()-start
        results.append({'requested_records': rows, 'actual_records': actual, 'duration_seconds': round(elapsed, 4), 'throughput_records_per_second': round(actual/elapsed, 2), 'engine': meta['engine']})
    (root/'performance.json').write_text(json.dumps(results, indent=2), encoding='utf-8'); return results

if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output', default='outputs/performance'); a=p.parse_args(); print(json.dumps(benchmark(a.output), indent=2))


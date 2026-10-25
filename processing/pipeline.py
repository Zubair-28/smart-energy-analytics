from __future__ import annotations
import json, time
from pathlib import Path
import numpy as np
import pandas as pd

REQUIRED = {'timestamp', 'entity_id', 'consumption_kwh'}

def generate_demo(path: str | Path, days: int = 60, entities: int = 12, seed: int = 7) -> Path:
    rng = np.random.default_rng(seed)
    idx = pd.date_range('2025-01-01', periods=days * 24, freq='h', tz='UTC')
    rows = []
    for e in range(1, entities + 1):
        base = 0.8 + e * 0.08
        for ts in idx:
            hour = ts.hour
            daily = 0.45 * np.sin((hour - 7) * np.pi / 12) + 0.55
            evening = 0.65 if 18 <= hour <= 22 else 0
            weekend = 0.85 if ts.dayofweek >= 5 else 1.0
            value = max(0.05, base * (daily + evening) * weekend + rng.normal(0, 0.10))
            rows.append((ts.isoformat(), f'building-{e:02d}', round(float(value), 4)))
    df = pd.DataFrame(rows, columns=['timestamp', 'entity_id', 'consumption_kwh'])
    # Known synthetic anomalies make detector evaluation reproducible.
    for day, ent, multiplier in [(10, 'building-03', 5), (31, 'building-08', 6), (45, 'building-03', 4)]:
        mask = (df.timestamp.str.startswith(f'2025-01-{day+1:02d}')) & (df.entity_id == ent)
        df.loc[mask, 'consumption_kwh'] *= multiplier
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True); df.to_csv(path, index=False); return path

def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    missing = sorted(REQUIRED - set(df.columns))
    if missing: raise ValueError(f'Missing required columns: {missing}')
    before = len(df)
    out = df.copy()
    out['timestamp'] = pd.to_datetime(out['timestamp'], errors='coerce', utc=True)
    out['consumption_kwh'] = pd.to_numeric(out['consumption_kwh'], errors='coerce')
    invalid = int(out[['timestamp','entity_id','consumption_kwh']].isna().any(axis=1).sum())
    out = out.dropna(subset=['timestamp','entity_id','consumption_kwh']).drop_duplicates()
    out['hour'] = out.timestamp.dt.hour
    out['day'] = out.timestamp.dt.date.astype(str)
    out['month'] = out.timestamp.dt.to_period('M').astype(str)
    out['day_of_week'] = out.timestamp.dt.day_name()
    out['is_weekend'] = out.timestamp.dt.dayofweek >= 5
    meta = {'input_records': before, 'processed_records': len(out), 'invalid_records': invalid,
            'duplicate_records_removed': before - invalid - len(out), 'missing_values': int(df.isna().sum().sum())}
    return out, meta

def run_pipeline(input_path: str | Path, output_dir: str | Path) -> dict:
    started = time.perf_counter(); engine = 'pandas-fallback'
    try:
        from pyspark.sql import SparkSession
        spark = SparkSession.builder.master('local[*]').appName('SmartEnergyAnalytics').getOrCreate()
        raw = spark.read.option('header', True).option('inferSchema', True).csv(str(input_path))
        df = raw.toPandas(); spark.stop(); engine = 'pyspark'
    except Exception:
        df = pd.read_csv(input_path)
    clean, quality = clean_data(df)
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    clean.to_csv(out / 'cleaned.csv', index=False)
    clean.groupby('hour', as_index=False).consumption_kwh.agg(['sum','mean','max']).reset_index().to_csv(out/'hourly.csv', index=False)
    clean.groupby('day', as_index=False).consumption_kwh.agg(['sum','mean','max']).reset_index().to_csv(out/'daily.csv', index=False)
    clean.groupby('month', as_index=False).consumption_kwh.agg(['sum','mean','max']).reset_index().to_csv(out/'monthly.csv', index=False)
    clean.groupby('entity_id', as_index=False).consumption_kwh.agg(['sum','mean','max']).reset_index().to_csv(out/'entities.csv', index=False)
    quality.update({'engine': engine, 'duration_seconds': round(time.perf_counter()-started, 4), 'dataset_path': str(input_path)})
    (out/'quality.json').write_text(json.dumps(quality, indent=2), encoding='utf-8')
    return quality


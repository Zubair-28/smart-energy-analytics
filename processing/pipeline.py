from __future__ import annotations
import json, time
from pathlib import Path
import numpy as np
import pandas as pd

REQUIRED = {'timestamp', 'entity_id', 'consumption_kwh'}
EXPECTED_ENTITY_PATTERN = r'^building-[0-9]+$'

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
    missing_required = int(out[list(REQUIRED)].isna().any(axis=1).sum())
    invalid_timestamps = int(out['timestamp'].isna().sum())
    invalid_consumption = int(out['consumption_kwh'].isna().sum() + (out['consumption_kwh'] < 0).fillna(False).sum())
    unexpected_entities = int((~out['entity_id'].astype('string').str.match(EXPECTED_ENTITY_PATTERN, na=False)).sum())
    duplicate_records = int(out.duplicated().sum())
    invalid_mask = (out['timestamp'].isna() | out['entity_id'].isna() |
                    out['consumption_kwh'].isna() | (out['consumption_kwh'] < 0))
    out = out.loc[~invalid_mask].drop_duplicates()
    out['hour'] = out.timestamp.dt.hour
    out['day'] = out.timestamp.dt.date.astype(str)
    out['month'] = out.timestamp.dt.to_period('M').astype(str)
    out['day_of_week'] = out.timestamp.dt.day_name()
    out['is_weekend'] = out.timestamp.dt.dayofweek >= 5
    meta = {'input_records': before, 'processed_records': len(out),
            'invalid_records': int(invalid_mask.sum()), 'records_removed': before - len(out),
            'duplicate_records_detected': duplicate_records, 'duplicate_records_removed': duplicate_records,
            'invalid_timestamps': invalid_timestamps, 'invalid_consumption_values': invalid_consumption,
            'unexpected_entity_ids': unexpected_entities, 'missing_required_records': missing_required,
            'missing_values': int(df.isna().sum().sum()), 'required_fields': sorted(REQUIRED),
            'quality_status': 'passed' if before == len(out) else 'issues_detected'}
    return out, meta

def run_pipeline(input_path: str | Path, output_dir: str | Path) -> dict:
    started = time.perf_counter(); engine = 'pandas-fallback'; engine_error = None
    try:
        from pyspark.sql import SparkSession
        spark = SparkSession.builder.master('local[*]').appName('SmartEnergyAnalytics').getOrCreate()
        raw = spark.read.option('header', True).option('inferSchema', True).csv(str(input_path))
        # Perform ingestion, type coercion, invalid-row filtering and
        # de-duplication in Spark before collecting the bounded demo frame.
        from pyspark.sql import functions as F
        spark_df = (raw.withColumn('timestamp', F.to_timestamp('timestamp'))
                    .withColumn('consumption_kwh', F.col('consumption_kwh').cast('double'))
                    .dropna(subset=['timestamp', 'entity_id', 'consumption_kwh'])
                    .filter(F.col('consumption_kwh') >= 0).dropDuplicates())
        df = spark_df.toPandas(); spark.stop(); engine = 'pyspark'
    except Exception as exc:
        engine_error = f'{type(exc).__name__}: {exc}'
        df = pd.read_csv(input_path)
    clean, quality = clean_data(df)
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    clean.to_csv(out / 'cleaned.csv', index=False)
    try:
        clean.to_parquet(out / 'cleaned.parquet', index=False)
        quality_parquet = True
    except (ImportError, ValueError):
        quality_parquet = False
    clean.groupby('hour', as_index=False).consumption_kwh.agg(['sum','mean','max']).reset_index().to_csv(out/'hourly.csv', index=False)
    clean.groupby('day', as_index=False).consumption_kwh.agg(['sum','mean','max']).reset_index().to_csv(out/'daily.csv', index=False)
    clean.groupby('month', as_index=False).consumption_kwh.agg(['sum','mean','max']).reset_index().to_csv(out/'monthly.csv', index=False)
    clean.groupby('entity_id', as_index=False).consumption_kwh.agg(['sum','mean','max']).reset_index().to_csv(out/'entities.csv', index=False)
    quality.update({'engine': engine, 'engine_error': engine_error, 'duration_seconds': round(time.perf_counter()-started, 4),
                    'dataset_path': str(input_path), 'processing_status': 'completed', 'parquet_written': quality_parquet})
    (out/'quality.json').write_text(json.dumps(quality, indent=2), encoding='utf-8')
    return quality


# SmartEnergy Analytics

A cloud-ready, PySpark-first platform for electricity consumption analytics, anomaly detection, demand forecasting, and data-quality reporting.

## Current implementation

- Reproducible demo dataset generator with clearly labeled synthetic records.
- PySpark processing path when `pyspark` is installed, with a local pandas fallback for development environments where Spark is unavailable.
- Hourly/daily/monthly analytics, entity comparisons, transparent rolling z-score anomaly detection, and a chronological baseline forecast.
- Streamlit dashboard with overview, analytics, anomaly monitor, forecast, insights, and quality/performance pages.
- Optional S3 upload/download integration using AWS's normal credential provider chain.
- CSV exports and JSON processing metadata.
- Unit tests for cleaning, analytics, anomaly detection, and forecasting.

## Quick start (Windows PowerShell)

```powershell
cd "$env:USERPROFILE\OneDrive\Desktop\smart-energy-analytics"
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\generate_demo_data.py --days 60 --entities 12
.\.venv\Scripts\python.exe scripts\run_pipeline.py
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Or run the complete local setup and validation in one command:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup_windows.ps1
```

Install PySpark when a Java runtime is available:

```powershell
.\.venv\Scripts\python.exe -m pip install pyspark
```

The fallback is not presented as distributed execution. Pipeline metadata records which engine actually ran.

On Windows, the pipeline automatically prefers the Java 17 runtime bundled with Tableau when available. If local Spark cannot create its loopback event channel because of host security/network policy, the run records the Spark exception and continues with the explicitly labeled pandas fallback.

## AWS S3

Copy `.env.example` to `.env`, set `S3_BUCKET`, and authenticate with AWS CLI/profile or environment credentials. Then run:

```powershell
.\.venv\Scripts\python.exe scripts\sync_s3.py upload
.\.venv\Scripts\python.exe scripts\run_pipeline.py --input s3://YOUR_BUCKET/smart-energy-analytics/raw/energy_demo.csv
```

The application never hard-codes credentials. S3 execution is only claimed after a real command succeeds.

See `docs/aws_setup.md` and run `py scripts/cloud_check.py --bucket YOUR_BUCKET` to verify the real S3 upload round trip.

## Dataset provenance

The included demo data is synthetic and is used only to make the application immediately demonstrable. It is not represented as smart-meter measurements. For an academic run, replace it with a public dataset and record its source, license, schema, time resolution, and cleaning decisions in `docs/dataset.md`.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## GitHub

The requested repository name is `smart-energy-analytics` under `Zubair-28`, private by default. GitHub CLI is not installed in the current environment, so repository creation/push remains a documented next step rather than an unverified claim.


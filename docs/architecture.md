# Architecture

The pipeline is: source CSV or S3 raw object -> schema validation and cleaning -> PySpark DataFrame transformations when PySpark is available -> CSV/Parquet-compatible analytical outputs -> Streamlit/Plotly dashboard. The local fallback exists only for environments without Java/Spark and is recorded in `outputs/quality.json`.

AWS S3 is organized under `smart-energy-analytics/raw`, `processed`, `analytics`, and `reports`. Credentials come from boto3's standard provider chain. No credentials are stored in this repository.


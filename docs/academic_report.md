# SmartEnergy Analytics

## Abstract

SmartEnergy Analytics is a cloud-ready Big Data Analytics platform for electricity-consumption analysis, candidate anomaly detection, historical-baseline demand forecasting, and data-quality reporting. The implementation uses Python, PySpark as the intended distributed engine, AWS S3 integration through boto3, and a Streamlit dashboard with Plotly visualizations. A reproducible synthetic dataset makes the demonstration runnable without misrepresenting generated values as real measurements.

## Problem statement

Large electricity datasets contain useful patterns but make manual comparison, peak identification, anomaly review, and demand estimation difficult. The project provides a repeatable processing and visualization workflow for historical records.

## Objectives and scope

The system validates and cleans timestamped consumption records, derives calendar features, aggregates usage by time and entity, flags statistically unusual observations, evaluates a simple forecast, presents actual outputs, and exports results. Real-time meter control, guaranteed savings, and live streaming remain outside scope.

## Architecture

Raw CSV or S3 object → schema validation and cleaning → PySpark DataFrame processing when the host supports it → processed summaries → analytics modules → Streamlit dashboard and exports. S3 keys follow `smart-energy-analytics/raw`, `processed`, `analytics`, and `reports`. Credentials use boto3's standard provider chain.

## Dataset and ethics

The bundled demo is synthetic, hourly, UTC-based, and generated for building entities. It contains documented injected spikes to exercise the detector. It is not a public smart-meter dataset and must not be presented as real measurements. An academic submission should substitute a public dataset and record its source, license, schema, resolution, missingness, and semantic treatment of negative readings.

## Methods

Cleaning parses UTC timestamps, coerces numeric consumption, removes malformed required rows and exact duplicates, and derives hour, date, month, weekday, and weekend fields. Aggregations produce hourly, daily, monthly, and entity summaries. The anomaly detector compares each entity's reading with a prior rolling mean and standard deviation. A zero-variance baseline treats a non-zero deviation as a candidate anomaly. Forecasting uses a chronological holdout and the mean of the previous seven daily totals. MAE and RMSE measure the test error.

## Results from the included demonstration

The checked demo run processed 2,016 records with zero invalid records, zero duplicate removals, and zero missing values. The benchmark runner records measured local throughput for approximately 1,000, 10,000, and 100,000 synthetic records. These figures describe the pandas fallback run in this environment; they are not claims about distributed Spark performance.

## Testing and limitations

The automated suite covers cleaning, anomaly detection, and forecasting, with 3 tests passing in the validated run. Streamlit responded with HTTP 200. Spark is installed, but local Spark startup is blocked by the host's Windows loopback/Java environment; the pipeline records the exception and uses the labeled fallback. S3 was implemented but not exercised because no bucket or AWS credentials were supplied.

## Future work

Use a public dataset, validate a real S3 round trip, run Spark on a supported local or cloud environment, persist processed Parquet outputs, add labeled anomaly evaluation, and compare local and cloud execution under documented conditions.


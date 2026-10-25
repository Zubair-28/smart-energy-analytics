# Methodology

Cleaning parses UTC timestamps, coerces numeric consumption, removes malformed required fields and exact duplicates, and derives hour/day/month/weekend features. Anomalies use a transparent per-entity rolling mean and standard deviation over prior observations; flagged readings are candidates, not confirmed faults. Forecasting uses a chronological holdout and a seven-day historical mean baseline, reporting MAE and RMSE. No results are hard-coded; they are generated from the processed data.


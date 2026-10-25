import pandas as pd
from analytics.models import anomalies, forecast

def test_anomaly_detector_flags_spike():
    ts = pd.date_range('2025-01-01', periods=50, freq='h', tz='UTC')
    df = pd.DataFrame({'timestamp': ts, 'entity_id': 'a', 'consumption_kwh': [1.0]*49+[20.0]})
    assert len(anomalies(df, window=12, z_threshold=3)) >= 1

def test_forecast_has_metrics():
    daily = pd.DataFrame({'day': pd.date_range('2025-01-01', periods=21), 'sum': range(21), 'mean': range(21), 'max': range(21)})
    result, metrics = forecast(daily, 7)
    assert metrics['mae'] >= 0 and len(result) == 14


import numpy as np
import pandas as pd

def anomalies(df: pd.DataFrame, window: int = 24, z_threshold: float = 3.0) -> pd.DataFrame:
    x = df.sort_values(['entity_id','timestamp']).copy()
    g = x.groupby('entity_id', group_keys=False)['consumption_kwh']
    x['expected_kwh'] = g.transform(lambda s: s.shift(1).rolling(window, min_periods=8).mean())
    x['std_kwh'] = g.transform(lambda s: s.shift(1).rolling(window, min_periods=8).std())
    deviation = (x.consumption_kwh - x.expected_kwh).abs()
    # A flat baseline has zero variance; any non-zero deviation is then a
    # candidate anomaly rather than being silently discarded.
    x['anomaly_score'] = (deviation / x.std_kwh.replace(0, np.nan)).abs()
    x.loc[(x.std_kwh == 0) & (deviation > 0), 'anomaly_score'] = np.inf
    return x[x.anomaly_score >= z_threshold].copy()

def forecast(daily: pd.DataFrame, horizon: int = 7) -> tuple[pd.DataFrame, dict]:
    x = daily.sort_values('day').copy(); x['day'] = pd.to_datetime(x['day'])
    values = x['sum'].astype(float).to_numpy()
    if len(values) < 14: raise ValueError('At least 14 daily observations are required for forecasting')
    split = max(7, len(values)-horizon); train, test = values[:split], values[split:]
    baseline = np.repeat(train[-7:].mean(), len(test))
    seasonal = np.array([train[i-7] for i in range(split, len(values))])
    baseline_mae = float(np.mean(np.abs(test-baseline))); baseline_rmse = float(np.sqrt(np.mean((test-baseline)**2)))
    seasonal_mae = float(np.mean(np.abs(test-seasonal))); seasonal_rmse = float(np.sqrt(np.mean((test-seasonal)**2)))
    future_days = pd.date_range(x.day.iloc[-1] + pd.Timedelta(days=1), periods=horizon)
    baseline_future = np.repeat(values[-7:].mean(), horizon)
    seasonal_future = np.resize(values[-7:], horizon)
    pred = pd.DataFrame({'day': future_days, 'baseline_forecast_kwh': baseline_future,
                         'seasonal_naive_kwh': seasonal_future, 'kind': 'forecast'})
    actual = pd.DataFrame({'day': x.day.iloc[split:], 'predicted_kwh': baseline, 'actual_kwh': test, 'kind': 'test'})
    return pd.concat([actual, pred], ignore_index=True), {'mae': baseline_mae, 'rmse': baseline_rmse,
        'baseline_mae': baseline_mae, 'baseline_rmse': baseline_rmse,
        'seasonal_naive_mae': seasonal_mae, 'seasonal_naive_rmse': seasonal_rmse, 'horizon_days': horizon,
        'test_records': len(test), 'evaluation': 'chronological holdout; no future observations used'}

def insights(clean: pd.DataFrame) -> list[str]:
    daily = clean.groupby('day').consumption_kwh.sum()
    peak = daily.idxmax(); entity = clean.groupby('entity_id').consumption_kwh.sum().idxmax()
    return [f'Peak total consumption occurred on {peak}.', f'{entity} had the highest total consumption in the selected data.', f'Average daily consumption was {daily.mean():.2f} kWh.']


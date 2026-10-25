import pandas as pd
from processing.pipeline import clean_data

def test_cleaning_parses_and_removes_invalid():
    df = pd.DataFrame({'timestamp':['2025-01-01T00:00:00Z','bad'], 'entity_id':['a','b'], 'consumption_kwh':['1.2','x']})
    clean, meta = clean_data(df)
    assert len(clean) == 1 and meta['invalid_records'] == 1


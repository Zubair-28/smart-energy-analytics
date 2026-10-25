from pathlib import Path
import json
import pandas as pd
import streamlit as st
import plotly.express as px
from config.settings import ROOT, DATA_PATH, OUTPUT_DIR
from processing.pipeline import generate_demo, run_pipeline, clean_data
from analytics.models import anomalies, forecast, insights

st.set_page_config(page_title='SmartEnergy Analytics', page_icon='⚡', layout='wide')
st.title('⚡ SmartEnergy Analytics')
st.caption('PySpark-first electricity analytics with transparent local fallback and AWS-ready storage.')

if not DATA_PATH.exists():
    # Streamlit Community Cloud does not receive local ignored data files or
    # the private .env file. Generate the documented demo dataset on first run
    # so a fresh deployment is immediately usable without AWS credentials.
    if DATA_PATH.name == 'energy_demo.csv':
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        generate_demo(DATA_PATH)
    else:
        if st.button('Generate documented synthetic demo data'):
            generate_demo(DATA_PATH); st.rerun()
        st.info(f'No input data found at {DATA_PATH}. Generate the demo dataset or set DATA_PATH in .env.'); st.stop()
if not (OUTPUT_DIR/'quality.json').exists(): run_pipeline(DATA_PATH, OUTPUT_DIR)
clean = pd.read_csv(OUTPUT_DIR/'cleaned.csv', parse_dates=['timestamp'])
quality = json.loads((OUTPUT_DIR/'quality.json').read_text())
daily = pd.read_csv(OUTPUT_DIR/'daily.csv'); entities = pd.read_csv(OUTPUT_DIR/'entities.csv'); hourly = pd.read_csv(OUTPUT_DIR/'hourly.csv')
page = st.sidebar.radio('Navigate', ['Energy overview','Consumption analytics','Anomaly monitor','Demand forecast','Energy insights','Data quality'])
if page == 'Energy overview':
    c1,c2,c3,c4 = st.columns(4); c1.metric('Total consumption', f"{clean.consumption_kwh.sum():,.1f} kWh"); c2.metric('Average daily', f"{daily['sum'].mean():,.1f} kWh"); c3.metric('Entities', clean.entity_id.nunique()); c4.metric('Records', f"{len(clean):,}")
    st.plotly_chart(px.line(daily, x='day', y='sum', title='Daily consumption'), use_container_width=True)
elif page == 'Consumption analytics':
    a,b = st.columns(2); a.plotly_chart(px.bar(hourly, x='hour', y='sum', title='Hourly profile'), use_container_width=True); b.plotly_chart(px.bar(entities.sort_values('sum', ascending=False), x='entity_id', y='sum', title='Entity comparison'), use_container_width=True)
    st.plotly_chart(px.line(daily, x='day', y='mean', title='Daily average reading'), use_container_width=True)
elif page == 'Anomaly monitor':
    flagged = anomalies(clean); st.metric('Candidate anomalies', len(flagged)); st.caption('Statistical candidates require domain investigation; they are not confirmed faults or theft.')
    st.dataframe(flagged[['timestamp','entity_id','consumption_kwh','expected_kwh','anomaly_score']].sort_values('anomaly_score', ascending=False), use_container_width=True)
elif page == 'Demand forecast':
    result, metrics = forecast(daily); st.write(metrics); hist = daily.assign(day=pd.to_datetime(daily.day), actual_kwh=daily['sum']); chart = px.line(hist, x='day', y='actual_kwh', title='Historical demand and baseline forecast'); chart.add_scatter(x=result[result.kind=='forecast'].day, y=result[result.kind=='forecast'].predicted_kwh, name='Forecast'); st.plotly_chart(chart, use_container_width=True)
elif page == 'Energy insights':
    for item in insights(clean): st.success(item)
elif page == 'Data quality':
    st.json(quality); st.download_button('Download cleaned CSV', clean.to_csv(index=False), 'cleaned.csv', 'text/csv'); st.download_button('Download quality JSON', json.dumps(quality, indent=2), 'quality.json', 'application/json')

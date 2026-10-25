from pathlib import Path
import json
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
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
    st.plotly_chart(px.line(daily, x='day', y='sum', title='Daily total consumption', labels={'day':'Date','sum':'Consumption (kWh)'}), use_container_width=True)
elif page == 'Consumption analytics':
    a,b = st.columns(2); a.plotly_chart(px.bar(hourly, x='hour', y='sum', title='Hourly total profile', labels={'hour':'Hour of day','sum':'Consumption (kWh)'}), use_container_width=True); b.plotly_chart(px.bar(entities.sort_values('sum', ascending=False), x='entity_id', y='sum', title='Building total comparison', labels={'entity_id':'Building','sum':'Consumption (kWh)'}), use_container_width=True)
    st.plotly_chart(px.line(daily, x='day', y='mean', title='Daily average reading per record', labels={'day':'Date','mean':'Average reading (kWh)'}), use_container_width=True)
elif page == 'Anomaly monitor':
    c1,c2,c3 = st.columns(3); selected_entity = c1.selectbox('Building', ['All'] + sorted(clean.entity_id.unique().tolist())); min_date = c2.date_input('From', pd.to_datetime(clean.day).min().date()); max_date = c3.date_input('To', pd.to_datetime(clean.day).max().date())
    view = clean[(pd.to_datetime(clean.day).dt.date >= min_date) & (pd.to_datetime(clean.day).dt.date <= max_date)]
    if selected_entity != 'All': view = view[view.entity_id == selected_entity]
    scored = anomalies(view); st.metric('Candidate anomalies', len(scored)); st.caption('Candidates use a trailing 24-reading mean and standard deviation per building. They require investigation and are not confirmed faults, theft, or wastage.')
    chart = go.Figure(); chart.add_trace(go.Scatter(x=view.timestamp, y=view.consumption_kwh, name='Actual consumption (kWh)')); chart.add_trace(go.Scatter(x=scored.timestamp, y=scored.expected_kwh, mode='markers', name='Expected at anomaly', marker={'color':'red','size':9})); chart.update_layout(title='Actual consumption and detected candidates', xaxis_title='Timestamp', yaxis_title='Consumption (kWh)'); st.plotly_chart(chart, use_container_width=True)
    cols = ['timestamp','entity_id','consumption_kwh','expected_kwh','anomaly_score']; st.dataframe(scored[cols].sort_values('anomaly_score', ascending=False), use_container_width=True); st.download_button('Download filtered anomalies CSV', scored[cols].to_csv(index=False), 'filtered_anomalies.csv', 'text/csv')
elif page == 'Demand forecast':
    result, metrics = forecast(daily); st.write(metrics); st.caption('Both methods are evaluated on a chronological holdout. The forecast horizon begins after the last observed date.')
    hist = daily.assign(day=pd.to_datetime(daily.day), actual_kwh=daily['sum']); chart = px.line(hist, x='day', y='actual_kwh', title='Historical demand and future forecasts', labels={'day':'Date','actual_kwh':'Consumption (kWh)'}); future = result[result.kind=='forecast']; chart.add_scatter(x=future.day, y=future.baseline_forecast_kwh, name='7-day mean forecast'); chart.add_scatter(x=future.day, y=future.seasonal_naive_kwh, name='Seasonal-naive forecast'); st.plotly_chart(chart, use_container_width=True)
elif page == 'Energy insights':
    for item in insights(clean): st.success(item)
elif page == 'Data quality':
    st.write(f"Processing engine: **{quality.get('engine', 'unknown')}**"); st.write(f"Status: **{quality.get('processing_status', 'unknown')}** | Duration: **{quality.get('duration_seconds', 0):.4f} seconds** | Source: `{quality.get('dataset_path', DATA_PATH)}`")
    if quality.get('engine_error'): st.warning(f"PySpark was unavailable; pandas fallback was used. Diagnostic: {quality['engine_error']}")
    st.json(quality); st.download_button('Download cleaned CSV', clean.to_csv(index=False), 'cleaned.csv', 'text/csv'); st.download_button('Download quality JSON', json.dumps(quality, indent=2), 'quality.json', 'application/json')

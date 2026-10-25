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
st.markdown('''
<style>
    :root { --navy:#12233f; --navy-2:#1b3155; --teal:#0f8b8d; --teal-soft:#dff4f1; --amber:#d99124; --coral:#c65d5d; --ink:#17243a; --muted:#66758a; --surface:#fffdf8; --line:#d9e2e8; }
    .stApp { background: linear-gradient(135deg, #eef4f6 0%, #f8f5ee 58%, #e9f1f1 100%); color: var(--ink); }
    [data-testid="stHeader"] { background: rgba(18,35,63,.96); }
    [data-testid="stToolbar"] { color: #ffffff; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #12233f 0%, #1b3155 58%, #12233f 100%); border-right: 1px solid #365275; box-shadow: 8px 0 24px rgba(18,35,63,.12); }
    [data-testid="stSidebar"] * { color: #f4f1e9; }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1.25rem; }
    [data-testid="stSidebar"] .stRadio > label { color: #a9bdd0; font-size: .68rem; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; margin: 1.35rem .75rem .6rem; }
    [data-testid="stSidebar"] [data-baseweb="radio"] { position: relative; margin: .34rem 0; padding: .72rem .78rem; border: 1px solid transparent; border-radius: 11px; transition: background .22s ease, transform .22s ease, box-shadow .22s ease, border-color .22s ease; cursor: pointer; }
    [data-testid="stSidebar"] [data-baseweb="radio"]:hover { background: rgba(127,226,213,.12); transform: translateX(5px); box-shadow: 0 5px 14px rgba(0,0,0,.12); }
    [data-testid="stSidebar"] [data-baseweb="radio"]:active { transform: translateX(3px) scale(.985); }
    [data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) { background: linear-gradient(100deg, rgba(15,139,141,.42), rgba(15,139,141,.10)); border-color: rgba(127,226,213,.24); box-shadow: inset 4px 0 0 #7fe2d5, 0 7px 18px rgba(0,0,0,.16); }
    [data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) label { color: #ffffff; font-weight: 750; }
    [data-testid="stSidebar"] [data-baseweb="radio"] label { transition: color .22s ease, letter-spacing .22s ease; }
    [data-testid="stSidebar"] [data-baseweb="radio"]:hover label { color: #7fe2d5; letter-spacing: .01em; }
    [data-testid="stSidebar"] [data-baseweb="radio"] div:first-child { display: none; }
    [data-testid="stSidebar"] [data-baseweb="radio"] label { display: flex; align-items: center; gap: .68rem; width: 100%; }
    [data-testid="stSidebar"] [data-baseweb="radio"] label::before { display: inline-flex; align-items: center; justify-content: center; width: 1.55rem; height: 1.55rem; border-radius: 8px; background: rgba(255,255,255,.08); color: #a9bdd0; font-size: .9rem; transition: background .22s ease, color .22s ease, transform .22s ease; }
    [data-testid="stSidebar"] [data-baseweb="radio"]:nth-of-type(1) label::before { content: '⌂'; }
    [data-testid="stSidebar"] [data-baseweb="radio"]:nth-of-type(2) label::before { content: '▥'; }
    [data-testid="stSidebar"] [data-baseweb="radio"]:nth-of-type(3) label::before { content: '!'; }
    [data-testid="stSidebar"] [data-baseweb="radio"]:nth-of-type(4) label::before { content: '↗'; }
    [data-testid="stSidebar"] [data-baseweb="radio"]:nth-of-type(5) label::before { content: '✦'; }
    [data-testid="stSidebar"] [data-baseweb="radio"]:nth-of-type(6) label::before { content: '✓'; }
    [data-testid="stSidebar"] [data-baseweb="radio"]:hover label::before { background: rgba(127,226,213,.17); color: #7fe2d5; transform: scale(1.08); }
    [data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) label::before { background: #7fe2d5; color: #12233f; transform: scale(1.06); }
    [data-testid="stSidebar"] [data-testid="stTextInput"] { margin: 1rem .75rem 0; }
    [data-testid="stSidebar"] [data-testid="stTextInput"] input { background: rgba(0,0,0,.15) !important; border: 1px solid rgba(127,226,213,.15) !important; color: #f4f1e9 !important; padding-left: 2.15rem !important; }
    [data-testid="stSidebar"] [data-testid="stTextInput"]::before { content: '⌕'; position: absolute; z-index: 2; color: #a9bdd0; left: 1.35rem; top: .47rem; font-size: 1.15rem; }
    .sidebar-brand { display:flex; align-items:center; gap:.72rem; padding:.1rem .75rem .95rem; border-bottom:1px solid rgba(127,226,213,.16); }
    .sidebar-brand-mark { display:flex; align-items:center; justify-content:center; width:2.25rem; height:2.25rem; border-radius:11px; background:linear-gradient(135deg,#7fe2d5,#0f8b8d); color:#12233f; font-weight:900; box-shadow:0 6px 14px rgba(0,0,0,.2); }
    .sidebar-brand-title { color:#ffffff; font-size:1rem; font-weight:800; letter-spacing:-.02em; }
    .sidebar-brand-subtitle { color:#a9bdd0; font-size:.68rem; margin-top:.12rem; }
    .sidebar-status { margin: 2rem .75rem 0; padding: .8rem .85rem; border:1px solid rgba(127,226,213,.2); border-radius:11px; background:rgba(255,255,255,.055); color:#a9bdd0; font-size:.72rem; }
    .sidebar-status span { color:#7fe2d5; font-weight:750; }
    .block-container { max-width: 1450px; padding-top: 2rem; padding-bottom: 3rem; }
    h1 { color: var(--navy); font-weight: 760; letter-spacing: -.035em; margin-bottom: .15rem; }
    h2, h3 { color: var(--navy); font-weight: 700; }
    .stCaption, [data-testid="stCaptionContainer"] { color: var(--muted); }
    [data-testid="stMetric"] { background: var(--surface); border: 1px solid var(--line); border-left: 5px solid var(--teal); border-radius: 12px; padding: 1rem 1.1rem; box-shadow: 0 5px 18px rgba(18,35,63,.07); }
    [data-testid="stMetricLabel"] { color: var(--muted); }
    [data-testid="stMetricValue"] { color: var(--navy); }
    .stButton > button, .stDownloadButton > button { border-radius: 8px; border: 1px solid var(--teal); color: var(--teal); background: #ffffff; font-weight: 650; }
    .stButton > button:hover, .stDownloadButton > button:hover { color: #ffffff; background: var(--teal); border-color: var(--teal); }
    [data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
    [data-testid="stAlert"] { border-radius: 10px; }
    div[data-baseweb="select"] > div, input { border-radius: 8px !important; border-color: var(--line) !important; background: var(--surface) !important; }
    .hero-note { background: linear-gradient(100deg, var(--navy), var(--navy-2)); color: #f5fbfb; border-radius: 14px; padding: 1rem 1.25rem; margin: .5rem 0 1.4rem; box-shadow: 0 8px 24px rgba(18,35,63,.16); }
    .hero-note strong { color: #7fe2d5; }
</style>
''', unsafe_allow_html=True)
with st.sidebar:
    st.markdown('<div class="sidebar-brand"><div class="sidebar-brand-mark">SE</div><div><div class="sidebar-brand-title">SmartEnergy</div><div class="sidebar-brand-subtitle">Analytics workspace</div></div></div>', unsafe_allow_html=True)
st.title('⚡ SmartEnergy Analytics')
st.markdown('<div class="hero-note"><strong>Energy intelligence workspace</strong><br>PySpark-first electricity analytics with transparent local fallback and AWS-ready storage.</div>', unsafe_allow_html=True)
CHART_TEMPLATE = 'plotly_white'
CHART_COLORS = ['#0f8b8d', '#d99124', '#c65d5d', '#476a95', '#7a9e9f']

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
navigation = ['Energy overview','Consumption analytics','Anomaly monitor','Demand forecast','Energy insights','Data quality']
nav_search = st.sidebar.text_input('Search workspace', placeholder='Search modules...', label_visibility='collapsed')
filtered_navigation = [item for item in navigation if nav_search.lower() in item.lower()]
if not filtered_navigation:
    st.sidebar.caption('No matching module')
    filtered_navigation = navigation
page = st.sidebar.radio('Workspace', filtered_navigation)
st.sidebar.markdown('<div class="sidebar-status"><span>●</span>&nbsp; Demo analytics ready<br><small>Six modules · Live local session</small></div>', unsafe_allow_html=True)
if page == 'Energy overview':
    c1,c2,c3,c4 = st.columns(4); c1.metric('Total consumption', f"{clean.consumption_kwh.sum():,.1f} kWh"); c2.metric('Average daily', f"{daily['sum'].mean():,.1f} kWh"); c3.metric('Entities', clean.entity_id.nunique()); c4.metric('Records', f"{len(clean):,}")
    fig = px.line(daily, x='day', y='sum', title='Daily total consumption', labels={'day':'Date','sum':'Consumption (kWh)'}, template=CHART_TEMPLATE, color_discrete_sequence=CHART_COLORS); fig.update_layout(margin=dict(l=10,r=10,t=55,b=10)); st.plotly_chart(fig, use_container_width=True)
elif page == 'Consumption analytics':
    a,b = st.columns(2); a.plotly_chart(px.bar(hourly, x='hour', y='sum', title='Hourly total profile', labels={'hour':'Hour of day','sum':'Consumption (kWh)'}, template=CHART_TEMPLATE, color_discrete_sequence=CHART_COLORS), use_container_width=True); b.plotly_chart(px.bar(entities.sort_values('sum', ascending=False), x='entity_id', y='sum', title='Building total comparison', labels={'entity_id':'Building','sum':'Consumption (kWh)'}, template=CHART_TEMPLATE, color_discrete_sequence=CHART_COLORS), use_container_width=True)
    st.plotly_chart(px.line(daily, x='day', y='mean', title='Daily average reading per record', labels={'day':'Date','mean':'Average reading (kWh)'}, template=CHART_TEMPLATE, color_discrete_sequence=CHART_COLORS), use_container_width=True)
elif page == 'Anomaly monitor':
    c1,c2,c3 = st.columns(3); selected_entity = c1.selectbox('Building', ['All'] + sorted(clean.entity_id.unique().tolist())); min_date = c2.date_input('From', pd.to_datetime(clean.day).min().date()); max_date = c3.date_input('To', pd.to_datetime(clean.day).max().date())
    view = clean[(pd.to_datetime(clean.day).dt.date >= min_date) & (pd.to_datetime(clean.day).dt.date <= max_date)]
    if selected_entity != 'All': view = view[view.entity_id == selected_entity]
    scored = anomalies(view); st.metric('Candidate anomalies', len(scored)); st.caption('Candidates use a trailing 24-reading mean and standard deviation per building. They require investigation and are not confirmed faults, theft, or wastage.')
    chart = go.Figure(); chart.add_trace(go.Scatter(x=view.timestamp, y=view.consumption_kwh, name='Actual consumption (kWh)', line={'color':'#0f8b8d'})); chart.add_trace(go.Scatter(x=scored.timestamp, y=scored.expected_kwh, mode='markers', name='Expected at anomaly', marker={'color':'#c65d5d','size':9})); chart.update_layout(template=CHART_TEMPLATE, title='Actual consumption and detected candidates', xaxis_title='Timestamp', yaxis_title='Consumption (kWh)'); st.plotly_chart(chart, use_container_width=True)
    cols = ['timestamp','entity_id','consumption_kwh','expected_kwh','anomaly_score']; st.dataframe(scored[cols].sort_values('anomaly_score', ascending=False), use_container_width=True); st.download_button('Download filtered anomalies CSV', scored[cols].to_csv(index=False), 'filtered_anomalies.csv', 'text/csv')
elif page == 'Demand forecast':
    result, metrics = forecast(daily); st.write(metrics); st.caption('Both methods are evaluated on a chronological holdout. The forecast horizon begins after the last observed date.')
    hist = daily.assign(day=pd.to_datetime(daily.day), actual_kwh=daily['sum']); chart = px.line(hist, x='day', y='actual_kwh', title='Historical demand and future forecasts', labels={'day':'Date','actual_kwh':'Consumption (kWh)'}, template=CHART_TEMPLATE, color_discrete_sequence=['#0f8b8d']); future = result[result.kind=='forecast']; chart.add_scatter(x=future.day, y=future.baseline_forecast_kwh, name='7-day mean forecast', line={'color':'#d99124','dash':'dash'}); chart.add_scatter(x=future.day, y=future.seasonal_naive_kwh, name='Seasonal-naive forecast', line={'color':'#476a95','dash':'dot'}); st.plotly_chart(chart, use_container_width=True)
elif page == 'Energy insights':
    for item in insights(clean): st.success(item)
elif page == 'Data quality':
    st.write(f"Processing engine: **{quality.get('engine', 'unknown')}**"); st.write(f"Status: **{quality.get('processing_status', 'unknown')}** | Duration: **{quality.get('duration_seconds', 0):.4f} seconds** | Source: `{quality.get('dataset_path', DATA_PATH)}`")
    if quality.get('engine_error'): st.warning(f"PySpark was unavailable; pandas fallback was used. Diagnostic: {quality['engine_error']}")
    st.json(quality); st.download_button('Download cleaned CSV', clean.to_csv(index=False), 'cleaned.csv', 'text/csv'); st.download_button('Download quality JSON', json.dumps(quality, indent=2), 'quality.json', 'application/json')

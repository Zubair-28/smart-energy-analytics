
from pathlib import Path
import json

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from config.settings import ROOT, DATA_PATH, OUTPUT_DIR
from processing.pipeline import generate_demo, run_pipeline, clean_data
from analytics.models import anomalies, forecast, insights


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="SmartEnergy Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="auto",
)


# ============================================================
# GLOBAL UI STYLES
# ============================================================

st.markdown(
    """
<style>
    :root {
        --navy: #12233f;
        --navy-2: #1b3155;
        --teal: #0f8b8d;
        --teal-light: #7fe2d5;
        --teal-soft: #e5f6f3;
        --amber: #d99124;
        --coral: #c65d5d;
        --ink: #17243a;
        --muted: #66758a;
        --surface: #ffffff;
        --canvas: #f3f6fa;
        --line: #e1e8ef;
    }

    /* --------------------------------------------------------
       APPLICATION BACKGROUND
    -------------------------------------------------------- */

    .stApp {
        background: var(--canvas);
        color: var(--ink);
    }

    [data-testid="stHeader"] {
        background: rgba(243, 246, 250, 0.96);
    }

    [data-testid="stToolbar"] {
        color: var(--navy);
    }

    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* --------------------------------------------------------
       TYPOGRAPHY
    -------------------------------------------------------- */

    h1 {
        color: var(--navy);
        font-weight: 800;
        letter-spacing: -0.045em;
        margin-bottom: 0.3rem;
    }

    h2, h3, h4 {
        color: var(--navy);
        font-weight: 750;
        letter-spacing: -0.02em;
    }

    p {
        line-height: 1.7;
    }

    [data-testid="stCaptionContainer"] {
        color: var(--muted);
    }

    /* --------------------------------------------------------
       SIDEBAR
    -------------------------------------------------------- */

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #101d35 0%,
            #172945 55%,
            #101d35 100%
        );

        border-right: 1px solid #263d5b;
        box-shadow: 8px 0 24px rgba(18, 35, 63, 0.08);
    }

    [data-testid="stSidebar"] * {
        color: #edf5f7;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.4rem;
    }

    .sidebar-brand {
        padding: 0.8rem 0.8rem 1.3rem;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.09);
    }

    .sidebar-brand-icon {
        font-size: 1.8rem;
        margin-bottom: 0.3rem;
    }

    .sidebar-brand-title {
        color: #ffffff;
        font-size: 1.12rem;
        font-weight: 800;
        letter-spacing: -0.025em;
    }

    .sidebar-brand-subtitle {
        color: #a9bdd0;
        font-size: 0.73rem;
        margin-top: 0.3rem;
    }

    .sidebar-section-label {
        color: #a9bdd0;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin: 1.4rem 0.75rem 0.65rem;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] {
        margin: 0.18rem 0;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button {
        min-height: 2.8rem;
        border: 1px solid transparent;
        border-radius: 10px;
        background: transparent;
        color: #dce7f1;
        text-align: left;
        padding: 0.55rem 0.8rem;
        font-weight: 550;
        transition:
            background 0.2s ease,
            transform 0.2s ease,
            border-color 0.2s ease;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button:hover {
        border-color: rgba(127, 226, 213, 0.24);
        background: rgba(127, 226, 213, 0.10);
        color: #7fe2d5;
        transform: translateX(3px);
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button:active {
        transform: scale(0.985);
    }

    [data-testid="stSidebar"] .st-key-nav-active button {
        background: linear-gradient(
            100deg,
            rgba(15, 139, 141, 0.36),
            rgba(15, 139, 141, 0.09)
        );
        border-color: rgba(127, 226, 213, 0.28);
        box-shadow: inset 4px 0 0 #36d6c0;
        color: #ffffff;
        font-weight: 750;
    }

    /* --------------------------------------------------------
       HERO BANNER
    -------------------------------------------------------- */

    .hero-note {
        position: relative;
        overflow: hidden;
        background: linear-gradient(
            115deg,
            #12233f 0%,
            #1b3155 58%,
            #174653 100%
        );
        color: #f5fbfb;
        border-radius: 20px;
        padding: 2rem 2.1rem;
        margin: 1.2rem 0 2rem;
        box-shadow: 0 12px 32px rgba(18, 35, 63, 0.10);
    }

    .hero-note::after {
        content: "";
        position: absolute;
        top: -100px;
        right: -60px;
        width: 250px;
        height: 250px;
        border: 1px solid rgba(127, 226, 213, 0.15);
        border-radius: 50%;
        box-shadow:
            0 0 0 24px rgba(127, 226, 213, 0.025),
            0 0 0 48px rgba(127, 226, 213, 0.025);
        pointer-events: none;
    }

    .hero-eyebrow {
        display: flex;
        align-items: center;
        gap: 9px;
        color: #7fe2d5;
        font-size: 0.72rem;
        font-weight: 850;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }

    .hero-eyebrow-dot {
        display: inline-block;
        width: 9px;
        height: 9px;
        background: #36d6c0;
        border-radius: 50%;
        box-shadow: 0 0 12px rgba(54, 214, 192, 0.45);
    }

    .hero-title {
        position: relative;
        z-index: 1;
        color: #ffffff;
        font-size: clamp(1.5rem, 2.8vw, 2.2rem);
        font-weight: 850;
        letter-spacing: -0.045em;
        line-height: 1.25;
        margin-bottom: 0.8rem;
    }

    .hero-description {
        position: relative;
        z-index: 1;
        max-width: 780px;
        color: #d9e7f1;
        font-size: 0.96rem;
        line-height: 1.8;
        margin-bottom: 1.2rem;
    }

    .hero-badge {
        position: relative;
        z-index: 1;
        display: inline-block;
        background: rgba(127, 226, 213, 0.09);
        border: 1px solid rgba(127, 226, 213, 0.25);
        border-radius: 8px;
        padding: 0.55rem 0.8rem;
        color: #9af0e4;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.07em;
        line-height: 1.6;
    }

    /* --------------------------------------------------------
       PAGE SECTION HEADERS
    -------------------------------------------------------- */

    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 0.8rem 0 0.25rem;
    }

    .section-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 38px;
        height: 38px;
        background: var(--teal-soft);
        color: var(--teal);
        border-radius: 11px;
        font-size: 1rem;
        font-weight: 850;
    }

    .section-title {
        color: var(--navy);
        font-size: 1.13rem;
        font-weight: 800;
        letter-spacing: -0.025em;
    }

    .section-subtitle {
        color: var(--muted);
        font-size: 0.83rem;
        line-height: 1.7;
        margin: 0.4rem 0 1.2rem;
    }

    /* --------------------------------------------------------
       METRIC CARDS
    -------------------------------------------------------- */

    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--line);
        border-left: 4px solid var(--teal);
        border-radius: 14px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 4px 16px rgba(18, 35, 63, 0.035);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 22px rgba(18, 35, 63, 0.07);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted);
        font-size: 0.82rem;
        font-weight: 650;
    }

    [data-testid="stMetricValue"] {
        color: var(--navy);
        font-weight: 800;
        letter-spacing: -0.035em;
    }

    [data-testid="stMetricDelta"] {
        font-weight: 600;
    }

    /* --------------------------------------------------------
       BUTTONS
    -------------------------------------------------------- */

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 9px;
        border: 1px solid var(--teal);
        color: var(--teal);
        background: #ffffff;
        font-weight: 700;
        min-height: 2.5rem;
        transition:
            background 0.2s ease,
            color 0.2s ease,
            transform 0.2s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        color: #ffffff;
        background: var(--teal);
        border-color: var(--teal);
        transform: translateY(-1px);
    }

    /* --------------------------------------------------------
       INPUTS
    -------------------------------------------------------- */

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-baseweb="datepicker"] > div {
        border-radius: 9px !important;
        border-color: var(--line) !important;
        background: #ffffff !important;
    }

    [data-testid="stDateInput"] input {
        border-radius: 9px !important;
        background: #ffffff !important;
    }

    /* --------------------------------------------------------
       TABLES AND ALERTS
    -------------------------------------------------------- */

    [data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 12px;
        overflow: hidden;
    }

    [data-testid="stAlert"] {
        border-radius: 11px;
    }

    /* --------------------------------------------------------
       INSIGHT CARDS
    -------------------------------------------------------- */

    .insight-card {
        display: flex;
        align-items: flex-start;
        gap: 14px;
        margin-bottom: 12px;
        padding: 18px 20px;
        background: #ffffff;
        border: 1px solid #e5eaf1;
        border-left: 4px solid #0b9b91;
        border-radius: 13px;
        box-shadow: 0 2px 8px rgba(16, 29, 53, 0.035);
        transition:
            transform 0.2s ease,
            box-shadow 0.2s ease;
    }

    .insight-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 7px 18px rgba(16, 29, 53, 0.07);
    }

    .insight-number {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        min-width: 34px;
        height: 34px;
        background: #e5f6f3;
        color: #087f79;
        border-radius: 9px;
        font-size: 0.8rem;
        font-weight: 850;
    }

    .insight-text {
        color: #35445b;
        font-size: 0.92rem;
        line-height: 1.75;
        padding-top: 3px;
        overflow-wrap: anywhere;
    }

    /* --------------------------------------------------------
       FOOTER
    -------------------------------------------------------- */

    .app-footer {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        flex-wrap: wrap;
        border-top: 1px solid var(--line);
        padding-top: 1rem;
        margin-top: 3rem;
        color: var(--muted);
        font-size: 0.73rem;
    }

    .app-footer strong {
        color: var(--navy);
    }

    /* --------------------------------------------------------
       RESPONSIVE LAYOUT
    -------------------------------------------------------- */

    @media (max-width: 768px) {
        .block-container {
            width: 100%;
            max-width: 100%;
            padding: 0.9rem 0.75rem 2rem;
        }

        .hero-note {
            padding: 1.2rem;
            margin: 0.8rem 0 1.25rem;
            border-radius: 14px;
        }

        .hero-title {
            font-size: clamp(1.25rem, 5vw, 1.55rem);
        }

        .hero-description {
            font-size: 0.86rem;
            line-height: 1.6;
        }

        .hero-eyebrow {
            font-size: 0.62rem;
            letter-spacing: 0.1em;
        }

        .hero-badge {
            max-width: 100%;
            font-size: 0.61rem;
            letter-spacing: 0.03em;
            overflow-wrap: anywhere;
        }

        .section-title {
            font-size: 1rem;
        }

        .section-subtitle {
            font-size: 0.8rem;
        }

        /* Stack chart, filter, and download columns on narrow screens. */
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap;
            gap: 0.75rem;
        }

        [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            flex: 1 1 100% !important;
            width: 100% !important;
            min-width: 100% !important;
        }

        /* Keep the four headline metrics compact in a two-by-two grid. */
        .st-key-overview-metrics [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            flex: 1 1 calc(50% - 0.4rem) !important;
            width: calc(50% - 0.4rem) !important;
            min-width: calc(50% - 0.4rem) !important;
        }

        [data-testid="stMetric"] {
            min-width: 0;
            padding: 0.8rem;
        }

        [data-testid="stMetricValue"] {
            font-size: clamp(1.05rem, 5vw, 1.4rem);
            overflow-wrap: anywhere;
        }

        [data-testid="stPlotlyChart"] {
            width: 100%;
            overflow: hidden;
        }

        [data-testid="stDataFrame"] {
            max-width: 100%;
            overflow-x: auto;
        }

        .stButton > button,
        .stDownloadButton > button {
            min-height: 2.75rem;
        }

        .insight-card {
            gap: 0.7rem;
            padding: 0.85rem;
        }

        .app-footer {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }
    }

    @media (max-width: 420px) {
        .block-container {
            padding-left: 0.55rem;
            padding-right: 0.55rem;
        }

        .hero-note {
            padding: 1rem;
        }

        .section-icon {
            min-width: 32px;
            height: 32px;
        }

        .st-key-overview-metrics [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            flex: 1 1 calc(50% - 0.3rem) !important;
            width: calc(50% - 0.3rem) !important;
            min-width: calc(50% - 0.3rem) !important;
        }

        .insight-number {
            min-width: 30px;
            height: 30px;
        }
    }

    @media (hover: none) and (pointer: coarse) {
        [data-testid="stMetric"]:hover,
        .insight-card:hover {
            transform: none;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# APPLICATION HEADER
# ============================================================

st.markdown(
    """
<div style="
    display:flex;
    align-items:center;
    gap:12px;
    margin-bottom:0.2rem;
">
    <span style="font-size:2.1rem; line-height:1;">⚡</span>
    <span style="
        color:#12233f;
        font-size:clamp(1.7rem, 3vw, 2.5rem);
        font-weight:850;
        letter-spacing:-0.045em;
        line-height:1.2;
    ">SmartEnergy Analytics</span>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="hero-note">
    <div class="hero-eyebrow">
        <span class="hero-eyebrow-dot"></span>
        ENERGY INTELLIGENCE WORKSPACE
    </div>
    <div class="hero-title">
        Understand consumption. Anticipate demand.
    </div>
    <div class="hero-description">
        Explore electricity consumption patterns, investigate potential
        anomalies, forecast future demand, and inspect data quality in
        one integrated analytics workspace.
    </div>
    <div class="hero-badge">
        PYSPARK-FIRST &nbsp;·&nbsp; LOCAL FALLBACK &nbsp;·&nbsp;
        AWS-READY STORAGE
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# CHART CONFIGURATION
# ============================================================

CHART_TEMPLATE = "plotly_white"

CHART_COLORS = [
    "#0f8b8d",
    "#d99124",
    "#c65d5d",
    "#476a95",
    "#7a9e9f",
]


# Consistent chart styling. The underlying data and calculations
# remain unchanged.
def style_chart(fig, height=420):
    fig.update_layout(
        template=CHART_TEMPLATE,
        height=height,
        margin=dict(l=18, r=18, t=70, b=18),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(
            family="Arial, sans-serif",
            size=12,
            color="#35445b",
        ),
        title=dict(
            font=dict(
                size=17,
                color="#12233f",
            ),
            x=0.02,
            xanchor="left",
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0.75)",
            borderwidth=0,
        ),
        hoverlabel=dict(
            bgcolor="#12233f",
            font_color="#ffffff",
        ),
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#e1e8ef",
        tickfont=dict(color="#66758a"),
        title_font=dict(color="#35445b"),
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#edf1f5",
        zeroline=False,
        linecolor="#e1e8ef",
        tickfont=dict(color="#66758a"),
        title_font=dict(color="#35445b"),
    )

    return fig


def section_heading(title, icon, subtitle):
    st.markdown(
        f"""
<div class="section-header">
    <div class="section-icon">{icon}</div>
    <div class="section-title">{title}</div>
</div>
<div class="section-subtitle">{subtitle}</div>
""",
        unsafe_allow_html=True,
    )


# ============================================================
# DATA INITIALIZATION
# ============================================================

if not DATA_PATH.exists():

    # Streamlit Community Cloud may not receive local ignored data
    # files or the private .env file. Generate demo data if appropriate.

    if DATA_PATH.name == "energy_demo.csv":

        DATA_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        generate_demo(DATA_PATH)

    else:

        if st.button("Generate documented synthetic demo data"):
            generate_demo(DATA_PATH)
            st.rerun()

        st.info(
            f"No input data found at {DATA_PATH}. "
            "Generate the demo dataset or set DATA_PATH in .env."
        )

        st.stop()


if not (OUTPUT_DIR / "quality.json").exists():
    run_pipeline(DATA_PATH, OUTPUT_DIR)


clean = pd.read_csv(
    OUTPUT_DIR / "cleaned.csv",
    parse_dates=["timestamp"],
)

quality = json.loads(
    (OUTPUT_DIR / "quality.json").read_text()
)

daily = pd.read_csv(
    OUTPUT_DIR / "daily.csv"
)

entities = pd.read_csv(
    OUTPUT_DIR / "entities.csv"
)

hourly = pd.read_csv(
    OUTPUT_DIR / "hourly.csv"
)


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

navigation = [
    "Energy overview",
    "Consumption analytics",
    "Anomaly monitor",
    "Demand forecast",
    "Energy insights",
    "Data quality",
]

nav_icons = {
    "Energy overview": "⌂",
    "Consumption analytics": "▥",
    "Anomaly monitor": "⌁",
    "Demand forecast": "↗",
    "Energy insights": "✦",
    "Data quality": "✓",
}


with st.sidebar:

    st.markdown(
        """
<div class="sidebar-brand">
    <div class="sidebar-brand-icon">⚡</div>
    <div class="sidebar-brand-title">SmartEnergy</div>
    <div class="sidebar-brand-subtitle">
        Analytics workspace
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


page = st.session_state.get(
    "active_page",
    navigation[0],
)

st.sidebar.markdown(
    '<div class="sidebar-section-label">Workspace</div>',
    unsafe_allow_html=True,
)


for item in navigation:

    key = "".join(
        ch.lower() if ch.isalnum() else "-"
        for ch in item
    ).strip("-")

    container_key = (
        "nav-active"
        if item == page
        else f"nav-{key}"
    )

    with st.sidebar.container(key=container_key):

        if st.button(
            f"{nav_icons[item]} {item}",
            key=f"go-{key}",
            use_container_width=True,
        ):
            st.session_state.active_page = item
            st.rerun()


# ============================================================
# PAGE 1: ENERGY OVERVIEW
# ============================================================

if page == "Energy overview":

    section_heading(
        "Energy at a glance",
        "▦",
        "A consolidated view of electricity consumption across "
        "your monitored buildings.",
    )

    with st.container(key="overview-metrics"):
        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Total consumption",
            f"{clean.consumption_kwh.sum():,.1f} kWh",
        )

        c2.metric(
            "Average daily",
            f"{daily['sum'].mean():,.1f} kWh",
        )

        c3.metric(
            "Entities monitored",
            clean.entity_id.nunique(),
        )

        c4.metric(
            "Total records",
            f"{len(clean):,}",
        )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    fig = px.line(
        daily,
        x="day",
        y="sum",
        title="Daily total consumption",
        labels={
            "day": "Date",
            "sum": "Consumption (kWh)",
        },
        template=CHART_TEMPLATE,
        color_discrete_sequence=[CHART_COLORS[0]],
    )

    fig.update_traces(
        line=dict(width=3),
        mode="lines",
        hovertemplate=(
            "<b>Date:</b> %{x}<br>"
            "<b>Consumption:</b> %{y:,.2f} kWh"
            "<extra></extra>"
        ),
    )

    fig = style_chart(fig, height=440)

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ============================================================
# PAGE 2: CONSUMPTION ANALYTICS
# ============================================================

elif page == "Consumption analytics":

    section_heading(
        "Consumption analytics",
        "▥",
        "Understand hourly usage patterns and compare total "
        "electricity consumption across buildings.",
    )

    a, b = st.columns(2, gap="large")

    with a:

        hourly_fig = px.bar(
            hourly,
            x="hour",
            y="sum",
            title="Hourly total profile",
            labels={
                "hour": "Hour of day",
                "sum": "Consumption (kWh)",
            },
            template=CHART_TEMPLATE,
            color_discrete_sequence=[CHART_COLORS[0]],
        )

        hourly_fig.update_traces(
            marker_line_width=0,
            hovertemplate=(
                "<b>Hour:</b> %{x}:00<br>"
                "<b>Consumption:</b> %{y:,.2f} kWh"
                "<extra></extra>"
            ),
        )

        hourly_fig = style_chart(hourly_fig)

        st.plotly_chart(
            hourly_fig,
            use_container_width=True,
        )

    with b:

        entity_fig = px.bar(
            entities.sort_values(
                "sum",
                ascending=False,
            ),
            x="entity_id",
            y="sum",
            title="Building total comparison",
            labels={
                "entity_id": "Building",
                "sum": "Consumption (kWh)",
            },
            template=CHART_TEMPLATE,
            color_discrete_sequence=[CHART_COLORS[1]],
        )

        entity_fig.update_traces(
            marker_line_width=0,
            hovertemplate=(
                "<b>Building:</b> %{x}<br>"
                "<b>Consumption:</b> %{y:,.2f} kWh"
                "<extra></extra>"
            ),
        )

        entity_fig = style_chart(entity_fig)

        st.plotly_chart(
            entity_fig,
            use_container_width=True,
        )

    daily_fig = px.line(
        daily,
        x="day",
        y="mean",
        title="Daily average reading per record",
        labels={
            "day": "Date",
            "mean": "Average reading (kWh)",
        },
        template=CHART_TEMPLATE,
        color_discrete_sequence=[CHART_COLORS[3]],
    )

    daily_fig.update_traces(
        line=dict(width=3),
        hovertemplate=(
            "<b>Date:</b> %{x}<br>"
            "<b>Average reading:</b> %{y:,.2f} kWh"
            "<extra></extra>"
        ),
    )

    daily_fig = style_chart(daily_fig)

    st.plotly_chart(
        daily_fig,
        use_container_width=True,
    )


# ============================================================
# PAGE 3: ANOMALY MONITOR
# ============================================================

elif page == "Anomaly monitor":

    section_heading(
        "Anomaly monitor",
        "⌁",
        "Investigate unusual electricity consumption patterns "
        "using building and date filters.",
    )

    c1, c2, c3 = st.columns(
        [1.2, 1, 1],
        gap="medium",
    )

    selected_entity = c1.selectbox(
        "Building",
        ["All"] + sorted(
            clean.entity_id.unique().tolist()
        ),
    )

    min_date = c2.date_input(
        "From",
        pd.to_datetime(clean.day).min().date(),
    )

    max_date = c3.date_input(
        "To",
        pd.to_datetime(clean.day).max().date(),
    )

    if min_date > max_date:

        st.error(
            "The start date must be earlier than or equal "
            "to the end date."
        )

        st.stop()

    view = clean[
        (
            pd.to_datetime(clean.day).dt.date
            >= min_date
        )
        &
        (
            pd.to_datetime(clean.day).dt.date
            <= max_date
        )
    ]

    if selected_entity != "All":
        view = view[
            view.entity_id == selected_entity
        ]

    scored = anomalies(view)

    st.metric(
        "Candidate anomalies",
        len(scored),
    )

    st.caption(
        "Candidates use a trailing 24-reading mean and standard "
        "deviation per building. They require investigation and "
        "are not confirmed faults, theft, or wastage."
    )

    chart = go.Figure()

    chart.add_trace(
        go.Scatter(
            x=view.timestamp,
            y=view.consumption_kwh,
            name="Actual consumption (kWh)",
            mode="lines",
            line={
                "color": CHART_COLORS[0],
                "width": 2,
            },
        )
    )

    chart.add_trace(
        go.Scatter(
            x=scored.timestamp,
            y=scored.expected_kwh,
            mode="markers",
            name="Expected at anomaly",
            marker={
                "color": CHART_COLORS[2],
                "size": 9,
                "symbol": "circle",
                "line": {
                    "color": "#ffffff",
                    "width": 1,
                },
            },
        )
    )

    chart.update_layout(
        title="Actual consumption and detected candidates",
        xaxis_title="Timestamp",
        yaxis_title="Consumption (kWh)",
    )

    chart = style_chart(chart, height=450)

    st.plotly_chart(
        chart,
        use_container_width=True,
    )

    st.markdown("### Anomaly details")

    cols = [
        "timestamp",
        "entity_id",
        "consumption_kwh",
        "expected_kwh",
        "anomaly_score",
    ]

    st.dataframe(
        scored[cols].sort_values(
            "anomaly_score",
            ascending=False,
        ),
        use_container_width=True,
    )

    st.download_button(
        "Download filtered anomalies CSV",
        scored[cols].to_csv(index=False),
        "filtered_anomalies.csv",
        "text/csv",
    )


# ============================================================
# PAGE 4: DEMAND FORECAST
# ============================================================

elif page == "Demand forecast":

    section_heading(
        "Demand forecast",
        "↗",
        "Compare historical electricity demand with future "
        "forecasts from the existing forecasting models.",
    )

    result, metrics = forecast(daily)

    st.markdown("### Model evaluation")

    baseline_col, seasonal_col = st.columns(2, gap="large")

    with baseline_col:
        st.markdown("#### 7-day mean baseline")
        c1, c2 = st.columns(2)
        c1.metric("Mean Absolute Error", f"{metrics['baseline_mae']:.2f}")
        c2.metric("Root Mean Squared Error", f"{metrics['baseline_rmse']:.2f}")

    with seasonal_col:
        st.markdown("#### Seasonal-naive model")
        c1, c2 = st.columns(2)
        c1.metric("Mean Absolute Error", f"{metrics['seasonal_naive_mae']:.2f}")
        c2.metric("Root Mean Squared Error", f"{metrics['seasonal_naive_rmse']:.2f}")

    st.info(
        f"Forecast horizon: {metrics['horizon_days']} days · "
        f"Test records: {metrics['test_records']} · "
        f"Evaluation: {metrics['evaluation']}"
    )

    st.caption(
        "Both methods are evaluated on a chronological holdout. "
        "The forecast horizon begins after the last observed date."
    )

    hist = daily.assign(
        day=pd.to_datetime(daily.day),
        actual_kwh=daily["sum"],
    )

    chart = px.line(
        hist,
        x="day",
        y="actual_kwh",
        title="Historical demand and future forecasts",
        labels={
            "day": "Date",
            "actual_kwh": "Consumption (kWh)",
        },
        template=CHART_TEMPLATE,
        color_discrete_sequence=[CHART_COLORS[0]],
    )

    chart.update_traces(
        line=dict(width=3),
        name="Historical consumption",
    )

    future = result[
        result.kind == "forecast"
    ]

    chart.add_scatter(
        x=future.day,
        y=future.baseline_forecast_kwh,
        name="7-day mean forecast",
        mode="lines",
        line={
            "color": CHART_COLORS[1],
            "width": 2.5,
            "dash": "dash",
        },
    )

    chart.add_scatter(
        x=future.day,
        y=future.seasonal_naive_kwh,
        name="Seasonal-naive forecast",
        mode="lines",
        line={
            "color": CHART_COLORS[3],
            "width": 2.5,
            "dash": "dot",
        },
    )

    chart = style_chart(chart, height=470)

    st.plotly_chart(
        chart,
        use_container_width=True,
    )


# ============================================================
# PAGE 5: ENERGY INSIGHTS
# ============================================================

elif page == "Energy insights":

    section_heading(
        "Energy insights",
        "✦",
        "Review the observations generated by the existing "
        "energy analytics and insight engine.",
    )

    insight_items = insights(clean)

    if not insight_items:

        st.info(
            "No insights are available for the current dataset."
        )

    else:

        for index, item in enumerate(
            insight_items,
            start=1,
        ):

            # IMPORTANT:
            # The HTML starts at the beginning of the string.
            # This prevents Streamlit from interpreting the HTML
            # as a Markdown code block.

            st.markdown(
                f"""
<div class="insight-card">
    <div class="insight-number">{index:02d}</div>
    <div class="insight-text">{item}</div>
</div>
""",
                unsafe_allow_html=True,
            )


# ============================================================
# PAGE 6: DATA QUALITY
# ============================================================

elif page == "Data quality":

    section_heading(
        "Data quality",
        "✓",
        "Inspect the processing engine, execution status, "
        "dataset source, and quality report.",
    )

    c1, c2 = st.columns(2, gap="medium")

    with c1:

        st.markdown("#### Processing engine")

        st.metric(
            "Engine",
            str(
                quality.get(
                    "engine",
                    "unknown",
                )
            ),
        )

    with c2:

        st.markdown("#### Processing status")

        st.metric(
            "Status",
            str(
                quality.get(
                    "processing_status",
                    "unknown",
                )
            ),
        )

    d1, d2 = st.columns(2, gap="medium")

    with d1:

        st.markdown("#### Execution duration")

        st.metric(
            "Duration",
            f"{quality.get('duration_seconds', 0):.4f} seconds",
        )

    with d2:

        st.markdown("#### Input records")

        st.metric(
            "Cleaned records",
            f"{len(clean):,}",
        )

    st.markdown("#### Dataset source")

    st.code(
        str(
            quality.get(
                "dataset_path",
                DATA_PATH,
            )
        ),
        language=None,
    )

    if quality.get("engine_error"):

        st.warning(
            "PySpark was unavailable; pandas fallback was used. "
            f"Diagnostic: {quality['engine_error']}"
        )

    st.markdown("#### Processing quality report")

    with st.expander(
        "View complete quality JSON",
        expanded=False,
    ):

        st.json(quality)

    st.markdown("#### Export data")

    download_col1, download_col2 = st.columns(2)

    with download_col1:

        st.download_button(
            "Download cleaned CSV",
            clean.to_csv(index=False),
            "cleaned.csv",
            "text/csv",
            use_container_width=True,
        )

    with download_col2:

        st.download_button(
            "Download quality JSON",
            json.dumps(
                quality,
                indent=2,
            ),
            "quality.json",
            "application/json",
            use_container_width=True,
        )


# ============================================================
# APPLICATION FOOTER
# ============================================================

st.markdown(
    """
<div class="app-footer">
    <span>
        <strong>SmartEnergy Analytics</strong>
        &nbsp;·&nbsp; Energy intelligence workspace
    </span>
    <span>
        Data-driven energy monitoring and forecasting
    </span>
</div>
""",
    unsafe_allow_html=True,
)

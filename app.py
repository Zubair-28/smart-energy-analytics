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
    initial_sidebar_state="expanded",
)


# ============================================================
# DESIGN SYSTEM
# UI ONLY: No changes to processing or analytical logic.
# ============================================================

st.markdown(
    """
    <style>
    /* --------------------------------------------------------
       DESIGN TOKENS
    -------------------------------------------------------- */

    :root {
        --navy: #101d35;
        --navy-light: #182a48;
        --navy-hover: #223957;

        --teal: #0b9b91;
        --teal-dark: #087f79;
        --teal-soft: #e5f6f3;

        --amber: #e6a23c;
        --coral: #d96565;
        --blue: #6489c6;

        --ink: #17253b;
        --muted: #718096;
        --muted-light: #a7b2c2;

        --background: #f4f7fb;
        --surface: #ffffff;
        --surface-soft: #f8fafc;

        --border: #e5eaf1;
        --border-strong: #d6deea;

        --shadow-sm: 0 2px 8px rgba(16, 29, 53, 0.035);
        --shadow-md: 0 8px 24px rgba(16, 29, 53, 0.055);
        --shadow-lg: 0 14px 36px rgba(16, 29, 53, 0.10);

        --radius-sm: 10px;
        --radius-md: 15px;
        --radius-lg: 20px;
    }


    /* --------------------------------------------------------
       GLOBAL APPLICATION
    -------------------------------------------------------- */

    .stApp {
        background: var(--background);
        color: var(--ink);
        font-family: Inter, -apple-system, BlinkMacSystemFont,
                     "Segoe UI", sans-serif;
    }

    [data-testid="stHeader"] {
        background: rgba(244, 247, 251, 0.92);
        backdrop-filter: blur(12px);
    }

    [data-testid="stToolbar"] {
        color: var(--ink);
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    .block-container {
        max-width: 1600px;
        padding: 2rem 2.4rem 3rem;
    }


    /* --------------------------------------------------------
       TYPOGRAPHY
    -------------------------------------------------------- */

    h1 {
        color: var(--navy) !important;
        font-size: clamp(1.9rem, 3vw, 2.55rem) !important;
        font-weight: 800 !important;
        letter-spacing: -0.055em !important;
        line-height: 1.2 !important;
        margin-bottom: 0.35rem !important;
    }

    h2 {
        color: var(--navy) !important;
        font-size: 1.5rem !important;
        font-weight: 750 !important;
        letter-spacing: -0.035em !important;
    }

    h3 {
        color: var(--navy) !important;
        font-size: 1.12rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }

    p {
        line-height: 1.65;
    }

    [data-testid="stCaptionContainer"] {
        color: var(--muted);
        font-size: 0.83rem;
        line-height: 1.6;
    }

    hr {
        border-color: var(--border);
        margin: 1.5rem 0;
    }


    /* --------------------------------------------------------
       SIDEBAR
    -------------------------------------------------------- */

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #101d35 0%,
            #142440 55%,
            #101d35 100%
        );

        border-right: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 8px 0 30px rgba(16, 29, 53, 0.07);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.4rem;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #dce6f2;
    }

    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #9caec5;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.55rem;
    }
    .sidebar-section-label {
        color: #8299b7;
        font-size: 0.66rem;
        font-weight: 800;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin: 1rem 0.65rem 0.55rem;
    }

    [data-testid="stSidebar"] [data-testid="stTextInput"] {
        margin: 0.15rem 0 0.5rem;
    }

    [data-testid="stSidebar"] [data-testid="stTextInput"] input {
        background: rgba(255, 255, 255, 0.065) !important;
        border: 1px solid rgba(255, 255, 255, 0.10) !important;
        border-radius: 11px !important;
        color: #ffffff !important;
        min-height: 43px;
        padding-left: 0.9rem !important;
        box-shadow: none !important;
    }

    [data-testid="stSidebar"] [data-testid="stTextInput"] input::placeholder {
        color: #91a3bc !important;
    }

    [data-testid="stSidebar"] [data-testid="stTextInput"] input:focus {
        border-color: rgba(19, 185, 168, 0.75) !important;
        box-shadow: 0 0 0 2px rgba(19, 185, 168, 0.10) !important;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] {
        margin: 0;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button {
        width: 100%;
        min-height: 46px;

        display: flex;
        align-items: center;
        justify-content: flex-start;

        padding: 0.65rem 0.9rem;

        background: transparent;
        color: #c6d3e4;

        border: 1px solid transparent;
        border-radius: 11px;

        font-size: 0.89rem;
        font-weight: 600;
        text-align: left;

        box-shadow: none;
        transition: all 0.18s ease;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button:hover {
        background: rgba(255, 255, 255, 0.065);
        color: #ffffff;
        border-color: rgba(255, 255, 255, 0.08);
        transform: translateX(2px);
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button:active {
        transform: scale(0.985);
    }

    [data-testid="stSidebar"] .st-key-nav-active button {
        background: linear-gradient(
            105deg,
            rgba(11, 155, 145, 0.25),
            rgba(11, 155, 145, 0.09)
        );

        border: 1px solid rgba(19, 185, 168, 0.20);

        box-shadow: inset 3px 0 0 #16c5b0;

        color: #ffffff;
        font-weight: 750;
    }

    [data-testid="stSidebar"] .st-key-nav-active button:hover {
        background: rgba(11, 155, 145, 0.27);
        border-color: rgba(19, 185, 168, 0.32);
    }
    /* --------------------------------------------------------
       HERO HEADER
    -------------------------------------------------------- */

    .hero-note {
        position: relative;
        overflow: hidden;

        background: linear-gradient(
            110deg,
            #101d35 0%,
            #192f4f 65%,
            #174452 100%
        );

        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: var(--radius-lg);

        padding: 1.45rem 1.6rem;
        margin: 0.8rem 0 1.8rem;

        box-shadow: var(--shadow-md);
    }

    .hero-note::after {
        content: "";
        position: absolute;

        width: 220px;
        height: 220px;

        top: -115px;
        right: -40px;

        border-radius: 50%;
        border: 1px solid rgba(116, 232, 216, 0.16);

        box-shadow:
            0 0 0 24px rgba(116, 232, 216, 0.025),
            0 0 0 48px rgba(116, 232, 216, 0.02);

        pointer-events: none;
    }

    .hero-eyebrow {
        display: flex;
        align-items: center;
        gap: 8px;

        color: #7ce0d0;
        font-size: 0.69rem;
        font-weight: 800;
        letter-spacing: 0.15em;
        text-transform: uppercase;

        margin-bottom: 0.55rem;
    }

    .hero-eyebrow-dot {
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #42d8bd;
        box-shadow: 0 0 12px rgba(66, 216, 189, 0.5);
    }

    .hero-title {
        color: #ffffff;
        font-size: 1.27rem;
        font-weight: 750;
        letter-spacing: -0.025em;
        margin-bottom: 0.35rem;
    }

    .hero-description {
        color: #bdccdd;
        font-size: 0.88rem;
        line-height: 1.7;
        max-width: 780px;
    }

    .hero-badge {
        display: inline-block;

        margin-top: 0.85rem;
        padding: 0.35rem 0.7rem;

        border: 1px solid rgba(124, 224, 208, 0.22);
        border-radius: 7px;

        background: rgba(124, 224, 208, 0.08);

        color: #9ce9dc;
        font-size: 0.69rem;
        font-weight: 700;
        letter-spacing: 0.025em;
    }


    /* --------------------------------------------------------
       PAGE SECTION HEADERS
    -------------------------------------------------------- */

    .section-heading {
        display: flex;
        align-items: center;
        gap: 10px;

        color: var(--navy);
        font-size: 1.02rem;
        font-weight: 800;
        letter-spacing: -0.025em;

        margin: 1.5rem 0 0.85rem;
    }

    .section-heading-icon {
        display: flex;
        align-items: center;
        justify-content: center;

        width: 31px;
        height: 31px;
        min-width: 31px;

        border-radius: 9px;
        background: var(--teal-soft);

        color: var(--teal-dark);
        font-size: 0.92rem;
    }

    .section-subtitle {
        color: var(--muted);
        font-size: 0.82rem;
        line-height: 1.6;
        margin: -0.35rem 0 1rem;
    }


    /* --------------------------------------------------------
       METRIC CARDS
    -------------------------------------------------------- */

    [data-testid="stMetric"] {
        position: relative;
        overflow: hidden;

        min-height: 120px;

        padding: 1.15rem 1.2rem;

        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);

        box-shadow: var(--shadow-sm);

        transition:
            transform 0.18s ease,
            box-shadow 0.18s ease,
            border-color 0.18s ease;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        border-color: #c8e8e3;
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
        font-size: 0.80rem !important;
        font-weight: 650 !important;
        line-height: 1.5 !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--navy) !important;
        font-size: clamp(1.35rem, 2vw, 1.9rem) !important;
        font-weight: 800 !important;
        letter-spacing: -0.045em !important;
        line-height: 1.3 !important;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.75rem !important;
    }

    [data-testid="stMetric"] [data-testid="stMetricValue"] svg {
        color: var(--teal);
    }


    /* --------------------------------------------------------
       CHART CONTAINERS
    -------------------------------------------------------- */

    [data-testid="stPlotlyChart"] {
        background: var(--surface);

        border: 1px solid var(--border);
        border-radius: var(--radius-md);

        padding: 0.6rem 0.45rem 0.3rem;

        box-shadow: var(--shadow-sm);

        transition:
            box-shadow 0.18s ease,
            border-color 0.18s ease;
    }

    [data-testid="stPlotlyChart"]:hover {
        box-shadow: var(--shadow-md);
        border-color: var(--border-strong);
    }


    /* --------------------------------------------------------
       BUTTONS
    -------------------------------------------------------- */

    .stButton > button,
    .stDownloadButton > button {
        min-height: 42px;

        border: 1px solid #d7e5e8;
        border-radius: 10px;

        background: #ffffff;
        color: var(--navy);

        font-size: 0.84rem;
        font-weight: 700;

        box-shadow: var(--shadow-sm);

        transition: all 0.18s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: var(--teal);
        color: #ffffff;
        border-color: var(--teal);

        box-shadow: 0 5px 14px rgba(11, 155, 145, 0.17);
        transform: translateY(-1px);
    }

    .stButton > button:active,
    .stDownloadButton > button:active {
        transform: scale(0.985);
    }

    .stButton > button:focus-visible,
    .stDownloadButton > button:focus-visible {
        outline: 2px solid var(--teal);
        outline-offset: 3px;
    }


    /* --------------------------------------------------------
       FORM CONTROLS
    -------------------------------------------------------- */

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stDateInput"] input {
        min-height: 42px;

        background: #ffffff !important;
        border: 1px solid var(--border-strong) !important;
        border-radius: 10px !important;

        color: var(--ink) !important;
        box-shadow: none !important;
    }

    [data-testid="stTextInput"] input:focus,
    [data-testid="stNumberInput"] input:focus,
    [data-testid="stDateInput"] input:focus {
        border-color: var(--teal) !important;
        box-shadow: 0 0 0 3px rgba(11, 155, 145, 0.09) !important;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
        background: #ffffff !important;
        border-color: var(--border-strong) !important;
        border-radius: 10px !important;
        min-height: 42px;
    }

    [data-testid="stSelectbox"] label,
    [data-testid="stDateInput"] label {
        color: var(--ink);
        font-size: 0.81rem;
        font-weight: 700;
    }


    /* --------------------------------------------------------
       DATA TABLES
    -------------------------------------------------------- */

    [data-testid="stDataFrame"] {
        overflow: hidden;

        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: var(--radius-md);

        box-shadow: var(--shadow-sm);
    }

    [data-testid="stDataFrame"] iframe {
        border-radius: var(--radius-md);
    }


    /* --------------------------------------------------------
       ALERTS AND INFORMATION PANELS
    -------------------------------------------------------- */

    [data-testid="stAlert"] {
        border-radius: 12px;
        border-width: 1px;
        box-shadow: var(--shadow-sm);
    }

    [data-testid="stAlert"] p {
        font-size: 0.87rem;
        line-height: 1.7;
    }

    [data-testid="stJson"] {
        padding: 0.8rem;

        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: var(--radius-md);

        box-shadow: var(--shadow-sm);
    }


    /* --------------------------------------------------------
       DATA QUALITY SUMMARY
    -------------------------------------------------------- */

    .quality-panel {
        padding: 1.2rem 1.35rem;
        margin: 0.75rem 0 1rem;

        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: var(--radius-md);

        box-shadow: var(--shadow-sm);
    }

    .quality-label {
        color: var(--muted);
        font-size: 0.72rem;
        font-weight: 750;
        letter-spacing: 0.08em;
        text-transform: uppercase;

        margin-bottom: 0.35rem;
    }

    .quality-value {
        color: var(--navy);
        font-size: 0.97rem;
        font-weight: 750;
        overflow-wrap: anywhere;
    }

    .quality-status {
        display: inline-block;

        padding: 0.28rem 0.65rem;

        background: var(--teal-soft);
        border: 1px solid #c6ebe4;
        border-radius: 7px;

        color: var(--teal-dark);
        font-size: 0.77rem;
        font-weight: 750;
    }


    /* --------------------------------------------------------
       FOOTER
    -------------------------------------------------------- */

    .app-footer {
        margin-top: 2.5rem;
        padding-top: 1.15rem;

        border-top: 1px solid var(--border);

        color: var(--muted);
        font-size: 0.74rem;
        line-height: 1.7;

        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        flex-wrap: wrap;
    }

    .app-footer strong {
        color: var(--navy);
        font-weight: 750;
    }


    /* --------------------------------------------------------
       RESPONSIVE LAYOUT
    -------------------------------------------------------- */

    @media (max-width: 1100px) {
        .block-container {
            padding: 1.6rem 1.5rem 2.5rem;
        }

        [data-testid="stMetric"] {
            padding: 1rem;
        }
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 1.2rem 0.9rem 2rem;
        }

        h1 {
            font-size: 1.8rem !important;
        }

        .hero-note {
            padding: 1.15rem;
            border-radius: 15px;
        }

        .hero-title {
            font-size: 1.08rem;
        }

        [data-testid="stMetric"] {
            min-height: 100px;
            padding: 0.85rem;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.25rem !important;
        }

        .app-footer {
            flex-direction: column;
            align-items: flex-start;
        }
    }

    /* Respect users who prefer reduced motion. */
    @media (prefers-reduced-motion: reduce) {
        *,
        *::before,
        *::after {
            transition-duration: 0.01ms !important;
            animation-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CHART THEME
# Presentation only. Data and analytical calculations remain
# unchanged.
# ============================================================

CHART_TEMPLATE = "plotly_white"

CHART_COLORS = [
    "#0b9b91",
    "#e6a23c",
    "#d96565",
    "#6489c6",
    "#789a9a",
]

CHART_FONT = "Inter, Segoe UI, sans-serif"


def style_chart(fig):
    """Apply a consistent visual theme to existing Plotly figures."""

    fig.update_layout(
        template=CHART_TEMPLATE,

        font=dict(
            family=CHART_FONT,
            size=12,
            color="#526177",
        ),

        title=dict(
            font=dict(
                family=CHART_FONT,
                size=17,
                color="#17253b",
            ),
            x=0.025,
            xanchor="left",
            y=0.97,
            yanchor="top",
        ),

        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",

        margin=dict(
            l=24,
            r=24,
            t=65,
            b=28,
        ),

        hoverlabel=dict(
            bgcolor="#101d35",
            bordercolor="#101d35",
            font=dict(
                family=CHART_FONT,
                size=12,
                color="#ffffff",
            ),
        ),

        legend=dict(
            bgcolor="rgba(255,255,255,0.82)",
            borderwidth=0,
            font=dict(
                family=CHART_FONT,
                size=11,
                color="#526177",
            ),
        ),
    )

    fig.update_xaxes(
        showgrid=False,
        showline=True,
        linecolor="#e5eaf1",
        linewidth=1,
        ticks="outside",
        tickcolor="#d6deea",
        tickfont=dict(
            size=11,
            color="#718096",
        ),
        title_font=dict(
            size=12,
            color="#526177",
        ),
        automargin=True,
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#edf1f6",
        griddash="solid",
        zeroline=False,
        showline=False,
        tickfont=dict(
            size=11,
            color="#718096",
        ),
        title_font=dict(
            size=12,
            color="#526177",
        ),
        automargin=True,
    )

    return fig


# ============================================================
# REUSABLE UI HELPERS
# ============================================================

def section_heading(title, icon="▦", subtitle=None):
    """Display a consistent section heading."""

    st.markdown(
        f"""
        <div class="section-heading">
            <span class="section-heading-icon">{icon}</span>
            <span>{title}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if subtitle:
        st.markdown(
            f'<div class="section-subtitle">{subtitle}</div>',
            unsafe_allow_html=True,
        )


def render_footer():
    """Render the application footer."""

    st.markdown(
        """
        <div class="app-footer">
            <div>
                <strong>SmartEnergy Analytics</strong>
                &nbsp;·&nbsp; Energy intelligence workspace
            </div>
            <div>
                Data-driven energy monitoring and forecasting
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# APPLICATION HEADER
# ============================================================

st.title("⚡ SmartEnergy Analytics")

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
            Explore electricity consumption patterns, investigate
            potential anomalies, forecast future demand, and inspect
            data quality in one integrated analytics workspace.
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
# DATA INITIALIZATION
# EXISTING FUNCTIONALITY PRESERVED
# ============================================================

if not DATA_PATH.exists():

    # Streamlit Community Cloud does not receive local ignored
    # data files or the private .env file. Generate the documented
    # demo dataset on first run so a fresh deployment is usable.

    if DATA_PATH.name == "energy_demo.csv":
        DATA_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        generate_demo(DATA_PATH)

    else:
        st.warning(
            f"No input data found at {DATA_PATH}. "
            "Generate the demo dataset or set DATA_PATH in .env."
        )

        if st.button(
            "Generate documented synthetic demo data",
            type="primary",
            use_container_width=False,
        ):
            generate_demo(DATA_PATH)
            st.rerun()

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
# Existing navigation behavior preserved.
# ============================================================

navigation = [
    "Energy overview",
    "Consumption analytics",
    "Anomaly monitor",
    "Demand forecast",
    "Energy insights",
    "Data quality",
]

nav_search = st.sidebar.text_input(
    "Search workspace",
    placeholder="Search modules...",
    label_visibility="collapsed",
)

filtered_navigation = [
    item
    for item in navigation
    if nav_search.lower() in item.lower()
]

if not filtered_navigation:
    st.sidebar.caption("No matching module")


page = st.session_state.get(
    "active_page",
    navigation[0],
)

st.sidebar.markdown(
    '<div class="sidebar-section-label">WORKSPACE</div>',
    unsafe_allow_html=True,
)

nav_icons = {
    "Energy overview": "⌂",
    "Consumption analytics": "▥",
    "Anomaly monitor": "⌁",
    "Demand forecast": "↗",
    "Energy insights": "✦",
    "Data quality": "✓",
}

for item in filtered_navigation:

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
            f"{nav_icons[item]}   {item}",
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
        icon="▦",
        subtitle=(
            "A high-level snapshot of electricity consumption "
            "and the data currently available."
        ),
    )

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
        "Entities",
        clean.entity_id.nunique(),
    )

    c4.metric(
        "Records",
        f"{len(clean):,}",
    )

    section_heading(
        "Consumption trends",
        icon="↗",
        subtitle=(
            "Track total electricity consumption across the "
            "available daily observation period."
        ),
    )

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
        color_discrete_sequence=CHART_COLORS,
    )

    fig.update_traces(
        line=dict(
            width=3,
            color="#0b9b91",
        ),
        mode="lines+markers",
        marker=dict(
            size=5,
            color="#0b9b91",
            line=dict(
                width=1.5,
                color="#ffffff",
            ),
        ),
        fill="tozeroy",
        fillcolor="rgba(11,155,145,0.07)",
        hovertemplate=(
            "<b>Date:</b> %{x}<br>"
            "<b>Consumption:</b> %{y:,.2f} kWh"
            "<extra></extra>"
        ),
    )

    style_chart(fig)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displaylogo": False,
            "responsive": True,
        },
    )


# ============================================================
# PAGE 2: CONSUMPTION ANALYTICS
# ============================================================

elif page == "Consumption analytics":

    section_heading(
        "Consumption analytics",
        icon="▥",
        subtitle=(
            "Examine hourly usage patterns, compare building-level "
            "consumption, and review average daily readings."
        ),
    )

    a, b = st.columns(2, gap="large")

    with a:

        fig_hourly = px.bar(
            hourly,
            x="hour",
            y="sum",
            title="Hourly total profile",
            labels={
                "hour": "Hour of day",
                "sum": "Consumption (kWh)",
            },
            template=CHART_TEMPLATE,
            color_discrete_sequence=CHART_COLORS,
        )

        fig_hourly.update_traces(
            marker_color="#0b9b91",
            marker_line_width=0,
            opacity=0.90,
            hovertemplate=(
                "<b>Hour:</b> %{x}:00<br>"
                "<b>Consumption:</b> %{y:,.2f} kWh"
                "<extra></extra>"
            ),
        )

        style_chart(fig_hourly)

        st.plotly_chart(
            fig_hourly,
            use_container_width=True,
            config={"displaylogo": False},
        )

    with b:

        fig_entities = px.bar(
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
            color_discrete_sequence=CHART_COLORS,
        )

        fig_entities.update_traces(
            marker_color="#6489c6",
            marker_line_width=0,
            opacity=0.90,
            hovertemplate=(
                "<b>Building:</b> %{x}<br>"
                "<b>Consumption:</b> %{y:,.2f} kWh"
                "<extra></extra>"
            ),
        )

        style_chart(fig_entities)

        st.plotly_chart(
            fig_entities,
            use_container_width=True,
            config={"displaylogo": False},
        )

    section_heading(
        "Daily average readings",
        icon="◷",
        subtitle=(
            "Review how the average consumption reading per record "
            "changes across the observation period."
        ),
    )

    fig_daily = px.line(
        daily,
        x="day",
        y="mean",
        title="Daily average reading per record",
        labels={
            "day": "Date",
            "mean": "Average reading (kWh)",
        },
        template=CHART_TEMPLATE,
        color_discrete_sequence=CHART_COLORS,
    )

    fig_daily.update_traces(
        line=dict(
            color="#6489c6",
            width=3,
        ),
        mode="lines+markers",
        marker=dict(size=5),
        hovertemplate=(
            "<b>Date:</b> %{x}<br>"
            "<b>Average reading:</b> %{y:,.2f} kWh"
            "<extra></extra>"
        ),
    )

    style_chart(fig_daily)

    st.plotly_chart(
        fig_daily,
        use_container_width=True,
        config={"displaylogo": False},
    )


# ============================================================
# PAGE 3: ANOMALY MONITOR
# Detection logic and filtering behavior preserved.
# ============================================================

elif page == "Anomaly monitor":

    section_heading(
        "Anomaly monitor",
        icon="⌁",
        subtitle=(
            "Inspect unusual consumption readings by building "
            "and date range. Candidates require further investigation."
        ),
    )

    c1, c2, c3 = st.columns(
        [1.2, 1, 1],
        gap="medium",
    )

    with c1:

        selected_entity = st.selectbox(
            "Building",
            ["All"] + sorted(
                clean.entity_id.unique().tolist()
            ),
        )

    with c2:

        min_date = st.date_input(
            "From",
            pd.to_datetime(clean.day).min().date(),
        )

    with c3:

        max_date = st.date_input(
            "To",
            pd.to_datetime(clean.day).max().date(),
        )

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

    st.markdown("")

    c1, c2 = st.columns(
        [1, 3],
        vertical_alignment="center",
    )

    with c1:

        st.metric(
            "Candidate anomalies",
            f"{len(scored):,}",
        )

    with c2:

        st.caption(
            "Candidates use a trailing 24-reading mean and "
            "standard deviation per building. They require "
            "investigation and are not confirmed faults, theft, "
            "or wastage."
        )

    section_heading(
        "Consumption deviation",
        icon="⌁",
        subtitle=(
            "Compare observed readings with the expected values "
            "associated with detected anomaly candidates."
        ),
    )

    chart = go.Figure()

    chart.add_trace(
        go.Scatter(
            x=view.timestamp,
            y=view.consumption_kwh,
            name="Actual consumption (kWh)",
            mode="lines",
            line={
                "color": "#0b9b91",
                "width": 2,
            },
            hovertemplate=(
                "<b>Timestamp:</b> %{x}<br>"
                "<b>Actual:</b> %{y:,.2f} kWh"
                "<extra></extra>"
            ),
        )
    )

    chart.add_trace(
        go.Scatter(
            x=scored.timestamp,
            y=scored.expected_kwh,
            mode="markers",
            name="Expected at anomaly",
            marker={
                "color": "#d96565",
                "size": 10,
                "symbol": "diamond",
                "line": {
                    "color": "#ffffff",
                    "width": 1.5,
                },
            },
            hovertemplate=(
                "<b>Timestamp:</b> %{x}<br>"
                "<b>Expected:</b> %{y:,.2f} kWh"
                "<extra></extra>"
            ),
        )
    )

    chart.update_layout(
        title="Actual consumption and detected candidates",
        xaxis_title="Timestamp",
        yaxis_title="Consumption (kWh)",
    )

    style_chart(chart)

    st.plotly_chart(
        chart,
        use_container_width=True,
        config={"displaylogo": False},
    )

    section_heading(
        "Detected candidate records",
        icon="▤",
        subtitle=(
            "Review the individual readings and their anomaly "
            "scores, or export the filtered results."
        ),
    )

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
        "↓  Download filtered anomalies CSV",
        scored[cols].to_csv(index=False),
        "filtered_anomalies.csv",
        "text/csv",
        use_container_width=False,
    )


# ============================================================
# PAGE 4: DEMAND FORECAST
# Forecasting methods and metrics preserved.
# ============================================================

elif page == "Demand forecast":

    section_heading(
        "Demand forecast",
        icon="↗",
        subtitle=(
            "Compare historical electricity demand with future "
            "estimates produced by the existing forecasting methods."
        ),
    )

    result, metrics = forecast(daily)

    section_heading(
        "Forecast evaluation",
        icon="▦",
        subtitle=(
            "Evaluation metrics from the existing forecasting "
            "implementation."
        ),
    )

    st.write(metrics)

    st.info(
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
        color_discrete_sequence=["#0b9b91"],
    )

    chart.update_traces(
        line=dict(width=3),
        name="Historical consumption",
        hovertemplate=(
            "<b>Date:</b> %{x}<br>"
            "<b>Actual:</b> %{y:,.2f} kWh"
            "<extra></extra>"
        ),
    )

    future = result[
        result.kind == "forecast"
    ]

    chart.add_scatter(
        x=future.day,
        y=future.baseline_forecast_kwh,
        name="7-day mean forecast",
        mode="lines+markers",
        line={
            "color": "#e6a23c",
            "width": 2.5,
            "dash": "dash",
        },
        marker={"size": 6},
        hovertemplate=(
            "<b>Date:</b> %{x}<br>"
            "<b>7-day mean:</b> %{y:,.2f} kWh"
            "<extra></extra>"
        ),
    )

    chart.add_scatter(
        x=future.day,
        y=future.seasonal_naive_kwh,
        name="Seasonal-naive forecast",
        mode="lines+markers",
        line={
            "color": "#6489c6",
            "width": 2.5,
            "dash": "dot",
        },
        marker={"size": 6},
        hovertemplate=(
            "<b>Date:</b> %{x}<br>"
            "<b>Seasonal naive:</b> %{y:,.2f} kWh"
            "<extra></extra>"
        ),
    )

    style_chart(chart)

    st.plotly_chart(
        chart,
        use_container_width=True,
        config={"displaylogo": False},
    )


# ============================================================
# PAGE 5: ENERGY INSIGHTS
# Insight generation preserved.
# ============================================================

elif page == "Energy insights":

    section_heading(
        "Energy insights",
        icon="✦",
        subtitle=(
            "Review the observations generated by the existing "
            "energy analytics and insight engine."
        ),
    )

    insight_items = insights(clean)

    if not insight_items:

        st.info(
            "No insights are available for the current dataset."
        )

    else:

        for index, item in enumerate(insight_items, start=1):

            st.markdown(
                f"""
                <div style="
                    display: flex;
                    align-items: flex-start;
                    gap: 14px;

                    margin-bottom: 12px;
                    padding: 18px 20px;

                    background: #ffffff;
                    border: 1px solid #e5eaf1;
                    border-left: 4px solid #0b9b91;
                    border-radius: 13px;

                    box-shadow: 0 2px 8px rgba(16,29,53,0.035);
                ">
                    <div style="
                        display: flex;
                        align-items: center;
                        justify-content: center;

                        min-width: 32px;
                        height: 32px;

                        background: #e5f6f3;
                        color: #087f79;

                        border-radius: 9px;
                        font-size: 0.82rem;
                        font-weight: 800;
                    ">
                        {index:02d}
                    </div>

                    <div style="
                        color: #35445b;
                        font-size: 0.91rem;
                        line-height: 1.75;
                        padding-top: 3px;
                    ">
                        {item}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# PAGE 6: DATA QUALITY
# Quality metadata and download behavior preserved.
# ============================================================

elif page == "Data quality":

    section_heading(
        "Data quality",
        icon="✓",
        subtitle=(
            "Inspect processing metadata, review the quality report, "
            "and download the generated output files."
        ),
    )

    engine = quality.get(
        "engine",
        "unknown",
    )

    processing_status = quality.get(
        "processing_status",
        "unknown",
    )

    duration = quality.get(
        "duration_seconds",
        0,
    )

    dataset_path = quality.get(
        "dataset_path",
        DATA_PATH,
    )

    q1, q2, q3 = st.columns(3)

    with q1:

        st.markdown(
            f"""
            <div class="quality-panel">
                <div class="quality-label">
                    Processing engine
                </div>
                <div class="quality-value">
                    {engine}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with q2:

        st.markdown(
            f"""
            <div class="quality-panel">
                <div class="quality-label">
                    Processing status
                </div>
                <div>
                    <span class="quality-status">
                        {processing_status}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with q3:

        st.markdown(
            f"""
            <div class="quality-panel">
                <div class="quality-label">
                    Processing duration
                </div>
                <div class="quality-value">
                    {duration:.4f} seconds
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="quality-panel">
            <div class="quality-label">
                Source dataset
            </div>
            <div class="quality-value">
                {dataset_path}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if quality.get("engine_error"):

        st.warning(
            "PySpark was unavailable; pandas fallback was used. "
            f"Diagnostic: {quality['engine_error']}"
        )

    section_heading(
        "Quality report",
        icon="▤",
        subtitle=(
            "The original quality-report JSON is displayed below "
            "for complete inspection."
        ),
    )

    st.json(quality)

    section_heading(
        "Export processed data",
        icon="↓",
        subtitle=(
            "Download the existing cleaned dataset or its quality "
            "report for further analysis."
        ),
    )

    d1, d2 = st.columns(2, gap="medium")

    with d1:

        st.download_button(
            "↓  Download cleaned CSV",
            clean.to_csv(index=False),
            "cleaned.csv",
            "text/csv",
            use_container_width=True,
        )

    with d2:

        st.download_button(
            "↓  Download quality JSON",
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

render_footer()

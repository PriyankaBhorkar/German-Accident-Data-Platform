from __future__ import annotations

import html
from textwrap import dedent
from typing import Any

import requests
import streamlit as st
import pandas as pd
import plotly.express as px


STATE_OPTIONS = {
    "01": "Schleswig-Holstein",
    "02": "Hamburg",
    "03": "Niedersachsen",
    "04": "Bremen",
    "05": "Nordrhein-Westfalen",
    "06": "Hessen",
    "07": "Rheinland-Pfalz",
    "08": "Baden-Württemberg",
    "09": "Bayern",
    "10": "Saarland",
    "11": "Berlin",
    "12": "Brandenburg",
    "13": "Mecklenburg-Vorpommern",
    "14": "Sachsen",
    "15": "Sachsen-Anhalt",
    "16": "Thüringen",
}
# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="German Road Safety Intelligence",
    page_icon="🚘",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>
    /* -------------------------------------------------------
       Global application
    ------------------------------------------------------- */

    html,
    body,
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background: #f4f6fb !important;
        color: #172033 !important;
    }

    [data-testid="stHeader"] {
        background: rgba(244, 246, 251, 0.92) !important;
        border-bottom: 1px solid rgba(226, 232, 240, 0.8);
    }

    [data-testid="stToolbar"] {
        right: 1rem;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2.4rem;
        padding-bottom: 4rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }

    footer {
        visibility: hidden;
    }

    /* -------------------------------------------------------
       Sidebar
    ------------------------------------------------------- */

    [data-testid="stSidebar"] {
        background: #171a24 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    [data-testid="stSidebar"] > div:first-child {
        background: #171a24 !important;
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
        padding-left: 1.25rem;
        padding-right: 1.25rem;
    }

    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #e5e7eb;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: 0.72rem 0.75rem;
        margin-bottom: 0.28rem;
        border-radius: 0.72rem;
        transition: all 0.18s ease;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(255, 255, 255, 0.07);
    }

    /* -------------------------------------------------------
       Sidebar branding
    ------------------------------------------------------- */

    .brand-wrapper {
        margin-bottom: 2rem;
    }

    .brand-mark {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 46px;
        height: 46px;
        border-radius: 14px;
        color: #ffffff;
        background: linear-gradient(135deg, #6366f1, #4338ca);
        box-shadow: 0 12px 28px rgba(79, 70, 229, 0.35);
        font-size: 0.92rem;
        font-weight: 800;
        margin-bottom: 1rem;
    }

    .brand-title {
        color: #ffffff;
        font-size: 1rem;
        font-weight: 750;
        line-height: 1.35;
    }

    .brand-subtitle {
        color: #9ca3af;
        font-size: 0.74rem;
        line-height: 1.55;
        margin-top: 0.3rem;
    }

    /* -------------------------------------------------------
       Sidebar status
    ------------------------------------------------------- */

    .sidebar-status {
        margin-top: 2rem;
        padding: 1rem;
        border-radius: 0.85rem;
        background: rgba(255, 255, 255, 0.055);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .status-row {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        color: #d1d5db;
        font-size: 0.75rem;
        font-weight: 650;
    }

    .status-dot-online {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background: #34d399;
        box-shadow: 0 0 0 4px rgba(52, 211, 153, 0.13);
    }

    .status-dot-offline {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background: #f87171;
        box-shadow: 0 0 0 4px rgba(248, 113, 113, 0.13);
    }

    .sidebar-link {
        display: inline-block;
        color: #a5b4fc !important;
        text-decoration: none !important;
        font-size: 0.73rem;
        font-weight: 650;
        margin-top: 0.85rem;
    }

    /* -------------------------------------------------------
       Hero
    ------------------------------------------------------- */

    .hero {
        position: relative;
        overflow: hidden;
        border-radius: 1.4rem;
        padding: 3.2rem 3.3rem;
        margin-bottom: 1.6rem;
        background:
            radial-gradient(
                circle at 88% 15%,
                rgba(129, 140, 248, 0.42),
                transparent 32%
            ),
            linear-gradient(135deg, #111827 0%, #211d52 100%);
        box-shadow: 0 24px 65px rgba(15, 23, 42, 0.16);
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 330px;
        height: 330px;
        right: -100px;
        bottom: -190px;
        border-radius: 50%;
        border: 55px solid rgba(255, 255, 255, 0.04);
    }

    .hero-badge {
        display: inline-block;
        color: #c7d2fe;
        background: rgba(99, 102, 241, 0.18);
        border: 1px solid rgba(165, 180, 252, 0.22);
        border-radius: 999px;
        padding: 0.43rem 0.78rem;
        margin-bottom: 1.2rem;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.1rem;
    }

    .hero-title {
        color: #ffffff;
        max-width: 800px;
        font-size: clamp(2.3rem, 4vw, 3.7rem);
        font-weight: 820;
        line-height: 1.08;
        letter-spacing: -0.05em;
        margin-bottom: 1rem;
    }

    .hero-description {
        color: #cbd5e1;
        max-width: 760px;
        font-size: 1rem;
        line-height: 1.75;
        margin-bottom: 1.75rem;
    }

    .hero-link {
        display: inline-block;
        color: #111827 !important;
        background: #ffffff;
        padding: 0.78rem 1.05rem;
        border-radius: 0.7rem;
        font-size: 0.82rem;
        font-weight: 750;
        text-decoration: none !important;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.18);
        transition: transform 0.15s ease;
    }

    .hero-link:hover {
        transform: translateY(-2px);
    }

    /* -------------------------------------------------------
       Metric cards
    ------------------------------------------------------- */

    .metric-card {
        background: #ffffff;
        border: 1px solid #e4e8f0;
        border-radius: 1rem;
        padding: 1.35rem;
        min-height: 135px;
        box-shadow: 0 9px 28px rgba(15, 23, 42, 0.045);
    }

    .metric-label {
        color: #64748b;
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.06rem;
        margin-bottom: 0.7rem;
    }

    .metric-value {
        color: #172033;
        font-size: 1.72rem;
        font-weight: 820;
        line-height: 1.1;
        letter-spacing: -0.04em;
    }

    .metric-note {
        color: #94a3b8;
        font-size: 0.71rem;
        margin-top: 0.6rem;
    }

    /* -------------------------------------------------------
       Section headings
    ------------------------------------------------------- */

    .section-heading {
        margin-top: 2.4rem;
        margin-bottom: 1.2rem;
    }

    .section-eyebrow {
        color: #4f46e5;
        font-size: 0.68rem;
        font-weight: 850;
        letter-spacing: 0.11rem;
        text-transform: uppercase;
        margin-bottom: 0.38rem;
    }

    .section-title {
        color: #172033;
        font-size: 1.65rem;
        font-weight: 820;
        letter-spacing: -0.035em;
    }

    .section-description {
        color: #64748b;
        font-size: 0.9rem;
        line-height: 1.65;
        max-width: 800px;
        margin-top: 0.35rem;
    }

    /* -------------------------------------------------------
       Feature cards
    ------------------------------------------------------- */

    .feature-card {
        background: #ffffff;
        border: 1px solid #e4e8f0;
        border-radius: 1rem;
        padding: 1.5rem;
        min-height: 215px;
        height: 100%;
        box-shadow: 0 9px 28px rgba(15, 23, 42, 0.04);
    }

    .feature-number {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        color: #4338ca;
        background: #eef2ff;
        border-radius: 11px;
        font-size: 0.72rem;
        font-weight: 850;
        margin-bottom: 1.1rem;
    }

    .feature-title {
        color: #172033;
        font-size: 1rem;
        font-weight: 780;
        margin-bottom: 0.65rem;
    }

    .feature-description {
        color: #64748b;
        font-size: 0.83rem;
        line-height: 1.7;
    }

    /* -------------------------------------------------------
       Architecture
    ------------------------------------------------------- */

    .architecture-card {
        background: #ffffff;
        border: 1px solid #e4e8f0;
        border-radius: 0.95rem;
        padding: 1.25rem;
        min-height: 145px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.035);
    }

    .architecture-step {
        color: #4f46e5;
        font-size: 0.65rem;
        font-weight: 850;
        letter-spacing: 0.09rem;
        margin-bottom: 0.6rem;
    }

    .architecture-name {
        color: #172033;
        font-size: 0.95rem;
        font-weight: 780;
        margin-bottom: 0.42rem;
    }

    .architecture-text {
        color: #64748b;
        font-size: 0.75rem;
        line-height: 1.6;
    }

    /* -------------------------------------------------------
       Inner pages
    ------------------------------------------------------- */

    .page-header {
        background: #ffffff;
        border: 1px solid #e4e8f0;
        border-radius: 1.1rem;
        padding: 1.8rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 8px 25px rgba(15, 23, 42, 0.035);
    }

    .page-title {
        color: #172033;
        font-size: 1.85rem;
        font-weight: 820;
        letter-spacing: -0.04em;
        margin-bottom: 0.5rem;
    }

    .page-description {
        color: #64748b;
        font-size: 0.9rem;
        line-height: 1.65;
        max-width: 850px;
    }

    .empty-panel {
        background: #ffffff;
        border: 1px dashed #cbd5e1;
        border-radius: 1rem;
        padding: 4rem 2rem;
        text-align: center;
        color: #64748b;
        font-size: 0.9rem;
    }

    .footer-text {
        color: #94a3b8;
        text-align: center;
        font-size: 0.7rem;
        padding-top: 3rem;
        padding-bottom: 1rem;
    }

    /* -------------------------------------------------------
       Responsive behaviour
    ------------------------------------------------------- */

    @media (max-width: 900px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .hero {
            padding: 2.2rem 1.8rem;
        }

        .hero-title {
            font-size: 2.2rem;
        }
    }

    /* ==========================================================
   STREAMLIT WIDGET COLOR FIX
========================================================== */

/* Force the main application to use light native controls */
html,
body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    color-scheme: light !important;
    background-color: #F4F6FB !important;
    color: #172033 !important;
}

/* Keep sidebar dark */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div:first-child {
    background-color: #171A24 !important;
    color-scheme: dark !important;
}

/* Main-area text */
[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4,
[data-testid="stMain"] p,
[data-testid="stMain"] span,
[data-testid="stMain"] label {
    color: #172033;
}

/* Professional form card */
[data-testid="stMain"] [data-testid="stForm"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 16px !important;
    padding: 1.5rem 1.5rem 1rem 1.5rem !important;
    box-shadow: 0 8px 28px rgba(15, 23, 42, 0.055) !important;
    margin-top: 1rem !important;
}

/* Widget labels */
[data-testid="stMain"] .stWidgetLabel p,
[data-testid="stMain"] label p,
[data-testid="stMain"] .stNumberInput label p,
[data-testid="stMain"] .stSlider label p,
[data-testid="stMain"] .stSelectbox label p,
[data-testid="stMain"] .stCheckbox label p {
    color: #334155 !important;
    font-size: 0.82rem !important;
    font-weight: 650 !important;
}

/* Number input container */
[data-testid="stMain"] div[data-baseweb="input"] {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 10px !important;
    overflow: hidden !important;
    box-shadow: none !important;
}

/* Number input actual text */
[data-testid="stMain"] div[data-baseweb="input"] input {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
    caret-color: #4F46E5 !important;
    font-weight: 600 !important;
}

/* Plus and minus buttons */
[data-testid="stMain"] .stNumberInput button {
    background-color: #F8FAFC !important;
    color: #334155 !important;
    border-left: 1px solid #E2E8F0 !important;
}

[data-testid="stMain"] .stNumberInput button:hover {
    background-color: #EEF2FF !important;
    color: #4338CA !important;
}

[data-testid="stMain"] .stNumberInput button svg {
    fill: #334155 !important;
    color: #334155 !important;
}

/* Select boxes */
[data-testid="stMain"] div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border-color: #CBD5E1 !important;
    color: #0F172A !important;
    border-radius: 10px !important;
}

[data-testid="stMain"] div[data-baseweb="select"] span {
    color: #0F172A !important;
}

/* Dropdown menu */
div[data-baseweb="popover"] {
    color-scheme: light !important;
}

div[data-baseweb="popover"] ul {
    background-color: #FFFFFF !important;
}

div[data-baseweb="popover"] li {
    background-color: #FFFFFF !important;
    color: #172033 !important;
}

div[data-baseweb="popover"] li:hover {
    background-color: #EEF2FF !important;
}

/* Slider */
[data-testid="stMain"] .stSlider {
    color: #334155 !important;
}

[data-testid="stMain"] .stSlider [role="slider"] {
    background-color: #4F46E5 !important;
    border: 2px solid #FFFFFF !important;
    box-shadow: 0 0 0 2px #4F46E5 !important;
}

[data-testid="stMain"] .stSlider [data-testid="stThumbValue"] {
    color: #4F46E5 !important;
    font-weight: 700 !important;
}

/* Checkbox */
[data-testid="stMain"] .stCheckbox p {
    color: #334155 !important;
}

/* Main form button */
[data-testid="stMain"] [data-testid="stFormSubmitButton"] button,
[data-testid="stMain"] .stButton button {
    width: 100% !important;
    min-height: 44px !important;
    background: linear-gradient(
        135deg,
        #4F46E5,
        #4338CA
    ) !important;
    border: 1px solid #4338CA !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    box-shadow: 0 7px 18px rgba(79, 70, 229, 0.2) !important;
    transition:
        transform 0.15s ease,
        box-shadow 0.15s ease !important;
}

/* Force all button child text to white */
[data-testid="stMain"] [data-testid="stFormSubmitButton"] button *,
[data-testid="stMain"] .stButton button * {
    color: #FFFFFF !important;
}

/* Button hover */
[data-testid="stMain"] [data-testid="stFormSubmitButton"] button:hover,
[data-testid="stMain"] .stButton button:hover {
    background: linear-gradient(
        135deg,
        #4338CA,
        #3730A3
    ) !important;
    border-color: #3730A3 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 10px 22px rgba(79, 70, 229, 0.28) !important;
}

/* Disabled button */
[data-testid="stMain"] button:disabled {
    background: #CBD5E1 !important;
    border-color: #CBD5E1 !important;
    color: #64748B !important;
    box-shadow: none !important;
}

/* Metric widgets */
[data-testid="stMain"] [data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 14px !important;
    padding: 1.15rem !important;
    box-shadow: 0 7px 22px rgba(15, 23, 42, 0.045) !important;
}

[data-testid="stMain"] [data-testid="stMetricLabel"] p {
    color: #64748B !important;
}

[data-testid="stMain"] [data-testid="stMetricValue"] {
    color: #172033 !important;
}

/* Dataframe background */
[data-testid="stMain"] [data-testid="stDataFrame"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* Alert boxes */
[data-testid="stMain"] [data-testid="stAlert"] {
    background-color: #FFFFFF !important;
    color: #172033 !important;
    border-radius: 12px !important;
}

/* Spinner text */
[data-testid="stMain"] [data-testid="stSpinner"] p {
    color: #475569 !important;
}

/* Footer */
.footer-text {
    color: #94A3B8 !important;
}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HTML RENDERING
# ============================================================

def render_html(markup: str) -> None:
    """
    Render HTML without Streamlit interpreting indented lines
    as Markdown code blocks.
    """

    cleaned_markup = "\n".join(
        line.strip()
        for line in dedent(markup).splitlines()
        if line.strip()
    )

    st.markdown(
        cleaned_markup,
        unsafe_allow_html=True,
    )


def safe(value: object) -> str:
    return html.escape(str(value))


# ============================================================
# API CLIENT
# ============================================================

@st.cache_data(ttl=30, show_spinner=False)
def api_get(
    endpoint: str,
    params: dict[str, Any] | None = None,
) -> tuple[Any | None, str | None]:

    try:
        response = requests.get(
            f"{BASE_URL}{endpoint}",
            params=params,
            timeout=10,
        )

        if response.status_code == 404:
            try:
                message = response.json().get(
                    "detail",
                    "No matching data was found.",
                )
            except ValueError:
                message = "No matching data was found."

            return None, message

        if response.status_code == 422:
            return None, "The API rejected one or more request parameters."

        response.raise_for_status()

        return response.json(), None

    except requests.exceptions.ConnectionError:
        return (
            None,
            "The FastAPI backend is unavailable. "
            "Start it on http://127.0.0.1:8000.",
        )

    except requests.exceptions.Timeout:
        return None, "The API request timed out."

    except requests.exceptions.RequestException as exc:
        return None, f"API request failed: {exc}"

    except ValueError:
        return None, "The API returned invalid JSON."


# ============================================================
# REUSABLE COMPONENTS
# ============================================================

def metric_card(
    label: str,
    value: object,
    note: str,
) -> None:

    render_html(
        f"""
        <div class="metric-card">
        <div class="metric-label">{safe(label)}</div>
        <div class="metric-value">{safe(value)}</div>
        <div class="metric-note">{safe(note)}</div>
        </div>
        """
    )


def section_heading(
    eyebrow: str,
    title: str,
    description: str,
) -> None:

    render_html(
        f"""
        <div class="section-heading">
        <div class="section-eyebrow">{safe(eyebrow)}</div>
        <div class="section-title">{safe(title)}</div>
        <div class="section-description">{safe(description)}</div>
        </div>
        """
    )


def feature_card(
    number: str,
    title: str,
    description: str,
) -> None:

    render_html(
        f"""
        <div class="feature-card">
        <div class="feature-number">{safe(number)}</div>
        <div class="feature-title">{safe(title)}</div>
        <div class="feature-description">{safe(description)}</div>
        </div>
        """
    )


def architecture_card(
    step: str,
    name: str,
    description: str,
) -> None:

    render_html(
        f"""
        <div class="architecture-card">
        <div class="architecture-step">{safe(step)}</div>
        <div class="architecture-name">{safe(name)}</div>
        <div class="architecture-text">{safe(description)}</div>
        </div>
        """
    )


def page_header(
    title: str,
    description: str,
) -> None:

    render_html(
        f"""
        <div class="page-header">
        <div class="page-title">{safe(title)}</div>
        <div class="page-description">{safe(description)}</div>
        </div>
        """
    )


def placeholder_panel(message: str) -> None:

    render_html(
        f"""
        <div class="empty-panel">
        {safe(message)}
        </div>
        """
    )


# ============================================================
# LOAD PLATFORM INFORMATION
# ============================================================

root_data, root_error = api_get("/")
earliest_data, earliest_error = api_get(
    "/statistics/earliest-year"
)
sources_data, sources_error = api_get(
    "/metadata/sources"
)
import_runs_data, import_runs_error = api_get(
    "/import-runs"
)
api_online = (
    isinstance(root_data, dict)
    and root_data.get("status") == "running"
)

api_version = (
    root_data.get("version", "—")
    if isinstance(root_data, dict)
    else "—"
)

earliest_year = (
    earliest_data.get("earliest_year", "—")
    if isinstance(earliest_data, dict)
    else "—"
)

source_count = (
    len(sources_data)
    if isinstance(sources_data, list)
    else "—"
)

total_import_runs = (
    len(import_runs_data)
    if isinstance(import_runs_data, list)
    else 0
)

total_records_imported = 0
latest_import_source = "—"
latest_import_status = "—"

if isinstance(import_runs_data, list) and import_runs_data:

    for import_run in import_runs_data:

        records_imported = import_run.get(
            "records_imported",
            0,
        )

        if records_imported is not None:

            try:
                total_records_imported += int(
                    records_imported
                )
            except (TypeError, ValueError):
                pass

    latest_import_run = max(
        import_runs_data,
        key=lambda item: item.get(
            "run_id",
            0,
        ),
    )

    latest_import_source = latest_import_run.get(
        "source_name",
        "—",
    )

    latest_import_status = latest_import_run.get(
        "status",
        "—",
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    render_html(
        """
        <div class="brand-wrapper">
        <div class="brand-title">Integrated German Road Accident Analysis</div>
        </div>
        """
    )

    selected_page = st.radio(
        "Navigation",
        [
            "Overview",
            "Assignment questions",
            "Fatal Accident Ranking",
            "Bicycle District Ranking",
            "Accident explorer",
            "Regional accident rates",

        ],
        label_visibility="collapsed",
    )

    status_class = (
        "status-dot-online"
        if api_online
        else "status-dot-offline"
    )

    status_text = (
        "FastAPI connected"
        if api_online
        else "FastAPI unavailable"
    )

    render_html(
        f"""
        <div class="sidebar-status">
        <div class="status-row">
        <span class="{status_class}"></span>
        <span>{safe(status_text)}</span>
        </div>
        <a
        class="sidebar-link"
        href="{BASE_URL}/docs"
        target="_blank"
        >
        Open API documentation ↗
        </a>
        </div>
        """
    )


# ============================================================
# OVERVIEW PAGE
# ============================================================

if selected_page == "Overview":

    render_html(
        f"""
        <div class="hero">
        
        <div class="hero-title">
        German Accident Data Platform
        </div>
        <div class="hero-description">
        A data-driven platform combining accident events, regional statistics and official geographic reference data for reproducible analysis.
        </div>
        <a
        class="hero-link"
        href="{BASE_URL}/docs"
        target="_blank"
        >
        Explore API documentation ↗
        </a>
        </div>
        """
    )

    metric_columns = st.columns(5)

    with metric_columns[0]:
        metric_card(
            "API STATUS",
            "Online" if api_online else "Offline",
            "FastAPI backend connection",
        )

    with metric_columns[1]:
        metric_card(
            "API VERSION",
            api_version,
            "Current service release",
        )

    with metric_columns[2]:
        metric_card(
            "REGISTERED SOURCES",
            source_count,
            "Datasets tracked with provenance",
        )
    
    with metric_columns[3]:

        metric_card(
            "RECORDS IMPORTED",
            f"{total_records_imported:,}",
            "Records in import history",
        )

    with metric_columns[4]:

        metric_card(
            "IMPORT RUNS",
            total_import_runs,
            "Recorded data-loading operations",
        )

   
    # ========================================================
    # SOURCES AND IMPORT HISTORY TABS
    # ========================================================

    st.markdown(
        "<div style='height: 14px'></div>",
        unsafe_allow_html=True,
    )

    source_tab, import_tab = st.tabs(
        [
            "Data sources",
            "Recent import runs",
        ]
    )

    # --------------------------------------------------------
    # DATA SOURCES TAB
    # --------------------------------------------------------

    with source_tab:

        st.markdown(
            "### Registered datasets"
        )

        st.caption(
            "Source metadata stored in the database, including "
            "dataset type, original location and licence."
        )

        if isinstance(sources_data, list) and sources_data:

            source_df = pd.DataFrame(
                sources_data
            )

            source_column_mapping = {
                "source_id": "Source ID",
                "name": "Dataset",
                "source_type": "Source type",
                "url": "Original URL",
                "license": "Licence",
            }

            source_df = source_df.rename(
                columns=source_column_mapping
            )

            available_source_columns = [
                column
                for column in source_column_mapping.values()
                if column in source_df.columns
            ]

            st.dataframe(
                source_df[
                    available_source_columns
                ],
                use_container_width=True,
                hide_index=True,
            )

        elif sources_error:

            st.error(
                sources_error
            )

        else:

            st.info(
                "No source metadata is currently available."
            )

    # --------------------------------------------------------
    # IMPORT HISTORY TAB
    # --------------------------------------------------------

    with import_tab:

        st.markdown(
            "### Latest dataset imports"
        )

        st.caption(
            "Recent import operations recorded by the backend."
        )

        if (
            isinstance(import_runs_data, list)
            and import_runs_data
        ):

            import_df = pd.DataFrame(
                import_runs_data
            )

            import_column_mapping = {
                "run_id": "Run ID",
                "source_name": "Dataset",
                "started_at": "Started",
                "finished_at": "Finished",
                "records_imported": "Records imported",
                "status": "Status",
                "notes": "Notes",
            }

            import_df = import_df.rename(
                columns=import_column_mapping
            )

            if "Run ID" in import_df.columns:

                import_df = import_df.sort_values(
                    by="Run ID",
                    ascending=False,
                )

            import_df = import_df.head(6)

            available_import_columns = [
                column
                for column in import_column_mapping.values()
                if column in import_df.columns
            ]

            st.dataframe(
                import_df[
                    available_import_columns
                ],
                use_container_width=True,
                hide_index=True,
            )

            st.markdown(
                (
                    f"**Latest imported dataset:** "
                    f"{latest_import_source}  \n"
                    f"**Latest import status:** "
                    f"{latest_import_status}"
                )
            )

        elif import_runs_error:

            st.error(
                import_runs_error
            )

        else:

            st.info(
                "No import history is currently available."
            )

    if root_error:
        st.error(root_error)



# ============================================================
# MANDATORY QUESTIONS PAGE
# ============================================================

elif selected_page == "Assignment questions":

    page_header(
        "Mandatory assignment questions",
        (
            "Select one of the five mandatory project questions "
            "to retrieve its answer directly from the FastAPI service."
        ),
    )

    mandatory_questions = {
        "Question 1 — Earliest accident year": 1,
        (
            "Question 2 — Personal-injury accidents "
            "in Saxony in 2023"
        ): 2,
        (
            "Question 3 — Data availability for "
            "North Rhine-Westphalia"
        ): 3,
        (
            "Question 4 — Data availability for "
            "Mecklenburg-Western Pomerania"
        ): 4,
        (
            "Question 5 — Pedestrian accidents "
            "in Berlin in 2023"
        ): 5,
    }

    selected_question_label = st.radio(
        "Select a mandatory question",
        options=list(mandatory_questions.keys()),
        key="mandatory_question_selector",
    )

    selected_question = mandatory_questions[
        selected_question_label
    ]

    st.markdown(
        "<div style='height: 12px'></div>",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # QUESTION 1
    # --------------------------------------------------------

    if selected_question == 1:

        section_heading(
            "Question 1",
            (
                "What is the earliest accident year "
                "in the complete dataset?"
            ),
            (
                "The result is determined from the minimum year "
                "available in the integrated accident table."
            ),
        )

        with st.spinner(
            "Loading the earliest accident year..."
        ):

            question_data, question_error = api_get(
                "/statistics/earliest-year"
            )

        if question_error:

            st.error(question_error)

        elif isinstance(question_data, dict):

            earliest_question_year = question_data.get(
                "earliest_year"
            )

            result_col1, result_col2 = st.columns(
                [1, 2],
                gap="large",
            )

            with result_col1:

                st.metric(
                    "Earliest accident year",
                    earliest_question_year
                    if earliest_question_year is not None
                    else "—",
                )

            with result_col2:

                st.success(
                    f"The earliest accident year in the complete "
                    f"dataset is {earliest_question_year}."
                )

            with st.expander(
                "API request and method"
            ):

                st.code(
                    "GET /statistics/earliest-year",
                    language="text",
                )

                st.write(
                    "The endpoint calculates the minimum value "
                    "of the accident year column."
                )

    # --------------------------------------------------------
    # QUESTION 2
    # --------------------------------------------------------

    elif selected_question == 2:

        section_heading(
            "Question 2",
            (
                "How many accidents involving personal injury "
                "occurred in Saxony in 2023?"
            ),
            (
                "The query filters accident events by year 2023 "
                "and Saxony's AGS state code 14."
            ),
        )

        with st.spinner(
            "Counting accidents in Saxony..."
        ):

            question_data, question_error = api_get(
                "/accidents/filter-by-category",
                params={
                    "year": 2023,
                    "state_code": "14",
                },
            )

        if question_error:

            st.error(question_error)

        elif isinstance(question_data, dict):

            accident_count = int(
                question_data.get(
                    "accident_count",
                    0,
                )
            )

            result_col1, result_col2 = st.columns(
                [1, 2],
                gap="large",
            )

            with result_col1:

                st.metric(
                    "Personal-injury accidents",
                    f"{accident_count:,}",
                )

            with result_col2:

                st.success(
                    f"{accident_count:,} accidents involving "
                    f"personal injury occurred in Saxony in 2023."
                )

            with st.expander(
                "API request and method"
            ):

                st.code(
                    (
                        "GET /accidents/filter-by-category"
                        "?year=2023&state_code=14"
                    ),
                    language="text",
                )

                st.write(
                    "The imported Unfallatlas event records "
                    "represent accidents involving personal injury. "
                    "Therefore, no individual severity category "
                    "is selected for this question."
                )

    # --------------------------------------------------------
    # QUESTION 3
    # --------------------------------------------------------

    elif selected_question == 3:

        section_heading(
            "Question 3",
            (
                "From which year onwards is data available for "
                "North Rhine-Westphalia?"
            ),
            (
                "The endpoint determines the earliest accident year "
                "for AGS state code 05."
            ),
        )

        with st.spinner(
            "Checking data availability for "
            "North Rhine-Westphalia..."
        ):

            question_data, question_error = api_get(
                "/statistics/state-earliest/05"
            )

        if question_error:

            st.error(question_error)

        elif isinstance(question_data, dict):

            available_year = question_data.get(
                "earliest_year"
            )

            state_name = question_data.get(
                "state_name",
                "North Rhine-Westphalia",
            )

            result_col1, result_col2 = st.columns(
                [1, 2],
                gap="large",
            )

            with result_col1:

                st.metric(
                    "Earliest available year",
                    available_year
                    if available_year is not None
                    else "—",
                )

            with result_col2:

                if available_year is None:

                    st.warning(
                        f"No accident data was found for "
                        f"{state_name}."
                    )

                else:

                    st.success(
                        f"Accident data for {state_name} is "
                        f"available from {available_year} onwards."
                    )

            with st.expander(
                "API request and method"
            ):

                st.code(
                    "GET /statistics/state-earliest/05",
                    language="text",
                )

                st.write(
                    "The endpoint filters regions beginning with "
                    "state code 05 and returns the minimum year."
                )

    # --------------------------------------------------------
    # QUESTION 4
    # --------------------------------------------------------

    elif selected_question == 4:

        section_heading(
            "Question 4",
            (
                "From which year onwards is data available for "
                "Mecklenburg-Western Pomerania?"
            ),
            (
                "The endpoint determines the earliest accident year "
                "for AGS state code 13."
            ),
        )

        with st.spinner(
            "Checking data availability for "
            "Mecklenburg-Western Pomerania..."
        ):

            question_data, question_error = api_get(
                "/statistics/state-earliest/13"
            )

        if question_error:

            st.error(question_error)

        elif isinstance(question_data, dict):

            available_year = question_data.get(
                "earliest_year"
            )

            state_name = question_data.get(
                "state_name",
                "Mecklenburg-Western Pomerania",
            )

            result_col1, result_col2 = st.columns(
                [1, 2],
                gap="large",
            )

            with result_col1:

                st.metric(
                    "Earliest available year",
                    available_year
                    if available_year is not None
                    else "—",
                )

            with result_col2:

                if available_year is None:

                    st.warning(
                        f"No accident data was found for "
                        f"{state_name}."
                    )

                else:

                    st.success(
                        f"Accident data for {state_name} is "
                        f"available from {available_year} onwards."
                    )

            with st.expander(
                "API request and method"
            ):

                st.code(
                    "GET /statistics/state-earliest/13",
                    language="text",
                )

                st.write(
                    "The endpoint filters regions beginning with "
                    "state code 13 and returns the minimum year."
                )

    # --------------------------------------------------------
    # QUESTION 5
    # --------------------------------------------------------

    elif selected_question == 5:

        section_heading(
            "Question 5",
            (
                "How many accidents involving pedestrians "
                "occurred in Berlin in 2023?"
            ),
            (
                "The query filters Berlin accident records from "
                "2023 using the pedestrian-involvement flag."
            ),
        )

        with st.spinner(
            "Counting pedestrian accidents in Berlin..."
        ):

            question_data, question_error = api_get(
                "/accidents/filter-by-category",
                params={
                    "year": 2023,
                    "state_code": "11",
                    "participant": "pedestrian",
                },
            )

        if question_error:

            st.error(question_error)

        elif isinstance(question_data, dict):

            accident_count = int(
                question_data.get(
                    "accident_count",
                    0,
                )
            )

            result_col1, result_col2 = st.columns(
                [1, 2],
                gap="large",
            )

            with result_col1:

                st.metric(
                    "Pedestrian-involved accidents",
                    f"{accident_count:,}",
                )

            with result_col2:

                st.success(
                    f"{accident_count:,} accidents involving "
                    f"pedestrians occurred in Berlin in 2023."
                )

            with st.expander(
                "API request and method"
            ):

                st.code(
                    (
                        "GET /accidents/filter-by-category"
                        "?year=2023&state_code=11"
                        "&participant=pedestrian"
                    ),
                    language="text",
                )

                st.write(
                    "The endpoint uses Berlin's state code 11 "
                    "and the pedestrian participant flag."
                )

# ============================================================
# REGIONAL ACCIDENT RATES PAGE
# ============================================================

elif selected_page == "Regional accident rates":

    page_header(
        "Regional accident rates",
        (
            "Compare official accidents-per-10,000-inhabitants "
            "indicators across German regions for a selected year."
        ),
    )

    with st.form("regional_rates_form"):

        col1, col2 = st.columns([2, 1])

        with col1:
            selected_year = st.number_input(
                "Analysis year",
                min_value=2000,
                max_value=2100,
                value=2023,
                step=1,
            )

        with col2:
            selected_limit = st.slider(
                "Number of regions",
                min_value=1,
                max_value=50,
                value=10,
            )

        load_rates = st.form_submit_button(
            "Load regional rates",
            use_container_width=True,
        )

    if load_rates:

        with st.spinner("Loading regional accident rates..."):

            rates_data, rates_error = api_get(
                f"/statistics/rates/{selected_year}",
                params={
                    "limit": selected_limit,
                },
            )

        if rates_error:

            st.error(rates_error)

        elif not rates_data:

            st.info(
                "No regional accident-rate data was returned "
                "for the selected year."
            )

        else:

            rates_df = pd.DataFrame(rates_data["results"])

            rate_column = "accidents_per_10000_inhabitants"

            rates_df[rate_column] = pd.to_numeric(
                rates_df[rate_column],
                errors="coerce",
            )

            rates_df = rates_df.dropna(
                subset=[rate_column]
            )

            highest_row = rates_df.loc[
                rates_df[rate_column].idxmax()
            ]

            metric_col1, metric_col2, metric_col3 = st.columns(3)

            metric_col1.metric(
                "Regions returned",
                len(rates_df),
            )

            metric_col2.metric(
                "Highest rate",
                f"{highest_row[rate_column]:.2f}",
                help="Accidents per 10,000 inhabitants",
            )

            metric_col3.metric(
                "Highest-rate region",
                highest_row["region_name"],
            )

            st.subheader("Regional ranking")

            chart_df = rates_df.sort_values(
                rate_column,
                ascending=True,
            )

            figure = px.bar(
                chart_df,
                x=rate_column,
                y="region_name",
                orientation="h",
                text=rate_column,
                template="plotly_white",
                color_discrete_sequence=["#5B5CEB"],
                labels={
                    "region_name": "Region",
                    rate_column: "Accidents per 10,000 inhabitants",
                },
            )

            figure.update_traces(
                marker_color="#5B5CEB",
                marker_line_color="#4F46E5",
                marker_line_width=0.5,
                texttemplate="%{text:.2f}",
                textposition="outside",
                textfont={
                    "color": "#172033",
                    "size": 12,
                },
                cliponaxis=False,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Accidents per 10,000 inhabitants: %{x:.2f}"
                    "<extra></extra>"
                ),
            )

            figure.update_layout(
                height=max(460, len(chart_df) * 48),
                margin={
                    "l": 30,
                    "r": 90,
                    "t": 20,
                    "b": 50,
                },
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font={
                    "family": "Arial, sans-serif",
                    "color": "#172033",
                    "size": 13,
                },
                showlegend=False,
                bargap=0.22,
                hoverlabel={
                    "bgcolor": "#172033",
                    "font_color": "#FFFFFF",
                    "font_size": 13,
                },
            )

            figure.update_xaxes(
                title_font={
                    "color": "#334155",
                    "size": 13,
                },
                tickfont={
                    "color": "#475569",
                    "size": 11,
                },
                gridcolor="#E2E8F0",
                zerolinecolor="#CBD5E1",
                linecolor="#CBD5E1",
                showline=True,
            )

            figure.update_yaxes(
                title_font={
                    "color": "#334155",
                    "size": 13,
                },
                tickfont={
                    "color": "#334155",
                    "size": 12,
                },
                gridcolor="rgba(0,0,0,0)",
                linecolor="#CBD5E1",
                showline=False,
            )

            with st.container(border=True):
                st.plotly_chart(
                    figure,
                    use_container_width=True,
                    theme=None,
                    config={
                        "displayModeBar": False,
                        "responsive": True,
                    },
                )



# ============================================================
# FATAL ACCIDENT DISTRICTS PAGE
# ============================================================

elif selected_page == "Fatal Accident Ranking":

    page_header(
        "Fatal accident district ranking",
        (
            "Identify districts with the highest fatal accident "
            "counts and compare them with official regional "
            "accident rates."
        ),
    )

    # --------------------------------------------------------
    # FILTER FORM
    # --------------------------------------------------------

    with st.form("fatal_district_form"):

        filter_col1, filter_col2 = st.columns(
            [2, 1],
            gap="large",
        )

        with filter_col1:

            fatal_year = st.number_input(
                "Analysis year",
                min_value=2000,
                max_value=2100,
                value=2023,
                step=1,
                key="fatal_district_year",
            )

        with filter_col2:

            fatal_limit = st.slider(
                "Number of districts",
                min_value=1,
                max_value=50,
                value=10,
                step=1,
                key="fatal_district_limit",
            )

        load_fatal = st.form_submit_button(
            "Load fatal district ranking",
            use_container_width=True,
        )

    # --------------------------------------------------------
    # API REQUEST AND RESULTS
    # --------------------------------------------------------

    if load_fatal:

        with st.spinner(
            "Combining accident events and regional indicators..."
        ):

            fatal_data, fatal_error = api_get(
                (
                    "/statistics/integrated/"
                    f"fatal-districts/{int(fatal_year)}"
                ),
                params={
                    "limit": int(fatal_limit),
                },
            )

        if fatal_error:

            st.error(fatal_error)

        elif not isinstance(fatal_data, dict):

            st.warning(
                "The API returned an unexpected response format."
            )

        else:

            fatal_results = fatal_data.get(
                "results",
                [],
            )

            if not fatal_results:

                st.info(
                    "No fatal accident district results were found "
                    "for the selected year."
                )

            else:

                # ------------------------------------------------
                # PREPARE DATAFRAME
                # ------------------------------------------------

                fatal_df = pd.DataFrame(
                    fatal_results
                )

                numeric_columns = [
                    "rank",
                    "total_accidents",
                    "fatal_accidents",
                    "accidents_per_10000_inhabitants",
                ]

                for column in numeric_columns:

                    if column in fatal_df.columns:

                        fatal_df[column] = pd.to_numeric(
                            fatal_df[column],
                            errors="coerce",
                        )

                fatal_df = fatal_df.dropna(
                    subset=[
                        "fatal_accidents",
                        "district_name",
                    ]
                )

                if fatal_df.empty:

                    st.info(
                        "The API returned results, but no valid "
                        "district values could be displayed."
                    )

                else:

                    highest_row = fatal_df.loc[
                        fatal_df[
                            "fatal_accidents"
                        ].idxmax()
                    ]

                    # --------------------------------------------
                    # KPI CARDS
                    # --------------------------------------------

                    metric_col1, metric_col2, metric_col3 = (
                        st.columns(
                            3,
                            gap="medium",
                        )
                    )

                    with metric_col1:

                        st.metric(
                            "Districts analysed",
                            len(fatal_df),
                        )

                    with metric_col2:

                        st.metric(
                            "Highest fatal count",
                            int(
                                highest_row[
                                    "fatal_accidents"
                                ]
                            ),
                        )

                    with metric_col3:

                        st.metric(
                            "Highest-ranked district",
                            highest_row[
                                "district_name"
                            ],
                        )

                    # --------------------------------------------
                    # FATAL ACCIDENT CHART
                    # --------------------------------------------

                    st.markdown(
                        "## Fatal accident ranking"
                    )

                    fatal_chart_df = fatal_df.sort_values(
                        by="fatal_accidents",
                        ascending=True,
                    )

                    maximum_fatal_value = float(
                        fatal_chart_df[
                            "fatal_accidents"
                        ].max()
                    )

                    fatal_figure = px.bar(
                        fatal_chart_df,
                        x="fatal_accidents",
                        y="district_name",
                        orientation="h",
                        text="fatal_accidents",
                        template="plotly_white",
                        color_discrete_sequence=[
                            "#5B5CEB"
                        ],
                        custom_data=[
                            "total_accidents",
                            "accidents_per_10000_inhabitants",
                        ],
                        labels={
                            "district_name": "District",
                            "fatal_accidents": (
                                "Fatal accidents"
                            ),
                            "total_accidents": (
                                "Total accidents"
                            ),
                            "accidents_per_10000_inhabitants": (
                                "Accidents per 10,000 inhabitants"
                            ),
                        },
                    )

                    fatal_figure.update_traces(
                        marker_color="#5B5CEB",
                        marker_line_color="#4F46E5",
                        marker_line_width=0.5,
                        texttemplate="%{text:.0f}",
                        textposition="outside",
                        textfont={
                            "color": "#172033",
                            "size": 12,
                        },
                        cliponaxis=False,
                        hovertemplate=(
                            "<b>%{y}</b><br>"
                            "Fatal accidents: %{x:.0f}<br>"
                            "Total accidents: "
                            "%{customdata[0]:.0f}<br>"
                            "Rate per 10,000 inhabitants: "
                            "%{customdata[1]:.2f}"
                            "<extra></extra>"
                        ),
                    )

                    fatal_figure.update_layout(
                        height=max(
                            500,
                            len(fatal_chart_df) * 52,
                        ),
                        margin={
                            "l": 40,
                            "r": 90,
                            "t": 25,
                            "b": 60,
                        },
                        paper_bgcolor="#FFFFFF",
                        plot_bgcolor="#FFFFFF",
                        font={
                            "family": (
                                "Arial, sans-serif"
                            ),
                            "color": "#172033",
                            "size": 13,
                        },
                        showlegend=False,
                        bargap=0.22,
                        hoverlabel={
                            "bgcolor": "#172033",
                            "bordercolor": "#172033",
                            "font_color": "#FFFFFF",
                            "font_size": 13,
                        },
                    )

                    fatal_figure.update_xaxes(
                        title_text="Fatal accidents",
                        range=[
                            0,
                            maximum_fatal_value * 1.12,
                        ],
                        title_font={
                            "color": "#334155",
                            "size": 13,
                        },
                        tickfont={
                            "color": "#475569",
                            "size": 11,
                        },
                        gridcolor="#E2E8F0",
                        zerolinecolor="#CBD5E1",
                        linecolor="#CBD5E1",
                        showline=True,
                        showgrid=True,
                    )

                    fatal_figure.update_yaxes(
                        title_text="District",
                        title_font={
                            "color": "#334155",
                            "size": 13,
                        },
                        tickfont={
                            "color": "#334155",
                            "size": 12,
                        },
                        gridcolor="rgba(0,0,0,0)",
                        showgrid=False,
                        automargin=True,
                    )

                    with st.container(
                        border=True
                    ):

                        st.plotly_chart(
                            fatal_figure,
                            use_container_width=True,
                            theme=None,
                            config={
                                "displayModeBar": False,
                                "responsive": True,
                            },
                        )

                    # --------------------------------------------
                    # RESULTS TABLE
                    # --------------------------------------------

                    st.markdown(
                        "## Integrated district data"
                    )

                    fatal_display_df = fatal_df.rename(
                        columns={
                            "rank": "Rank",
                            "district_code": "District code",
                            "district_name": "District",
                            "total_accidents": "Total accidents",
                            "fatal_accidents": "Fatal accidents",
                            "accidents_per_10000_inhabitants": (
                                "Accidents per 10,000 inhabitants"
                            ),
                        }
                    )

                    display_columns = [
                        "Rank",
                        "District code",
                        "District",
                        "Total accidents",
                        "Fatal accidents",
                        "Accidents per 10,000 inhabitants",
                    ]

                    available_display_columns = [
                        column
                        for column in display_columns
                        if column in fatal_display_df.columns
                    ]

                    fatal_table_df = fatal_display_df[
                        available_display_columns
                    ].copy()

                    # Format integer columns
                    integer_columns = [
                        "Rank",
                        "Total accidents",
                        "Fatal accidents",
                    ]

                    for column in integer_columns:

                        if column in fatal_table_df.columns:

                            fatal_table_df[column] = (
                                fatal_table_df[column]
                                .fillna(0)
                                .astype(int)
                            )

                    # Preserve leading zeros in district codes
                    if "District code" in fatal_table_df.columns:

                        fatal_table_df[
                            "District code"
                        ] = fatal_table_df[
                            "District code"
                        ].astype(str)

                    # Format rate column
                    rate_column_name = (
                        "Accidents per 10,000 inhabitants"
                    )

                    if rate_column_name in fatal_table_df.columns:

                        fatal_table_df[
                            rate_column_name
                        ] = fatal_table_df[
                            rate_column_name
                        ].map(
                            lambda value: (
                                f"{float(value):.2f}"
                                if pd.notna(value)
                                else "—"
                            )
                        )

                    # Convert dataframe to HTML
                    fatal_table_html = fatal_table_df.to_html(
                        index=False,
                        classes="fatal-purple-table",
                        border=0,
                        justify="left",
                        escape=True,
                    )

                    # Table CSS
                    render_html(
                        """
                        <style>
                        .fatal-table-container {
                            width: 100%;
                            overflow-x: auto;
                            margin-top: 0.8rem;
                            margin-bottom: 1.3rem;
                            border: 1px solid #DDDDF7;
                            border-radius: 14px;
                            background: #FFFFFF;
                            box-shadow:
                                0 8px 25px
                                rgba(79, 70, 229, 0.07);
                        }

                        .fatal-purple-table {
                            width: 100%;
                            min-width: 900px;
                            border-collapse: collapse;
                            background: #FFFFFF;
                            color: #172033;
                            font-family:
                                Arial,
                                sans-serif;
                            font-size: 0.84rem;
                        }

                        .fatal-purple-table thead tr {
                            background:
                                linear-gradient(
                                    135deg,
                                    #5B5CEB,
                                    #4338CA
                                );
                        }

                        .fatal-purple-table thead th {
                            color: #FFFFFF !important;
                            background: transparent !important;
                            font-weight: 700;
                            text-align: left;
                            padding: 0.95rem 1rem;
                            border-bottom: 1px solid #4338CA;
                            white-space: nowrap;
                        }

                        .fatal-purple-table tbody td {
                            color: #27324A !important;
                            background: #FFFFFF;
                            padding: 0.82rem 1rem;
                            border-bottom: 1px solid #E8EAF3;
                            white-space: nowrap;
                        }

                        .fatal-purple-table tbody tr:nth-child(even) td {
                            background: #F7F7FF;
                        }

                        .fatal-purple-table tbody tr:hover td {
                            background: #ECECFF;
                            transition:
                                background-color
                                0.15s ease;
                        }

                        .fatal-purple-table tbody tr:last-child td {
                            border-bottom: none;
                        }

                        /* Right-align numeric columns */
                        .fatal-purple-table th:nth-child(1),
                        .fatal-purple-table td:nth-child(1),
                        .fatal-purple-table th:nth-child(4),
                        .fatal-purple-table td:nth-child(4),
                        .fatal-purple-table th:nth-child(5),
                        .fatal-purple-table td:nth-child(5),
                        .fatal-purple-table th:nth-child(6),
                        .fatal-purple-table td:nth-child(6) {
                            text-align: right;
                        }

                        /* Purple rank */
                        .fatal-purple-table td:first-child {
                            color: #4F46E5 !important;
                            font-weight: 750;
                        }

                        /* District code */
                        .fatal-purple-table td:nth-child(2) {
                            color: #4338CA !important;
                            font-weight: 650;
                        }

                        /* District name */
                        .fatal-purple-table td:nth-child(3) {
                            color: #172033 !important;
                            font-weight: 700;
                        }

                        /* Fatal count emphasis */
                        .fatal-purple-table td:nth-child(5) {
                            color: #4338CA !important;
                            font-weight: 750;
                        }
                        </style>
                        """
                    )

                    render_html(
                        f"""
                        <div class="fatal-table-container">
                        {fatal_table_html}
                        </div>
                        """
                    )

                    # --------------------------------------------
                    # DATA SOURCE INFORMATION
                    # --------------------------------------------

                    datasets_combined = (
                        fatal_data.get(
                            "datasets_combined",
                            [],
                        )
                    )

                    if datasets_combined:

                        with st.expander(
                            "Datasets included in this analysis"
                        ):

                            for dataset in datasets_combined:

                                st.write(
                                    f"• {dataset}"
                                )
# ============================================================
# BICYCLE RISK DISTRICTS PAGE
# ============================================================

elif selected_page == "Bicycle District Ranking":

    page_header(
        "Bicycle risk district ranking",
        (
            "Compare district-level bicycle accident shares while "
            "applying a minimum total-accident threshold to avoid "
            "rankings based on very small samples."
        ),
    )

    # --------------------------------------------------------
    # FILTER FORM
    # --------------------------------------------------------

    with st.form("bicycle_risk_form"):

        bicycle_filter_columns = st.columns(
            [1.2, 1.2, 1.4],
            gap="large",
        )

        with bicycle_filter_columns[0]:

            bicycle_year = st.number_input(
                "Analysis year",
                min_value=2000,
                max_value=2100,
                value=2023,
                step=1,
                key="bicycle_analysis_year",
            )

        with bicycle_filter_columns[1]:

            bicycle_limit = st.slider(
                "Number of districts",
                min_value=1,
                max_value=50,
                value=10,
                step=1,
                key="bicycle_district_limit",
            )

        with bicycle_filter_columns[2]:

            minimum_accidents = st.number_input(
                "Minimum total accidents",
                min_value=1,
                max_value=10000,
                value=100,
                step=10,
                key="bicycle_minimum_accidents",
                help=(
                    "Districts with fewer total accidents than this "
                    "value will not be included."
                ),
            )

        load_bicycle = st.form_submit_button(
            "Load bicycle risk ranking",
            use_container_width=True,
        )

    # --------------------------------------------------------
    # API REQUEST
    # --------------------------------------------------------

    if load_bicycle:

        with st.spinner(
            "Calculating district-level bicycle accident shares..."
        ):

            bicycle_data, bicycle_error = api_get(
                (
                    "/statistics/integrated/"
                    f"bicycle-risk-districts/{int(bicycle_year)}"
                ),
                params={
                    "limit": int(bicycle_limit),
                    "minimum_accidents": int(minimum_accidents),
                },
            )

        # ----------------------------------------------------
        # ERROR HANDLING
        # ----------------------------------------------------

        if bicycle_error:

            st.error(bicycle_error)

        elif not isinstance(bicycle_data, dict):

            st.warning(
                "The API returned an unexpected response format."
            )

        else:

            bicycle_results = bicycle_data.get(
                "results",
                [],
            )

            if not bicycle_results:

                st.info(
                    "No districts matched the selected year and "
                    "minimum-accident threshold."
                )

            else:

                # ------------------------------------------------
                # CREATE DATAFRAME
                # ------------------------------------------------

                bicycle_df = pd.DataFrame(
                    bicycle_results
                )

                numeric_columns = [
                    "rank",
                    "total_accidents",
                    "bicycle_accidents",
                    "bicycle_accident_share_percent",
                    "accidents_per_10000_inhabitants",
                ]

                for column in numeric_columns:

                    if column in bicycle_df.columns:

                        bicycle_df[column] = pd.to_numeric(
                            bicycle_df[column],
                            errors="coerce",
                        )

                bicycle_df = bicycle_df.dropna(
                    subset=[
                        "district_name",
                        "bicycle_accident_share_percent",
                    ]
                )

                if bicycle_df.empty:

                    st.info(
                        "The API returned results, but no valid "
                        "district values could be displayed."
                    )

                else:

                    # Sort results by bicycle share
                    bicycle_df = bicycle_df.sort_values(
                        by="bicycle_accident_share_percent",
                        ascending=False,
                    ).reset_index(drop=True)

                    highest_row = bicycle_df.iloc[0]

                    # ------------------------------------------------
                    # KPI CARDS
                    # ------------------------------------------------

                    metric_col1, metric_col2, metric_col3 = (
                        st.columns(
                            3,
                            gap="medium",
                        )
                    )

                    with metric_col1:

                        st.metric(
                            "Districts analysed",
                            len(bicycle_df),
                        )

                    with metric_col2:

                        st.metric(
                            "Highest bicycle share",
                            (
                                f"{highest_row[
                                    'bicycle_accident_share_percent'
                                ]:.2f}%"
                            ),
                        )

                    with metric_col3:

                        st.metric(
                            "Highest-ranked district",
                            highest_row["district_name"],
                        )

                    # ------------------------------------------------
                    # BICYCLE ACCIDENT SHARE CHART
                    # ------------------------------------------------

                    st.markdown(
                        "## Bicycle accident share ranking"
                    )

                    bicycle_chart_df = bicycle_df.sort_values(
                        by="bicycle_accident_share_percent",
                        ascending=True,
                    )

                    maximum_share = float(
                        bicycle_chart_df[
                            "bicycle_accident_share_percent"
                        ].max()
                    )

                    bicycle_figure = px.bar(
                        bicycle_chart_df,
                        x="bicycle_accident_share_percent",
                        y="district_name",
                        orientation="h",
                        text="bicycle_accident_share_percent",
                        template="plotly_white",
                        color_discrete_sequence=[
                            "#5B5CEB"
                        ],
                        custom_data=[
                            "total_accidents",
                            "bicycle_accidents",
                            "accidents_per_10000_inhabitants",
                        ],
                        labels={
                            "district_name": "District",
                            "bicycle_accident_share_percent": (
                                "Bicycle accident share (%)"
                            ),
                            "total_accidents": (
                                "Total accidents"
                            ),
                            "bicycle_accidents": (
                                "Bicycle accidents"
                            ),
                            "accidents_per_10000_inhabitants": (
                                "Accidents per 10,000 inhabitants"
                            ),
                        },
                    )

                    bicycle_figure.update_traces(
                        marker_color="#5B5CEB",
                        marker_line_color="#4F46E5",
                        marker_line_width=0.5,
                        texttemplate="%{text:.2f}%",
                        textposition="outside",
                        textfont={
                            "color": "#172033",
                            "size": 12,
                        },
                        cliponaxis=False,
                        hovertemplate=(
                            "<b>%{y}</b><br>"
                            "Bicycle accident share: "
                            "%{x:.2f}%<br>"
                            "Total accidents: "
                            "%{customdata[0]:.0f}<br>"
                            "Bicycle accidents: "
                            "%{customdata[1]:.0f}<br>"
                            "Rate per 10,000 inhabitants: "
                            "%{customdata[2]:.2f}"
                            "<extra></extra>"
                        ),
                    )

                    bicycle_figure.update_layout(
                        height=max(
                            500,
                            len(bicycle_chart_df) * 52,
                        ),
                        margin={
                            "l": 50,
                            "r": 100,
                            "t": 25,
                            "b": 65,
                        },
                        paper_bgcolor="#FFFFFF",
                        plot_bgcolor="#FFFFFF",
                        font={
                            "family": (
                                "Arial, sans-serif"
                            ),
                            "color": "#172033",
                            "size": 13,
                        },
                        showlegend=False,
                        bargap=0.22,
                        hoverlabel={
                            "bgcolor": "#172033",
                            "bordercolor": "#172033",
                            "font_color": "#FFFFFF",
                            "font_size": 13,
                        },
                    )

                    bicycle_figure.update_xaxes(
                        title_text=(
                            "Bicycle accident share (%)"
                        ),
                        range=[
                            0,
                            max(
                                maximum_share * 1.14,
                                1,
                            ),
                        ],
                        title_font={
                            "color": "#334155",
                            "size": 13,
                        },
                        tickfont={
                            "color": "#475569",
                            "size": 11,
                        },
                        gridcolor="#E2E8F0",
                        zerolinecolor="#CBD5E1",
                        linecolor="#CBD5E1",
                        showline=True,
                        showgrid=True,
                    )

                    bicycle_figure.update_yaxes(
                        title_text="District",
                        title_font={
                            "color": "#334155",
                            "size": 13,
                        },
                        tickfont={
                            "color": "#334155",
                            "size": 12,
                        },
                        gridcolor="rgba(0,0,0,0)",
                        showgrid=False,
                        automargin=True,
                    )

                    with st.container(
                        border=True
                    ):

                        st.plotly_chart(
                            bicycle_figure,
                            use_container_width=True,
                            theme=None,
                            config={
                                "displayModeBar": False,
                                "responsive": True,
                            },
                        )

                    # ------------------------------------------------
                    # WHITE AND PURPLE TABLE
                    # ------------------------------------------------

                    st.markdown(
                        "## Integrated bicycle-risk data"
                    )

                    bicycle_display_df = bicycle_df.rename(
                        columns={
                            "rank": "Rank",
                            "district_code": (
                                "District code"
                            ),
                            "district_name": "District",
                            "total_accidents": (
                                "Total accidents"
                            ),
                            "bicycle_accidents": (
                                "Bicycle accidents"
                            ),
                            "bicycle_accident_share_percent": (
                                "Bicycle share (%)"
                            ),
                            "accidents_per_10000_inhabitants": (
                                "Accidents per 10,000 inhabitants"
                            ),
                        }
                    )

                    display_columns = [
                        "Rank",
                        "District code",
                        "District",
                        "Total accidents",
                        "Bicycle accidents",
                        "Bicycle share (%)",
                        (
                            "Accidents per 10,000 "
                            "inhabitants"
                        ),
                    ]

                    available_columns = [
                        column
                        for column in display_columns
                        if column
                        in bicycle_display_df.columns
                    ]

                    table_df = bicycle_display_df[
                        available_columns
                    ].copy()

                    # Format integer columns
                    integer_columns = [
                        "Rank",
                        "Total accidents",
                        "Bicycle accidents",
                    ]

                    for column in integer_columns:

                        if column in table_df.columns:

                            table_df[column] = (
                                table_df[column]
                                .fillna(0)
                                .astype(int)
                            )

                    # Format decimal columns
                    if "Bicycle share (%)" in table_df.columns:

                        table_df[
                            "Bicycle share (%)"
                        ] = table_df[
                            "Bicycle share (%)"
                        ].map(
                            lambda value: (
                                f"{value:.2f}%"
                            )
                        )

                    rate_column_name = (
                        "Accidents per 10,000 "
                        "inhabitants"
                    )

                    if rate_column_name in table_df.columns:

                        table_df[
                            rate_column_name
                        ] = table_df[
                            rate_column_name
                        ].map(
                            lambda value: (
                                f"{value:.2f}"
                            )
                        )

                    # Convert dataframe into an HTML table
                    bicycle_table_html = table_df.to_html(
                        index=False,
                        classes="bicycle-purple-table",
                        border=0,
                        justify="left",
                        escape=True,
                    )

                    # Table-specific styling
                    st.markdown(
                        """
                        <style>
                        .bicycle-table-container {
                            width: 100%;
                            overflow-x: auto;
                            margin-top: 0.8rem;
                            margin-bottom: 1.2rem;
                            border: 1px solid #DDDDF7;
                            border-radius: 14px;
                            background: #FFFFFF;
                            box-shadow:
                                0 8px 25px
                                rgba(79, 70, 229, 0.07);
                        }

                        .bicycle-purple-table {
                            width: 100%;
                            border-collapse: collapse;
                            background: #FFFFFF;
                            color: #172033;
                            font-family:
                                Arial,
                                sans-serif;
                            font-size: 0.84rem;
                        }

                        .bicycle-purple-table thead tr {
                            background:
                                linear-gradient(
                                    135deg,
                                    #5B5CEB,
                                    #4338CA
                                );
                        }

                        .bicycle-purple-table thead th {
                            color: #FFFFFF !important;
                            font-weight: 700;
                            text-align: left;
                            padding: 0.95rem 1rem;
                            border-bottom:
                                1px solid #4338CA;
                            white-space: nowrap;
                        }

                        .bicycle-purple-table tbody td {
                            color: #27324A !important;
                            padding: 0.82rem 1rem;
                            border-bottom:
                                1px solid #E8EAF3;
                            background: #FFFFFF;
                            white-space: nowrap;
                        }

                        .bicycle-purple-table tbody tr:nth-child(even) td {
                            background: #F7F7FF;
                        }

                        .bicycle-purple-table tbody tr:hover td {
                            background: #ECECFF;
                            transition:
                                background-color
                                0.15s ease;
                        }

                        .bicycle-purple-table tbody tr:last-child td {
                            border-bottom: none;
                        }

                        .bicycle-purple-table th:nth-child(n+4),
                        .bicycle-purple-table td:nth-child(n+4) {
                            text-align: right;
                        }

                        .bicycle-purple-table td:first-child {
                            color: #4F46E5 !important;
                            font-weight: 700;
                        }

                        .bicycle-purple-table td:nth-child(3) {
                            color: #172033 !important;
                            font-weight: 650;
                        }
                        </style>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        (
                            '<div class="bicycle-table-container">'
                            f"{bicycle_table_html}"
                            "</div>"
                        ),
                        unsafe_allow_html=True,
                    )

                    # ------------------------------------------------
                    # EXPLANATION
                    # ------------------------------------------------

                    st.caption(
                        "The minimum-accident threshold prevents "
                        "districts with very small samples from "
                        "dominating the ranking."
                    )

                    datasets_combined = bicycle_data.get(
                        "datasets_combined",
                        [],
                    )

                    if datasets_combined:

                        with st.expander(
                            "Datasets included in this analysis"
                        ):

                            for dataset in datasets_combined:

                                st.write(
                                    f"• {dataset}"
                                )
# ============================================================
# ACCIDENT EXPLORER PAGE
# ============================================================

elif selected_page == "Accident explorer":

    page_header(
        "Accident explorer",
        (
            "Filter accident records by year, federal state, "
            "accident severity and participant type."
        ),
    )

    category_options = {
        "All categories": None,
        "Fatal accident": 1,
        "Serious injury accident": 2,
        "Minor injury accident": 3,
    }

    participant_options = {
        "All participant types": None,
        "Pedestrian": "pedestrian",
        "Bicycle": "bicycle",
        "Motorcycle": "motorcycle",
        "Car": "car",
    }

    state_labels = {
        "All federal states": None,
        **{
            f"{code} — {name}": code
            for code, name in STATE_OPTIONS.items()
        },
    }

    # Everything from here until form_submit_button
    # must remain inside this form block.
    with st.form("accident_filter_form"):

        st.markdown("### Filter configuration")

        st.caption(
            "Select one or more conditions and calculate "
            "the matching number of accident records."
        )

        filter_columns = st.columns(
            [1.1, 1.1, 1.6, 1.5, 1.4],
            gap="small",
        )

        # Filter by year checkbox
        with filter_columns[0]:
            apply_year_filter = st.checkbox(
                "Filter by year",
                value=True,
            )

        # Accident year
        with filter_columns[1]:
            filter_year = st.number_input(
                "Accident year",
                min_value=2000,
                max_value=2100,
                value=2023,
                step=1,
                disabled=not apply_year_filter,
            )

        # Federal state
        with filter_columns[2]:
            selected_state_label = st.selectbox(
                "Federal state",
                options=list(state_labels.keys()),
            )

        # Severity
        with filter_columns[3]:
            selected_category_label = st.selectbox(
                "Accident severity",
                options=list(category_options.keys()),
            )

        # Participant
        with filter_columns[4]:
            selected_participant_label = st.selectbox(
                "Participant type",
                options=list(participant_options.keys()),
            )

        st.markdown(
            "<div style='height: 10px'></div>",
            unsafe_allow_html=True,
        )

        # This button must stay inside with st.form(...)
        run_filter = st.form_submit_button(
            "Count matching accidents",
            use_container_width=True,
        )

    # This part must be outside the form
    if run_filter:

        filter_params = {}

        if apply_year_filter:
            filter_params["year"] = int(filter_year)

        selected_state_code = state_labels[
            selected_state_label
        ]

        if selected_state_code is not None:
            filter_params["state_code"] = selected_state_code

        selected_category = category_options[
            selected_category_label
        ]

        if selected_category is not None:
            filter_params["accident_category"] = selected_category

        selected_participant = participant_options[
            selected_participant_label
        ]

        if selected_participant is not None:
            filter_params["participant"] = selected_participant

        with st.spinner(
            "Counting matching accident records..."
        ):

            filter_data, filter_error = api_get(
                "/accidents/filter-by-category",
                params=filter_params,
            )

        if filter_error:

            st.error(filter_error)

        elif isinstance(filter_data, dict):

            accident_count = filter_data.get(
                "accident_count",
                0,
            )

            st.markdown("### Analysis result")

            result_col1, result_col2 = st.columns(
                [1, 2],
                gap="large",
            )

            with result_col1:
                st.metric(
                    "Matching accidents",
                    f"{int(accident_count):,}",
                )

            with result_col2:

                st.markdown("#### Applied filters")

                if apply_year_filter:
                    st.write(
                        f"**Year:** {int(filter_year)}"
                    )
                else:
                    st.write(
                        "**Year:** All available years"
                    )

                st.write(
                    f"**Federal state:** "
                    f"{selected_state_label}"
                )

                st.write(
                    f"**Accident severity:** "
                    f"{selected_category_label}"
                )

                st.write(
                    f"**Participant type:** "
                    f"{selected_participant_label}"
                )

            if int(accident_count) == 0:
                st.info(
                    "No accidents matched the selected filters."
                )
# ============================================================
# FOOTER
# ============================================================

render_html(
    """
    <div class="footer-text">
    DBW Accident Data API · FastAPI · PostgreSQL · Streamlit
    </div>
    """
)
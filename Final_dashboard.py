
import math
import json
from io import BytesIO
from datetime import date, timedelta
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen
from xml.sax.saxutils import escape

import numpy as np
import pandas as pd
import streamlit as st
try:
    from streamlit_geolocation import streamlit_geolocation
except ImportError:
    streamlit_geolocation = None
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from scipy.optimize import lsq_linear, minimize

st.set_page_config(
    page_title="Soilless Nutri Master",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

def apply_dashboard_theme():
    """Apply a responsive professional dashboard theme without extra packages."""
    st.markdown(
        """
        <style>
        :root {
            --forest: #0b5d4b;
            --emerald: #118568;
            --mint: #dff5ec;
            --aqua: #20a4a6;
            --navy: #14334a;
            --gold: #f2b84b;
            --ink: #18312b;
            --muted: #60766f;
            --surface: #ffffff;
            --line: #dceae5;
        }

        html, body, [class*="css"] {
            font-family: "Segoe UI", Inter, Arial, sans-serif;
            color: var(--ink);
        }

        /* Hide Streamlit branding and platform controls in web and mobile views. */
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="stAppDeployButton"],
        [data-testid="stMainMenu"],
        #MainMenu,
        .stDeployButton,
        [class*="viewerBadge"],
        footer {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            min-height: 0 !important;
        }

        html, body, [data-testid="stAppViewContainer"] {
            overflow-x: hidden !important;
        }

        .stApp {
            background:
                radial-gradient(circle at 88% 4%, rgba(32,164,166,.13), transparent 24rem),
                radial-gradient(circle at 4% 18%, rgba(17,133,104,.10), transparent 22rem),
                #f5faf8;
        }
        .block-container {
            max-width: 1480px;
            padding-top: .75rem;
            padding-bottom: 3rem;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(165deg, #083e35 0%, #0b5d4b 52%, #117568 100%);
            border-right: 0;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
            color: #f2fffb;
        }
        [data-testid="stSidebar"] [data-testid="stProgressBar"] > div > div {
            background: linear-gradient(90deg, #f2b84b, #ffe19b);
        }
        .side-brand {
            display:flex; align-items:center; gap:.75rem;
            padding:.4rem 0 1rem; border-bottom:1px solid rgba(255,255,255,.18);
        }
        .side-logo {
            width:46px; height:46px; border-radius:14px;
            display:grid; place-items:center; font-size:1.55rem;
            background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.24);
        }
        .side-brand-title {font-size:1.03rem; font-weight:750; color:#fff; line-height:1.2;}
        .side-brand-sub {font-size:.73rem; color:#bde6db; margin-top:.15rem;}
        .side-kicker {font-size:.68rem; font-weight:800; letter-spacing:.13em; color:#9bd7c8; margin-top:1.25rem;}
        .side-current {
            margin:.45rem 0 .8rem; padding:.85rem 1rem; border-radius:14px;
            background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.17);
            color:#fff; font-weight:700;
        }
        .side-list {margin:.6rem 0 0; padding:0; list-style:none;}
        .side-list li {padding:.38rem 0; color:#d9f4ec !important; font-size:.84rem;}
        .side-list li::before {content:"✓"; color:#ffd47b; font-weight:800; margin-right:.55rem;}
        .side-note {
            margin-top:1.1rem; padding:.8rem .9rem; border-radius:12px;
            background:rgba(5,36,31,.28); color:#cdece4; font-size:.76rem; line-height:1.45;
        }

        /* Hero */
        .dashboard-hero {
            position:relative; overflow:hidden; display:flex; justify-content:space-between;
            gap:1.5rem; align-items:center; padding:1.65rem 1.8rem; margin-bottom:1rem;
            border-radius:22px; color:white;
            background:linear-gradient(115deg, #0a4d40 0%, #0d765f 53%, #15979a 100%);
            box-shadow:0 18px 45px rgba(11,93,75,.22);
        }
        .dashboard-hero::after {
            content:""; position:absolute; width:310px; height:310px; right:-85px; top:-160px;
            border-radius:50%; border:52px solid rgba(255,255,255,.08);
        }
        .hero-content {position:relative; z-index:1;}
        .hero-kicker {font-size:.69rem; font-weight:800; letter-spacing:.16em; color:#bff4e5;}
        .dashboard-hero h1 {font-size:2rem; line-height:1.12; margin:.38rem 0 .5rem; color:#fff;}
        .dashboard-hero p {margin:0; max-width:780px; color:#dcfff6; font-size:.94rem;}
        .hero-mark {
            position:relative; z-index:1; flex:0 0 auto; width:104px; height:104px;
            border-radius:25px; display:grid; place-items:center; font-size:3rem;
            background:rgba(255,255,255,.13); border:1px solid rgba(255,255,255,.25);
            box-shadow:inset 0 1px 0 rgba(255,255,255,.25);
        }
        .feature-strip {display:flex; flex-wrap:wrap; gap:.45rem; margin-top:.85rem;}
        .feature-chip {
            padding:.32rem .62rem; border-radius:999px; font-size:.7rem; font-weight:700;
            color:#effffb; background:rgba(255,255,255,.11); border:1px solid rgba(255,255,255,.18);
        }

        /* Main stepper */
        .wizard-stepper {
            display:grid; grid-template-columns:repeat(5,1fr); gap:.55rem;
            margin:.95rem 0 1.35rem;
        }
        .step-card {
            display:flex; align-items:center; gap:.58rem; min-height:58px; padding:.65rem .72rem;
            border-radius:14px; background:#fff; border:1px solid var(--line);
            box-shadow:0 4px 14px rgba(26,77,65,.05);
        }
        .step-number {
            flex:0 0 29px; width:29px; height:29px; border-radius:50%; display:grid;
            place-items:center; background:#edf5f2; color:#6c817a; font-size:.75rem; font-weight:800;
        }
        .step-label {font-size:.75rem; line-height:1.15; font-weight:700; color:#71847e;}
        .step-card.done {background:#f0fbf7; border-color:#b7e6d7;}
        .step-card.done .step-number {background:#24a47e; color:#fff;}
        .step-card.done .step-label {color:#21735d;}
        .step-card.current {
            border-color:#20a4a6; background:linear-gradient(135deg,#e9fbf6,#eaf8fb);
            box-shadow:0 7px 20px rgba(32,164,166,.14);
        }
        .step-card.current .step-number {background:linear-gradient(135deg,#0d765f,#20a4a6); color:#fff;}
        .step-card.current .step-label {color:#0a6258;}

        /* Page content */
        .page-heading {
            display:flex; gap:.85rem; align-items:center; margin:.2rem 0 1rem;
            padding:.9rem 1.05rem; background:rgba(255,255,255,.78);
            border:1px solid var(--line); border-radius:16px;
        }
        .page-icon {
            width:43px; height:43px; flex:0 0 43px; display:grid; place-items:center;
            border-radius:13px; font-size:1.25rem; background:linear-gradient(135deg,#dff5ec,#dff2f5);
        }
        .page-heading h2 {margin:0; color:#123e35; font-size:1.22rem;}
        .page-heading p {margin:.18rem 0 0; color:var(--muted); font-size:.81rem;}
        h2, h3, h4 {color:#174d41; letter-spacing:-.01em;}
        hr {border-color:#dceae5 !important;}

        [data-testid="stMetric"] {
            background:linear-gradient(145deg,#ffffff,#f7fcfa); border:1px solid var(--line);
            border-left:5px solid #20a47e; border-radius:16px; padding:.82rem 1rem;
            box-shadow:0 7px 22px rgba(20,71,59,.07);
        }
        [data-testid="stMetricLabel"] {color:#60766f; font-weight:700;}
        [data-testid="stMetricValue"] {color:#0b5d4b; font-weight:800;}
        [data-testid="stDataFrame"] {
            border:1px solid var(--line); border-radius:14px; overflow:hidden;
            box-shadow:0 5px 18px rgba(20,71,59,.06);
        }
        [data-testid="stExpander"] {
            background:rgba(255,255,255,.76); border:1px solid var(--line);
            border-radius:14px; overflow:hidden;
        }
        [data-testid="stAlert"] {border-radius:14px; border-width:0 0 0 5px; box-shadow:0 4px 14px rgba(20,71,59,.04);}
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        [data-testid="stNumberInput"] input,
        [data-testid="stTextInput"] input,
        [data-testid="stDateInput"] input {
            border-radius:10px !important;
        }
        .stButton > button, [data-testid="stDownloadButton"] > button {
            border-radius:11px; min-height:2.7rem; font-weight:750;
            border:1px solid #bcdad1; transition:all .16s ease;
        }
        .stButton > button:hover, [data-testid="stDownloadButton"] > button:hover {
            transform:translateY(-1px); box-shadow:0 7px 16px rgba(11,93,75,.14);
            border-color:#168f72; color:#0b5d4b;
        }
        .stButton > button[kind="primary"] {
            color:#fff; border:0;
            background:linear-gradient(105deg,#0b6e57,#169276 58%,#15979a);
            box-shadow:0 7px 18px rgba(11,110,87,.22);
        }
        [data-testid="stDownloadButton"] > button {
            color:#fff; border:0; background:linear-gradient(105deg,#123f58,#167a83);
        }
        .dashboard-footer {
            margin-top:2rem; padding:1rem 0 .3rem; border-top:1px solid var(--line);
            text-align:center; color:#6d817a; font-size:.75rem;
        }

        @media (max-width: 900px) {
            .block-container {padding:1rem .8rem 2.5rem;}
            .dashboard-hero {padding:1.25rem; border-radius:18px;}
            .dashboard-hero h1 {font-size:1.55rem;}
            .hero-mark {width:72px; height:72px; font-size:2rem; border-radius:18px;}
            .wizard-stepper {grid-template-columns:repeat(2,1fr);}
            .step-card:last-child {grid-column:span 2;}
        }
        @media (max-width: 560px) {
            .dashboard-hero {align-items:flex-start;}
            .hero-mark {display:none;}
            .dashboard-hero h1 {font-size:1.35rem;}
            .dashboard-hero p {font-size:.82rem;}
            .feature-chip {font-size:.63rem;}
            .wizard-stepper {gap:.38rem;}
            .step-card {min-height:50px; padding:.48rem;}
            .step-label {font-size:.66rem;}
            .page-heading {padding:.72rem;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def render_page_heading(icon, title, subtitle):
    st.markdown(
        f"""
        <div class="page-heading">
          <div class="page-icon">{icon}</div>
          <div><h2>{title}</h2><p>{subtitle}</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# Reference nutrient formulations (mg/L = ppm)
# -----------------------------
FORMULATIONS = {
    "Hoagland & Arnon (1938)": {
        "N": 210.0, "P": 31.0, "K": 234.0, "Ca": 160.0, "Mg": 34.0, "S": 64.0,
        "Fe": 2.5, "Cu": 0.02, "Zn": 0.05, "Mn": 0.5, "B": 0.5, "Mo": 0.01
    },
    "Hewitt (1966)": {
        "N": 168.0, "P": 41.0, "K": 156.0, "Ca": 160.0, "Mg": 36.0, "S": 48.0,
        "Fe": 2.8, "Cu": 0.064, "Zn": 0.065, "Mn": 0.54, "B": 0.54, "Mo": 0.04
    },
    "Cooper (1979) – midpoint": {
        "N": 218.0, "P": 60.0, "K": 300.0, "Ca": 177.5, "Mg": 50.0, "S": 68.0,
        "Fe": 12.0, "Cu": 0.1, "Zn": 0.1, "Mn": 2.0, "B": 0.3, "Mo": 0.2
    },
    "Cooper (1979) – minimum": {
        "N": 200.0, "P": 60.0, "K": 300.0, "Ca": 170.0, "Mg": 50.0, "S": 68.0,
        "Fe": 12.0, "Cu": 0.1, "Zn": 0.1, "Mn": 2.0, "B": 0.3, "Mo": 0.2
    },
    "Cooper (1979) – maximum": {
        "N": 236.0, "P": 60.0, "K": 300.0, "Ca": 185.0, "Mg": 50.0, "S": 68.0,
        "Fe": 12.0, "Cu": 0.1, "Zn": 0.1, "Mn": 2.0, "B": 0.3, "Mo": 0.2
    },
    "Steiner (1984) – chemical-source table": {
        "N": 168.0, "P": 31.0, "K": 273.0, "Ca": 180.0, "Mg": 48.0, "S": 112.0,
        "Fe": 5.0, "Cu": 0.02, "Zn": 0.11, "Mn": 0.62, "B": 0.44, "Mo": 0.10
    },
    "Modified Hoagland – elemental output": {
        "N": 224.0, "P": 62.0, "K": 235.0, "Ca": 160.0, "Mg": 24.0, "S": 32.0,
        "Fe": 2.0, "Cu": 0.03, "Zn": 0.13, "Mn": 0.11, "B": 0.27, "Mo": 0.05
    },
}

ELEMENTS = ["N", "P", "K", "Ca", "Mg", "S", "Fe", "Cu", "Zn", "Mn", "B", "Mo"]

# Planning profiles for crops commonly grown in soilless systems.  Each Kc is
# applied only during its named stage; predefined profiles are read-only in the
# UI, while "Custom crop" exposes all durations and coefficients to the user.
CROP_PROFILES = {
    "Tomato": {"area": 0.30, "stages": [("Initial", 20, 0.45), ("Development", 30, 0.75), ("Maturity / production", 50, 1.05), ("Final", 20, 0.80)]},
    "Cherry tomato": {"area": 0.25, "stages": [("Initial", 15, 0.45), ("Development", 25, 0.75), ("Maturity / production", 50, 1.10), ("Final", 20, 0.85)]},
    "Cucumber": {"area": 0.30, "stages": [("Initial", 10, 0.50), ("Development", 20, 0.75), ("Maturity / production", 45, 1.00), ("Final", 15, 0.80)]},
    "Bell pepper / Capsicum": {"area": 0.25, "stages": [("Initial", 20, 0.45), ("Development", 30, 0.70), ("Maturity / production", 50, 1.00), ("Final", 20, 0.80)]},
    "Eggplant / Brinjal": {"area": 0.35, "stages": [("Initial", 20, 0.45), ("Development", 35, 0.75), ("Maturity / production", 60, 1.05), ("Final", 25, 0.85)]},
    "Strawberry": {"area": 0.08, "stages": [("Initial", 30, 0.40), ("Development", 35, 0.65), ("Maturity / production", 60, 0.85), ("Final", 25, 0.70)]},
    "Lettuce": {"area": 0.04, "stages": [("Initial", 7, 0.35), ("Development", 10, 0.55), ("Maturity", 18, 0.80), ("Final", 5, 0.65)]},
    "Palak / Spinach": {"area": 0.0225, "stages": [("Initial", 5, 0.40), ("Development", 10, 0.55), ("Maturity", 15, 0.70), ("Final", 5, 0.60)]},
    "Basil": {"area": 0.04, "stages": [("Initial", 7, 0.42), ("Development", 12, 0.50), ("Maturity / harvest", 20, 0.59), ("Final", 6, 0.50)]},
    "Mint": {"area": 0.03, "stages": [("Initial", 10, 0.40), ("Development", 15, 0.60), ("Maturity / harvest", 25, 0.85), ("Final", 10, 0.70)]},
    "Coriander / Cilantro": {"area": 0.02, "stages": [("Initial", 7, 0.35), ("Development", 10, 0.55), ("Maturity / harvest", 17, 0.75), ("Final", 6, 0.60)]},
    "Kale": {"area": 0.09, "stages": [("Initial", 10, 0.40), ("Development", 15, 0.65), ("Maturity", 25, 0.90), ("Final", 10, 0.75)]},
    "Pak choi / Bok choy": {"area": 0.06, "stages": [("Initial", 7, 0.40), ("Development", 10, 0.60), ("Maturity", 18, 0.85), ("Final", 5, 0.70)]},
    "Melon": {"area": 0.40, "stages": [("Initial", 15, 0.45), ("Development", 25, 0.75), ("Maturity / production", 45, 1.05), ("Final", 15, 0.80)]},
}

# "efficiency" represents delivery efficiency for open systems and fresh-water
# recovery efficiency for closed systems.  Drainage is consumed only in open
# drain-to-waste systems; return flow is recirculation, not crop water use.
SYSTEM_PROFILES = {
    "NFT (closed recirculating)": {"mode": "Closed recirculating", "efficiency": 97.0, "drainage": 0.0},
    "Deep-water culture (closed recirculating)": {"mode": "Closed recirculating", "efficiency": 98.0, "drainage": 0.0},
    "Aeroponics (closed recirculating)": {"mode": "Closed recirculating", "efficiency": 95.0, "drainage": 0.0},
    "Passive hydroponics (closed)": {"mode": "Closed recirculating", "efficiency": 97.0, "drainage": 0.0},
    "Aquaponics (closed recirculating)": {"mode": "Closed recirculating", "efficiency": 95.0, "drainage": 0.0},
    "Dutch bucket (recirculating)": {"mode": "Closed recirculating", "efficiency": 95.0, "drainage": 0.0},
    "Dutch bucket (drain-to-waste)": {"mode": "Open drain-to-waste", "efficiency": 90.0, "drainage": 15.0},
    "Cocopeat grow bag (drain-to-waste)": {"mode": "Open drain-to-waste", "efficiency": 90.0, "drainage": 20.0},
}

# Fractions are elemental mass fraction in the fertilizer/product.
# Values are calculated from molecular weights or common declared grades.
CHEMICALS = {
    "Calcium nitrate / Calcium nitrate tetrahydrate [Ca(NO3)2·4H2O]": {
        "formula": "Ca(NO3)2·4H2O", "mw": 236.15,
        "fractions": {"N": 0.11862, "Ca": 0.16972}, "tank": "A"
    },
    "Potassium nitrate [KNO3]": {
        "formula": "KNO3", "mw": 101.10,
        "fractions": {"N": 0.13854, "K": 0.38673}, "tank": "A/B"
    },
    "Potassium dihydrogen phosphate / Monopotassium phosphate [KH2PO4]": {
        "formula": "KH2PO4", "mw": 136.09,
        "fractions": {"P": 0.22761, "K": 0.28731}, "tank": "B"
    },
    "Monoammonium phosphate [NH4H2PO4]": {
        "formula": "NH4H2PO4", "mw": 115.08,
        "fractions": {"N": 0.12172, "P": 0.26926}, "tank": "B"
    },
    "Potassium sulfate [K2SO4]": {
        "formula": "K2SO4", "mw": 174.26,
        "fractions": {"K": 0.44874, "S": 0.18401}, "tank": "B"
    },
    "Magnesium sulphate / Magnesium sulfate heptahydrate [MgSO4·7H2O]": {
        "formula": "MgSO4·7H2O", "mw": 246.47,
        "fractions": {"Mg": 0.09860, "S": 0.13010}, "tank": "B"
    },
    "Magnesium nitrate hexahydrate [Mg(NO3)2·6H2O]": {
        "formula": "Mg(NO3)2·6H2O", "mw": 256.41,
        "fractions": {"Mg": 0.09479, "N": 0.10925}, "tank": "A"
    },
    "Calcium chloride dihydrate [CaCl2·2H2O]": {
        "formula": "CaCl2·2H2O", "mw": 147.02,
        "fractions": {"Ca": 0.27261}, "tank": "A"
    },
    "Ammonium sulfate [(NH4)2SO4]": {
        "formula": "(NH4)2SO4", "mw": 132.14,
        "fractions": {"N": 0.21202, "S": 0.24259}, "tank": "B"
    },
    "Boric acid [H3BO3]": {
        "formula": "H3BO3", "mw": 61.83,
        "fractions": {"B": 0.17484}, "tank": "B"
    },
    "Manganous sulphate / Manganese sulfate monohydrate [MnSO4·H2O]": {
        "formula": "MnSO4·H2O", "mw": 169.02,
        "fractions": {"Mn": 0.32510, "S": 0.18970}, "tank": "B"
    },
    "Zinc sulphate / Zinc sulfate heptahydrate [ZnSO4·7H2O]": {
        "formula": "ZnSO4·7H2O", "mw": 287.54,
        "fractions": {"Zn": 0.22741, "S": 0.11150}, "tank": "B"
    },
    "Copper sulphate / Copper sulfate pentahydrate [CuSO4·5H2O]": {
        "formula": "CuSO4·5H2O", "mw": 249.68,
        "fractions": {"Cu": 0.25450, "S": 0.12840}, "tank": "B"
    },
    "Sodium molybdate dihydrate [Na2MoO4·2H2O]": {
        "formula": "Na2MoO4·2H2O", "mw": 241.95,
        "fractions": {"Mo": 0.39660}, "tank": "B"
    },
    "EDTA iron / Fe-EDTA (commercial 13% Fe)": {
        "formula": "Commercial chelate", "mw": None,
        "fractions": {"Fe": 0.13}, "tank": "A"
    },
    "Fe-DTPA 10% Fe": {
        "formula": "Commercial chelate", "mw": None,
        "fractions": {"Fe": 0.10}, "tank": "A"
    },
    "Fe-EDDHA 6% Fe": {
        "formula": "Commercial chelate", "mw": None,
        "fractions": {"Fe": 0.06}, "tank": "A"
    },
    "Zn-EDTA 14% Zn": {
        "formula": "Commercial chelate", "mw": None,
        "fractions": {"Zn": 0.14}, "tank": "A"
    },
    # Common market grades used in hydroponic/aeroponic nutrient preparation.
    # Declared grades are kept separate from reagent-pure salts because their
    # elemental analyses are not identical.
    "Calcium nitrate (commercial greenhouse grade 15.5% N, 19% Ca)": {
        "formula": "Declared commercial grade", "mw": None,
        "fractions": {"N": 0.155, "Ca": 0.19}, "tank": "A"
    },
    "Potassium nitrate (commercial 13% N, 46% K2O)": {
        "formula": "13-0-46 fertilizer grade", "mw": None,
        "fractions": {"N": 0.13, "K": 0.3818}, "tank": "A/B"
    },
    "Potassium dihydrogen phosphate / Monopotassium phosphate (commercial 0-52-34)": {
        "formula": "0-52-34 fertilizer grade", "mw": None,
        "fractions": {"P": 0.2269, "K": 0.2822}, "tank": "B"
    },
    "Monoammonium phosphate (commercial 12-61-0)": {
        "formula": "12-61-0 fertilizer grade", "mw": None,
        "fractions": {"N": 0.12, "P": 0.2662}, "tank": "B"
    },
    "Potassium sulfate (water-soluble commercial 0-0-50)": {
        "formula": "0-0-50 fertilizer grade", "mw": None,
        "fractions": {"K": 0.4151, "S": 0.18}, "tank": "B"
    },
    "Magnesium sulfate heptahydrate (commercial Epsom salt 9.8% Mg)": {
        "formula": "MgSO4·7H2O, commercial grade", "mw": None,
        "fractions": {"Mg": 0.098, "S": 0.13}, "tank": "B"
    },
    "Magnesium nitrate (commercial 11% N, 9.5% Mg)": {
        "formula": "Declared commercial grade", "mw": None,
        "fractions": {"N": 0.11, "Mg": 0.095}, "tank": "A"
    },
    "Ammonium nitrate [NH4NO3]": {
        "formula": "NH4NO3", "mw": 80.04,
        "fractions": {"N": 0.3500}, "tank": "B"
    },
    "Urea [CO(NH2)2]": {
        "formula": "CO(NH2)2", "mw": 60.06,
        "fractions": {"N": 0.4665}, "tank": "B"
    },
    "Phosphoric acid 85% [H3PO4]": {
        "formula": "H3PO4, 85% w/w", "mw": 98.00,
        "fractions": {"P": 0.2687}, "tank": "B"
    },
    "Nitric acid 68% [HNO3]": {
        "formula": "HNO3, 68% w/w", "mw": 63.01,
        "fractions": {"N": 0.1511}, "tank": "A"
    },
    "Potassium hydroxide [KOH]": {
        "formula": "KOH", "mw": 56.11,
        "fractions": {"K": 0.6968}, "tank": "A/B"
    },
    "Ferrous sulfate heptahydrate [FeSO4·7H2O]": {
        "formula": "FeSO4·7H2O", "mw": 278.01,
        "fractions": {"Fe": 0.2009, "S": 0.1153}, "tank": "B"
    },
    "Ferrous sulfate monohydrate [FeSO4·H2O]": {
        "formula": "FeSO4·H2O", "mw": 169.93,
        "fractions": {"Fe": 0.3286, "S": 0.1887}, "tank": "B"
    },
    "EDTA iron / Ferric monosodium EDTA [C10H12FeN2NaO8] (13% Fe default)": {
        "formula": "NaFeEDTA, declared Fe basis", "mw": None,
        "fractions": {"Fe": 0.13}, "tank": "A"
    },
    "Zinc sulfate monohydrate [ZnSO4·H2O]": {
        "formula": "ZnSO4·H2O", "mw": 179.47,
        "fractions": {"Zn": 0.3643, "S": 0.1787}, "tank": "B"
    },
    "Zinc-EDTA (commercial 15% Zn)": {
        "formula": "Zn-EDTA, declared grade", "mw": None,
        "fractions": {"Zn": 0.15}, "tank": "A"
    },
    "Copper-EDTA (commercial 14% Cu)": {
        "formula": "Cu-EDTA, declared grade", "mw": None,
        "fractions": {"Cu": 0.14}, "tank": "A"
    },
    "EDTA copper(II) disodium salt (HiMedia/reagent grade)": {
        "formula": "C10H12CuN2Na2O8", "mw": 397.74,
        "fractions": {"Cu": 0.1598}, "tank": "A"
    },
    "Manganese-EDTA (commercial 13% Mn)": {
        "formula": "Mn-EDTA, declared grade", "mw": None,
        "fractions": {"Mn": 0.13}, "tank": "A"
    },
    "Manganese chloride tetrahydrate [MnCl2·4H2O] (plant-culture grade)": {
        "formula": "MnCl2·4H2O", "mw": 197.91,
        "fractions": {"Mn": 0.2776}, "tank": "B"
    },
    "Boron ethanolamine (commercial 10% B)": {
        "formula": "Boron ethanolamine, declared grade", "mw": None,
        "fractions": {"B": 0.10}, "tank": "B"
    },
    "Disodium octaborate tetrahydrate (commercial 20.5% B)": {
        "formula": "Na2B8O13·4H2O", "mw": 412.52,
        "fractions": {"B": 0.205}, "tank": "B"
    },
    "Borax decahydrate [Na2B4O7·10H2O]": {
        "formula": "Na2B4O7·10H2O", "mw": 381.37,
        "fractions": {"B": 0.1134}, "tank": "B"
    },
    "Ammonium molybdate tetrahydrate [(NH4)6Mo7O24·4H2O]": {
        "formula": "(NH4)6Mo7O24·4H2O", "mw": 1235.86,
        "fractions": {"Mo": 0.5435}, "tank": "B"
    },
    "Magnesium-EDTA (reagent/HiMedia-compatible salt)": {
        "formula": "C10H12N2O8Na2Mg", "mw": 358.50,
        "fractions": {"Mg": 0.0678}, "tank": "A"
    },
    "Calcium-EDTA (commercial 10% Ca)": {
        "formula": "Ca-EDTA, declared grade", "mw": None,
        "fractions": {"Ca": 0.10}, "tank": "A"
    },
}

DEFAULT_SELECTION = [
    "Calcium nitrate / Calcium nitrate tetrahydrate [Ca(NO3)2·4H2O]",
    "Potassium nitrate [KNO3]",
    "Potassium dihydrogen phosphate / Monopotassium phosphate [KH2PO4]",
    "Potassium sulfate [K2SO4]",
    "Magnesium sulphate / Magnesium sulfate heptahydrate [MgSO4·7H2O]",
    "Boric acid [H3BO3]",
    "Manganous sulphate / Manganese sulfate monohydrate [MnSO4·H2O]",
    "Zinc sulphate / Zinc sulfate heptahydrate [ZnSO4·7H2O]",
    "Copper sulphate / Copper sulfate pentahydrate [CuSO4·5H2O]",
    "Sodium molybdate dihydrate [Na2MoO4·2H2O]",
    "EDTA iron / Fe-EDTA (commercial 13% Fe)",
]

# Only one product may be selected for each micronutrient.  This prevents, for
# example, ZnSO4 and Zn-EDTA (or two different Fe chelates) from being dosed
# together accidentally.
MICRONUTRIENT_SOURCES = {
    "Fe": [
        "EDTA iron / Fe-EDTA (commercial 13% Fe)", "Fe-DTPA 10% Fe", "Fe-EDDHA 6% Fe",
        "EDTA iron / Ferric monosodium EDTA [C10H12FeN2NaO8] (13% Fe default)",
        "Ferrous sulfate heptahydrate [FeSO4·7H2O]",
        "Ferrous sulfate monohydrate [FeSO4·H2O]",
    ],
    "Zn": [
        "Zinc sulphate / Zinc sulfate heptahydrate [ZnSO4·7H2O]", "Zinc sulfate monohydrate [ZnSO4·H2O]",
        "Zn-EDTA 14% Zn", "Zinc-EDTA (commercial 15% Zn)",
    ],
    "Cu": [
        "Copper sulphate / Copper sulfate pentahydrate [CuSO4·5H2O]", "Copper-EDTA (commercial 14% Cu)",
        "EDTA copper(II) disodium salt (HiMedia/reagent grade)",
    ],
    "Mn": [
        "Manganous sulphate / Manganese sulfate monohydrate [MnSO4·H2O]",
        "Manganese chloride tetrahydrate [MnCl2·4H2O] (plant-culture grade)",
        "Manganese-EDTA (commercial 13% Mn)",
    ],
    "B": [
        "Boric acid [H3BO3]", "Boron ethanolamine (commercial 10% B)",
        "Disodium octaborate tetrahydrate (commercial 20.5% B)",
        "Borax decahydrate [Na2B4O7·10H2O]",
    ],
    "Mo": [
        "Sodium molybdate dihydrate [Na2MoO4·2H2O]",
        "Ammonium molybdate tetrahydrate [(NH4)6Mo7O24·4H2O]",
    ],
}
MICRONUTRIENT_PRODUCTS = {
    product for products in MICRONUTRIENT_SOURCES.values() for product in products
}
DEFAULT_MICRONUTRIENT_SOURCE = {
    nutrient: next((p for p in products if p in DEFAULT_SELECTION), products[0])
    for nutrient, products in MICRONUTRIENT_SOURCES.items()
}
DEFAULT_MACRONUTRIENT_SELECTION = [
    product for product in DEFAULT_SELECTION if product not in MICRONUTRIENT_PRODUCTS
]

# Cooper is protected from accidental source combinations. These core salts
# provide independent, controllable N, P, K, Ca, Mg and S contributions.
COOPER_SAFE_MACROS = [
    "Calcium nitrate / Calcium nitrate tetrahydrate [Ca(NO3)2·4H2O]",
    "Potassium nitrate [KNO3]",
    "Potassium dihydrogen phosphate / Monopotassium phosphate [KH2PO4]",
    "Monoammonium phosphate [NH4H2PO4]",
    "Potassium sulfate [K2SO4]",
    "Magnesium sulphate / Magnesium sulfate heptahydrate [MgSO4·7H2O]",
]
COOPER_SAFE_MICROS = {
    "Fe": [
        "EDTA iron / Fe-EDTA (commercial 13% Fe)", "Fe-DTPA 10% Fe", "Fe-EDDHA 6% Fe",
        "EDTA iron / Ferric monosodium EDTA [C10H12FeN2NaO8] (13% Fe default)",
    ],
    "Zn": [
        "Zn-EDTA 14% Zn", "Zinc-EDTA (commercial 15% Zn)",
        "Zinc sulphate / Zinc sulfate heptahydrate [ZnSO4·7H2O]",
        "Zinc sulfate monohydrate [ZnSO4·H2O]",
    ],
    "Cu": [
        "Copper-EDTA (commercial 14% Cu)",
        "EDTA copper(II) disodium salt (HiMedia/reagent grade)",
        "Copper sulphate / Copper sulfate pentahydrate [CuSO4·5H2O]",
    ],
    "Mn": [
        "Manganese-EDTA (commercial 13% Mn)",
        "Manganous sulphate / Manganese sulfate monohydrate [MnSO4·H2O]",
        "Manganese chloride tetrahydrate [MnCl2·4H2O] (plant-culture grade)",
    ],
    "B": MICRONUTRIENT_SOURCES["B"],
    "Mo": MICRONUTRIENT_SOURCES["Mo"],
}
FORMULATION_RECOMMENDED_MACROS = {
    "Hoagland & Arnon (1938)": COOPER_SAFE_MACROS + ["Ammonium nitrate [NH4NO3]"],
    "Hewitt (1966)": COOPER_SAFE_MACROS,
    "Cooper (1979) – midpoint": COOPER_SAFE_MACROS,
    "Cooper (1979) – minimum": COOPER_SAFE_MACROS,
    "Cooper (1979) – maximum": COOPER_SAFE_MACROS,
    "Steiner (1984) – chemical-source table": COOPER_SAFE_MACROS,
    "Modified Hoagland – elemental output": COOPER_SAFE_MACROS,
}

# -----------------------------
# ET helpers
# -----------------------------
def extraterrestrial_radiation(latitude_deg: float, doy: int) -> float:
    phi = math.radians(latitude_deg)
    dr = 1 + 0.033 * math.cos(2 * math.pi * doy / 365)
    delta = 0.409 * math.sin(2 * math.pi * doy / 365 - 1.39)
    x = -math.tan(phi) * math.tan(delta)
    x = min(1.0, max(-1.0, x))
    ws = math.acos(x)
    gsc = 0.0820
    return (24 * 60 / math.pi) * gsc * dr * (
        ws * math.sin(phi) * math.sin(delta)
        + math.cos(phi) * math.cos(delta) * math.sin(ws)
    )

def eto_hargreaves(tmin, tmax, tmean, latitude, doy):
    ra = extraterrestrial_radiation(latitude, doy)
    return max(0.0, 0.0023 * (tmean + 17.8) * math.sqrt(max(tmax - tmin, 0)) * ra)

def saturation_vp(t):
    return 0.6108 * math.exp((17.27 * t) / (t + 237.3))

def eto_fao56(tmin, tmax, tmean, rhmin, rhmax, wind2, solar_rad, elevation):
    es_tmin = saturation_vp(tmin)
    es_tmax = saturation_vp(tmax)
    es = (es_tmin + es_tmax) / 2
    ea = (es_tmin * rhmax / 100 + es_tmax * rhmin / 100) / 2
    delta = 4098 * saturation_vp(tmean) / ((tmean + 237.3) ** 2)
    pressure = 101.3 * (((293 - 0.0065 * elevation) / 293) ** 5.26)
    gamma = 0.000665 * pressure
    rns = (1 - 0.23) * solar_rad
    # Simplified daily estimate: net longwave radiation is approximated.
    sigma = 4.903e-9
    tmax_k = tmax + 273.16
    tmin_k = tmin + 273.16
    rnl = sigma * ((tmax_k**4 + tmin_k**4) / 2) * (0.34 - 0.14 * math.sqrt(max(ea, 0)))
    rn = max(0.0, rns - rnl)
    g = 0
    numerator = 0.408 * delta * (rn - g) + gamma * (900 / (tmean + 273)) * wind2 * (es - ea)
    denominator = delta + gamma * (1 + 0.34 * wind2)
    return max(0.0, numerator / denominator)

def fetch_open_meteo_daily(latitude, longitude, selected_date):
    """Retrieve one daily weather record without requiring an API key."""
    today = date.today()
    endpoint = (
        "https://archive-api.open-meteo.com/v1/archive"
        if selected_date < today
        else "https://api.open-meteo.com/v1/forecast"
    )
    daily_variables = [
        "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
        "relative_humidity_2m_max", "relative_humidity_2m_min",
        "wind_speed_10m_mean", "shortwave_radiation_sum",
        "et0_fao_evapotranspiration",
    ]
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": selected_date.isoformat(),
        "end_date": selected_date.isoformat(),
        "daily": ",".join(daily_variables),
        "wind_speed_unit": "ms",
        "timezone": "auto",
    }
    url = f"{endpoint}?{urlencode(params)}"
    try:
        with urlopen(url, timeout=20) as response:
            payload = json.load(response)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Weather service returned HTTP {exc.code}: {detail[:180]}") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"Could not connect to the weather service: {exc}") from exc

    daily = payload.get("daily") or {}
    if not daily.get("time"):
        raise RuntimeError("No weather record was returned for the selected location and date.")

    def first(name, fallback=None):
        values = daily.get(name) or []
        value = values[0] if values else fallback
        return fallback if value is None else float(value)

    tmin = first("temperature_2m_min")
    tmax = first("temperature_2m_max")
    if tmin is None or tmax is None:
        raise RuntimeError("The API response did not contain minimum and maximum temperature.")
    tmean = first("temperature_2m_mean", (tmin + tmax) / 2)
    wind10 = first("wind_speed_10m_mean", 2.67)
    # FAO-56 logarithmic wind-profile conversion from 10 m to 2 m.
    wind2 = wind10 * 4.87 / math.log(67.8 * 10 - 5.42)
    return {
        "date": daily["time"][0],
        "latitude": float(payload.get("latitude", latitude)),
        "longitude": float(payload.get("longitude", longitude)),
        "elevation": float(payload.get("elevation", 0.0)),
        "timezone": payload.get("timezone", "auto"),
        "tmin": tmin,
        "tmax": tmax,
        "tmean": tmean,
        "rhmin": first("relative_humidity_2m_min", 40.0),
        "rhmax": first("relative_humidity_2m_max", 85.0),
        "wind10": wind10,
        "wind2": wind2,
        "solar_rad": first("shortwave_radiation_sum", 18.0),
        "api_eto": first("et0_fao_evapotranspiration", float("nan")),
        "source": "Open-Meteo historical reanalysis" if selected_date < today else "Open-Meteo forecast",
    }

DAILY_WEATHER_VARIABLES = [
    "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
    "relative_humidity_2m_max", "relative_humidity_2m_min",
    "wind_speed_10m_mean", "shortwave_radiation_sum",
    "et0_fao_evapotranspiration",
]

def _request_open_meteo_range(endpoint, latitude, longitude, start_date, end_date):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily": ",".join(DAILY_WEATHER_VARIABLES),
        "wind_speed_unit": "ms",
        "timezone": "auto",
    }
    url = f"{endpoint}?{urlencode(params)}"
    try:
        with urlopen(url, timeout=35) as response:
            return json.load(response)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Weather service returned HTTP {exc.code}: {detail[:180]}") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"Could not connect to the weather service: {exc}") from exc

def _weather_rows_from_payload(payload, source):
    daily = payload.get("daily") or {}
    times = daily.get("time") or []
    rows = []

    def value(name, index, fallback):
        values = daily.get(name) or []
        item = values[index] if index < len(values) else fallback
        return fallback if item is None else float(item)

    for index, day_text in enumerate(times):
        tmin = value("temperature_2m_min", index, 20.0)
        tmax = value("temperature_2m_max", index, 32.0)
        tmean = value("temperature_2m_mean", index, (tmin + tmax) / 2)
        wind10 = value("wind_speed_10m_mean", index, 2.67)
        wind2 = wind10 * 4.87 / math.log(67.8 * 10 - 5.42)
        rows.append({
            "date": day_text,
            "tmin": tmin,
            "tmax": tmax,
            "tmean": tmean,
            "rhmin": value("relative_humidity_2m_min", index, 40.0),
            "rhmax": value("relative_humidity_2m_max", index, 85.0),
            "wind2": wind2,
            "solar_rad": value("shortwave_radiation_sum", index, 18.0),
            "api_eto": value("et0_fao_evapotranspiration", index, float("nan")),
            "source": source,
        })
    return rows

def fetch_open_meteo_schedule(latitude, longitude, start_date, end_date):
    """Return weather for every crop day.

    Exact historical data and the available 16-day forecast are used first.
    Future days beyond that horizon use a five-year daily climatology for the
    same coordinate, so every estimated day is explicit rather than silently
    repeating one weather record through the crop period.
    """
    today = date.today()
    forecast_end = today + timedelta(days=15)
    rows_by_date = {}
    metadata = {"latitude": latitude, "longitude": longitude, "elevation": 0.0, "timezone": "auto"}
    warnings = []

    def add_segment(endpoint, segment_start, segment_end, source):
        if segment_start > segment_end:
            return
        try:
            payload = _request_open_meteo_range(
                endpoint, latitude, longitude, segment_start, segment_end
            )
            metadata.update({
                "latitude": float(payload.get("latitude", metadata["latitude"])),
                "longitude": float(payload.get("longitude", metadata["longitude"])),
                "elevation": float(payload.get("elevation", metadata["elevation"])),
                "timezone": payload.get("timezone", metadata["timezone"]),
            })
            for row in _weather_rows_from_payload(payload, source):
                rows_by_date[row["date"]] = row
        except RuntimeError as exc:
            warnings.append(str(exc))

    if start_date < today:
        add_segment(
            "https://archive-api.open-meteo.com/v1/archive",
            start_date,
            min(end_date, today - timedelta(days=1)),
            "Open-Meteo historical reanalysis",
        )
    if end_date >= today:
        add_segment(
            "https://api.open-meteo.com/v1/forecast",
            max(start_date, today),
            min(end_date, forecast_end),
            "Open-Meteo forecast",
        )

    requested_dates = [
        start_date + timedelta(days=offset)
        for offset in range((end_date - start_date).days + 1)
    ]
    missing_dates = [d for d in requested_dates if d.isoformat() not in rows_by_date]
    if missing_dates:
        climate_end = date(today.year - 1, 12, 31)
        climate_start = date(today.year - 5, 1, 1)
        payload = _request_open_meteo_range(
            "https://archive-api.open-meteo.com/v1/archive",
            latitude, longitude, climate_start, climate_end,
        )
        metadata.update({
            "latitude": float(payload.get("latitude", metadata["latitude"])),
            "longitude": float(payload.get("longitude", metadata["longitude"])),
            "elevation": float(payload.get("elevation", metadata["elevation"])),
            "timezone": payload.get("timezone", metadata["timezone"]),
        })
        climate_rows = _weather_rows_from_payload(payload, "Five-year historical climatology")
        grouped = {}
        for row in climate_rows:
            row_date = date.fromisoformat(row["date"])
            grouped.setdefault((row_date.month, row_date.day), []).append(row)
        numeric_fields = ["tmin", "tmax", "tmean", "rhmin", "rhmax", "wind2", "solar_rad", "api_eto"]
        for missing_date in missing_dates:
            samples = grouped.get((missing_date.month, missing_date.day))
            if not samples and missing_date.month == 2 and missing_date.day == 29:
                samples = grouped.get((2, 28))
            if not samples:
                continue
            row = {
                field: float(np.nanmean([sample[field] for sample in samples]))
                for field in numeric_fields
            }
            row.update({"date": missing_date.isoformat(), "source": "Five-year historical climatology"})
            rows_by_date[missing_date.isoformat()] = row

    unresolved = [d.isoformat() for d in requested_dates if d.isoformat() not in rows_by_date]
    if unresolved:
        detail = f" First missing date: {unresolved[0]}."
        if warnings:
            detail += f" Weather service detail: {warnings[-1]}"
        raise RuntimeError("Could not build a weather record for every crop day." + detail)

    return [rows_by_date[d.isoformat()] for d in requested_dates], metadata

def make_manual_weather_schedule(start_date, duration, weather_values):
    rows = []
    for offset in range(duration):
        row = dict(weather_values)
        row.update({
            "date": (start_date + timedelta(days=offset)).isoformat(),
            "source": "Manual weather repeated (no daily API schedule)",
            "api_eto": float("nan"),
        })
        rows.append(row)
    return rows

def build_stage_water_schedule(
    weather_rows, stages, latitude, elevation, et_method, plant_area,
    plants, system_mode, efficiency, drainage,
):
    rows = []
    stage_days = []
    for stage_name, days, kc in stages:
        stage_days.extend([(stage_name, float(kc))] * int(days))
    if len(stage_days) != len(weather_rows):
        raise ValueError("Stage durations and weather schedule length do not match.")

    efficiency_fraction = efficiency / 100.0
    drainage_fraction = drainage / 100.0
    for day_index, (weather, stage_info) in enumerate(zip(weather_rows, stage_days), start=1):
        stage_name, kc = stage_info
        day_date = date.fromisoformat(weather["date"])
        api_eto = weather.get("api_eto", float("nan"))
        if et_method == "FAO-56 Penman–Monteith" and np.isfinite(api_eto):
            # Open-Meteo supplies daily FAO-56 reference ET directly when API
            # weather is available.  The local equation remains the fallback
            # for measured/manual inputs.
            eto = max(0.0, float(api_eto))
        elif et_method == "FAO-56 Penman–Monteith":
            eto = eto_fao56(
                weather["tmin"], weather["tmax"], weather["tmean"],
                weather["rhmin"], weather["rhmax"], weather["wind2"],
                weather["solar_rad"], elevation,
            )
        else:
            eto = eto_hargreaves(
                weather["tmin"], weather["tmax"], weather["tmean"],
                latitude, day_date.timetuple().tm_yday,
            )
        etc = eto * kc
        net_per_plant = etc * plant_area
        if system_mode == "Open drain-to-waste":
            supply_per_plant = net_per_plant / (
                efficiency_fraction * (1.0 - drainage_fraction)
            )
            drainage_per_plant = supply_per_plant * drainage_fraction
        else:
            supply_per_plant = net_per_plant / efficiency_fraction
            drainage_per_plant = 0.0
        rows.append({
            "Date": day_date.isoformat(),
            "Day": day_index,
            "Stage": stage_name,
            "Kc": kc,
            "ET0 (mm/day)": eto,
            "ETc (mm/day)": etc,
            "Net uptake (L/plant/day)": net_per_plant,
            "Fresh supply (L/plant/day)": supply_per_plant,
            "Total fresh supply (L/day)": supply_per_plant * plants,
            "Drainage/discard (L/day)": drainage_per_plant * plants,
            "Weather source": weather["source"],
        })
    daily_df = pd.DataFrame(rows)
    stage_summary = (
        daily_df.groupby(["Stage", "Kc"], sort=False, as_index=False)
        .agg(**{
            "Days": ("Day", "count"),
            "Average ET0 (mm/day)": ("ET0 (mm/day)", "mean"),
            "Average fresh supply (L/plant/day)": ("Fresh supply (L/plant/day)", "mean"),
            "Peak fresh supply (L/plant/day)": ("Fresh supply (L/plant/day)", "max"),
            "Stage fresh water (L)": ("Total fresh supply (L/day)", "sum"),
            "Stage drainage/discard (L)": ("Drainage/discard (L/day)", "sum"),
        })
    )
    return daily_df, stage_summary

# -----------------------------
# Nutrient solver
# -----------------------------
def chemical_matrix(selected, nutrient_order, purities, custom_fractions):
    A = np.zeros((len(nutrient_order), len(selected)), dtype=float)
    for j, chem in enumerate(selected):
        fractions = dict(CHEMICALS[chem]["fractions"])
        fractions.update(custom_fractions.get(chem, {}))
        purity = purities.get(chem, 100.0) / 100.0
        for i, nutrient in enumerate(nutrient_order):
            A[i, j] = fractions.get(nutrient, 0.0) * purity
    return A

def solve_balance(A, b, weights, costs=None, mode="Best nutrient match", max_doses=None):
    # x is mg fertilizer/L; A*x gives mg nutrient/L.
    # Normalize every nutrient by its target. Without this normalization, a
    # 1 mg/L Cu or Zn error is numerically overwhelmed by a small NPK error.
    scale = np.where(np.asarray(b, dtype=float) > 0, np.asarray(b, dtype=float), 1.0)
    W = np.diag(np.sqrt(np.asarray(weights, dtype=float)) / scale)
    Aw = W @ A
    bw = W @ b
    upper = np.full(A.shape[1], np.inf)
    if max_doses is not None:
        upper = np.asarray(max_doses, dtype=float)
    if mode == "Best nutrient match":
        result = lsq_linear(Aw, bw, bounds=(np.zeros(A.shape[1]), upper), max_iter=10000)
        return result.x
    costs = np.ones(A.shape[1]) if costs is None else np.asarray(costs, dtype=float)

    # Combined objective: normalized nutrient mismatch + a small secondary penalty.
    def objective(x):
        mismatch = np.sum(weights * (((A @ x) - b) / scale) ** 2)
        if mode == "Lowest cost":
            secondary = 1e-5 * np.sum(costs * x)
        elif mode == "Lowest total fertilizer mass":
            secondary = 1e-5 * np.sum(x)
        else:
            secondary = 0.0
        return mismatch + secondary

    bounds = [(0, None if not np.isfinite(upper[i]) else upper[i]) for i in range(A.shape[1])]
    x0 = lsq_linear(Aw, bw, bounds=(np.zeros(A.shape[1]), upper), max_iter=10000).x
    result = minimize(objective, x0=x0, method="SLSQP", bounds=bounds,
                      options={"maxiter": 5000, "ftol": 1e-12})
    return np.maximum(result.x, 0)

def evaluate_fertilizer_balance(
    selected, targets, purities, custom_fractions, max_doses, costs,
    weights, optimization_mode, tolerance
):
    """Solve and classify a fertilizer selection before it can be submitted."""
    if not selected:
        raise ValueError("Select at least one fertilizer source.")
    b = np.array([targets[e] for e in ELEMENTS], dtype=float)
    A = chemical_matrix(selected, ELEMENTS, purities, custom_fractions)
    max_array = [np.inf if max_doses[c] <= 0 else max_doses[c] for c in selected]
    cost_array = [costs[c] / 1_000_000 for c in selected]
    x = solve_balance(A, b, weights, cost_array, optimization_mode, max_array)
    achieved = A @ x
    difference = achieved - b
    pct_diff = np.divide(
        difference * 100.0, b,
        out=np.where(np.abs(achieved) < 1e-12, 0.0, np.inf),
        where=b > 0,
    )
    statuses = []
    for target, dev, actual in zip(b, pct_diff, achieved):
        if target == 0:
            statuses.append("No target" if abs(actual) < 1e-12 else "Unwanted contribution")
        elif abs(dev) <= tolerance:
            statuses.append("Balanced")
        elif dev < 0:
            statuses.append("Deficient")
        else:
            statuses.append("Excessive")
    result = pd.DataFrame({
        "Nutrient": ELEMENTS,
        "Required (mg/L)": b,
        "Achieved (mg/L)": achieved,
        "Difference": difference,
        "Deviation (%)": pct_diff,
        "Status": statuses,
    })
    blocking = result[result["Status"].isin(["Deficient", "Excessive", "Unwanted contribution"])]
    return {
        "A": A, "b": b, "x": x, "achieved": achieved,
        "nutrient_result": result, "blocking": blocking,
        "balanced": blocking.empty,
    }

def _effective_fractions(chemical, purities=None, custom_fractions=None):
    """Return the elemental fractions actually used for a fertilizer product."""
    purities = purities or {}
    custom_fractions = custom_fractions or {}
    fractions = dict(CHEMICALS[chemical]["fractions"])
    fractions.update(custom_fractions.get(chemical, {}))
    purity = purities.get(chemical, 100.0) / 100.0
    return {element: value * purity for element, value in fractions.items()}

def build_nutrient_selection_hints(
    evaluation, selected, candidate_products, purities, custom_fractions
):
    """Explain likely causes and useful source choices for every blocking nutrient."""
    rows = []
    selected_set = set(selected)
    contribution = evaluation["A"] * evaluation["x"][None, :]

    for _, issue in evaluation["blocking"].iterrows():
        nutrient = issue["Nutrient"]
        status = issue["Status"]
        nutrient_index = ELEMENTS.index(nutrient)

        if status in ("Excessive", "Unwanted contribution"):
            ranked = sorted(
                (
                    (selected[j], contribution[nutrient_index, j])
                    for j in range(len(selected))
                    if contribution[nutrient_index, j] > 1e-9
                ),
                key=lambda item: item[1],
                reverse=True,
            )
            main_sources = ", ".join(
                f"{name} ({amount:.2f} mg/L {nutrient})"
                for name, amount in ranked[:3]
            )
            advice = (
                "Reduce, remove, or replace the main contributing source and recalculate."
                if main_sources else
                "Review declared percentages and purity overrides for the selected products."
            )
            rows.append({
                "Nutrient": nutrient,
                "Problem": status,
                "Main selected source(s)": main_sources or "Not identified",
                "Selection hint": advice,
            })
            continue

        current_suppliers = [
            product for product in selected
            if _effective_fractions(product, purities, custom_fractions).get(nutrient, 0.0) > 0
        ]
        alternatives = []
        for product in candidate_products:
            if product in selected_set:
                continue
            fractions = CHEMICALS[product]["fractions"]
            primary = fractions.get(nutrient, 0.0)
            if primary <= 0:
                continue
            collateral = sum(value for element, value in fractions.items() if element != nutrient)
            selectivity = primary / max(collateral, 1e-12)
            alternatives.append((product, selectivity))
        alternatives.sort(key=lambda item: item[1], reverse=True)
        suggested = ", ".join(product for product, _ in alternatives[:3])

        if not current_suppliers:
            advice = f"Add a {nutrient} source: {suggested}." if suggested else f"Add a product supplying {nutrient}."
        elif suggested:
            advice = (
                f"The selected {nutrient} source is constrained by other nutrients. "
                f"Try adding or substituting: {suggested}."
            )
        else:
            advice = (
                f"Check the maximum dose, purity and declared {nutrient} percentage of the selected source."
            )
        rows.append({
            "Nutrient": nutrient,
            "Problem": status,
            "Main selected source(s)": ", ".join(current_suppliers[:3]) or "None selected",
            "Selection hint": advice,
        })

    return pd.DataFrame(rows)

def _selection_error_score(evaluation):
    """Score a trial selection; lower values indicate a closer nutrient balance."""
    result = evaluation["nutrient_result"]
    targets = result["Required (mg/L)"].to_numpy(dtype=float)
    differences = result["Difference"].to_numpy(dtype=float)
    relative = np.abs(differences) / np.where(targets > 0, targets, 1.0)
    return (
        int(len(evaluation["blocking"])),
        float(np.sqrt(np.mean(relative ** 2))),
        float(np.max(relative)),
    )

def recommend_macro_changes(
    evaluation, selected_macro, selected_micro, macro_options, targets,
    purities, custom_fractions, max_doses, costs, weights, tolerance,
    max_suggestions=5,
):
    """Test simple add/remove/swap actions and return only actions that improve balance."""
    baseline = _selection_error_score(evaluation)
    selected_macro = list(selected_macro)
    selected_micro = list(selected_micro)
    hazardous_words = ("acid", "hydroxide")
    available = [
        product for product in macro_options
        if product not in selected_macro
        and not any(word in product.lower() for word in hazardous_words)
    ]
    trials = []
    seen = set()

    def test(action, proposed_macros):
        proposed_macros = list(dict.fromkeys(proposed_macros))
        signature = tuple(sorted(proposed_macros))
        if signature in seen:
            return
        seen.add(signature)
        proposed = proposed_macros + selected_micro
        trial_purities = {p: purities.get(p, 100.0) for p in proposed}
        trial_costs = {p: costs.get(p, 0.0) for p in proposed}
        trial_limits = {p: max_doses.get(p, 0.0) for p in proposed}
        trial_overrides = {p: custom_fractions.get(p, {}) for p in proposed}
        try:
            trial = evaluate_fertilizer_balance(
                selected=proposed, targets=targets, purities=trial_purities,
                custom_fractions=trial_overrides, max_doses=trial_limits,
                costs=trial_costs, weights=weights,
                optimization_mode="Best nutrient match", tolerance=tolerance,
            )
        except (ValueError, RuntimeError):
            return
        score = _selection_error_score(trial)
        materially_better = (
            score[0] < baseline[0]
            or (score[0] == baseline[0] and score[1] < baseline[1] - 1e-4)
        )
        if materially_better:
            blocking_names = ", ".join(trial["blocking"]["Nutrient"].tolist())
            trials.append({
                "score": score,
                "Action to try": action,
                "Expected remaining problem nutrients": blocking_names or "None – potentially balanced",
                "Expected maximum deviation (%)": score[2] * 100.0,
            })

    for product in available:
        test(f"Add: {product}", selected_macro + [product])

    for old_product in selected_macro:
        test(f"Remove: {old_product}", [p for p in selected_macro if p != old_product])

    # A swap is tested only when the two products supply at least one common nutrient.
    for old_product in selected_macro:
        old_elements = set(CHEMICALS[old_product]["fractions"])
        remaining = [p for p in selected_macro if p != old_product]
        for new_product in available:
            if old_elements.intersection(CHEMICALS[new_product]["fractions"]):
                test(f"Replace: {old_product} → {new_product}", remaining + [new_product])

    trials.sort(key=lambda row: row["score"])
    if not trials:
        return pd.DataFrame()
    result = pd.DataFrame(trials[:max_suggestions]).drop(columns="score")
    return result

def make_html_report(
    project, targets, nutrient_result, fertilizer_result, water_result,
    weather_result, stock_result, crop_profile, stage_result, daily_schedule,
):
    def df_html(df):
        return df.to_html(index=False, border=1, float_format=lambda x: f"{x:,.3f}")
    return f"""
    <html>
    <head>
      <meta charset="utf-8">
      <title>Nutrient Dosing Report</title>
      <style>
      body {{ font-family: Arial, sans-serif; margin: 35px; color:#202124; }}
      h1,h2 {{ color:#1b5e20; }}
      table {{ border-collapse:collapse; width:100%; margin-bottom:20px; }}
      th,td {{ padding:7px; border:1px solid #bbb; }}
      th {{ background:#eef6ee; }}
      .note {{ padding:12px; background:#fff8e1; border-left:4px solid #ffb300; }}
      </style>
    </head>
    <body>
      <h1>Nutrient Dosing and Fertigation Report</h1>
      <p><b>Project:</b> {project['project_name']}<br>
      <b>Crop:</b> {project['crop']}<br>
      <b>Plants:</b> {project['plants']:,}<br>
      <b>Crop duration:</b> {project['duration']} days<br>
      <b>Cultivation system:</b> {project['system']}<br>
      <b>Formulation:</b> {project['formulation']}</p>

      <h2>Crop stage profile</h2>
      {df_html(crop_profile)}

      <h2>Location and weather inputs</h2>
      {df_html(weather_result)}

      <h2>Water requirement summary</h2>
      {df_html(water_result)}

      <h2>Stage-wise water requirement</h2>
      {df_html(stage_result)}

      <h2>Complete day-wise water schedule</h2>
      {df_html(daily_schedule)}

      <h2>Nutrient targets</h2>
      {df_html(targets)}

      <h2>Nutrient balance</h2>
      {df_html(nutrient_result)}

      <h2>Fertilizer quantities</h2>
      {df_html(fertilizer_result)}

      <h2>Stock solution plan</h2>
      {df_html(stock_result)}

      <h2>Preparation instructions</h2>
      <ol>
        <li>Use clean water and calibrated weighing equipment.</li>
        <li>Fill each stock tank to about 60–70% of final volume.</li>
        <li>Dissolve each fertilizer separately before adding it to its assigned stock tank.</li>
        <li>Never mix concentrated calcium fertilizer directly with concentrated phosphate or sulfate fertilizer.</li>
        <li>After complete dissolution, bring each stock tank to its final marked volume.</li>
        <li>Inject Stock A and Stock B separately into flowing irrigation water at the selected injection ratio.</li>
        <li>Measure final EC and pH and inspect for cloudiness or precipitation before application.</li>
      </ol>
      <div class="note">
      Calculations are planning estimates. Source-water nutrients, alkalinity, crop stage, climate,
      fertilizer purity, solubility and measured EC/pH should be checked before field use.
      </div>
    </body>
    </html>
    """

def _pdf_text(value):
    """Convert values to text supported by ReportLab's built-in fonts."""
    if isinstance(value, (float, np.floating)):
        if not np.isfinite(value):
            return "N/A"
        return f"{value:,.3f}"
    text = str(value).translate(str.maketrans({
        "–": "-", "—": "-", "×": "x", "·": ".", "²": "2",
        "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
        "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9",
    }))
    return escape(text)

def make_pdf_report(
    project, targets, nutrient_result, fertilizer_result, water_result,
    weather_result, stock_result, crop_profile, stage_result, daily_schedule,
):
    """Create a real PDF byte stream (not HTML renamed as .pdf)."""
    output = BytesIO()
    page_width, page_height = landscape(A4)
    doc = SimpleDocTemplate(
        output, pagesize=landscape(A4),
        leftMargin=12 * mm, rightMargin=12 * mm,
        topMargin=12 * mm, bottomMargin=12 * mm,
        title="Nutrient Dosing and Fertigation Report",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=17, leading=20, textColor=colors.HexColor("#1b5e20"), spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="SectionTitle", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=11, leading=14, textColor=colors.HexColor("#1b5e20"),
        spaceBefore=7, spaceAfter=4,
    ))
    cell_style = ParagraphStyle(
        "PdfCell", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=6.8, leading=8.2, wordWrap="CJK",
    )
    header_style = ParagraphStyle(
        "PdfHeader", parent=cell_style, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#173b1d"),
    )
    usable_width = page_width - 24 * mm

    def pdf_table(df):
        columns = list(df.columns)
        table_data = [[Paragraph(_pdf_text(c), header_style) for c in columns]]
        for row in df.itertuples(index=False, name=None):
            table_data.append([Paragraph(_pdf_text(v), cell_style) for v in row])
        # Give descriptive first columns more room and share the rest evenly.
        if len(columns) == 1:
            widths = [usable_width]
        elif len(columns) >= 8:
            first = min(30 * mm, usable_width * 0.14)
            widths = [first] + [(usable_width - first) / (len(columns) - 1)] * (len(columns) - 1)
        else:
            first = min(68 * mm, usable_width * 0.34)
            widths = [first] + [(usable_width - first) / (len(columns) - 1)] * (len(columns) - 1)
        table = Table(table_data, colWidths=widths, repeatRows=1, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8f2e9")),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#9e9e9e")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        return table

    story = [
        Paragraph("Nutrient Dosing and Fertigation Report", styles["ReportTitle"]),
        Paragraph(
            f"<b>Project:</b> {_pdf_text(project['project_name'])}<br/>"
            f"<b>Crop:</b> {_pdf_text(project['crop'])} &nbsp;&nbsp; "
            f"<b>Plants:</b> {project['plants']:,} &nbsp;&nbsp; "
            f"<b>Crop period:</b> {project['duration']} days<br/>"
            f"<b>System:</b> {_pdf_text(project['system'])}<br/>"
            f"<b>Formulation:</b> {_pdf_text(project['formulation'])}",
            styles["BodyText"],
        ),
        Paragraph("Crop stage profile", styles["SectionTitle"]),
        pdf_table(crop_profile),
        Paragraph("Location and weather inputs", styles["SectionTitle"]),
        pdf_table(weather_result),
        Paragraph("Water requirement summary", styles["SectionTitle"]),
        pdf_table(water_result),
        Paragraph("Stage-wise water requirement", styles["SectionTitle"]),
        pdf_table(stage_result),
        PageBreak(),
        Paragraph("Complete day-wise water schedule", styles["SectionTitle"]),
        pdf_table(daily_schedule),
        PageBreak(),
        Paragraph("Nutrient targets", styles["SectionTitle"]),
        pdf_table(targets),
        Paragraph("Nutrient balance", styles["SectionTitle"]),
        pdf_table(nutrient_result),
        Paragraph("Fertilizer quantities", styles["SectionTitle"]),
        pdf_table(fertilizer_result),
        PageBreak(),
        Paragraph("Stock solution plan", styles["SectionTitle"]),
        pdf_table(stock_result),
        Paragraph("Preparation instructions", styles["SectionTitle"]),
        Paragraph(
            "1. Use clean water and calibrated weighing equipment.<br/>"
            "2. Prepare Stock A and Stock B separately.<br/>"
            "3. Never mix concentrated calcium directly with concentrated phosphate or sulfate.<br/>"
            "4. Verify final EC, pH, clarity, fertilizer purity and source-water analysis before application.",
            styles["BodyText"],
        ),
    ]

    def add_page_number(canvas, document):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.drawRightString(page_width - 12 * mm, 7 * mm, f"Page {document.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    output.seek(0)
    return output.getvalue()

# -----------------------------
# UI
# -----------------------------
STEP_LABELS = [
    "Project & Water", "Nutrient Targets", "Fertilizer Selection",
    "Balance & Stock", "Report"
]
if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 1
if "wizard_data" not in st.session_state:
    st.session_state.wizard_data = {}

wizard_step = int(st.session_state.wizard_step)
apply_dashboard_theme()

st.markdown(
    """
    <div class="dashboard-hero">
      <div class="hero-content">
        <div class="hero-kicker">SMART SOILLESS CULTIVATION</div>
        <h1>Soilless Nutri Master</h1>
        <p>Design a balanced nutrient programme, estimate crop-stage water demand from location-based weather, and prepare precise Stock A and Stock B solutions.</p>
        <div class="feature-strip">
          <span class="feature-chip">🌦 Weather-linked ET₀</span>
          <span class="feature-chip">🌱 Stage-wise Kc</span>
          <span class="feature-chip">⚖ Live nutrient validation</span>
          <span class="feature-chip">📄 PDF · Excel · HTML</span>
        </div>
      </div>
      <div class="hero-mark">🌿</div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        """
        <div class="side-brand">
          <div class="side-logo">🌿</div>
          <div><div class="side-brand-title">Soilless Nutri<br>Master</div>
          <div class="side-brand-sub">Decision-support dashboard</div></div>
        </div>
        <div class="side-kicker">CURRENT WORKFLOW</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="side-current">Step {wizard_step} of {len(STEP_LABELS)}<br>'
        f'<span style="font-size:.78rem;font-weight:500;color:#c7ece2">{STEP_LABELS[wizard_step - 1]}</span></div>',
        unsafe_allow_html=True,
    )
    st.progress((wizard_step - 1) / (len(STEP_LABELS) - 1))
    st.markdown(
        """
        <div class="side-kicker">DASHBOARD MODULES</div>
        <ul class="side-list">
          <li>Crop-stage water scheduling</li>
          <li>Weather and GPS integration</li>
          <li>Nutrient target selection</li>
          <li>Fertilizer balance assistant</li>
          <li>Stock solution preparation</li>
          <li>Multi-format reporting</li>
        </ul>
        <div class="side-note"><b>Planning note</b><br>Verify source-water chemistry, EC, pH and measured reservoir makeup before operational dosing.</div>
        """,
        unsafe_allow_html=True,
    )

step_cards = []
for number, label in enumerate(STEP_LABELS, start=1):
    state = "done" if number < wizard_step else "current" if number == wizard_step else "locked"
    marker = "✓" if number < wizard_step else str(number)
    step_cards.append(
        f'<div class="step-card {state}"><div class="step-number">{marker}</div>'
        f'<div class="step-label">{label}</div></div>'
    )
st.markdown(f'<div class="wizard-stepper">{"".join(step_cards)}</div>', unsafe_allow_html=True)

if wizard_step == 1:
    render_page_heading(
        "🌱", "Project, Crop & Water Planning",
        "Select the crop and cultivation system, then generate a location-specific stage-wise irrigation schedule.",
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        project_name = st.text_input("Project name", "Hydroponic nutrient plan")
        crop_selection = st.selectbox("Crop", list(CROP_PROFILES) + ["Custom crop"])
    with c2:
        plants = st.number_input("Number of plants", min_value=1, value=1000, step=1)
        crop_start = st.date_input("Crop start date", date.today(), key="crop_start_date")
    with c3:
        system = st.selectbox("Cultivation system", list(SYSTEM_PROFILES) + ["Other / custom system"])
    with c4:
        st.caption("Crop period, stage Kc, system efficiency and drainage are filled automatically.")

    if crop_selection == "Custom crop":
        st.markdown("#### Custom crop profile")
        custom_col1, custom_col2 = st.columns(2)
        with custom_col1:
            crop = st.text_input("Custom crop name", "Custom crop")
        with custom_col2:
            plant_area = st.number_input(
                "Effective area per plant (m²)", min_value=0.001,
                value=0.10, step=0.01, key="custom_plant_area",
            )
        custom_stage_names = ["Initial", "Development", "Maturity / production", "Final"]
        stage_columns = st.columns(4)
        stages = []
        for index, (column, stage_name) in enumerate(zip(stage_columns, custom_stage_names)):
            with column:
                st.markdown(f"**{stage_name}**")
                stage_duration = st.number_input(
                    "Duration (days)", min_value=1, value=[10, 20, 30, 10][index],
                    step=1, key=f"custom_stage_days_{index}",
                )
                stage_kc = st.number_input(
                    "Crop coefficient (Kc)", min_value=0.05, max_value=2.0,
                    value=[0.40, 0.65, 0.95, 0.75][index], step=0.05,
                    key=f"custom_stage_kc_{index}",
                )
                stages.append((stage_name, int(stage_duration), float(stage_kc)))
    else:
        crop = crop_selection
        crop_profile = CROP_PROFILES[crop_selection]
        plant_area = float(crop_profile["area"])
        stages = list(crop_profile["stages"])

    duration = sum(stage_days for _, stage_days, _ in stages)
    crop_end = crop_start + timedelta(days=duration - 1)
    profile_df = pd.DataFrame(stages, columns=["Crop stage", "Duration (days)", "Fixed Kc"])
    profile_df["Start day"] = profile_df["Duration (days)"].cumsum().shift(fill_value=0) + 1
    profile_df["End day"] = profile_df["Duration (days)"].cumsum()
    st.success(
        f"{crop}: {duration}-day crop period, {plant_area:.4f} m² effective area per plant, "
        f"from {crop_start.isoformat()} to {crop_end.isoformat()}."
    )
    st.dataframe(profile_df, use_container_width=True, hide_index=True)
    st.caption(
        "Predefined durations, effective areas and Kc values are planning defaults for soilless production. "
        "Calibrate them against measured daily reservoir makeup for the cultivar, spacing and greenhouse."
    )

    if system == "Other / custom system":
        s1, s2, s3 = st.columns(3)
        with s1:
            system_mode = st.radio(
                "Water handling", ["Closed recirculating", "Open drain-to-waste"],
                key="custom_system_mode",
            )
        with s2:
            irrigation_eff = st.number_input(
                "Efficiency / recovery (%)", min_value=1.0, max_value=100.0,
                value=90.0, key="custom_system_efficiency",
            )
        with s3:
            leaching = st.number_input(
                "Drainage fraction (%)", min_value=0.0, max_value=60.0,
                value=10.0 if system_mode == "Open drain-to-waste" else 0.0,
                key="custom_system_drainage",
                disabled=system_mode == "Closed recirculating",
            )
            if system_mode == "Closed recirculating":
                leaching = 0.0
    else:
        system_profile = SYSTEM_PROFILES[system]
        system_mode = system_profile["mode"]
        irrigation_eff = float(system_profile["efficiency"])
        leaching = float(system_profile["drainage"])
        st.info(
            f"Automatic system defaults — {system_mode}; efficiency/recovery: "
            f"{irrigation_eff:.0f}%; drainage allowance: {leaching:.0f}%."
        )

    st.subheader("Day-wise evapotranspiration from coordinate-based weather")
    st.markdown("#### Use the phone's current location")
    st.caption(
        "Tap the location button and allow access. The app fetches daily weather for the crop dates; "
        "days beyond the forecast horizon use a labeled five-year climatology for this location."
    )
    gps_location = None
    if streamlit_geolocation is not None:
        gps_location = streamlit_geolocation()
        if (
            isinstance(gps_location, dict)
            and gps_location.get("latitude") is not None
            and gps_location.get("longitude") is not None
        ):
            gps_latitude = float(gps_location["latitude"])
            gps_longitude = float(gps_location["longitude"])
            gps_signature = (round(gps_latitude, 7), round(gps_longitude, 7))
            if st.session_state.get("last_gps_signature") != gps_signature:
                st.session_state["geo_latitude"] = gps_latitude
                st.session_state["geo_longitude"] = gps_longitude
                st.session_state["last_gps_signature"] = gps_signature
                st.session_state["gps_weather_pending"] = True
                st.session_state.pop("api_schedule", None)
            st.session_state["gps_accuracy_m"] = gps_location.get("accuracy")
            st.session_state["location_method"] = "Phone GPS/browser location"
    else:
        st.warning(
            "Phone-location support is not installed on this server. Install requirements.txt; "
            "latitude and longitude can still be entered manually."
        )

    c1, c2, c3 = st.columns([1, 1, 1.2])
    with c1:
        latitude = st.number_input(
            "Latitude (decimal degrees)", min_value=-90.0, max_value=90.0,
            value=22.30, format="%.5f", key="geo_latitude",
        )
    with c2:
        longitude = st.number_input(
            "Longitude (decimal degrees)", min_value=-180.0, max_value=180.0,
            value=87.32, format="%.5f", key="geo_longitude",
        )
    with c3:
        st.write("")
        fetch_weather = st.button(
            "Fetch weather & calculate stage schedule", type="primary", use_container_width=True,
        )

    last_gps_signature = st.session_state.get("last_gps_signature")
    if last_gps_signature and (
        abs(float(latitude) - last_gps_signature[0]) > 1e-6
        or abs(float(longitude) - last_gps_signature[1]) > 1e-6
    ):
        st.session_state["location_method"] = "Manual coordinates"
    if st.session_state.get("location_method") == "Phone GPS/browser location":
        gps_accuracy = st.session_state.get("gps_accuracy_m")
        accuracy_text = f" Estimated accuracy: {float(gps_accuracy):.0f} m." if gps_accuracy is not None else ""
        st.success(f"Phone location received successfully.{accuracy_text}")

    et_method = st.radio(
        "ET calculation method",
        ["FAO-56 Penman–Monteith", "Hargreaves–Samani"],
        horizontal=True,
    )
    schedule_signature = (
        round(float(latitude), 5), round(float(longitude), 5),
        crop_start.isoformat(), crop_end.isoformat(),
    )
    auto_fetch_gps_weather = bool(st.session_state.pop("gps_weather_pending", False))
    if fetch_weather or auto_fetch_gps_weather:
        try:
            with st.spinner("Fetching daily weather and climatology..."):
                weather_rows, api_metadata = fetch_open_meteo_schedule(
                    latitude, longitude, crop_start, crop_end,
                )
            st.session_state["api_schedule"] = {
                "signature": schedule_signature,
                "rows": weather_rows,
                "metadata": api_metadata,
            }
            st.rerun()
        except RuntimeError as exc:
            st.error(str(exc))
            if auto_fetch_gps_weather:
                st.info("The GPS coordinates were retained. Tap the weather button to try again.")

    api_schedule = st.session_state.get("api_schedule")
    weather_is_current = bool(api_schedule and api_schedule.get("signature") == schedule_signature)
    with st.expander("Manual weather fallback", expanded=not weather_is_current):
        st.caption("These values are repeated for every crop day only when a matching API schedule is not loaded.")
        w1, w2, w3, w4 = st.columns(4)
        with w1:
            tmin = st.number_input("Minimum temperature (°C)", value=20.0, key="wx_tmin")
            tmax = st.number_input("Maximum temperature (°C)", value=32.0, key="wx_tmax")
        with w2:
            tmean = st.number_input("Mean temperature (°C)", value=26.0, key="wx_tmean")
            elevation_manual = st.number_input("Elevation (m)", value=100.0, key="wx_elevation")
        with w3:
            rhmin = st.number_input("Minimum RH (%)", min_value=0.0, max_value=100.0, value=40.0, key="wx_rhmin")
            rhmax = st.number_input("Maximum RH (%)", min_value=0.0, max_value=100.0, value=85.0, key="wx_rhmax")
        with w4:
            wind2 = st.number_input("Wind at 2 m (m/s)", min_value=0.0, value=2.0, key="wx_wind2")
            solar_rad = st.number_input("Solar radiation (MJ/m²/day)", min_value=0.0, value=18.0, key="wx_solar_rad")

    if weather_is_current:
        weather_rows = api_schedule["rows"]
        weather_metadata = api_schedule["metadata"]
        elevation = float(weather_metadata["elevation"])
        source_counts = pd.Series([row["source"] for row in weather_rows]).value_counts()
        weather_source = "; ".join(f"{name}: {count} day(s)" for name, count in source_counts.items())
        manual_weather_confirmed = True
        st.success(f"Complete {duration}-day weather schedule loaded. {weather_source}.")
    else:
        weather_metadata = {
            "latitude": latitude, "longitude": longitude,
            "elevation": elevation_manual, "timezone": "Manual",
        }
        elevation = float(elevation_manual)
        weather_rows = make_manual_weather_schedule(
            crop_start, duration,
            {"tmin": tmin, "tmax": tmax, "tmean": tmean, "rhmin": rhmin,
             "rhmax": rhmax, "wind2": wind2, "solar_rad": solar_rad},
        )
        weather_source = "Manual weather repeated for every crop day"
        st.warning("A matching day-wise API schedule is not loaded.")
        manual_weather_confirmed = st.checkbox(
            "Use the displayed manual weather values for every day of this crop schedule."
        )

    daily_schedule, stage_summary = build_stage_water_schedule(
        weather_rows, stages, latitude, elevation, et_method, plant_area,
        int(plants), system_mode, float(irrigation_eff), float(leaching),
    )
    seasonal = float(daily_schedule["Total fresh supply (L/day)"].sum())
    peak_total_daily = float(daily_schedule["Total fresh supply (L/day)"].max())
    average_per_plant = float(daily_schedule["Fresh supply (L/plant/day)"].mean())
    peak_per_plant = float(daily_schedule["Fresh supply (L/plant/day)"].max())
    total_drainage = float(daily_schedule["Drainage/discard (L/day)"].sum())
    reservoir_volume = max(peak_total_daily, 0.001)
    replacement_count = int(duration)

    weather_df = pd.DataFrame({
        "Variable": [
            "Schedule source", "Location method", "GPS accuracy", "Crop start", "Crop end",
            "Latitude", "Longitude", "Elevation", "Timezone", "ET method",
        ],
        "Value": [
            weather_source, st.session_state.get("location_method", "Manual coordinates"),
            st.session_state.get("gps_accuracy_m", "Not available"),
            crop_start.isoformat(), crop_end.isoformat(), weather_metadata["latitude"],
            weather_metadata["longitude"], elevation, weather_metadata["timezone"], et_method,
        ],
        "Unit": ["", "", "m", "", "", "degree", "degree", "m", "", ""],
    })
    water_df = pd.DataFrame({
        "Item": [
            "Crop period", "Average fresh supply per plant", "Peak fresh supply per plant",
            "Peak total daily fresh supply", "Total crop-period fresh water", "Total drainage/discard",
        ],
        "Value": [duration, average_per_plant, peak_per_plant, peak_total_daily, seasonal, total_drainage],
        "Unit": ["days", "L/plant/day", "L/plant/day", "L/day", "L/crop period", "L/crop period"],
    })

    st.subheader("Stage-wise water requirement")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Average per plant", f"{average_per_plant:.2f} L/day")
    m2.metric("Peak per plant", f"{peak_per_plant:.2f} L/day")
    m3.metric("Peak total supply", f"{peak_total_daily:,.0f} L/day")
    m4.metric("Crop-period fresh water", f"{seasonal:,.0f} L")
    st.dataframe(stage_summary, use_container_width=True, hide_index=True)
    with st.expander("View complete day-wise water schedule", expanded=False):
        st.dataframe(daily_schedule, use_container_width=True, hide_index=True)
    if system_mode == "Closed recirculating":
        st.info("Fresh supply is makeup water. The much larger flow returning through channels/nozzles is recirculation and is not counted as plant consumption.")
    else:
        st.info("Fresh supply includes delivery inefficiency and the automatic drainage fraction for this drain-to-waste system.")

    st.divider()
    if st.button("Submit Page 1 and Continue", type="primary", use_container_width=True):
        page_errors = []
        if not project_name.strip():
            page_errors.append("Project name is required.")
        if not crop.strip():
            page_errors.append("Crop name is required.")
        if not weather_is_current and not manual_weather_confirmed:
            page_errors.append("Fetch the day-wise weather schedule, or explicitly confirm the manual fallback.")
        if not weather_is_current:
            if tmax < tmin:
                page_errors.append("Maximum temperature cannot be lower than minimum temperature.")
            if not (tmin <= tmean <= tmax):
                page_errors.append("Mean temperature must lie between minimum and maximum temperature.")
            if rhmax < rhmin:
                page_errors.append("Maximum relative humidity cannot be lower than minimum relative humidity.")
        if not np.isfinite(seasonal) or seasonal <= 0:
            page_errors.append("Calculated crop-period water requirement must be greater than zero.")
        if page_errors:
            for message in page_errors:
                st.error(message)
        else:
            st.session_state.wizard_data["project_water"] = {
                "project_name": project_name.strip(), "crop": crop.strip(),
                "plants": int(plants), "duration": int(duration), "stages": stages,
                "crop_start": crop_start, "crop_end": crop_end, "system": system,
                "system_mode": system_mode, "irrigation_eff": float(irrigation_eff),
                "leaching": float(leaching), "latitude": float(latitude),
                "longitude": float(longitude), "weather_source": weather_source,
                "et_method": et_method, "plant_area": float(plant_area),
                "reservoir_volume": float(reservoir_volume),
                "seasonal_water": float(seasonal), "replacement_count": int(replacement_count),
                "weather_df": weather_df, "water_df": water_df,
                "stage_summary": stage_summary, "daily_schedule": daily_schedule,
                "crop_profile_df": profile_df,
            }
            st.session_state.wizard_step = 2
            st.rerun()

elif wizard_step == 2:
    render_page_heading(
        "🧪", "Elemental Nutrient Targets",
        "Use a published formulation or define a complete custom elemental target in mg/L.",
    )
    formulation = st.selectbox("Reference formulation", list(FORMULATIONS.keys()) + ["Fully custom"])
    if formulation == "Fully custom":
        default_targets = {e: 0.0 for e in ELEMENTS}
    else:
        default_targets = FORMULATIONS[formulation]
        st.success("The published elemental targets are locked for this predefined formulation.")

    target_cols = st.columns(4)
    targets = {}
    for idx, e in enumerate(ELEMENTS):
        with target_cols[idx % 4]:
            target_key = f"target_{formulation}_{e}"
            if formulation != "Fully custom":
                st.session_state[target_key] = float(default_targets.get(e, 0.0))
            targets[e] = st.number_input(
                f"{e} target (mg/L or ppm)",
                min_value=0.0,
                value=float(default_targets.get(e, 0.0)),
                step=0.01 if e in ["Fe", "Cu", "Zn", "Mn", "B", "Mo"] else 1.0,
                key=target_key,
                disabled=formulation != "Fully custom"
            )

    st.info("For dilute aqueous solutions, mg/L is numerically approximately equal to ppm.")
    target_df = pd.DataFrame({"Nutrient": ELEMENTS, "Target (mg/L)": [targets[e] for e in ELEMENTS]})
    target_m1, target_m2, target_m3 = st.columns(3)
    target_m1.metric("Essential elements", len(ELEMENTS))
    target_m2.metric("Macronutrient total", f"{sum(targets[e] for e in ELEMENTS[:6]):,.1f} mg/L")
    target_m3.metric("Micronutrient total", f"{sum(targets[e] for e in ELEMENTS[6:]):,.2f} mg/L")
    st.dataframe(target_df, use_container_width=True, hide_index=True)

    st.divider()
    back_col, next_col = st.columns(2)
    with back_col:
        if st.button("Back to Page 1", use_container_width=True):
            st.session_state.wizard_step = 1
            st.rerun()
    with next_col:
        if st.button("Submit Page 2 and Continue", type="primary", use_container_width=True):
            missing_targets = [e for e in ELEMENTS if not np.isfinite(targets[e]) or targets[e] <= 0]
            if missing_targets:
                st.error(
                    "Every essential nutrient target must be greater than zero before continuing. "
                    f"Check: {', '.join(missing_targets)}."
                )
            else:
                st.session_state.wizard_data["targets"] = {
                    "formulation": formulation,
                    "targets": dict(targets),
                    "target_df": target_df,
                }
                st.session_state.wizard_step = 3
                st.rerun()

elif wizard_step == 3:
    target_state = st.session_state.wizard_data["targets"]
    formulation = target_state["formulation"]
    targets = target_state["targets"]
    target_df = target_state["target_df"]
    render_page_heading(
        "⚖️", "Fertilizer Selection & Live Balance",
        "Choose market-available fertilizer sources and validate the combination before proceeding.",
    )
    st.info(
        "The catalogue includes commercial greenhouse grades, reagent/plant-culture salts and "
        "EDTA chelates commonly sold for soilless cultivation. Select the exact grade printed on "
        "the supplier label and adjust its declared elemental percentage when necessary."
    )
    macro_options = [p for p in CHEMICALS if p not in MICRONUTRIENT_PRODUCTS]
    cooper_mode = formulation.startswith("Cooper (1979)")
    recommended_macros = FORMULATION_RECOMMENDED_MACROS.get(
        formulation, DEFAULT_MACRONUTRIENT_SELECTION
    )
    recommended_macros = [p for p in recommended_macros if p in macro_options]
    macro_widget_key = f"manual_macronutrient_sources_{formulation}"
    if macro_widget_key not in st.session_state:
        st.session_state[macro_widget_key] = list(recommended_macros)

    guide_col, restore_col = st.columns([3, 1])
    with guide_col:
        st.caption(
            "Start with the recommended set, then use the live assistant below if a nutrient remains deficient or excessive."
        )
    with restore_col:
        if st.button(
            "Restore recommended set", key=f"restore_macros_{formulation}",
            use_container_width=True,
        ):
            st.session_state[macro_widget_key] = list(recommended_macros)
            st.rerun()

    selected_macro = st.multiselect(
        "Macronutrient fertilizers",
        macro_options,
        key=macro_widget_key,
        help=(
            "All available macronutrient fertilizers are selectable. The displayed defaults are "
            "recommendations only; the balance check below validates your final combination."
        )
    )
    with st.expander("Fertilizer role guide – see which nutrients each product supplies", expanded=False):
        role_rows = []
        for product in macro_options:
            supplied = list(CHEMICALS[product]["fractions"].keys())
            role_rows.append({
                "Fertilizer": product,
                "Supplies": ", ".join(supplied),
                "Selection role": (
                    f"Independent {supplied[0]} source"
                    if len(supplied) == 1 else
                    f"Combined {' + '.join(supplied)} source"
                ),
                "Selected": "Yes" if product in selected_macro else "No",
            })
        st.dataframe(pd.DataFrame(role_rows), use_container_width=True, hide_index=True)
    if cooper_mode:
        st.info(
            "The recommended Cooper macronutrient sources are preselected, but they are not locked. "
            "You may add or remove fertilizers; an unbalanced combination cannot continue to the next page."
        )
    st.markdown("#### Micronutrient sources (one product per nutrient)")
    st.caption("Selecting one source automatically excludes every alternative source of the same nutrient.")
    micro_cols = st.columns(3)
    selected_micro = []
    for idx, (nutrient, products) in enumerate(MICRONUTRIENT_SOURCES.items()):
        available_products = COOPER_SAFE_MICROS[nutrient] if cooper_mode else products
        preferred = (
            COOPER_SAFE_MICROS[nutrient][0]
            if formulation != "Fully custom"
            else DEFAULT_MICRONUTRIENT_SOURCE[nutrient]
        )
        if preferred not in available_products:
            preferred = available_products[0]
        with micro_cols[idx % 3]:
            choice = st.selectbox(
                f"{nutrient} source",
                available_products,
                index=available_products.index(preferred),
                key=f"source_{formulation}_{nutrient}"
            )
            selected_micro.append(choice)
    selected = selected_macro + selected_micro

    st.markdown("#### Balance acceptance settings")
    c1, c2 = st.columns(2)
    with c1:
        optimization_mode = st.selectbox(
            "Optimization objective",
            ["Best nutrient match", "Lowest cost", "Lowest total fertilizer mass"],
            key=f"optimization_{formulation}"
        )
    with c2:
        tolerance_key = f"tolerance_{formulation}"
        if formulation != "Fully custom":
            st.session_state[tolerance_key] = 5.0
        tolerance = st.number_input(
            "Maximum permitted deviation (%)", min_value=0.0, max_value=25.0,
            value=5.0, step=0.5, key=tolerance_key,
            disabled=formulation != "Fully custom"
        )
        if formulation != "Fully custom":
            st.caption("The acceptance limit is locked at ±5% for predefined formulations.")

    with st.expander("Advanced nutrient-priority weights", expanded=False):
        priority_cols = st.columns(6)
        weights = []
        for i, e in enumerate(ELEMENTS):
            default_w = 10.0 if e in ["N", "P", "K", "Ca", "Mg", "S"] else 5.0
            with priority_cols[i % 6]:
                weights.append(st.number_input(
                    f"{e} weight", min_value=0.01, value=default_w,
                    key=f"selection_weight_{formulation}_{e}"
                ))

    st.markdown("#### Product settings")
    product_rows = []
    purities, costs, max_doses, custom_fractions = {}, {}, {}, {}
    for chem in selected:
        with st.expander(chem, expanded=False):
            info = CHEMICALS[chem]
            st.write(f"Formula: **{info['formula']}** | Default stock group: **{info['tank']}**")
            c1, c2, c3 = st.columns(3)
            with c1:
                purities[chem] = st.number_input(
                    "Purity or declared-grade factor (%)", min_value=0.1, max_value=100.0,
                    value=100.0, key=f"purity_{chem}"
                )
            with c2:
                costs[chem] = st.number_input(
                    "Cost per kg", min_value=0.0, value=0.0, key=f"cost_{chem}"
                )
            with c3:
                max_doses[chem] = st.number_input(
                    "Maximum dose (mg fertilizer/L; 0 = no limit)", min_value=0.0,
                    value=0.0, key=f"max_{chem}"
                )
            st.caption("For a local/commercial product, override the elemental percentages below.")
            overrides = {}
            cols = st.columns(6)
            for i, e in enumerate(ELEMENTS):
                base_pct = info["fractions"].get(e, 0.0) * 100
                with cols[i % 6]:
                    pct = st.number_input(
                        f"{e} %", min_value=0.0, max_value=100.0,
                        value=float(base_pct), step=0.01, key=f"frac_{chem}_{e}"
                    )
                    if abs(pct - base_pct) > 1e-12:
                        overrides[e] = pct / 100
            custom_fractions[chem] = overrides
            product_rows.append({
                "Fertilizer": chem, "Formula": info["formula"],
                "Purity/grade (%)": purities[chem],
                "Default tank": info["tank"]
            })

    if product_rows:
        st.dataframe(pd.DataFrame(product_rows), use_container_width=True, hide_index=True)
    if any(("acid" in chem.lower() or "hydroxide" in chem.lower()) for chem in selected):
        st.warning(
            "Concentrated acids and alkalis are hazardous. Use suitable PPE, add acid to water, "
            "and keep concentrated pH-adjustment products separate from incompatible stock salts."
        )

    st.markdown("#### Immediate combination validation")
    evaluation = evaluate_fertilizer_balance(
        selected=selected, targets=targets, purities=purities,
        custom_fractions=custom_fractions, max_doses=max_doses, costs=costs,
        weights=weights, optimization_mode=optimization_mode, tolerance=tolerance,
    )
    nutrient_result = evaluation["nutrient_result"]
    finite_deviation = nutrient_result["Deviation (%)"].replace([np.inf, -np.inf], np.nan).abs()
    maximum_deviation = float(finite_deviation.max()) if finite_deviation.notna().any() else float("inf")
    balance_m1, balance_m2, balance_m3 = st.columns(3)
    balance_m1.metric("Selected fertilizer sources", len(selected))
    balance_m2.metric("Balance status", "Accepted" if evaluation["balanced"] else "Needs adjustment")
    balance_m3.metric(
        "Maximum deviation",
        f"{maximum_deviation:.2f}%" if np.isfinite(maximum_deviation) else "Not finite",
    )
    st.dataframe(
        nutrient_result.style.format({
            "Required (mg/L)": "{:.3f}", "Achieved (mg/L)": "{:.3f}",
            "Difference": "{:+.3f}", "Deviation (%)": "{:+.2f}",
        }),
        use_container_width=True, hide_index=True,
    )
    if evaluation["balanced"]:
        st.success(
            f"Combination accepted: every nutrient is within ±{tolerance:.2f}% of the selected target."
        )
    else:
        st.error(
            "Combination rejected. The following nutrients are outside the permitted range; "
            "change the fertilizer sources, purity, maximum dose or tolerance before continuing."
        )
        st.dataframe(
            evaluation["blocking"][[
                "Nutrient", "Required (mg/L)", "Achieved (mg/L)",
                "Deviation (%)", "Status"
            ]].style.format({
                "Required (mg/L)": "{:.3f}", "Achieved (mg/L)": "{:.3f}",
                "Deviation (%)": "{:+.2f}",
            }),
            use_container_width=True, hide_index=True,
        )

        st.markdown("#### Fertilizer selection assistant")
        st.caption(
            "These are decision-support hints calculated from the current nutrient targets, selected products, "
            "purity and declared analysis. Apply one change at a time and review the balance again."
        )
        nutrient_hints = build_nutrient_selection_hints(
            evaluation=evaluation, selected=selected,
            candidate_products=list(CHEMICALS.keys()), purities=purities,
            custom_fractions=custom_fractions,
        )
        if not nutrient_hints.empty:
            st.dataframe(nutrient_hints, use_container_width=True, hide_index=True)

        with st.spinner("Testing simple fertilizer additions, removals and substitutions..."):
            change_hints = recommend_macro_changes(
                evaluation=evaluation, selected_macro=selected_macro,
                selected_micro=selected_micro, macro_options=macro_options,
                targets=targets, purities=purities,
                custom_fractions=custom_fractions, max_doses=max_doses,
                costs=costs, weights=weights, tolerance=tolerance,
            )
        if not change_hints.empty:
            st.write("**Best changes to try first**")
            st.dataframe(
                change_hints.style.format({"Expected maximum deviation (%)": "{:.2f}"}),
                use_container_width=True, hide_index=True,
            )
        else:
            st.warning(
                "No single add, remove or substitute action clearly improves this selection. "
                "Restore the recommended set, review product percentages, or change more than one source."
            )

    st.divider()
    back_col, next_col = st.columns(2)
    with back_col:
        if st.button("Back to Page 2", use_container_width=True):
            st.session_state.wizard_step = 2
            st.rerun()
    with next_col:
        continue_selection = st.button(
            "Submit Balanced Combination and Continue",
            type="primary", use_container_width=True,
            disabled=not evaluation["balanced"],
        )
        if continue_selection:
            st.session_state.wizard_data["fertilizer_selection"] = {
                "selected": list(selected), "purities": dict(purities),
                "costs": dict(costs), "max_doses": dict(max_doses),
                "custom_fractions": dict(custom_fractions),
                "weights": list(weights), "optimization_mode": optimization_mode,
                "tolerance": float(tolerance), "x": evaluation["x"],
                "nutrient_result": nutrient_result,
            }
            st.session_state.wizard_step = 4
            st.rerun()

elif wizard_step == 4:
    render_page_heading(
        "🧴", "Validated Balance & Stock Preparation",
        "Review the accepted nutrient balance and prepare compatible concentrated Stock A and Stock B solutions.",
    )
    project_state = st.session_state.wizard_data["project_water"]
    target_state = st.session_state.wizard_data["targets"]
    selection_state = st.session_state.wizard_data["fertilizer_selection"]
    selected = selection_state["selected"]
    x = selection_state["x"]
    nutrient_result = selection_state["nutrient_result"]
    final_volume = project_state["reservoir_volume"]
    seasonal_solution_volume = project_state["seasonal_water"]

    st.success(
        f"This combination passed Page 3 at ±{selection_state['tolerance']:.2f}% tolerance."
    )
    st.dataframe(
        nutrient_result.style.format({
            "Required (mg/L)": "{:.3f}",
            "Achieved (mg/L)": "{:.3f}",
            "Difference": "{:+.3f}",
            "Deviation (%)": "{:+.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    stock_factor = st.selectbox(
        "Stock concentration factor", [10, 50, 100, 200], index=2,
        key="wizard_stock_factor"
    )
    # Each stock is injected separately at 1:factor. Therefore each stock tank
    # needs final-water-volume/factor litres; A and B are not combined.
    stock_volume_A = seasonal_solution_volume / stock_factor
    stock_volume_B = seasonal_solution_volume / stock_factor
    peak_stock_volume = final_volume / stock_factor

    stock_m1, stock_m2, stock_m3, stock_m4 = st.columns(4)
    stock_m1.metric("Crop-period final water", f"{seasonal_solution_volume:,.2f} L")
    stock_m2.metric("Stock concentration", f"{stock_factor}×")
    stock_m3.metric("Stock A and B volume", f"{stock_volume_A:,.2f} L each")
    stock_m4.metric("Peak-day stock injection", f"{peak_stock_volume:,.3f} L each")
    st.success(
        f"Automatic stock sizing: {seasonal_solution_volume:,.2f} L of final nutrient solution at "
        f"{stock_factor}× requires {stock_volume_A:,.2f} L of Stock A and "
        f"{stock_volume_B:,.2f} L of Stock B, prepared separately. For the peak daily "
        f"{final_volume:,.2f} L batch, inject {peak_stock_volume:,.3f} L from each stock."
    )
    st.caption(
        f"Formula: stock volume = final nutrient-solution volume ÷ concentration factor. "
        f"Stock A and Stock B are each dosed at 1:{stock_factor}; they are never mixed together as concentrates."
    )

    fert_rows, stock_rows = [], []
    for chem, mg_l in zip(selected, x):
        if mg_l <= 1e-9:
            continue
        g_per_1000 = mg_l
        g_for_reservoir = mg_l * final_volume / 1000
        g_crop_period = mg_l * seasonal_solution_volume / 1000
        kg_season_batch = g_crop_period / 1000

        tank_default = CHEMICALS[chem]["tank"]
        if tank_default == "A/B":
            # KNO3 can be placed in either tank; default to A to balance stock loading.
            tank = "A"
        else:
            tank = tank_default

        stock_vol = stock_volume_A if tank == "A" else stock_volume_B
        # If stock is injected at 1:factor, final solution receives stock_volume/factor conceptually.
        # Required stock concentration = final concentration * factor.
        stock_concentration_g_l = mg_l * stock_factor / 1000
        stock_mass_g = mg_l * stock_factor * stock_vol / 1000

        fert_rows.append({
            "Fertilizer": chem,
            "Dose (mg/L)": mg_l,
            "g per 100 L": mg_l / 10,
            "g per 1,000 L": g_per_1000,
            f"g per peak daily batch ({final_volume:,.0f} L)": g_for_reservoir,
            f"Total chemical for {seasonal_solution_volume:,.2f} L (g)": g_crop_period,
            "Total chemical for crop period (kg)": kg_season_batch,
            "Stock tank": tank
        })
        stock_rows.append({
            "Stock": f"Stock {tank}",
            "Fertilizer": chem,
            "Stock factor": f"{stock_factor}×",
            "Final water treated (L)": seasonal_solution_volume,
            "Automatic stock volume (L)": stock_vol,
            "Stock concentration (g/L)": stock_concentration_g_l,
            "Mass to add for crop-period water (g)": stock_mass_g
        })

    fertilizer_result = pd.DataFrame(fert_rows)
    stock_result = pd.DataFrame(stock_rows)

    st.markdown("#### Fertilizer quantities")
    st.dataframe(fertilizer_result, use_container_width=True, hide_index=True)

    st.markdown("#### Stock A and Stock B")
    st.dataframe(stock_result, use_container_width=True, hide_index=True)
    st.info(
        f"Preparation: place the listed Stock A chemicals in a separate container and make the final "
        f"Stock A volume up to {stock_volume_A:,.2f} L. Prepare Stock B separately and make its final "
        f"volume up to {stock_volume_B:,.2f} L. You may prepare smaller proportional batches instead "
        f"of storing the complete crop-period stock at once."
    )

    has_calcium_A = any(("Calcium" in row["Fertilizer"] and row["Stock"] == "Stock A") for row in stock_rows)
    has_phosphate_A = any((("phosphate" in row["Fertilizer"].lower()) and row["Stock"] == "Stock A") for row in stock_rows)
    has_sulfate_A = any((("sulfate" in row["Fertilizer"].lower()) and row["Stock"] == "Stock A") for row in stock_rows)
    if has_calcium_A and (has_phosphate_A or has_sulfate_A):
        st.error("Compatibility warning: concentrated calcium cannot share Stock A with phosphate or sulfate.")
        stock_compatible = False
    else:
        st.success("Compatibility check passed: concentrated calcium is separated from phosphate and sulfate.")
        stock_compatible = True

    st.divider()
    back_col, next_col = st.columns(2)
    with back_col:
        if st.button("Back to Page 3", use_container_width=True):
            st.session_state.wizard_step = 3
            st.rerun()
    with next_col:
        if st.button(
            "Submit Page 4 and Create Reports", type="primary",
            use_container_width=True, disabled=not stock_compatible,
        ):
            st.session_state.wizard_data["stock_plan"] = {
                "stock_factor": stock_factor,
                "stock_volume_A": float(stock_volume_A),
                "stock_volume_B": float(stock_volume_B),
                "peak_stock_volume": float(peak_stock_volume),
                "seasonal_solution_volume": float(seasonal_solution_volume),
                "fertilizer_result": fertilizer_result,
                "stock_result": stock_result,
            }
            st.session_state.wizard_step = 5
            st.rerun()

elif wizard_step == 5:
    render_page_heading(
        "📊", "Project Report & Downloads",
        "Download the completed nutrient, fertilizer, stock-solution and stage-wise water plan.",
    )
    project_state = st.session_state.wizard_data["project_water"]
    target_state = st.session_state.wizard_data["targets"]
    selection_state = st.session_state.wizard_data["fertilizer_selection"]
    stock_state = st.session_state.wizard_data["stock_plan"]
    formulation = target_state["formulation"]
    target_df = target_state["target_df"]
    nutrient_result = selection_state["nutrient_result"]
    fertilizer_result = stock_state["fertilizer_result"]
    stock_result = stock_state["stock_result"]
    weather_df = project_state["weather_df"]
    water_df = project_state["water_df"]
    crop_profile_df = project_state["crop_profile_df"]
    stage_summary = project_state["stage_summary"]
    daily_schedule = project_state["daily_schedule"]
    stock_factor = stock_state["stock_factor"]
    stock_volume_A = stock_state.get(
        "stock_volume_A", project_state["seasonal_water"] / stock_factor
    )
    stock_volume_B = stock_state.get(
        "stock_volume_B", project_state["seasonal_water"] / stock_factor
    )
    peak_stock_volume = stock_state.get(
        "peak_stock_volume", project_state["reservoir_volume"] / stock_factor
    )
    project = {
        "project_name": project_state["project_name"],
        "crop": project_state["crop"],
        "plants": project_state["plants"],
        "duration": project_state["duration"],
        "system": project_state["system"],
        "formulation": formulation
    }

    report_m1, report_m2, report_m3, report_m4 = st.columns(4)
    report_m1.metric("Crop", project_state["crop"])
    report_m2.metric("Plants", f"{project_state['plants']:,}")
    report_m3.metric("Crop period", f"{project_state['duration']} days")
    report_m4.metric("Report formats", "HTML · PDF · Excel")

    report_html = make_html_report(
        project=project,
        targets=target_df,
        nutrient_result=nutrient_result,
        fertilizer_result=fertilizer_result,
        water_result=water_df,
        weather_result=weather_df,
        stock_result=stock_result,
        crop_profile=crop_profile_df,
        stage_result=stage_summary,
        daily_schedule=daily_schedule,
    )

    report_pdf = make_pdf_report(
        project=project,
        targets=target_df,
        nutrient_result=nutrient_result,
        fertilizer_result=fertilizer_result,
        water_result=water_df,
        weather_result=weather_df,
        stock_result=stock_result,
        crop_profile=crop_profile_df,
        stage_result=stage_summary,
        daily_schedule=daily_schedule,
    )

    d1, d2, d3 = st.columns(3)
    with d1:
        st.download_button(
            "Download HTML report",
            data=report_html.encode("utf-8"),
            file_name="nutrient_dosing_report.html",
            mime="text/html",
            use_container_width=True
        )
    with d2:
        st.download_button(
            "Download PDF report",
            data=report_pdf,
            file_name="nutrient_dosing_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        weather_df.to_excel(writer, index=False, sheet_name="Weather inputs")
        crop_profile_df.to_excel(writer, index=False, sheet_name="Crop stage profile")
        water_df.to_excel(writer, index=False, sheet_name="Water summary")
        stage_summary.to_excel(writer, index=False, sheet_name="Stage water schedule")
        daily_schedule.to_excel(writer, index=False, sheet_name="Daily water schedule")
        target_df.to_excel(writer, index=False, sheet_name="Nutrient targets")
        nutrient_result.to_excel(writer, index=False, sheet_name="Nutrient balance")
        fertilizer_result.to_excel(writer, index=False, sheet_name="Fertilizer quantities")
        stock_result.to_excel(writer, index=False, sheet_name="Stock solutions")
    excel_buffer.seek(0)

    with d3:
        st.download_button(
            "Download Excel workbook",
            data=excel_buffer,
            file_name="nutrient_dosing_calculation.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    st.markdown("#### Preparation procedure")
    st.write(
        f"For the calculated **{project_state['seasonal_water']:,.2f} L crop-period final solution**, "
        f"prepare **{stock_volume_A:,.2f} L of Stock A** and **{stock_volume_B:,.2f} L of Stock B** "
        f"separately at **{stock_factor}× concentration**. For the peak daily final-solution batch, "
        f"dose **{peak_stock_volume:,.3f} L from each stock**. At a 1:{stock_factor} setting, "
        f"inject each stock separately into flowing water."
    )
    st.warning(
        "Do not mix concentrated Stock A and Stock B directly. Confirm fertilizer solubility, "
        "source-water analysis, EC and pH before crop application."
    )
    if project_state.get("system_mode") == "Closed recirculating":
        st.info(
            "For a closed recirculating system, the crop-period fertilizer quantity is an upper planning "
            "estimate assuming every litre of fresh makeup water receives the full target concentration. "
            "In operation, replenish nutrients according to measured EC, pH and solution analysis because "
            "water and individual nutrients are not always depleted at the same rate."
        )

    st.divider()
    back_col, restart_col = st.columns(2)
    with back_col:
        if st.button("Back to Page 4", use_container_width=True):
            st.session_state.wizard_step = 4
            st.rerun()
    with restart_col:
        if st.button("Start a New Calculation", use_container_width=True):
            st.session_state.wizard_data = {}
            st.session_state.wizard_step = 1
            st.rerun()

st.markdown(
    """
    <div class="dashboard-footer">
      Soilless Nutri Master &nbsp;•&nbsp; Weather-aware water planning &nbsp;•&nbsp; Nutrient-balance decision support<br>
      Planning estimates must be verified with source-water analysis, EC, pH and measured crop response.
    </div>
    """,
    unsafe_allow_html=True,
)

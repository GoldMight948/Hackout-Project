"""
Modern SaaS UI Design System & Theming Engine for Emission Leak Detector.
Provides Microsoft Power BI / Tableau-grade styling, crisp contrast, glassmorphism,
smooth responsiveness, and high-visibility clean SaaS theme.
"""

import streamlit as st

def inject_custom_css():
    """Injects responsive, enterprise-grade CSS with guaranteed text contrast and SaaS layout."""
    # Enterprise Light Theme Design Variables
    bg_main = "#F8FAFC"
    bg_card = "#FFFFFF"
    bg_card_hover = "#F1F5F9"
    bg_subtle = "#F8FAFC"
    text_primary = "#0F172A"
    text_secondary = "#334155"
    text_muted = "#64748B"
    border_color = "#E2E8F0"
    border_hover = "#CBD5E1"
    shadow_card = "0 4px 16px rgba(0, 0, 0, 0.04)"
    input_bg = "#FFFFFF"
    input_text = "#0F172A"
    metric_bg = "#F8FAFC"

    custom_css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap');

    :root {{
        --bg-main: {bg_main};
        --bg-card: {bg_card};
        --bg-card-hover: {bg_card_hover};
        --bg-subtle: {bg_subtle};
        --text-primary: {text_primary};
        --text-secondary: {text_secondary};
        --text-muted: {text_muted};
        --border-color: {border_color};
        --border-hover: {border_hover};
        --primary-green: #10B981;
        --primary-dark-green: #065F46;
        --accent-emerald: #059669;
        --shadow-card: {shadow_card};
    }}

    html, body, [class*="css"], .stApp {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        background-color: var(--bg-main) !important;
        color: var(--text-primary) !important;
    }}

    /* Container Spacing */
    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 100% !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
    }}

    /* Top Step Indicator */
    .step-indicator-wrapper {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 12px 20px;
        margin-bottom: 22px;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        box-shadow: var(--shadow-card);
    }}

    .step-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #ECFDF5;
        color: #065F46;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        border: 1px solid #A7F3D0;
    }}

    .step-pill {{
        display: inline-flex;
        align-items: center;
        padding: 5px 12px;
        border-radius: 16px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 2px;
        transition: all 0.2s ease;
    }}

    .step-pill.active {{
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: #FFFFFF !important;
        font-weight: 700;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.35);
    }}

    .step-pill.completed {{
        background: var(--bg-subtle);
        color: var(--text-secondary) !important;
        border: 1px solid var(--border-color);
    }}

    .step-pill.upcoming {{
        background: transparent;
        color: var(--text-muted) !important;
    }}

    /* High-Contrast Modern SaaS Cards - Equalized Spacing & Elevation */
    .saas-card {{
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        margin-bottom: 18px !important;
        box-shadow: var(--shadow-card) !important;
        color: var(--text-primary) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
        box-sizing: border-box;
    }}

    .saas-card:hover {{
        border-color: var(--border-hover) !important;
        transform: translateY(-2px);
    }}

    .saas-card-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
        min-height: 28px;
    }}

    .saas-card-title {{
        font-size: 1.0rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        margin: 0 !important;
        letter-spacing: -0.01em;
    }}

    .saas-card-subtitle {{
        font-size: 0.82rem !important;
        color: var(--text-muted) !important;
        margin-top: 3px !important;
        line-height: 1.4 !important;
    }}

    /* KPI Banner Cards - STRICT UNIFORM SIZING & FLEXBOX ALIGNMENT */
    .kpi-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: var(--shadow-card);
        position: relative;
        overflow: hidden;
        color: var(--text-primary) !important;
        min-height: 130px;
        height: 130px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
    }}

    .kpi-card:hover {{
        border-color: var(--border-hover);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.06);
    }}

    .kpi-card::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: #10B981;
    }}

    .kpi-card.deficit::before {{
        background: #EF4444;
    }}

    .kpi-card.warning::before {{
        background: #F59E0B;
    }}

    .kpi-card.info::before {{
        background: #3B82F6;
    }}

    .kpi-title {{
        font-size: 0.76rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        font-weight: 700 !important;
        color: var(--text-muted) !important;
        margin-bottom: 4px !important;
        display: flex;
        align-items: center;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .kpi-value {{
        font-size: 1.75rem !important;
        font-weight: 800 !important;
        color: var(--text-primary) !important;
        line-height: 1.1 !important;
        letter-spacing: -0.02em !important;
        margin: 4px 0;
    }}

    .kpi-subtext {{
        font-size: 0.78rem !important;
        color: var(--text-muted) !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    /* Headline Hero Card */
    .headline-hero {{
        background: linear-gradient(135deg, #064E3B 0%, #065F46 60%, #047857 100%);
        border-radius: 18px;
        padding: 26px 32px;
        color: #FFFFFF !important;
        margin-bottom: 22px;
        box-shadow: 0 12px 30px -6px rgba(6, 78, 59, 0.35);
    }}

    .headline-hero h2, .headline-hero h1, .headline-hero div, .headline-hero p, .headline-hero span {{
        color: #FFFFFF !important;
    }}

    /* Badges */
    .badge-critical {{
        background-color: #FEE2E2 !important;
        color: #991B1B !important;
        border: 1px solid #F87171 !important;
        font-size: 0.75rem;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}

    .badge-high {{
        background-color: #FFEDD5 !important;
        color: #9A3412 !important;
        border: 1px solid #FB923C !important;
        font-size: 0.75rem;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}

    .badge-medium {{
        background-color: #FEF3C7 !important;
        color: #92400E !important;
        border: 1px solid #FBBF24 !important;
        font-size: 0.75rem;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}

    .badge-low {{
        background-color: #DCFCE7 !important;
        color: #166534 !important;
        border: 1px solid #4ADE80 !important;
        font-size: 0.75rem;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}

    /* Table & Data Editor Visibility */
    div[data-testid="stDataFrame"] {{
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }}

    /* Button Enhancements */
    .stButton > button {{
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.25rem !important;
        transition: all 0.2s ease !important;
        border: 1px solid var(--border-color) !important;
    }}

    .stButton > button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
    }}

    /* Form Inputs High-Visibility & Crisp Contrast Override */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="base-input"] {{
        background-color: var(--bg-card) !important;
        border: 1.5px solid var(--border-hover) !important;
        border-radius: 10px !important;
        transition: all 0.2s ease !important;
    }}

    div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {{
        border-color: #10B981 !important;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2) !important;
    }}

    input, textarea, select {{
        color: var(--text-primary) !important;
        background-color: transparent !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }}

    /* Widget Labels Visibility */
    div[data-testid="stWidgetLabel"] label p, label[data-testid="stWidgetLabel"] p {{
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        color: var(--text-primary) !important;
        margin-bottom: 4px !important;
        letter-spacing: -0.01em;
    }}

    /* Form Input Section Containers */
    .input-section-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 16px;
        box-shadow: var(--shadow-card);
    }}

    .input-section-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid var(--border-color);
    }}

    /* Chatbot Copilot Styling */
    .copilot-container {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        box-shadow: var(--shadow-card);
        padding: 16px;
        margin-bottom: 20px;
    }}

    .chat-bubble-user {{
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: #FFFFFF !important;
        border-radius: 14px 14px 2px 14px;
        padding: 10px 14px;
        margin: 8px 0 8px auto;
        max-width: 85%;
        font-size: 0.9rem;
        box-shadow: 0 2px 8px rgba(16,185,129,0.25);
    }}

    .chat-bubble-bot {{
        background: var(--bg-subtle);
        border: 1px solid var(--border-color);
        color: var(--text-primary) !important;
        border-radius: 14px 14px 14px 2px;
        padding: 12px 16px;
        margin: 8px auto 8px 0;
        max-width: 92%;
        font-size: 0.9rem;
        line-height: 1.5;
    }}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: var(--bg-card) !important;
        border-right: 1px solid var(--border-color) !important;
    }}

    section[data-testid="stSidebar"] .block-container {{
        padding-top: 1.5rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
    }}

    /* Mobile adjustments */
    @media (max-width: 900px) {{
        .block-container {{
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}
        .kpi-value {{
            font-size: 1.5rem !important;
        }}
    }}

    /* Feather Icon Alignment & Consistency */
    .feather-icon-wrap {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        vertical-align: middle;
        line-height: 1;
        flex-shrink: 0;
    }}

    .feather-icon-wrap svg {{
        display: inline-block;
        vertical-align: middle;
        overflow: visible;
    }}

    .icon-inline-title {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-weight: 700;
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

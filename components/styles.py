"""
Custom CSS and responsive theming for Emission Leak Detector.
Provides clean card styling, priority badges, progress breadcrumbs, and mobile adjustments.
"""

import streamlit as st

def inject_custom_css():
    """Injects responsive modern CSS into the Streamlit app."""
    custom_css = """
    <style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Reduce default top padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3.5rem;
        max-width: 1140px;
    }

    /* Top Step Progress Bar */
    .step-indicator-wrapper {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 12px 18px;
        margin-bottom: 24px;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    
    .step-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #ECFDF5;
        color: #065F46;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid #A7F3D0;
    }

    .step-pill {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 16px;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 2px;
    }

    .step-pill.active {
        background: #10B981;
        color: white;
        font-weight: 700;
    }

    .step-pill.completed {
        background: #F1F5F9;
        color: #0F172A;
        border: 1px solid #CBD5E1;
    }

    .step-pill.upcoming {
        background: transparent;
        color: #94A3B8;
    }

    /* Big Headline Cards */
    .headline-card {
        background: linear-gradient(135deg, #064E3B 0%, #065F46 60%, #047857 100%);
        border-radius: 16px;
        padding: 24px 28px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(6, 78, 59, 0.25);
    }

    .headline-title {
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #A7F3D0;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .headline-number {
        font-size: 2.8rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 8px;
        letter-spacing: -0.02em;
    }

    .headline-subtitle {
        font-size: 0.95rem;
        color: #D1FAE5;
    }

    /* Clean Card Container */
    .clean-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .clean-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 6px 12px rgba(0,0,0,0.05);
    }

    /* Leak Point Rank Row */
    .leak-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 14px 16px;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        margin-bottom: 10px;
        transition: all 0.2s ease;
    }

    .leak-row:hover {
        border-color: #94A3B8;
        background: #F8FAFC;
    }

    .leak-rank-badge {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.95rem;
    }

    /* Priority Badges */
    .badge-priority-very-high {
        background-color: #FEE2E2;
        color: #B91C1C;
        border: 1px solid #FCA5A5;
        font-size: 0.75rem;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .badge-priority-high {
        background-color: #FFEDD5;
        color: #C2410C;
        border: 1px solid #FDBA74;
        font-size: 0.75rem;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .badge-priority-medium {
        background-color: #FEF3C7;
        color: #B45309;
        border: 1px solid #FDE68A;
        font-size: 0.75rem;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .badge-priority-low {
        background-color: #ECFDF5;
        color: #047857;
        border: 1px solid #A7F3D0;
        font-size: 0.75rem;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    /* Fix Recommendation Card */
    .fix-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #10B981;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }

    .fix-card.hard {
        border-left-color: #F59E0B;
    }

    .fix-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 8px;
    }

    .fix-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0F172A;
    }

    .fix-meta-tag {
        font-size: 0.8rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 6px;
        background: #F1F5F9;
        color: #475569;
    }

    /* Pill buttons & Streamlit button overrides */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        padding: 0.5rem 1.2rem;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    }

    /* Suggestion Box Cards */
    .suggestion-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }

    /* Mobile adjustments */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .headline-number {
            font-size: 2.1rem;
        }
        .step-indicator-wrapper {
            flex-direction: column;
            align-items: flex-start;
            gap: 8px;
        }
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

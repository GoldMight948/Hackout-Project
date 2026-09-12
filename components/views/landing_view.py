"""
Step 1: Landing Page View.
Modern SaaS hero section, sustainability illustrations, feature cards, benefits,
and instant calls-to-action for Login and Profile Creation.
"""

import streamlit as st
from components.icons import feather_icon, COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_INFO, COLOR_NEUTRAL

def render_landing_view():
  """Renders the high-impact modern SaaS landing page."""
  
  # Hero Section
  st.markdown(f"""
    <div class="headline-hero" style="text-align: center; padding: 48px 36px; margin-top: 10px;">
      <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.25); border-radius: 24px; padding: 6px 18px; margin-bottom: 18px;">
        {feather_icon('globe', color='#FFFFFF', size=16, margin_right=4)}
        <span style="font-weight: 700; font-size: 0.88rem; letter-spacing: 0.04em;">ENTERPRISE DECARBONIZATION & CIRCULAR OS</span>
      </div>
      <h1 style="font-size: 2.8rem; font-weight: 800; line-height: 1.15; margin-bottom: 14px; letter-spacing: -0.02em;">
        Industrial Emission Leak-Point Detector<br/>
        <span style="color: #A7F3D0;">& Circular Alternative Recommender</span>
      </h1>
      <p style="font-size: 1.15rem; max-width: 820px; margin: 0 auto 28px auto; line-height: 1.6; opacity: 0.95;">
        Pinpoint operational carbon leak points across energy, transport, waste, and water.
        Reconcile government carbon credits, calculate compliance risk, and unlock circular alternatives
        that deliver immediate ROI and verifiable decarbonization.
      </p>
    </div>
  """, unsafe_allow_html=True)

  # Hero Action Buttons
  c_btn1, c_btn2 = st.columns([1, 1], gap="medium")
  with c_btn1:
    if st.button("Sign In to Existing Account", key="landing_login", type="primary", use_container_width=True):
      st.session_state["auth_tab"] = "login"
      st.session_state["current_step"] = 2
      st.rerun()
  with c_btn2:
    if st.button("Create Business Profile", key="landing_profile", type="primary", use_container_width=True):
      st.session_state["auth_tab"] = "register"
      st.session_state["current_step"] = 2
      st.rerun()

  st.markdown("<div style='margin-bottom: 36px;'></div>", unsafe_allow_html=True)

  # Key Features Section
  st.markdown("""
    <div style="text-align: center; margin-bottom: 24px;">
      <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #8BA49A; font-weight: 700;">
        Platform Capabilities
      </span>
      <h2 style="font-size: 1.85rem; font-weight: 800; margin-top: 4px;">
        Designed for Industrial Facilities, SMEs, and Fleet Operators
      </h2>
    </div>
  """, unsafe_allow_html=True)

  f1, f2, f3, f4 = st.columns(4, gap="medium")

  with f1:
    st.markdown(f"""
      <div class="saas-card" style="height: 100%;">
        <div style="margin-bottom: 12px;">{feather_icon('alert-triangle', color=COLOR_WARNING, size=28, margin_right=0)}</div>
        <div class="saas-card-title">Top 10 Leak Detection</div>
        <p class="saas-card-subtitle">
          Automated multi-factor algorithms rank your worst operational hotspots by tonnes of CO₂e, financial loss, and urgency score.
        </p>
      </div>
    """, unsafe_allow_html=True)

  with f2:
    st.markdown(f"""
      <div class="saas-card" style="height: 100%;">
        <div style="margin-bottom: 12px;">{feather_icon('dollar-sign', color=COLOR_SUCCESS, size=28, margin_right=0)}</div>
        <div class="saas-card-title">Carbon Credit Ledger</div>
        <p class="saas-card-subtitle">
          Benchmark against government-allocated credits. Real-time deficit calculations, compliance purchasing costs, and trading revenue.
        </p>
      </div>
    """, unsafe_allow_html=True)

  with f3:
    st.markdown(f"""
      <div class="saas-card" style="height: 100%;">
        <div style="margin-bottom: 12px;">{feather_icon('refresh-cw', color=COLOR_PRIMARY, size=28, margin_right=0)}</div>
        <div class="saas-card-title">4R Circular Recommender</div>
        <p class="saas-card-subtitle">
          Translate landfill solid waste, water discharge, and heat into Reuse, Recycle, Recover, and Replace circular loops.
        </p>
      </div>
    """, unsafe_allow_html=True)

  with f4:
    st.markdown(f"""
      <div class="saas-card" style="height: 100%;">
        <div style="margin-bottom: 12px;">{feather_icon('sliders', color=COLOR_INFO, size=28, margin_right=0)}</div>
        <div class="saas-card-title">Real-Time What-If Engine</div>
        <p class="saas-card-subtitle">
          Move interactive operational sliders to preview footprint reductions, financial paybacks, and net-zero milestones live.
        </p>
      </div>
    """, unsafe_allow_html=True)

  st.markdown("<div style='margin-bottom: 28px;'></div>", unsafe_allow_html=True)

  # Benefits & ROI
  b1, b2 = st.columns([1.1, 0.9], gap="large")

  with b1:
    st.markdown(f"""
      <div class="saas-card">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
          {feather_icon('trending-up', color=COLOR_SUCCESS, size=22, margin_right=0)}
          <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700;">Measurable Enterprise ROI</h3>
        </div>
        <ul style="margin: 0 0 0 20px; padding: 0; line-height: 1.8; font-size: 0.92rem;">
          <li><strong>Cut Utility Overhead:</strong> Identify 15%–35% direct electricity and gas savings in under 6 months.</li>
          <li><strong>Eliminate Compliance Penalties:</strong> Proactively balance carbon caps to avoid penalty taxes and surcharges.</li>
          <li><strong>Boost Customer Trust:</strong> Deliver certified environmental impact summaries for corporate supply chains and auditors.</li>
          <li><strong>Unlock Subsidies:</strong> Connect directly with clean energy rebates, IRA incentives, and state grants.</li>
        </ul>
      </div>
    """, unsafe_allow_html=True)

  with b2:
    st.markdown(f"""
      <div class="saas-card">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
          {feather_icon('award', color=COLOR_INFO, size=22, margin_right=0)}
          <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700;">4 Pre-Configured Industry Baselines</h3>
        </div>
        <p style="font-size: 0.88rem; line-height: 1.5; margin-bottom: 14px;">
          Skip manual data gathering! Test with production data from our calibrated industrial presets:
        </p>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.85rem; font-weight: 600;">
          <div style="background: var(--bg-subtle); padding: 8px 12px; border-radius: 8px; border: 1px solid var(--border-color); display: flex; align-items: center;">
            {feather_icon('box', color=COLOR_NEUTRAL, size=15)} <span>Food Processing Bakery</span>
          </div>
          <div style="background: var(--bg-subtle); padding: 8px 12px; border-radius: 8px; border: 1px solid var(--border-color); display: flex; align-items: center;">
            {feather_icon('home', color=COLOR_NEUTRAL, size=15)} <span>Retail Store & Boutique</span>
          </div>
          <div style="background: var(--bg-subtle); padding: 8px 12px; border-radius: 8px; border: 1px solid var(--border-color); display: flex; align-items: center;">
            {feather_icon('truck', color=COLOR_NEUTRAL, size=15)} <span>Logistics & Courier Hub</span>
          </div>
          <div style="background: var(--bg-subtle); padding: 8px 12px; border-radius: 8px; border: 1px solid var(--border-color); display: flex; align-items: center;">
            {feather_icon('settings', color=COLOR_NEUTRAL, size=15)} <span>Precision Metalworks Plant</span>
          </div>
        </div>
      </div>
    """, unsafe_allow_html=True)

"""
Step 7: Carbon Credit Analysis & Marketplace View.
Computes statutory surplus/deficit, estimated buying compliance costs or selling revenue,
and features a simulated Carbon Offset Marketplace (buy/sell credits).
"""

import streamlit as st
import pandas as pd
from database.db_manager import record_market_transaction, get_market_transactions
from components.icons import feather_icon, render_icon_heading, COLOR_WARNING, COLOR_SUCCESS, COLOR_NEUTRAL, COLOR_INFO

def render_carbon_credits_view():
  """Renders Step 7 Carbon Credit Analysis and Marketplace."""
  res = st.session_state.get("emissions_results")
  if not res:
    st.warning("Please complete Step 3 Setup or load a preset first.")
    return

  user = st.session_state.get("current_user", {})
  user_email = user.get("email", "guest@enterprise.com")

  c_top_back, c_top_space = st.columns([1.5, 4.5])
  with c_top_back:
    if st.button("← Back to Dashboard", key="credits_top_back_dash"):
      st.session_state["current_step"] = 5
      st.session_state["nav_section"] = "dashboard"
      st.rerun()

  st.markdown("""
    <div style="margin-bottom: 8px;">
      <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #5A8766; font-weight: 700;">
        Step 7 — Carbon Credit Reconciliation & Compliance Ledger
      </span>
    </div>
  """, unsafe_allow_html=True)
  st.markdown(render_icon_heading(
    "dollar-sign",
    "Government Allowance Reconciliation & Market Exposure",
    level="h2",
    color=COLOR_SUCCESS,
    subtitle="Reconcile your annual emissions against government-allocated credits, calculate financial exposure, and trade surplus credits."
  ), unsafe_allow_html=True)

  # Net Carbon Status Banner
  if not res["is_deficit"]:
    st.markdown(f"""
      <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #6EE7B7; border-radius: 14px; padding: 22px 26px; margin-bottom: 24px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px;">
        <div style="display: flex; align-items: center; gap: 16px;">
          <div style="background: rgba(16, 185, 129, 0.15); padding: 12px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
            {feather_icon('check-circle', color=COLOR_SUCCESS, size=32, margin_right=0)}
          </div>
          <div>
            <div style="font-size: 1.25rem; font-weight: 800; color: #065F46;">
              Status: Carbon Neutral / Surplus Allowance
            </div>
            <div style="font-size: 0.92rem; color: #047857; margin-top: 4px;">
              Your emissions ({res['total_co2']:,.1f} t) are below your statutory allocation ({res['govt_credits']:,.0f} credits). 
              You have <strong>{res['credits_remaining']:,.1f} surplus credits</strong> available to bank or sell on the carbon market.
            </div>
          </div>
        </div>
        <div style="text-align: right;">
          <div style="font-size: 0.8rem; color: #047857; font-weight: 700; text-transform: uppercase;">Potential Trading Revenue</div>
          <div style="font-size: 1.8rem; font-weight: 800; color: #065F46;">+₹{res['est_revenue']:,.0f}</div>
        </div>
      </div>
    """, unsafe_allow_html=True)
  else:
    st.markdown(f"""
      <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #FCA5A5; border-radius: 14px; padding: 22px 26px; margin-bottom: 24px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px;">
        <div style="display: flex; align-items: center; gap: 16px;">
          <div style="background: rgba(239, 68, 68, 0.15); padding: 12px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
            {feather_icon('alert-triangle', color=COLOR_WARNING, size=32, margin_right=0)}
          </div>
          <div>
            <div style="font-size: 1.25rem; font-weight: 800; color: #991B1B;">
              Status: Carbon Credit Deficit — Action Required
            </div>
            <div style="font-size: 0.92rem; color: #7F1D1D; margin-top: 4px;">
              Your annual emissions ({res['total_co2']:,.1f} t) exceed your government credit cap ({res['govt_credits']:,.0f} credits). 
              You have a deficit of <strong>{res['credits_required']:,.1f} credits</strong> that must be offset to avoid regulatory fines.
            </div>
          </div>
        </div>
        <div style="text-align: right;">
          <div style="font-size: 0.8rem; color: #991B1B; font-weight: 700; text-transform: uppercase;">Estimated Buying Cost</div>
          <div style="font-size: 1.8rem; font-weight: 800; color: #DC2626;">-₹{res['est_purchase_cost']:,.0f}</div>
        </div>
      </div>
    """, unsafe_allow_html=True)

  # 7 Core Credit Metrics Cards
  c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
  with c1:
    st.markdown(f"""
      <div class="kpi-card info">
        <div class="kpi-title">{feather_icon('shield', color=COLOR_INFO, size=14)} Govt Credits</div>
        <div class="kpi-value">{res['govt_credits']:,.0f}</div>
        <div class="kpi-subtext">allocated cap</div>
      </div>
    """, unsafe_allow_html=True)
  with c2:
    st.markdown(f"""
      <div class="kpi-card">
        <div class="kpi-title">{feather_icon('activity', color=COLOR_NEUTRAL, size=14)} Credits Used</div>
        <div class="kpi-value">{res['credits_used']:,.1f}</div>
        <div class="kpi-subtext">actual emissions</div>
      </div>
    """, unsafe_allow_html=True)
  with c3:
    st.markdown(f"""
      <div class="kpi-card">
        <div class="kpi-title">{feather_icon('leaf', color=COLOR_SUCCESS, size=14)} Credits Remaining</div>
        <div class="kpi-value" style="color: #5A8766;">{res['credits_remaining']:,.1f}</div>
        <div class="kpi-subtext">surplus balance</div>
      </div>
    """, unsafe_allow_html=True)
  with c4:
    st.markdown(f"""
      <div class="kpi-card {'deficit' if res['is_deficit'] else ''}">
        <div class="kpi-title">{feather_icon('alert-triangle', color=COLOR_WARNING, size=14)} Credits Required</div>
        <div class="kpi-value" style="color: {'#EF4444' if res['is_deficit'] else '#5A8766'};">
          {res['credits_required']:,.1f}
        </div>
        <div class="kpi-subtext">shortfall to cover</div>
      </div>
    """, unsafe_allow_html=True)
  with c5:
    st.markdown(f"""
      <div class="kpi-card">
        <div class="kpi-title">{feather_icon('dollar-sign', color=COLOR_NEUTRAL, size=14)} Market Price</div>
        <div class="kpi-value">₹{res['credit_price']:.0f}</div>
        <div class="kpi-subtext">per tonne CO₂</div>
      </div>
    """, unsafe_allow_html=True)
  with c6:
    st.markdown(f"""
      <div class="kpi-card {'deficit' if res['is_deficit'] else ''}">
        <div class="kpi-title">{feather_icon('trending-down', color=COLOR_WARNING, size=14)} Est. Buying Cost</div>
        <div class="kpi-value">₹{res['est_purchase_cost']:,.0f}</div>
        <div class="kpi-subtext">compliance purchase</div>
      </div>
    """, unsafe_allow_html=True)
  with c7:
    st.markdown(f"""
      <div class="kpi-card">
        <div class="kpi-title">{feather_icon('trending-up', color=COLOR_SUCCESS, size=14)} Selling Value</div>
        <div class="kpi-value" style="color: #6B8E7D;">₹{res['est_revenue']:,.0f}</div>
        <div class="kpi-subtext">if surplus sold</div>
      </div>
    """, unsafe_allow_html=True)

  st.markdown("<div style='margin-bottom: 28px;'></div>", unsafe_allow_html=True)

  # Carbon Offset Marketplace Section (UI Simulation)
  st.markdown(f"""
    <div class="saas-card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <div>
          <div class="saas-card-title">{feather_icon('dollar-sign', color=COLOR_SUCCESS, size=18)} Carbon Offset Marketplace (Simulated Trading Desk)</div>
          <div class="saas-card-subtitle">
            Purchase verified carbon credits (Verra VCS / Gold Standard) to eliminate deficits, or list surplus credits:
          </div>
        </div>
        <span class="badge-low">VERIFIED REGISTRY</span>
      </div>
  """, unsafe_allow_html=True)

  col_trade1, col_trade2 = st.columns([1.2, 0.8], gap="large")

  with col_trade1:
    st.markdown(f"""
      <div style="font-weight: 700; font-size: 1.05rem; margin-bottom: 12px; display: flex; align-items: center;">
        {feather_icon('leaf', color=COLOR_SUCCESS, size=18)} <span>Verified Projects Available on Spot Market</span>
      </div>
    """, unsafe_allow_html=True)
    
    market_projects = [
      {"name": "Appalachian Reforestation Carbon Project", "type": "Forestry & Land Use", "registry": "Verra VCS", "price": 34.50, "avail": 1250},
      {"name": "Industrial Landfill Methane Capture Skid", "type": "Methane Abatement", "registry": "Gold Standard", "price": 28.00, "avail": 840},
      {"name": "Commercial Wind Power Farm Expansion", "type": "Renewable Energy", "registry": "CAR / ACR", "price": 22.50, "avail": 3100},
      {"name": "Direct Air Capture & Permanent Mineralization", "type": "Engineered Removal", "registry": "Puro.earth", "price": 140.00, "avail": 180}
    ]

    for p_idx, proj in enumerate(market_projects):
      with st.container():
        st.markdown(f"""
          <div style="background: var(--bg-subtle); border: 1px solid var(--border-color); border-radius: 10px; padding: 12px 16px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <div>
                <strong style="font-size: 0.95rem;">{proj['name']}</strong>
                <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 2px;">
                  {proj['type']} &bull; Registry: <strong>{proj['registry']}</strong> &bull; {proj['avail']} credits available
                </div>
              </div>
              <div style="text-align: right;">
                <div style="font-weight: 800; font-size: 1.1rem; color: #5A8766;">
                  ₹{proj['price']:.2f} <span style="font-size: 0.75rem; font-weight: 500; color: var(--text-muted);">/ credit</span>
                </div>
              </div>
            </div>
          </div>
        """, unsafe_allow_html=True)

        c_buy, c_calc = st.columns([1, 2])
        with c_buy:
          if st.button(f"Buy Credits ({proj['name'].split()[0]})", key=f"buy_btn_{p_idx}", use_container_width=True):
            # Execute simulated purchase
            qty = res['credits_required'] if res['is_deficit'] and res['credits_required'] > 0 else 25.0
            record_market_transaction(user_email, "BUY", qty, proj['price'], f"Offset via {proj['name']}")
            st.success(f"Successfully purchased {qty:.1f} credits from {proj['name']} at ₹{proj['price']:.2f}/credit!")
            st.rerun()

  with col_trade2:
    st.markdown(f"""
      <div style="font-weight: 700; font-size: 1.05rem; margin-bottom: 12px; display: flex; align-items: center;">
        {feather_icon('zap', color=COLOR_WARNING, size=18)} <span>Instant Transaction Desk</span>
      </div>
    """, unsafe_allow_html=True)
    with st.form("trade_form"):
      t_action = st.radio("Order Type", ["Buy Carbon Credits (Offset Deficit)", "Sell Surplus Credits"], horizontal=True)
      default_qty = float(res['credits_required']) if res['is_deficit'] else float(res['credits_remaining'])
      t_qty = st.number_input("Credits (Metric Tonnes CO₂)", min_value=1.0, value=max(1.0, default_qty), step=5.0)
      t_price = st.number_input("Target Price (₹ / tonne)", min_value=1.0, value=float(res['credit_price']), step=1.0)
      
      total_est = t_qty * t_price
      st.markdown(f"""
        <div style="background: var(--bg-subtle); padding: 12px; border-radius: 8px; margin: 12px 0; border: 1px solid var(--border-color);">
          <div style="font-size: 0.8rem; color: var(--text-muted);">Total Estimated Settlement:</div>
          <div style="font-size: 1.4rem; font-weight: 800; color: #5A8766;">₹{total_est:,.2f}</div>
        </div>
      """, unsafe_allow_html=True)

      submit_trade = st.form_submit_button(
        "Execute Simulated Market Order",
        type="primary",
        use_container_width=True
      )

      if submit_trade:
        action_type = "BUY" if "Buy" in t_action else "SELL"
        record_market_transaction(user_email, action_type, t_qty, t_price, "Manual Exchange Order")
        st.success(f"Order filled! {action_type} {t_qty:,.0f} credits @ ₹{t_price:.2f}/credit (₹{total_est:,.2f}).")
        st.rerun()

    # Recent Transactions
    txs = get_market_transactions(user_email)
    if txs:
      st.markdown(f"""
        <div style="font-weight: 700; font-size: 1rem; margin-top: 14px; margin-bottom: 8px; display: flex; align-items: center;">
          {feather_icon('file-text', color=COLOR_NEUTRAL, size=16)} <span>Recent Ledger Orders</span>
        </div>
      """, unsafe_allow_html=True)
      for t in txs[:3]:
        t_color = "#5A8766" if t["tx_type"] == "SELL" else "#3B82F6"
        st.markdown(f"""
          <div style="font-size: 0.82rem; padding: 6px 0; border-bottom: 1px dotted var(--border-color);">
            <span style="color: {t_color}; font-weight: 700;">[{t['tx_type']}]</span> 
            <strong>{t['credits']} credits</strong> @ ₹{t['price_per_credit']:.2f} (₹{t['total_amount']:,.2f}) &bull; {t['timestamp'].split()[0]}
          </div>
        """, unsafe_allow_html=True)

  st.markdown("</div>", unsafe_allow_html=True)

  # Navigation
  st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)
  c_b1, c_b2 = st.columns([1, 1])
  with c_b1:
    if st.button("← Back to Dashboard", key="credits_back_dash"):
      st.session_state["current_step"] = 5
      st.session_state["nav_section"] = "dashboard"
      st.rerun()
  with c_b2:
    if st.button("Proceed to AI Decarbonization Recommendations →", type="primary", key="credits_next_recom", use_container_width=True):
      st.session_state["current_step"] = 8
      st.session_state["nav_section"] = "recommendations"
      st.rerun()

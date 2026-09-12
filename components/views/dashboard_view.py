"""
Step 5: Executive Dashboard View.
Delivers a modern SaaS analytics interface (similar to Microsoft Power BI & Tableau).
Includes Top KPI cards, Gauge chart, Donut chart, Pie chart, Bar chart,
Stacked Bar chart, Line chart, Area chart, and quick links to Analytics.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import date, datetime
from components.calculations import (
  calculate_detailed_emissions, calculate_carbon_credit_audit, get_statutory_carbon_quota,
  generate_hotspot_recommendations
)

from components.ml_forecast import generate_monthly_timeseries, forecast_emissions_ml
from components.auth import is_demo_session, reset_current_demo_profile
from database.db_manager import (
  get_activity_logs, get_aggregated_activity_summary,
  save_activity_log, delete_activity_log, sync_activity_logs_to_dashboard,
  ACTIVITY_EMISSION_FACTORS, seed_demo_activity_logs
)
from components.icons import (
  feather_icon, COLOR_WARNING, COLOR_SUCCESS, COLOR_NEUTRAL,
  COLOR_SECONDARY, COLOR_INFO, COLOR_AMBER
)
from components.chatbot import render_copilot_chat

def render_dashboard_view():
  """Renders executive KPI cards, annual baseline, and dynamic daily/weekly activity visualizations."""
  if "emissions_results" not in st.session_state or st.session_state["emissions_results"] is None:
    inputs = st.session_state.get("form_inputs", {})
    if not inputs:
      st.warning("No data found. Please complete Setup or load a demo dataset.")
      if st.button("Go to Setup"):
        st.session_state["current_step"] = 3
        st.session_state["nav_section"] = "setup"
        st.rerun()
      return
    st.session_state["emissions_results"] = calculate_detailed_emissions(inputs)

  user = st.session_state.get("current_user", {})
  user_email = user.get("email", "guest@enterprise.com")
  is_demo = is_demo_session()

  # Dynamic synchronization with operational activity logs
  agg_stat = get_aggregated_activity_summary(user_email)
  total_logs_count = agg_stat.get("total_entries", 0)
  current_data_sig = f"{user_email}_{total_logs_count}_{agg_stat.get('total_co2', 0.0):.4f}_{agg_stat.get('latest_date', '')}"
  last_data_sig = st.session_state.get("dash_data_signature")
  res_co2 = st.session_state.get("emissions_results", {}).get("total_co2", 0.0) if st.session_state.get("emissions_results") else 0.0

  if total_logs_count > 0 and (
    last_data_sig != current_data_sig or
    st.session_state.get("dash_synced_email") != user_email or
    res_co2 == 0.0
  ):
    synced_res = sync_activity_logs_to_dashboard(user_email, is_demo=is_demo)
    if synced_res:
      st.session_state["emissions_results"] = synced_res
    st.session_state["dash_synced_email"] = user_email
    st.session_state["dash_synced_entries"] = total_logs_count
    st.session_state["dash_data_signature"] = current_data_sig
    st.session_state["manual_setup_override"] = False

  res = st.session_state["emissions_results"]
  user_logs = get_activity_logs(user_email, limit=500)
  audit_data = calculate_carbon_credit_audit(user, user_logs, res)
  comp_name = res.get("raw_inputs", {}).get("business_name") or st.session_state.get("form_inputs", {}).get("business_name") or user.get("company_name", "Enterprise Facility")
  chart_text_color = "#1E293B"

  # Demo Profile Isolation Banner
  if is_demo:
    d_icon = feather_icon("box", color=COLOR_WARNING, size=20, margin_right=8)
    c_banner1, c_banner2 = st.columns([3.5, 1.2])
    with c_banner1:
      st.markdown(f"""
        <div style="background: rgba(245, 158, 11, 0.12); border: 1px solid #FCD34D; border-radius: 10px; padding: 10px 16px; margin-bottom: 16px; display: flex; align-items: center;">
          {d_icon}
          <div style="font-size: 0.88rem; color: #92400E;">
            <strong>Demo Profile Sandbox Mode:</strong> You are exploring a pre-calibrated sample enterprise. Your activity logs and assessments are isolated in sandbox storage.
          </div>
        </div>
      """, unsafe_allow_html=True)
    with c_banner2:
      if st.button("Reset Demo Defaults", key="dash_reset_demo_btn", use_container_width=True):
        reset_current_demo_profile()
        st.success("Demo profile reset to factory defaults!")
        st.rerun()

  # Defaulted Fields Notice Banner (Task 4: Surface Silent Defaults)
  def_fields = res.get("defaulted_fields", [])
  if def_fields:
    field_labels = {
      "water_m3": "Water Consumption (est. 1,200 m³/yr)",
      "raw_material_tonnes": "Raw Materials (est. 150 t/yr)",
      "production_units": "Production Output (est. 25,000 units/yr)",
      "total_credits": "Carbon Credits Quota (est. 150 t)",
      "machine_hours": "Machine Operating Hours (est. 2,200 hrs/yr)"
    }
    human_readable = [field_labels.get(f, f) for f in def_fields]
    info_icon = feather_icon("info", color=COLOR_INFO, size=18, margin_right=8)
    c_notif1, c_notif2 = st.columns([4.2, 1.2])
    with c_notif1:
      st.markdown(f"""
        <div style="background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 10px; padding: 9px 15px; margin-bottom: 14px; display: flex; align-items: center;">
          {info_icon}
          <div style="font-size: 0.85rem; color: #1E40AF;">
            <strong>Notice — Baseline Estimates Active:</strong> Some operational parameters were omitted from assessment inputs and are using standard industry baseline defaults:
            <span style="font-weight: 600;">{", ".join(human_readable)}</span>.
          </div>
        </div>
      """, unsafe_allow_html=True)
    with c_notif2:
      if st.button("Update in Setup", key="dash_update_defaults_btn", use_container_width=True):
        st.session_state["nav_section"] = "setup"
        st.session_state["current_step"] = 3
        st.rerun()

  # Header section with Feather Icon
  head_icon = feather_icon("pie-chart", color="#8BA49A", size=30, margin_right=10)
  cal_icon = feather_icon("calendar", color="var(--text-muted)", size=15, margin_right=6)
  st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
      <div>
        <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #8BA49A; font-weight: 700;">
          Executive Overview & Carbon Intelligence
        </span>
        <h1 style="font-size: 2.1rem; font-weight: 800; margin: 4px 0 0 0; letter-spacing: -0.02em; display: flex; align-items: center;">
          {head_icon} {comp_name} Carbon Dashboard
        </h1>
      </div>
      <div style="display: flex; gap: 10px; align-items: center;">
        <span style="background: var(--bg-card); border: 1px solid var(--border-color); padding: 6px 14px; border-radius: 8px; font-size: 0.85rem; font-weight: 600; display: flex; align-items: center;">
          {cal_icon} Compliance Status
        </span>
        <span class="{'badge-low' if not res['is_deficit'] else 'badge-critical'}">
          {res['net_carbon_status']}
        </span>
      </div>
    </div>
  """, unsafe_allow_html=True)

  # Master View Mode Tabs: Annual Baseline vs Periodic Tracking
  tab_annual, tab_periodic = st.tabs([
    "Enterprise Baseline (Annual Assessment)",
    "Daily & Weekly Activity Tracking & Trends"
  ])

  with tab_annual:
    # Live Operational Sync Banner (reflects real-time daily activity logs)
    agg_stat = get_aggregated_activity_summary(user_email)
    if agg_stat["total_entries"] > 0:
      sync_icon = feather_icon("refresh-cw", color="#8BA49A", size=16, margin_right=8)
      st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 10px 14px; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
          <div style="display: flex; align-items: center;">
            {sync_icon}
            <div style="font-size: 0.86rem; color: #065F46;">
              <strong>Dynamic Real-Time Sync Active:</strong> Baseline metrics actively reflect <strong>{agg_stat['total_entries']}</strong> logged operational shifts ({agg_stat['date_range']}) generating <strong>{agg_stat['total_co2']:,.1f} t CO₂e</strong>.
            </div>
          </div>
          <span style="font-size: 0.75rem; background: #DCFCE7; color: #166534; padding: 3px 10px; border-radius: 6px; font-weight: 700;">
            LIVE OPERATIONAL RUN-RATE
          </span>
        </div>
      """, unsafe_allow_html=True)

    # Carbon Copilot Assistant Quick Drawer
    with st.expander("Carbon Copilot AI — Intelligent Navigation & Personalized Carbon Advisory", expanded=False):
      render_copilot_chat(key_prefix="dash_copilot")

    # Equal-Sized Enterprise KPI Grid - Row 1 (4 Core Metrics)
    k1, k2, k3, k4 = st.columns(4)
    
    with k1:
      logged_sub = f"{agg_stat['total_co2']:,.2f} t accrued ({total_logs_count} logs)" if total_logs_count > 0 else "Annualized run-rate"
      st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-title">
            {feather_icon("leaf", color=COLOR_SUCCESS, size=15, margin_right=5)} Total Emissions
          </div>
          <div class="kpi-value">{res['total_co2']:,.1f}</div>
          <div class="kpi-subtext">tonnes CO₂e / yr • {logged_sub}</div>
        </div>
      """, unsafe_allow_html=True)

    with k2:
      st.markdown(f"""
        <div class="kpi-card info">
          <div class="kpi-title">
            {feather_icon("award", color=COLOR_INFO, size=15, margin_right=5)} Govt Quota
          </div>
          <div class="kpi-value">{res['govt_credits']:,.0f}</div>
          <div class="kpi-subtext">statutory carbon credits</div>
        </div>
      """, unsafe_allow_html=True)

    with k3:
      used_sub = f"{agg_stat['total_co2']:,.2f} t logged to date" if total_logs_count > 0 else "1 credit = 1 t CO₂e"
      st.markdown(f"""
        <div class="kpi-card warning">
          <div class="kpi-title">
            {feather_icon("activity", color=COLOR_AMBER, size=15, margin_right=5)} Credits Used
          </div>
          <div class="kpi-value">{res['credits_used']:,.1f}</div>
          <div class="kpi-subtext">run-rate quota • {used_sub}</div>
        </div>
      """, unsafe_allow_html=True)

    with k4:
      deficit_class = "deficit" if res['is_deficit'] else "low"
      def_icon = feather_icon("alert-triangle" if res['is_deficit'] else "check-circle", color=COLOR_WARNING if res['is_deficit'] else COLOR_SUCCESS, size=15, margin_right=5)
      net_val = res['credits_required'] if res['is_deficit'] else res['credits_remaining']
      net_sub = 'tonnes deficit (compliance buy)' if res['is_deficit'] else 'tonnes surplus balance'
      st.markdown(f"""
        <div class="kpi-card {deficit_class}">
          <div class="kpi-title">
            {def_icon} Net Carbon Status
          </div>
          <div class="kpi-value" style="color: {'#EF4444' if res['is_deficit'] else '#8BA49A'};">
            {net_val:,.1f}
          </div>
          <div class="kpi-subtext">{net_sub}</div>
        </div>
      """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

    # Equal-Sized Enterprise KPI Grid - Row 2 (3 Secondary Metrics)
    k5, k6, k7 = st.columns(3)

    with k5:
      st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-title">
            {feather_icon("shield", color=COLOR_SUCCESS, size=15, margin_right=5)} Trading Reserve
          </div>
          <div class="kpi-value">{res['credits_remaining']:,.1f}</div>
          <div class="kpi-subtext">excess credits available to sell</div>
        </div>
      """, unsafe_allow_html=True)

    with k6:
      st.markdown(f"""
        <div class="kpi-card {'deficit' if res['compliance_cost'] > 0 else ''}">
          <div class="kpi-title">
            {feather_icon("dollar-sign", color=COLOR_NEUTRAL, size=15, margin_right=5)} Compliance Liability
          </div>
          <div class="kpi-value">₹{res['compliance_cost']:,.0f}</div>
          <div class="kpi-subtext">@ benchmark ₹{res['credit_price']:.0f}/tonne</div>
        </div>
      """, unsafe_allow_html=True)

    with k7:
      score_val = res['sustainability_score']
      score_color = "#8BA49A" if score_val >= 70 else ("#F59E0B" if score_val >= 45 else "#EF4444")
      score_badge = "Tier A (Leader)" if score_val >= 75 else ("Tier B (Standard)" if score_val >= 50 else "Tier C (Action Needed)")
      st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-title">
            {feather_icon("target", color=score_color, size=15, margin_right=5)} Eco Score
          </div>
          <div class="kpi-value" style="color: {score_color};">{score_val:.0f} / 100</div>
          <div class="kpi-subtext">{score_badge}</div>
        </div>
      """, unsafe_allow_html=True)

    # =========================================================================
    # STATUTORY GOVERNMENT QUOTA CROSS-CHECK & CARBON CREDIT CONSUMPTION AUDIT
    # =========================================================================
    audit_icon = feather_icon("award", color="#8BA49A", size=20, margin_right=8)
    st.markdown(f"""
      <div class="saas-card" style="margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
          <div>
            <div class="saas-card-title" style="display: flex; align-items: center; font-size: 1.15rem;">
              {audit_icon} Statutory Government Quota Cross-Check & Carbon Credit Intelligence
            </div>
            <div class="saas-card-subtitle" style="margin-top: 4px;">
              Cross-referencing initial government statutory quota issued against measured daily/weekly credit burn and expected annual use:
            </div>
          </div>
          <span class="{'badge-low' if not audit_data['is_projected_deficit'] else 'badge-critical'}" style="font-size: 0.85rem; padding: 6px 14px;">
            {audit_data['audit_verdict']}
          </span>
        </div>
    """, unsafe_allow_html=True)

    # 4 Equal-Sized Audit Summary KPI Cards
    ac1, ac2, ac3, ac4 = st.columns(4)

    with ac1:
      st.markdown(f"""
        <div class="kpi-card info">
          <div class="kpi-title">
            {feather_icon("shield", color=COLOR_INFO, size=15, margin_right=5)} Initial Govt Quota
          </div>
          <div class="kpi-value">{audit_data['initial_govt_quota']:,.0f}</div>
          <div class="kpi-subtext">Statutory allocation • {audit_data['employees']} emp</div>
        </div>
      """, unsafe_allow_html=True)

    with ac2:
      st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-title">
            {feather_icon("sun", color=COLOR_SUCCESS, size=15, margin_right=5)} Daily Credit Use
          </div>
          <div class="kpi-value">{audit_data['actual_daily_avg']:.3f}</div>
          <div class="kpi-subtext">credits / day • Cap: {audit_data['daily_quota_target']:.3f} ({audit_data['daily_pct_of_allowance']:.1f}%)</div>
        </div>
      """, unsafe_allow_html=True)

    with ac3:
      st.markdown(f"""
        <div class="kpi-card warning">
          <div class="kpi-title">
            {feather_icon("calendar", color=COLOR_WARNING, size=15, margin_right=5)} Weekly Credit Use
          </div>
          <div class="kpi-value">{audit_data['actual_weekly_avg']:.2f}</div>
          <div class="kpi-subtext">credits / week • Cap: {audit_data['weekly_quota_target']:.2f} ({audit_data['weekly_pct_of_allowance']:.1f}%)</div>
        </div>
      """, unsafe_allow_html=True)

    with ac4:
      exp_color = "#EF4444" if audit_data['is_projected_deficit'] else "#8BA49A"
      exp_sub = f"Deficit: -{audit_data['projected_credits_needed']:,.0f} credits" if audit_data['is_projected_deficit'] else f"Surplus: +{audit_data['projected_surplus_credits']:,.0f} credits"
      st.markdown(f"""
        <div class="kpi-card {'deficit' if audit_data['is_projected_deficit'] else 'low'}">
          <div class="kpi-title">
            {feather_icon("trending-up", color=exp_color, size=15, margin_right=5)} Expected Annual Use
          </div>
          <div class="kpi-value" style="color: {exp_color};">{audit_data['expected_annual_burn']:,.1f}</div>
          <div class="kpi-subtext">Run-rate forecast • {exp_sub}</div>
        </div>
      """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    # Cross-Check Comparison Matrix Table
    status_badge_daily = '<span class="badge-low" style="padding: 3px 8px; font-size: 0.75rem;">WITHIN DAILY CAP</span>' if audit_data['actual_daily_avg'] <= audit_data['daily_quota_target'] else '<span class="badge-critical" style="padding: 3px 8px; font-size: 0.75rem;">EXCEEDS DAILY CAP</span>'
    status_badge_weekly = '<span class="badge-low" style="padding: 3px 8px; font-size: 0.75rem;">WITHIN WEEKLY CAP</span>' if audit_data['actual_weekly_avg'] <= audit_data['weekly_quota_target'] else '<span class="badge-medium" style="padding: 3px 8px; font-size: 0.75rem;">FREIGHT / LOGISTICS SURGE</span>'
    status_badge_annual = '<span class="badge-low" style="padding: 3px 8px; font-size: 0.75rem;">FULL-YEAR COMPLIANT</span>' if not audit_data['is_projected_deficit'] else f'<span class="badge-critical" style="padding: 3px 8px; font-size: 0.75rem;">🔴 SHORTFALL (-{audit_data["projected_credits_needed"]:,.0f} t)</span>'
    status_badge_bank = f'<span class="badge-low" style="padding: 3px 8px; font-size: 0.75rem;">{audit_data["accrued_balance_pct"]:.1f}% AVAILABLE</span>' if audit_data['accrued_balance_pct'] >= 50 else f'<span class="badge-medium" style="padding: 3px 8px; font-size: 0.75rem;">🟡 {audit_data["accrued_balance_pct"]:.1f}% REMAINING</span>'

    monthly_accrued_estimate = (audit_data['actual_daily_avg'] * 30.4) + (audit_data['actual_weekly_avg'] * 4.33)

    matrix_html = f"""
      <div style="overflow-x: auto; margin-bottom: 14px;">
        <table class="saas-table" style="width: 100%; font-size: 0.88rem; border-collapse: collapse;">
          <thead>
            <tr style="border-bottom: 2px solid var(--border-color); text-align: left;">
              <th style="padding: 10px 12px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; font-size: 0.75rem;">Operational Scope</th>
              <th style="padding: 10px 12px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; font-size: 0.75rem;">Govt Issued Quota Allowance</th>
              <th style="padding: 10px 12px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; font-size: 0.75rem;">⚡ Actual Measured Rate</th>
              <th style="padding: 10px 12px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; font-size: 0.75rem;">📈 Expected Forecast Burn</th>
              <th style="padding: 10px 12px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; font-size: 0.75rem;">Cross-Check Compliance Audit</th>
            </tr>
          </thead>
          <tbody>
            <tr style="border-bottom: 1px solid var(--border-color);">
              <td style="padding: 10px 12px; font-weight: 600;">{feather_icon('sun', size=16, margin_right=6)} <strong>Daily Carbon Credits</strong></td>
              <td style="padding: 10px 12px;"><strong>{audit_data['daily_quota_target']:.3f}</strong> credits / day</td>
              <td style="padding: 10px 12px;"><strong>{audit_data['actual_daily_avg']:.3f}</strong> credits / day <span style="font-size: 0.78rem; color: var(--text-muted);">({audit_data['daily_entries_count']} daily logs)</span></td>
              <td style="padding: 10px 12px;"><strong>{audit_data['expected_daily_burn']:.3f}</strong> credits / day pace</td>
              <td style="padding: 10px 12px;">{status_badge_daily}</td>
            </tr>
            <tr style="border-bottom: 1px solid var(--border-color);">
              <td style="padding: 10px 12px; font-weight: 600;"><strong>Weekly Carbon Credits</strong></td>
              <td style="padding: 10px 12px;"><strong>{audit_data['weekly_quota_target']:.2f}</strong> credits / week</td>
              <td style="padding: 10px 12px;"><strong>{audit_data['actual_weekly_avg']:.2f}</strong> credits / week <span style="font-size: 0.78rem; color: var(--text-muted);">({audit_data['weekly_entries_count']} weekly logs)</span></td>
              <td style="padding: 10px 12px;"><strong>{audit_data['expected_weekly_burn']:.2f}</strong> credits / week pace</td>
              <td style="padding: 10px 12px;">{status_badge_weekly}</td>
            </tr>
            <tr style="border-bottom: 1px solid var(--border-color);">
              <td style="padding: 10px 12px; font-weight: 600;">{feather_icon('calendar', size=16, margin_right=6)} <strong>Monthly Run-Rate</strong></td>
              <td style="padding: 10px 12px;"><strong>{audit_data['monthly_quota_target']:.2f}</strong> credits / month</td>
              <td style="padding: 10px 12px;"><strong>{monthly_accrued_estimate:.2f}</strong> credits / month measured</td>
              <td style="padding: 10px 12px;"><strong>{audit_data['expected_monthly_burn']:.2f}</strong> credits / month forecast</td>
              <td style="padding: 10px 12px;"><span style="font-size: 0.8rem; color: var(--text-muted);">Run-Rate Tracking</span></td>
            </tr>
            <tr style="border-bottom: 1px solid var(--border-color); background: rgba(16, 185, 129, 0.03);">
              <td style="padding: 10px 12px; font-weight: 700; color: #065F46;">{feather_icon('award', size=16, margin_right=6)} <strong>Annual Statutory Quota</strong></td>
              <td style="padding: 10px 12px; font-weight: 700; color: #6B8E7D;"><strong>{audit_data['initial_govt_quota']:,.0f}</strong> credits initially issued</td>
              <td style="padding: 10px 12px;"><strong>{audit_data['accrued_credits_used']:,.2f}</strong> credits used to date <span style="font-size: 0.78rem; color: var(--text-muted);">({audit_data['total_entries_count']} shifts)</span></td>
              <td style="padding: 10px 12px; font-weight: 700; color: {'#DC2626' if audit_data['is_projected_deficit'] else '#6B8E7D'};"><strong>{audit_data['expected_annual_burn']:,.1f}</strong> credits expected full year</td>
              <td style="padding: 10px 12px;">{status_badge_annual}</td>
            </tr>
            <tr>
              <td style="padding: 10px 12px; font-weight: 600;">{feather_icon('briefcase', size=16, margin_right=6)} <strong>Remaining Quota in Bank</strong></td>
              <td style="padding: 10px 12px;"><strong>{audit_data['initial_govt_quota']:,.0f}</strong> credits initial total</td>
              <td style="padding: 10px 12px;"><strong>{audit_data['accrued_remaining_balance']:,.2f}</strong> credits balance <span style="font-size: 0.78rem; color: var(--text-muted);">({audit_data['accrued_balance_pct']:.1f}%)</span></td>
              <td style="padding: 10px 12px;"><strong>~{audit_data['quota_runway_days']}</strong> days runway at expected pace</td>
              <td style="padding: 10px 12px;">{status_badge_bank}</td>
            </tr>
          </tbody>
        </table>
      </div>
    """
    st.markdown(matrix_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)


    # Monthly Timeseries Data for Trajectory
    monthly_df = generate_monthly_timeseries(res["pillar_co2"])

    # Row 1 Charts (Balanced 1:1, Equal Height 280px): Gauge & Pillar Breakdown
    col_gauge, col_pie = st.columns([1, 1], gap="medium")

    with col_gauge:
      gauge_title = feather_icon("target", color=COLOR_SUCCESS, size=18, margin_right=6)
      st.markdown(f"""
        <div class="saas-card">
          <div class="saas-card-title" style="display: flex; align-items: center;">{gauge_title} Overall Sustainability Performance (0–100)</div>
          <div class="saas-card-subtitle">Comprehensive operational green efficiency score</div>
      """, unsafe_allow_html=True)

      fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=res["sustainability_score"],
        number={'suffix': "/100", 'font': {'size': 28, 'color': chart_text_color}},
        gauge={
          'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': chart_text_color},
          'bar': {'color': "#8BA49A", 'thickness': 0.28},
          'bgcolor': "rgba(0,0,0,0)",
          'borderwidth': 1,
          'bordercolor': "var(--border-color)",
          'steps': [
            {'range': [0, 45], 'color': 'rgba(239, 68, 68, 0.25)'},
            {'range': [45, 70], 'color': 'rgba(245, 158, 11, 0.25)'},
            {'range': [70, 100], 'color': 'rgba(16, 185, 129, 0.25)'}
          ],
          'threshold': {
            'line': {'color': "#065F46", 'width': 4},
            'thickness': 0.75,
            'value': 85
          }
        }
      ))
      fig_gauge.update_layout(
        height=260,
        margin=dict(l=20, r=20, t=15, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': chart_text_color}
      )
      st.plotly_chart(fig_gauge, use_container_width=True)
      st.markdown("</div>", unsafe_allow_html=True)

    with col_pie:
      pie_icon = feather_icon("pie-chart", color=COLOR_AMBER, size=18, margin_right=6)
      st.markdown(f"""
        <div class="saas-card">
          <div class="saas-card-title" style="display: flex; align-items: center;">{pie_icon} Emission Distribution by Operational Pillar</div>
          <div class="saas-card-subtitle">Proportion of annual emissions by functional stream</div>
      """, unsafe_allow_html=True)

      pie_labels = list(res["pillar_co2"].keys())
      pie_values = list(res["pillar_co2"].values())
      pillar_palette = ["#F59E0B", "#EF4444", "#F97316", "#8BA49A", "#06B6D4", "#6366F1"]

      fig_pie = go.Figure(data=[go.Pie(
        labels=pie_labels,
        values=pie_values,
        hole=0.55,
        marker=dict(colors=pillar_palette, line=dict(color='var(--bg-card)', width=2)),
        textinfo='percent',
        hovertemplate='<b>%{label}</b><br>Emissions: %{value:,.1f} t CO₂<br>Share: %{percent}<extra></extra>'
      )])
      fig_pie.update_layout(
        height=260,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, font=dict(size=10, color=chart_text_color)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
      )
      st.plotly_chart(fig_pie, use_container_width=True)
      st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # Row 2 Charts (Balanced 1:1.2, Equal Height 290px): Hotspots Bar & 12-Month Trajectory Stacked Bar
    col_bar, col_stacked = st.columns([1, 1.25], gap="medium")

    with col_bar:
      bar_icon = feather_icon("bar-chart-2", color=COLOR_WARNING, size=18, margin_right=6)
      st.markdown(f"""
        <div class="saas-card">
          <div class="saas-card-title" style="display: flex; align-items: center;">{bar_icon} Top Emission Hotspots (tonnes CO₂e)</div>
          <div class="saas-card-subtitle">Highest volume industrial sources ranked by volume</div>
      """, unsafe_allow_html=True)

      sorted_cats = sorted(res["pillar_co2"].items(), key=lambda x: x[1], reverse=True)
      cat_names = [k for k, v in sorted_cats]
      cat_vals = [v for k, v in sorted_cats]

      fig_bar = go.Figure(data=[go.Bar(
        x=cat_vals,
        y=cat_names,
        orientation='h',
        marker=dict(
          color=cat_vals,
          colorscale=[[0, '#8BA49A'], [0.5, '#F59E0B'], [1.0, '#DC2626']],
          line=dict(width=0)
        ),
        text=[f"{v:,.1f} t" for v in cat_vals],
        textposition='auto',
        hovertemplate='<b>%{y}</b>: %{x:,.1f} tonnes CO₂e<extra></extra>'
      )])
      fig_bar.update_layout(
        height=280,
        margin=dict(l=10, r=20, t=10, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.15)', tickfont=dict(size=11, color=chart_text_color)),
        yaxis=dict(autorange="reversed", tickfont=dict(size=11, color=chart_text_color))
      )
      st.plotly_chart(fig_bar, use_container_width=True)
      st.markdown("</div>", unsafe_allow_html=True)

    with col_stacked:
      stack_icon = feather_icon("columns", color=COLOR_NEUTRAL, size=18, margin_right=6)
      st.markdown(f"""
        <div class="saas-card">
          <div class="saas-card-title" style="display: flex; align-items: center;">{stack_icon} 12-Month Operational Emission Trajectory</div>
          <div class="saas-card-subtitle">Monthly profile across pillars with annual quota run-rate benchmark</div>
      """, unsafe_allow_html=True)

      fig_stacked = go.Figure()
      pillars = [c for c in monthly_df.columns if c not in ["Month", "Month_Num", "Total_Monthly_CO2"]]
      palette = ["#F59E0B", "#EF4444", "#F97316", "#8BA49A", "#06B6D4", "#6366F1"]

      for idx, pillar in enumerate(pillars):
        fig_stacked.add_trace(go.Bar(
          name=pillar,
          x=monthly_df["Month"],
          y=monthly_df[pillar],
          marker_color=palette[idx % len(palette)],
          hovertemplate=f'<b>{pillar}</b>: %{{y:,.1f}} t<extra></extra>'
        ))

      # Add monthly quota target line
      monthly_quota = res['govt_credits'] / 12.0
      fig_stacked.add_trace(go.Scatter(
        name=f"Monthly Quota Target ({monthly_quota:,.1f} t)",
        x=monthly_df["Month"],
        y=[monthly_quota] * len(monthly_df),
        mode='lines',
        line=dict(color='#8BA49A', dash='dash', width=2),
        hovertemplate="Monthly Quota: %{y:,.1f} t<extra></extra>"
      ))

      fig_stacked.update_layout(
        barmode='stack',
        height=280,
        margin=dict(l=10, r=10, t=10, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color=chart_text_color)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(tickfont=dict(size=10, color=chart_text_color)),
        yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.15)', tickfont=dict(size=10, color=chart_text_color))
      )
      st.plotly_chart(fig_stacked, use_container_width=True)
      st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # TARGETED GREEN RECOMMENDATIONS BASED ON EMISSION LEAK HOTSPOTS
    # =========================================================================
    hotspot_recs = generate_hotspot_recommendations(res, user)
    top_3_hotspot_recs = hotspot_recs[:3]

    recom_head_icon = feather_icon("lightbulb", color=COLOR_AMBER, size=20, margin_right=8)
    st.markdown(f"""
      <div class="saas-card" style="margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
          <div>
            <div class="saas-card-title" style="display: flex; align-items: center; font-size: 1.15rem;">
              {recom_head_icon} Green Recommendations Targeted to Operational Leak Hotspots
            </div>
            <div class="saas-card-subtitle" style="margin-top: 4px;">
              Actionable decarbonization & circular solutions dynamically prioritized based on your facility's top emission leak points:
            </div>
          </div>
          <span class="badge-low" style="font-size: 0.82rem; padding: 5px 12px;">
            🎯 DYNAMIC HOTSPOT MATCHING ACTIVE
          </span>
        </div>
    """, unsafe_allow_html=True)

    if not top_3_hotspot_recs:
      st.info("Complete assessment or log operational shift activity to generate hotspot-targeted recommendations.")
    else:
      r_cols = st.columns(len(top_3_hotspot_recs), gap="medium")
      for r_idx, r in enumerate(top_3_hotspot_recs):
        with r_cols[r_idx]:
          r_card_icon = feather_icon(r.get("feather_icon", "zap"), color="#8BA49A", size=16, margin_right=6)
          diff_badge = "badge-low" if r["difficulty"] == "Easy" else ("badge-medium" if r["difficulty"] == "Medium" else "badge-critical")
          st.markdown(f"""
            <div style="background: var(--bg-subtle); border: 1px solid var(--border-color); border-radius: 12px; padding: 16px; height: 100%; display: flex; flex-direction: column; justify-content: space-between; border-top: 4px solid {'#8BA49A' if r['targeted_hotspot_rank'] == 1 else ('#F59E0B' if r['targeted_hotspot_rank'] == 2 else '#3B82F6')};">
              <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                  <span style="font-size: 0.75rem; font-weight: 800; background: rgba(16,185,129,0.15); color: #047857; padding: 2px 8px; border-radius: 6px;">
                    {r['hotspot_priority_tag']}
                  </span>
                  <span class="{diff_badge}" style="font-size: 0.72rem; padding: 2px 6px;">
                    {r['difficulty']}
                  </span>
                </div>
                <div style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 4px;">
                  Targeting Hotspot #{r['targeted_hotspot_rank']}: <strong>{r['targeted_hotspot_source']}</strong> ({r['targeted_hotspot_co2']:,.1f} t)
                </div>
                <div style="font-size: 0.98rem; font-weight: 700; color: var(--text-primary); margin-bottom: 8px; line-height: 1.35;">
                  {r['title']}
                </div>
                <div style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.4; margin-bottom: 12px;">
                  {r['description'][:130]}...
                </div>
              </div>
              <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px; font-size: 0.82rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                  <span style="color: var(--text-muted);">CO₂ Reduction:</span>
                  <strong style="color: #8BA49A;">-{r['co2_saved_t']:,.1f} t/yr ({r['co2_saved_pct']}%)</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                  <span style="color: var(--text-muted);">Annual Savings:</span>
                  <strong style="color: #6B8E7D;">+₹{r['annual_savings_inr']:,.0f}/yr</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                  <span style="color: var(--text-muted);">CapEx Est:</span>
                  <strong>{r['cost_estimate']}</strong>
                </div>
                <div style="display: flex; justify-content: space-between;">
                  <span style="color: var(--text-muted);">Payback:</span>
                  <strong style="color: #2563EB;">{r['payback_time']} (ROI {r['expected_roi']}%)</strong>
                </div>
              </div>
            </div>
          """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    c_rm1, c_rm2 = st.columns([2.5, 1])
    with c_rm1:
      st.markdown(f"""
        <span style="font-size: 0.84rem; color: var(--text-muted);">
          Each recommendation is calibrated to your measured emission volume and regulatory compliance quotas (₹3,154/t).
        </span>
      """, unsafe_allow_html=True)
    with c_rm2:
      if st.button("Explore All Hotspot Recommendations →", key="dash_view_all_recs_btn", type="primary", use_container_width=True):
        st.session_state["current_step"] = 8
        st.session_state["nav_section"] = "recommendations"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

  # Call-to-actions to Deep-Dive Analytics & Leak Points
  st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)
  c_act1, c_act2, c_act3, c_act4 = st.columns(4)
  with c_act1:
    if st.button("Carbon Copilot Assistant →", use_container_width=True):
      st.session_state["nav_section"] = "copilot"
      st.rerun()
  with c_act2:
    if st.button("Inspect 10 Leak Points →", type="primary", use_container_width=True):
      st.session_state["current_step"] = 6
      st.session_state["nav_section"] = "leak_detection"
      st.rerun()
  with c_act3:
    if st.button("🌍 Reconcile Carbon Credits →", use_container_width=True):
      st.session_state["current_step"] = 7
      st.session_state["nav_section"] = "carbon_credits"
      st.rerun()
  with c_act4:
    if st.button("Daily & Weekly Activity Logs →", use_container_width=True):
      st.session_state["nav_section"] = "activity_logs"
      st.rerun()

  # =========================================================================
  # TAB 2: DAILY & WEEKLY PERIODIC OPERATIONAL ACTIVITY TRACKING
  # =========================================================================
  with tab_periodic:
    # Action Banner for Just-Logged Quick Entry
    dash_just_logged = st.session_state.get("dash_just_logged")
    if dash_just_logged:
      next_q_date = dash_just_logged.get("next_date", date.today() + timedelta(days=1))
      st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid #6EE7B7; border-radius: 8px; padding: 10px 14px; margin-bottom: 14px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
          <div style="display: flex; align-items: center;">
            {feather_icon('check-circle', color='#6B8E7D', size=18, margin_right=8)}
            <span style="font-size: 0.88rem; font-weight: 700; color: #065F46;">
              Quick Entry #{dash_just_logged['id']} saved for {dash_just_logged['date']}. Executive Dashboard updated!
            </span>
          </div>
        </div>
      """, unsafe_allow_html=True)
      cq_a1, cq_a2 = st.columns([1.3, 1.3])
      with cq_a1:
        if st.button(f"Log Next Day ({next_q_date.strftime('%b %d')})", key="dash_log_next_day_btn", type="primary", use_container_width=True):
          st.session_state["dash_quick_next_date"] = next_q_date
          st.session_state["dash_just_logged"] = None
          st.rerun()
      with cq_a2:
        if st.button(f"Delete Entry #{dash_just_logged['id']}", key="dash_del_just_logged_btn", type="secondary", use_container_width=True):
          del_id = dash_just_logged["id"]
          delete_activity_log(del_id, user_email)
          sync_activity_logs_to_dashboard(user_email, is_demo=is_demo)
          st.session_state["dash_just_logged"] = None
          st.success(f"Entry #{del_id} deleted! Dashboard updated.")
          st.rerun()
      st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    # Inline Quick-Logger Card
    with st.expander("⚡ Quick Log Operational Activity (Fuel, Waste, Utilities)", expanded=False):
      with st.form("dash_quick_log_form"):
        cq1, cq2, cq3 = st.columns(3)
        default_q_date = st.session_state.get("dash_quick_next_date", date.today())
        with cq1:
          ql_freq = st.selectbox("Frequency", ["Daily", "Weekly"], key="ql_freq")
          ql_date = st.date_input("Activity Date", value=default_q_date, key="ql_date")
        with cq2:
          ql_diesel = st.number_input("⛽ Diesel Fuel (Liters)", min_value=0.0, value=0.0, step=10.0, key="ql_diesel")
          ql_gas = st.number_input("Natural Gas (m³)", min_value=0.0, value=0.0, step=25.0, key="ql_gas")
        with cq3:
          ql_waste = st.number_input("Solid Waste (kg)", min_value=0.0, value=0.0, step=20.0, key="ql_waste")
          ql_elec = st.number_input("⚡ Electricity (kWh)", min_value=0.0, value=0.0, step=100.0, key="ql_elec")
        
        ql_notes = st.text_input("Operational Shift / Batch Note", placeholder="e.g. Shift 1 production run, boiler blowout, holiday packaging surge", key="ql_notes")
        ql_sub = st.form_submit_button("💾 Record Entry to Ledger & Recalculate", type="primary", use_container_width=True)
        if ql_sub:
          if ql_diesel + ql_gas + ql_waste + ql_elec <= 0:
            st.error("Please enter at least one positive operational quantity.")
          else:
            rec_id = save_activity_log(user_email, {
              "log_date": ql_date.isoformat(),
              "frequency": ql_freq.lower(),
              "period_label": ql_date.strftime("%Y-%m-%d") if ql_freq == "Daily" else f"Week {ql_date.strftime('%U, %Y')}",
              "diesel_liters": ql_diesel,
              "gas_m3": ql_gas,
              "organic_waste_kg": round(ql_waste * 0.45, 1),
              "plastic_waste_kg": round(ql_waste * 0.35, 1),
              "paper_waste_kg": round(ql_waste * 0.20, 1),
              "electricity_kwh": ql_elec,
              "notes": ql_notes
            }, is_demo=is_demo)

            next_d = ql_date + timedelta(days=1)
            st.session_state["dash_quick_next_date"] = next_d
            st.session_state["dash_just_logged"] = {
              "id": rec_id,
              "date": ql_date.strftime("%Y-%m-%d"),
              "next_date": next_d
            }
            sync_activity_logs_to_dashboard(user_email, is_demo=is_demo)
            st.success("✅ Activity logged successfully! Executive Dashboard updated.")
            st.rerun()

    # Fetch periodic logs from SQLite
    p_logs = get_activity_logs(user_email, limit=200)
    p_agg = get_aggregated_activity_summary(user_email)

    if not p_logs or p_agg["total_entries"] == 0:
      st.markdown(f"""
        <div class="saas-card" style="text-align: center; padding: 36px 20px;">
          <div style="margin-bottom: 12px;">{feather_icon('calendar', color=COLOR_NEUTRAL, size=36)}</div>
          <div style="font-weight: 700; font-size: 1.15rem; color: var(--text-primary);">No Periodic Activity Logs Recorded Yet</div>
          <div style="font-size: 0.88rem; color: var(--text-muted); max-width: 500px; margin: 6px auto 20px auto;">
            Start logging daily or weekly fuel consumption, waste collections, and energy meter readings to visualize real-time emission trends.
          </div>
        </div>
      """, unsafe_allow_html=True)
      c_emp1, c_emp2 = st.columns(2)
      with c_emp1:
        if st.button("Open Full Activity Logger View", type="primary", use_container_width=True):
          st.session_state["nav_section"] = "activity_logs"
          st.rerun()
      with c_emp2:
        if st.button("Load Sample Demonstration Activity Logs", use_container_width=True):
          seed_demo_activity_logs()
          st.success("Sample operational logs populated!")
          st.rerun()
    else:
      # 4 Balanced Equal-Sized Periodic KPI Cards for Carbon Credit Intelligence
      pk1, pk2, pk3, pk4 = st.columns(4)
      with pk1:
        st.markdown(f"""
          <div class="kpi-card info">
            <div class="kpi-title">
              {feather_icon("shield", color=COLOR_INFO, size=15, margin_right=5)} Initial Govt Quota
            </div>
            <div class="kpi-value">{audit_data['initial_govt_quota']:,.0f}</div>
            <div class="kpi-subtext">credits issued • {audit_data['regulatory_regime']}</div>
          </div>
        """, unsafe_allow_html=True)

      with pk2:
        st.markdown(f"""
          <div class="kpi-card">
            <div class="kpi-title">
              {feather_icon("sun", color=COLOR_SUCCESS, size=15, margin_right=5)} Daily Credit Burn
            </div>
            <div class="kpi-value">{audit_data['actual_daily_avg']:.3f}</div>
            <div class="kpi-subtext">credits/day • Cap: {audit_data['daily_quota_target']:.3f} ({audit_data['daily_pct_of_allowance']:.1f}%)</div>
          </div>
        """, unsafe_allow_html=True)

      with pk3:
        st.markdown(f"""
          <div class="kpi-card warning">
            <div class="kpi-title">
              {feather_icon("calendar", color=COLOR_WARNING, size=15, margin_right=5)} Weekly Credit Burn
            </div>
            <div class="kpi-value">{audit_data['actual_weekly_avg']:.2f}</div>
            <div class="kpi-subtext">credits/week • Cap: {audit_data['weekly_quota_target']:.2f} ({audit_data['weekly_pct_of_allowance']:.1f}%)</div>
          </div>
        """, unsafe_allow_html=True)

      with pk4:
        p_exp_color = "#EF4444" if audit_data['is_projected_deficit'] else "#8BA49A"
        st.markdown(f"""
          <div class="kpi-card {'deficit' if audit_data['is_projected_deficit'] else 'low'}">
            <div class="kpi-title">
              {feather_icon("trending-up", color=p_exp_color, size=15, margin_right=5)} Expected Annual Burn
            </div>
            <div class="kpi-value" style="color: {p_exp_color};">{audit_data['expected_annual_burn']:,.1f}</div>
            <div class="kpi-subtext">forecast • Quota Runway: ~{audit_data['quota_runway_days']} days</div>
          </div>
        """, unsafe_allow_html=True)

      st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

      # Convert logs to chronologically ordered DataFrame
      df_periodic = pd.DataFrame(p_logs)
      df_periodic = df_periodic.sort_values(by="log_date", ascending=True)

      # Visualization 1: Time Series Stacked Bar Chart (Emission Trend by Product)
      st.markdown(f"""
        <div class="saas-card">
          <div class="saas-card-title" style="display: flex; align-items: center;">
            {feather_icon('bar-chart-2', color=COLOR_SUCCESS, size=18, margin_right=6)} Periodic Emission Trajectory by Product (Fuel, Waste, Energy)
          </div>
          <div class="saas-card-subtitle">
            Daily & weekly operational emission contributions cross-referenced against statutory quota run-rate:
          </div>
      """, unsafe_allow_html=True)

      daily_quota_runrate = round(res['govt_credits'] / 365.0, 2)

      fig_p_trend = go.Figure()
      fig_p_trend.add_trace(go.Bar(
        name="Fuel & Thermal CO₂",
        x=df_periodic["log_date"],
        y=df_periodic["calculated_fuel_co2"],
        marker_color="#F59E0B",
        hovertemplate="<b>%{x}</b><br>Fuel: %{y:,.3f} t CO₂<extra></extra>"
      ))
      fig_p_trend.add_trace(go.Bar(
        name="Waste Streams CO₂",
        x=df_periodic["log_date"],
        y=df_periodic["calculated_waste_co2"],
        marker_color="#EF4444",
        hovertemplate="<b>%{x}</b><br>Waste: %{y:,.3f} t CO₂<extra></extra>"
      ))
      fig_p_trend.add_trace(go.Bar(
        name="Electricity CO₂",
        x=df_periodic["log_date"],
        y=df_periodic["calculated_electricity_co2"],
        marker_color="#3B82F6",
        hovertemplate="<b>%{x}</b><br>Electricity: %{y:,.3f} t CO₂<extra></extra>"
      ))
      fig_p_trend.add_trace(go.Bar(
        name="Transport Freight CO₂",
        x=df_periodic["log_date"],
        y=df_periodic["calculated_transport_co2"],
        marker_color="#8BA49A",
        hovertemplate="<b>%{x}</b><br>Transport: %{y:,.3f} t CO₂<extra></extra>"
      ))

      # Benchmark line for daily quota runrate
      fig_p_trend.add_trace(go.Scatter(
        name=f"Daily Quota Limit ({daily_quota_runrate:.2f} t/day)",
        x=df_periodic["log_date"],
        y=[daily_quota_runrate] * len(df_periodic),
        mode="lines",
        line=dict(color="#8BA49A", dash="dash", width=2),
        hovertemplate="Statutory Allowance Run-Rate: %{y:,.2f} t/day<extra></extra>"
      ))

      fig_p_trend.update_layout(
        barmode="stack",
        height=320,
        margin=dict(l=10, r=10, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11, color=chart_text_color)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(size=11, color=chart_text_color)),
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)", tickfont=dict(size=11, color=chart_text_color), title="tonnes CO₂e")
      )
      st.plotly_chart(fig_p_trend, use_container_width=True)
      st.markdown("</div>", unsafe_allow_html=True)

      st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

      # Visualization Row 2: Fuel Consumption Breakdown & Waste Stream Breakdown
      col_fuel, col_waste = st.columns([1.1, 1.1], gap="large")

      with col_fuel:
        f_icon = feather_icon("droplet", color=COLOR_WARNING, size=18, margin_right=6)
        st.markdown(f"""
          <div class="saas-card">
            <div class="saas-card-title" style="display: flex; align-items: center;">
              {f_icon} Fuel Consumption Breakdown (Diesel & Gas)
            </div>
            <div class="saas-card-subtitle">Daily volumes of liquid diesel and pipeline gas:</div>
        """, unsafe_allow_html=True)

        fig_fuel = go.Figure()
        fig_fuel.add_trace(go.Scatter(
          name="Diesel (Liters)",
          x=df_periodic["log_date"],
          y=df_periodic["diesel_liters"],
          mode="lines+markers",
          line=dict(color="#D97706", width=2.5),
          marker=dict(size=6),
          hovertemplate="Diesel: %{y:,.1f} L<extra></extra>"
        ))
        fig_fuel.add_trace(go.Scatter(
          name="Natural Gas (m³)",
          x=df_periodic["log_date"],
          y=df_periodic["gas_m3"],
          mode="lines+markers",
          line=dict(color="#F59E0B", width=2.5, dash="dot"),
          marker=dict(size=6),
          hovertemplate="Natural Gas: %{y:,.1f} m³<extra></extra>"
        ))
        fig_fuel.update_layout(
          height=280,
          margin=dict(l=10, r=10, t=10, b=20),
          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color=chart_text_color)),
          paper_bgcolor="rgba(0,0,0,0)",
          plot_bgcolor="rgba(0,0,0,0)",
          xaxis=dict(tickfont=dict(size=10, color=chart_text_color)),
          yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)", tickfont=dict(size=10, color=chart_text_color))
        )
        st.plotly_chart(fig_fuel, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

      with col_waste:
        w_icon = feather_icon("trash-2", color="#EF4444", size=18, margin_right=6)
        st.markdown(f"""
          <div class="saas-card">
            <div class="saas-card-title" style="display: flex; align-items: center;">
              {w_icon} Waste Stream Composition (Total kg)
            </div>
            <div class="saas-card-subtitle">Aggregate distribution of solid waste streams:</div>
        """, unsafe_allow_html=True)

        waste_streams = {
          "Organic": sum(df_periodic["organic_waste_kg"]),
          "Plastic": sum(df_periodic["plastic_waste_kg"]),
          "Metal": sum(df_periodic["metal_waste_kg"]),
          "Paper": sum(df_periodic["paper_waste_kg"]),
          "Hazardous": sum(df_periodic["hazardous_waste_kg"])
        }
        # Filter non-zero streams
        w_labels = [k for k, v in waste_streams.items() if v > 0]
        w_values = [v for k, v in waste_streams.items() if v > 0]

        if w_values:
          fig_w_donut = go.Figure(data=[go.Pie(
            labels=w_labels,
            values=w_values,
            hole=0.6,
            marker=dict(colors=["#8BA49A", "#EF4444", "#6B7280", "#F59E0B", "#991B1B"]),
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b>: %{value:,.1f} kg (%{percent})<extra></extra>"
          )])
          fig_w_donut.update_layout(
            height=280,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            annotations=[dict(
              text=f"<b>{sum(w_values):,.0f} kg</b><br>Total Waste",
              x=0.5, y=0.5, font_size=12, showarrow=False, font_color=chart_text_color
            )]
          )
          st.plotly_chart(fig_w_donut, use_container_width=True)
        else:
          st.info("No solid waste quantities recorded in current filter.")
        st.markdown("</div>", unsafe_allow_html=True)

      st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

      # Visualization Row 3: Cumulative Periodic Footprint & Recent Ledger
      col_cum, col_table = st.columns([1.1, 1.1], gap="large")

      with col_cum:
        st.markdown(f"""
          <div class="saas-card">
            <div class="saas-card-title">{feather_icon('trending-up', color=COLOR_INFO, size=18, margin_right=6)} Cumulative Carbon Credit Consumption vs Initial Quota</div>
            <div class="saas-card-subtitle">Accrued credit usage tracking toward initial government allowance ceiling:</div>
        """, unsafe_allow_html=True)

        cum_vals = df_periodic["calculated_total_co2"].cumsum()
        fig_cum = go.Figure()
        fig_cum.add_trace(go.Scatter(
          x=df_periodic["log_date"],
          y=cum_vals,
          fill="tozeroy",
          name="Accrued Credits Used",
          line=dict(color="#3B82F6", width=2.5),
          fillcolor="rgba(59, 130, 246, 0.2)",
          hovertemplate="Accrued: %{y:,.2f} credits<extra></extra>"
        ))
        # Initial Govt Quota ceiling line
        fig_cum.add_trace(go.Scatter(
          x=df_periodic["log_date"],
          y=[audit_data['initial_govt_quota']] * len(df_periodic),
          mode="lines",
          name=f"Govt Quota Ceiling ({audit_data['initial_govt_quota']:,.0f} credits)",
          line=dict(color="#8BA49A", dash="dash", width=2),
          hovertemplate="Initial Statutory Quota: %{y:,.0f} credits<extra></extra>"
        ))
        fig_cum.update_layout(
          height=260,
          margin=dict(l=10, r=10, t=10, b=20),
          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color=chart_text_color)),
          paper_bgcolor="rgba(0,0,0,0)",
          plot_bgcolor="rgba(0,0,0,0)",
          xaxis=dict(tickfont=dict(size=10, color=chart_text_color)),
          yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)", tickfont=dict(size=10, color=chart_text_color), title="credits (t CO₂e)")
        )
        st.plotly_chart(fig_cum, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

      with col_table:
        st.markdown(f"""
          <div class="saas-card">
            <div class="saas-card-title">{feather_icon('clock', color=COLOR_NEUTRAL, size=18, margin_right=6)} Operational Carbon Credit Ledger</div>
            <div class="saas-card-subtitle">Recent shift credit consumption vs statutory quota limits:</div>
        """, unsafe_allow_html=True)

        for l in p_logs[:6]:
          c_td, c_ts, c_tbtn = st.columns([1.8, 2.6, 0.6])
          with c_td:
            freq_badge = "Daily" if l.get("frequency") == "daily" else "Weekly"
            st.markdown(f"**{l['log_date']}** <span style='font-size: 0.78rem; background: rgba(59,130,246,0.1); color: #2563EB; padding: 2px 6px; border-radius: 4px;'>{freq_badge}</span>", unsafe_allow_html=True)
          with c_ts:
            c_val = l.get('calculated_total_co2', 0.0)
            cap_target = audit_data['daily_quota_target'] if l.get("frequency") == "daily" else audit_data['weekly_quota_target']
            pct_cap = (c_val / cap_target * 100) if cap_target > 0 else 0.0
            cap_color = "#8BA49A" if pct_cap <= 100 else "#EF4444"
            st.markdown(f"<strong style='color: #8BA49A;'>{c_val:.2f} credits</strong> &bull; <span style='font-size: 0.78rem; color: {cap_color};'>{pct_cap:.0f}% of cap</span>", unsafe_allow_html=True)
          with c_tbtn:
            if st.button("", key=f"dash_del_tbl_{l['id']}", help="Delete this entry and recalculate dashboard"):
              delete_activity_log(l["id"], user_email)
              sync_activity_logs_to_dashboard(user_email, is_demo=is_demo)
              st.success(f"Entry #{l['id']} deleted! Dashboard updated.")
              st.rerun()

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        if st.button("Open Full Activity Logger & CSV Manager →", use_container_width=True, key="dash_open_full_logger_btn"):
          st.session_state["nav_section"] = "activity_logs"
          st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


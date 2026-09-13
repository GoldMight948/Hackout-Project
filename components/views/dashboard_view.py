"""
Step 5: Executive Dashboard View.
Delivers a modern desktop-first SaaS analytics interface inspired by enterprise executive dashboards.
Sections:
1. Top Header (Search, Date Period, Live Sync Status, Ask Copilot, User Capsule)
2. Dashboard Header ({comp_name} Carbon Dashboard, Subtitle, Compliance Badge, Download Report)
3. Executive KPI Summary (Single 5-Card Row: Total Emissions, Govt Quota, Credits Used, Net Status, Eco Score)
4. Primary Analytics (2-Column Grid: Top Hotspots Bar Chart + 12-Month Trajectory Stacked Bar Chart)
5. Statutory Compliance & Performance (65% / 35%: Quota & Compliance Matrix Table + Speedometer Gauge)
6. Secondary Intelligence (3-Column Grid: Pillar Donut + Top 3 Green Fixes + Recent Shift Activity)
7. Bottom Quick Actions (4 Navigation Shortcuts)
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import date, datetime, timedelta
from components.calculations import (
  calculate_detailed_emissions, calculate_carbon_credit_audit,
  get_statutory_carbon_quota, generate_hotspot_recommendations,
  safe_float
)
from components.ml_forecast import generate_monthly_timeseries
from components.auth import is_demo_session, reset_current_demo_profile
from database.db_manager import (
  get_activity_logs, get_aggregated_activity_summary,
  sync_activity_logs_to_dashboard, get_latest_emissions
)

from components.icons import (
  feather_icon, COLOR_WARNING, COLOR_SUCCESS, COLOR_NEUTRAL,
  COLOR_SECONDARY, COLOR_INFO, COLOR_AMBER
)
import io
from components.csv_importer import (
  import_past_data_from_csv, generate_sample_past_data_csv,
  generate_blank_activity_csv_template
)

def render_dashboard_view():
  """Renders the clean, structured, desktop-first executive carbon dashboard."""
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
  user_name = user.get("owner_name", user.get("name", "David Kovac"))
  user_role = user.get("role", "Admin")
  avatar_initials = "".join([p[0] for p in user_name.split()[:2]]).upper() if user_name else "DK"
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
  elif total_logs_count == 0 and res_co2 == 0.0:
    db_emissions = get_latest_emissions(user_email)
    if db_emissions and (db_emissions.get("total_co2", 0.0) > 0.0 or any(safe_float(db_emissions.get(k, 0)) > 0 for k in ["electricity_kwh", "diesel_liters", "gas_m3", "truck_km"])):
      res_calc = calculate_detailed_emissions(db_emissions)
      st.session_state["emissions_results"] = res_calc
      st.session_state["form_inputs"] = db_emissions
      st.session_state["dash_synced_email"] = user_email


  res = st.session_state["emissions_results"]
  user_logs = get_activity_logs(user_email, limit=500)
  audit_data = calculate_carbon_credit_audit(user, user_logs, res)
  comp_name = res.get("raw_inputs", {}).get("business_name") or st.session_state.get("form_inputs", {}).get("business_name") or user.get("company_name", "Enterprise Facility")
  chart_text_color = "#1E293B"

  # =========================================================================
  # 1. TOP UTILITY BAR: Context Anchor + Date, Status, Copilot Controls
  # =========================================================================
  cal_icon = feather_icon("calendar", color="#64748B", size=14, margin_right=4)
  col_anchor, col_date = st.columns([5.5, 2.0], gap="small")

  with col_anchor:
    st.markdown(f"""
      <div id="dash-top-bar-marker" style="display:none;"></div>
      <div style="display: flex; align-items: center; gap: 8px; height: 38px; min-width: 0; overflow: hidden; white-space: nowrap;">
        <span style="font-size: 0.76rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.08em; flex-shrink: 0; white-space: nowrap;">Enterprise Audit</span>
        <span style="color: var(--border-color); font-weight: 300; flex-shrink: 0;">/</span>
        <span style="font-size: 0.85rem; font-weight: 800; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="{comp_name}">{comp_name}</span>
      </div>
    """, unsafe_allow_html=True)

  with col_date:
    raw_range = agg_stat.get("date_range", "")
    if raw_range and raw_range != "N/A" and " - " in raw_range:
      date_display = raw_range
    else:
      today_dt = date.today()
      start_dt = today_dt - timedelta(days=29)
      date_display = f"{start_dt.strftime('%b %d')} - {today_dt.strftime('%b %d, %Y')}"
    st.markdown(f'<div class="header-pill" style="height: 38px; width: 100%; justify-content: center;">{cal_icon} <span>{date_display}</span></div>', unsafe_allow_html=True)

  st.markdown("<hr style='margin: 12px 0 16px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)

  # Baseline Estimates Banner (Notice if optional inputs defaulted)
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
    info_icon = feather_icon("info", color=COLOR_INFO, size=16, margin_right=8)
    c_notif1, c_notif2 = st.columns([4.2, 1.0])
    with c_notif1:
      st.markdown(f"""
        <div style="background: rgba(59, 130, 246, 0.07); border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 8px; padding: 7px 12px; margin-bottom: 12px; display: flex; align-items: center;">
          {info_icon}
          <div style="font-size: 0.82rem; color: #1E40AF;">
            <strong>Notice — Baseline Estimates:</strong> Parameters using standard industry baselines: <span style="font-weight: 600;">{", ".join(human_readable)}</span>.
          </div>
        </div>
      """, unsafe_allow_html=True)
    with c_notif2:
      if st.button("Update Setup", key="dash_update_defaults_btn", use_container_width=True):
        st.session_state["nav_section"] = "setup"
        st.session_state["current_step"] = 3
        st.rerun()

  # =========================================================================
  # 2. DASHBOARD HEADER: Title + Subtitle + Actions
  # =========================================================================
  col_head_left, col_head_right = st.columns([3.2, 1.8], gap="medium")
  with col_head_left:
    st.markdown(f"""
      <div style="margin-bottom: 14px;">
        <h1 style="font-size: 1.85rem; font-weight: 800; color: var(--text-primary); margin: 0 0 2px 0; letter-spacing: -0.02em;">
          {comp_name} Carbon Dashboard
        </h1>
        <p style="font-size: 0.88rem; color: var(--text-muted); margin: 0;">
          Real-time overview of emissions, statutory quotas and sustainability performance
        </p>
      </div>
    """, unsafe_allow_html=True)

  with col_head_right:
    c_hdr_badge, c_hdr_btn = st.columns([1.3, 1.1], gap="small")
    with c_hdr_badge:
      if res["is_deficit"]:
        st.markdown(f"""
          <div style="display: flex; justify-content: flex-end; align-items: flex-start; padding-top: 6px;">
            <span style="background: rgba(239, 68, 68, 0.12); color: #DC2626; border: 1.5px solid #F87171; border-radius: 8px; padding: 7px 12px; font-weight: 800; font-size: 0.78rem; letter-spacing: 0.05em; display: inline-flex; align-items: center; gap: 6px; white-space: nowrap; box-shadow: 0 1px 3px rgba(239, 68, 68, 0.08);">
              <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: #DC2626;"></span>
              DEFICIT
            </span>
          </div>
        """, unsafe_allow_html=True)
      else:
        st.markdown(f"""
          <div style="display: flex; justify-content: flex-end; align-items: flex-start; padding-top: 6px;">
            <span style="background: rgba(16, 185, 129, 0.12); color: #047857; border: 1.5px solid #34D399; border-radius: 8px; padding: 7px 12px; font-weight: 800; font-size: 0.78rem; letter-spacing: 0.05em; display: inline-flex; align-items: center; gap: 6px; white-space: nowrap; box-shadow: 0 1px 3px rgba(16, 185, 129, 0.08);">
              <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: #10B981;"></span>
              SURPLUS
            </span>
          </div>
        """, unsafe_allow_html=True)
    with c_hdr_btn:
      import_active = st.session_state.get("show_dash_csv_import", False)
      btn_label = "✖ Close" if import_active else "📥 Import CSV"
      if st.button(btn_label, key="dash_toggle_import_csv", use_container_width=True):
        st.session_state["show_dash_csv_import"] = not import_active
        st.rerun()

  # =========================================================================
  # 2.5 NEW USER ONBOARDING & CSV PAST DATA INGESTION MODULE
  # =========================================================================
  is_new_user = (not is_demo) and (total_logs_count == 0 and res.get("total_co2", 0.0) <= 0.0)
  show_csv_module = is_new_user or st.session_state.get("show_dash_csv_import", False)

  if show_csv_module:
    card_border = "#10B981" if is_new_user else "var(--border-color)"
    card_bg = "linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%)" if is_new_user else "var(--bg-card)"
    card_tag = "NEW WORKSPACE • READY FOR DATA" if is_new_user else "HISTORICAL DATA BATCH INGESTION"
    card_tag_class = "badge-low" if is_new_user else "badge-medium"
    card_heading = "Import Past Data from CSV to Power Your Dashboard Analysis" if is_new_user else "Import Additional Past Data from CSV"
    card_sub = (
      "Welcome to your production facility workspace! To unlock personalized leak diagnostics, "
      "statutory PAT compliance audits, and full 12-month projections, import your past operational logs or utility bills below."
      if is_new_user else
      "Upload additional historical utility spreadsheets or operational logs to update your SQLite records and live emissions analysis."
    )
    cloud_icon = feather_icon('upload-cloud', color='#059669', size=20, margin_right=8)

    st.markdown(f"""
      <div class="saas-card" style="border: 1.5px solid {card_border}; background: {card_bg}; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
          <div>
            <span class="{card_tag_class}" style="font-size: 0.75rem; letter-spacing: 0.08em;">{card_tag}</span>
            <h2 style="font-size: 1.35rem; font-weight: 800; margin: 6px 0 2px 0; color: var(--text-primary); display: flex; align-items: center;">
              {cloud_icon} {card_heading}
            </h2>
            <p style="font-size: 0.88rem; color: var(--text-muted); margin: 0; max-width: 780px;">
              {card_sub}
            </p>
          </div>
        </div>
    """, unsafe_allow_html=True)

    col_csv1, col_csv2 = st.columns([1.25, 0.95], gap="large")
    with col_csv1:
      dash_uploaded_csv = st.file_uploader(
        "Upload Past Utility or Operational Spreadsheet",
        type=["csv", "xlsx", "xls"],
        key="dash_past_data_csv_uploader",
        help="Upload CSV or Excel file containing past operational records (dates, electricity, fuels, freight, waste)."
      )
      if dash_uploaded_csv is not None:
        last_dash_file = st.session_state.get("dash_last_processed_file")
        trigger_ingest = False
        if last_dash_file != dash_uploaded_csv.name:
          trigger_ingest = True
        elif st.button("🚀 Ingest CSV & Update Dashboard Analysis", type="primary", use_container_width=True, key="dash_btn_process_csv"):
          trigger_ingest = True

        if trigger_ingest:
          with st.spinner("Processing spreadsheet and computing emissions analytics..."):
            import_res = import_past_data_from_csv(dash_uploaded_csv, user_email, is_demo=is_demo)
            st.session_state["dash_last_processed_file"] = dash_uploaded_csv.name
            if import_res.get("success"):
              st.session_state["show_dash_csv_import"] = False
              st.success(import_res.get("message", "Import successful!"))
              st.rerun()
            else:
              st.error(import_res.get("error", "Error parsing file."))


    with col_csv2:
      st.markdown(f"""
        <div style="font-size: 0.82rem; font-weight: 700; color: var(--text-primary); margin-bottom: 8px;">
          {feather_icon('zap', color=COLOR_WARNING, size=15, margin_right=5)} Fast Ingestion Options:
        </div>
      """, unsafe_allow_html=True)

      user_ind = user.get("industry", "Manufacturing Plant")
      if st.button("⚡ Pre-populate with Sample 1-Year Past Activity (CSV)", use_container_width=True, key="dash_btn_sample_csv"):
        with st.spinner("Loading 12 months of historical operational activity..."):
          sample_csv_text = generate_sample_past_data_csv(user_ind)
          import_res = import_past_data_from_csv(io.StringIO(sample_csv_text), user_email, is_demo=is_demo)
          if import_res.get("success"):
            st.session_state["show_dash_csv_import"] = False
            st.success("✅ Imported 12 months of historical operational activity! Synchronizing dashboard...")
            st.rerun()
          else:
            st.error("Failed to generate sample data.")

      st.download_button(
        label="📄 Download Blank CSV Template",
        data=generate_blank_activity_csv_template(),
        file_name="operational_activity_template.csv",
        mime="text/csv",
        use_container_width=True,
        key="dash_download_activity_csv_tmpl"
      )

      c_opt1, c_opt2 = st.columns(2)
      with c_opt1:
        if st.button("⚙️ Setup Baseline", key="dash_new_user_go_setup", use_container_width=True):
          st.session_state["nav_section"] = "setup"
          st.session_state["current_step"] = 3
          st.rerun()
      with c_opt2:
        if st.button("📅 Shift Logger", key="dash_new_user_go_logs", use_container_width=True):
          st.session_state["nav_section"] = "activity_logs"
          st.session_state["current_step"] = 4
          st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

  # =========================================================================
  # 3. EXECUTIVE KPI SUMMARY: Single 5-Card Row (Real Data Only)
  # =========================================================================
  k1, k2, k3, k4, k5 = st.columns(5, gap="small")

  with k1:
    # 1. Total Emissions
    co2_sub = f"{agg_stat['total_co2']:,.1f} t accrued ({total_logs_count} logs)" if total_logs_count > 0 else "Annual baseline run-rate"
    st.markdown(f"""
      <div class="kpi-card-v2">
        <div>
          <div class="kpi-top-row">
            <span class="kpi-label">Total Emissions</span>
            <div class="kpi-icon-pill" style="background: rgba(16, 185, 129, 0.12);">
              {feather_icon("leaf", color="#059669", size=16, margin_right=0)}
            </div>
          </div>
          <div>
            <span class="kpi-main-number">{res['total_co2']:,.1f}</span>
            <span class="kpi-unit">t CO₂e/yr</span>
          </div>
        </div>
        <div class="kpi-bottom-row">
          <span style="color: var(--text-muted); font-size: 0.75rem;">{co2_sub}</span>
        </div>
      </div>
    """, unsafe_allow_html=True)

  with k2:
    # 2. Govt Quota
    quota_regime = audit_data.get("regulatory_regime", "BEE PAT Cap")
    st.markdown(f"""
      <div class="kpi-card-v2">
        <div>
          <div class="kpi-top-row">
            <span class="kpi-label">Govt Quota</span>
            <div class="kpi-icon-pill" style="background: rgba(59, 130, 246, 0.12);">
              {feather_icon("award", color="#2563EB", size=16, margin_right=0)}
            </div>
          </div>
          <div>
            <span class="kpi-main-number">{res['govt_credits']:,.0f}</span>
            <span class="kpi-unit">credits</span>
          </div>
        </div>
        <div class="kpi-bottom-row">
          <span style="color: #2563EB; font-weight: 600; font-size: 0.75rem;" title="Statutory allocation • {quota_regime}">Statutory PAT Allocation</span>
        </div>
      </div>
    """, unsafe_allow_html=True)

  with k3:
    # 3. Credits Used
    used_pct = (res['credits_used'] / max(res['govt_credits'], 1)) * 100
    st.markdown(f"""
      <div class="kpi-card-v2">
        <div>
          <div class="kpi-top-row">
            <span class="kpi-label">Credits Used</span>
            <div class="kpi-icon-pill" style="background: rgba(245, 158, 11, 0.12);">
              {feather_icon("activity", color="#D97706", size=16, margin_right=0)}
            </div>
          </div>
          <div>
            <span class="kpi-main-number">{res['credits_used']:,.1f}</span>
            <span class="kpi-unit">credits</span>
          </div>
        </div>
        <div class="kpi-bottom-row">
          <span style="color: #D97706; font-weight: 600; font-size: 0.75rem;">{used_pct:.0f}% of quota burned</span>
        </div>
      </div>
    """, unsafe_allow_html=True)

  with k4:
    # 4. Net Carbon Status
    net_val = res['credits_remaining'] if not res['is_deficit'] else res['credits_required']
    net_sub = "Surplus reserve balance" if not res['is_deficit'] else "Compliance deficit buy"
    net_col = "#059669" if not res['is_deficit'] else "#DC2626"
    net_bg = "rgba(16, 185, 129, 0.12)" if not res['is_deficit'] else "rgba(239, 68, 68, 0.12)"
    net_icon = "shield" if not res['is_deficit'] else "alert-triangle"
    st.markdown(f"""
      <div class="kpi-card-v2">
        <div>
          <div class="kpi-top-row">
            <span class="kpi-label">Net Carbon Status</span>
            <div class="kpi-icon-pill" style="background: {net_bg};">
              {feather_icon(net_icon, color=net_col, size=16, margin_right=0)}
            </div>
          </div>
          <div>
            <span class="kpi-main-number" style="color: {net_col};">{net_val:,.1f}</span>
            <span class="kpi-unit">tonnes</span>
          </div>
        </div>
        <div class="kpi-bottom-row">
          <span style="color: {net_col}; font-weight: 700; font-size: 0.75rem;">{net_sub}</span>
        </div>
      </div>
    """, unsafe_allow_html=True)

  with k5:
    # 5. Eco Score
    score_val = res['sustainability_score']
    score_color = "#059669" if score_val >= 70 else ("#D97706" if score_val >= 45 else "#DC2626")
    score_bg = "rgba(16, 185, 129, 0.12)" if score_val >= 70 else ("rgba(245, 158, 11, 0.12)" if score_val >= 45 else "rgba(239, 68, 68, 0.12)")
    score_badge = "Tier A (Leader)" if score_val >= 75 else ("Tier B (Standard)" if score_val >= 50 else "Tier C (Action Needed)")
    st.markdown(f"""
      <div class="kpi-card-v2">
        <div>
          <div class="kpi-top-row">
            <span class="kpi-label">Eco Score</span>
            <div class="kpi-icon-pill" style="background: {score_bg};">
              {feather_icon("target", color=score_color, size=16, margin_right=0)}
            </div>
          </div>
          <div>
            <span class="kpi-main-number" style="color: {score_color};">{score_val:.0f}</span>
            <span class="kpi-unit">/ 100</span>
          </div>
        </div>
        <div class="kpi-bottom-row">
          <span style="color: {score_color}; font-weight: 700; font-size: 0.75rem;">{score_badge}</span>
        </div>
      </div>
    """, unsafe_allow_html=True)

  st.markdown("<div style='margin-bottom: 18px;'></div>", unsafe_allow_html=True)

  # =========================================================================
  # 4. PRIMARY ANALYTICS: 2 Balanced Columns
  # =========================================================================
  col_bar, col_stacked = st.columns([1, 1.25], gap="medium")

  with col_bar:
    bar_icon = feather_icon("bar-chart-2", color="#D97706", size=18, margin_right=6)
    st.markdown(f"""
      <div class="saas-card" style="height: 100%;">
        <div class="saas-card-title" style="display: flex; align-items: center;">
          {bar_icon} Top Emission Hotspots (tonnes CO₂e)
        </div>
        <div class="saas-card-subtitle">Highest volume operational sources ranked by emissions:</div>
    """, unsafe_allow_html=True)

    if res["total_co2"] <= 0.0:
      st.markdown("""
        <div style="background: var(--bg-subtle); border: 1px dashed var(--border-color); border-radius: 10px; padding: 48px 20px; text-align: center; margin-top: 10px;">
          <div style="font-size: 2.2rem; margin-bottom: 8px;">🌱</div>
          <div style="font-weight: 700; font-size: 0.95rem; color: var(--text-primary); margin-bottom: 4px;">Zero Active Emission Hotspots</div>
          <div style="font-size: 0.82rem; color: var(--text-muted); max-width: 320px; margin: 0 auto;">
            Your facility emissions are at 0.0 t CO₂e. Import your past CSV data above or log daily operational shifts to rank emission sources.
          </div>
        </div>
      """, unsafe_allow_html=True)
    else:
      sorted_cats = sorted(res["pillar_co2"].items(), key=lambda x: x[1], reverse=True)
      cat_names = [k for k, v in sorted_cats]
      cat_vals = [v for k, v in sorted_cats]

      fig_bar = go.Figure(data=[go.Bar(
        x=cat_vals,
        y=cat_names,
        orientation='h',
        marker=dict(
          color=cat_vals,
          colorscale=[[0, '#10B981'], [0.5, '#F59E0B'], [1.0, '#DC2626']],
          line=dict(width=0)
        ),
        text=[f"{v:,.1f} t" for v in cat_vals],
        textposition='auto',
        hovertemplate='<b>%{y}</b>: %{x:,.1f} tonnes CO₂e<extra></extra>'
      )])
      fig_bar.update_layout(
        height=290,
        margin=dict(l=10, r=15, t=10, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.12)', tickfont=dict(size=11, color=chart_text_color)),
        yaxis=dict(autorange="reversed", tickfont=dict(size=11, color=chart_text_color))
      )
      st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

  with col_stacked:
    stack_icon = feather_icon("columns", color="#2563EB", size=18, margin_right=6)
    st.markdown(f"""
      <div class="saas-card" style="height: 100%;">
        <div class="saas-card-title" style="display: flex; align-items: center;">
          {stack_icon} 12-Month Operational Emission Trajectory
        </div>
        <div class="saas-card-subtitle">Monthly profile across pillars with annual quota benchmark line:</div>
    """, unsafe_allow_html=True)

    if res["total_co2"] <= 0.0:
      st.markdown("""
        <div style="background: var(--bg-subtle); border: 1px dashed var(--border-color); border-radius: 10px; padding: 48px 20px; text-align: center; margin-top: 10px;">
          <div style="font-size: 2.2rem; margin-bottom: 8px;">📈</div>
          <div style="font-weight: 700; font-size: 0.95rem; color: var(--text-primary); margin-bottom: 4px;">12-Month Trajectory Awaiting Data</div>
          <div style="font-size: 0.82rem; color: var(--text-muted); max-width: 340px; margin: 0 auto;">
            Monthly operational breakdown and statutory quota benchmarks will dynamically project once historical CSV logs or utility data are imported.
          </div>
        </div>
      """, unsafe_allow_html=True)
    else:
      monthly_df = generate_monthly_timeseries(res["pillar_co2"])
      pillars = [c for c in monthly_df.columns if c not in ["Month", "Month_Num", "Total_Monthly_CO2"]]
      palette = ["#10B981", "#F59E0B", "#EF4444", "#3B82F6", "#8B5CF6", "#06B6D4"]

      fig_stacked = go.Figure()
      for idx, pillar in enumerate(pillars):
        fig_stacked.add_trace(go.Bar(
          name=pillar,
          x=monthly_df["Month"],
          y=monthly_df[pillar],
          marker_color=palette[idx % len(palette)],
          hovertemplate=f'<b>{pillar}</b>: %{{y:,.1f}} t<extra></extra>'
        ))

      monthly_quota = res['govt_credits'] / 12.0
      fig_stacked.add_trace(go.Scatter(
        name=f"Monthly Quota Target ({monthly_quota:,.1f} t)",
        x=monthly_df["Month"],
        y=[monthly_quota] * len(monthly_df),
        mode='lines',
        line=dict(color='#059669', dash='dash', width=2),
        hovertemplate="Monthly Quota: %{y:,.1f} t<extra></extra>"
      ))

      fig_stacked.update_layout(
        barmode='stack',
        height=290,
        margin=dict(l=10, r=10, t=10, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color=chart_text_color)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(tickfont=dict(size=10, color=chart_text_color)),
        yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.12)', tickfont=dict(size=10, color=chart_text_color))
      )
      st.plotly_chart(fig_stacked, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

  st.markdown("<div style='margin-bottom: 18px;'></div>", unsafe_allow_html=True)

  # =========================================================================
  # 5. STATUTORY COMPLIANCE & PERFORMANCE: 65% / 35% Split
  # =========================================================================
  col_comp_tbl, col_comp_gauge = st.columns([1.85, 1.15], gap="medium")

  with col_comp_tbl:
    tbl_icon = feather_icon("shield", color="#059669", size=18, margin_right=6)
    st.markdown(f"""
      <div class="saas-card" style="height: 100%;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
          <div>
            <div class="saas-card-title" style="display: flex; align-items: center;">
              {tbl_icon} Statutory Quota & Compliance Matrix
            </div>
            <div class="saas-card-subtitle">
              Measured burn rate vs government statutory quota benchmarks:
            </div>
          </div>
          <span class="{'status-pill status-pill-green' if not audit_data['is_projected_deficit'] else 'status-pill status-pill-red'}">
            {audit_data['audit_verdict']}
          </span>
        </div>
    """, unsafe_allow_html=True)

    status_pill_daily = '<span class="status-pill status-pill-green">WITHIN DAILY CAP</span>' if audit_data['actual_daily_avg'] <= audit_data['daily_quota_target'] else '<span class="status-pill status-pill-red">EXCEEDS DAILY CAP</span>'
    status_pill_weekly = '<span class="status-pill status-pill-green">WITHIN WEEKLY CAP</span>' if audit_data['actual_weekly_avg'] <= audit_data['weekly_quota_target'] else '<span class="status-pill status-pill-amber">LOGISTICS SURGE</span>'
    status_pill_annual = '<span class="status-pill status-pill-green">FULL-YEAR COMPLIANT</span>' if not audit_data['is_projected_deficit'] else f'<span class="status-pill status-pill-red">SHORTFALL (-{audit_data["projected_credits_needed"]:,.0f} t)</span>'
    status_pill_market = '<span class="status-pill status-pill-green">TRADABLE SURPLUS</span>' if not res['is_deficit'] else '<span class="status-pill status-pill-red">COMPLIANCE DEFICIT</span>'

    monthly_runrate = res['total_co2'] / 12.0
    monthly_allowance = res['govt_credits'] / 12.0
    monthly_util = (monthly_runrate / max(monthly_allowance, 0.1)) * 100
    status_pill_monthly = '<span class="status-pill status-pill-green">NORMAL RUN-RATE</span>' if monthly_util <= 100 else '<span class="status-pill status-pill-amber">ELEVATED RUN-RATE</span>'

    tbl_html = f"""
      <table class="compliance-table">
        <thead>
          <tr>
            <th>Operational Scope</th>
            <th>Statutory Allowance</th>
            <th>Measured Run-Rate</th>
            <th>Utilization</th>
            <th>Compliance Status</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Daily Operations</strong></td>
            <td>{audit_data['daily_quota_target']:.3f} credits/day</td>
            <td><strong>{audit_data['actual_daily_avg']:.3f}</strong> credits/day</td>
            <td>{audit_data['daily_pct_of_allowance']:.1f}%</td>
            <td>{status_pill_daily}</td>
          </tr>
          <tr>
            <td><strong>Weekly Operations</strong></td>
            <td>{audit_data['weekly_quota_target']:.2f} credits/wk</td>
            <td><strong>{audit_data['actual_weekly_avg']:.2f}</strong> credits/wk</td>
            <td>{audit_data['weekly_pct_of_allowance']:.1f}%</td>
            <td>{status_pill_weekly}</td>
          </tr>
          <tr>
            <td><strong>Monthly Run-Rate</strong></td>
            <td>{monthly_allowance:,.1f} credits/mo</td>
            <td><strong>{monthly_runrate:,.1f}</strong> credits/mo</td>
            <td>{monthly_util:.1f}%</td>
            <td>{status_pill_monthly}</td>
          </tr>
          <tr style="background: rgba(16, 185, 129, 0.03);">
            <td><strong>Annual Quota Ceiling</strong></td>
            <td>{audit_data['initial_govt_quota']:,.0f} credits total</td>
            <td><strong>{audit_data['expected_annual_burn']:,.1f}</strong> credits forecast</td>
            <td>{(audit_data['expected_annual_burn']/max(audit_data['initial_govt_quota'],1))*100:.1f}%</td>
            <td>{status_pill_annual}</td>
          </tr>
          <tr>
            <td><strong>Trading Reserve / Position</strong></td>
            <td>{audit_data['initial_govt_quota']:,.0f} credits cap</td>
            <td><strong>{net_val:,.1f}</strong> tonnes {net_sub}</td>
            <td>~{audit_data['quota_runway_days']} d runway</td>
            <td>{status_pill_market}</td>
          </tr>
        </tbody>
      </table>
      <div style="margin-top: 10px; display: flex; justify-content: flex-end;">
    """
    st.markdown(tbl_html, unsafe_allow_html=True)
    if st.button("Reconcile in Carbon Market →", type="primary", key="dash_btn_reconcile_market", use_container_width=True):
      st.session_state["current_step"] = 7
      st.session_state["nav_section"] = "carbon_credits"
      st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)

  with col_comp_gauge:
    gauge_icon = feather_icon("target", color="#059669", size=18, margin_right=6)
    st.markdown(f"""
      <div class="saas-card" style="height: 100%;">
        <div class="saas-card-title" style="display: flex; align-items: center;">
          {gauge_icon} Overall Sustainability Performance
        </div>
        <div class="saas-card-subtitle">Composite ESG readiness score (0–100):</div>
    """, unsafe_allow_html=True)

    fig_gauge = go.Figure(go.Indicator(
      mode="gauge+number",
      value=res["sustainability_score"],
      number={'suffix': "/100", 'font': {'size': 26, 'color': chart_text_color}},
      gauge={
        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': chart_text_color},
        'bar': {'color': "#10B981", 'thickness': 0.28},
        'bgcolor': "rgba(0,0,0,0)",
        'borderwidth': 1,
        'bordercolor': "var(--border-color)",
        'steps': [
          {'range': [0, 45], 'color': 'rgba(239, 68, 68, 0.22)'},
          {'range': [45, 70], 'color': 'rgba(245, 158, 11, 0.22)'},
          {'range': [70, 100], 'color': 'rgba(16, 185, 129, 0.22)'}
        ],
        'threshold': {
          'line': {'color': "#065F46", 'width': 3},
          'thickness': 0.75,
          'value': 80
        }
      }
    ))
    fig_gauge.update_layout(
      height=210,
      margin=dict(l=15, r=15, t=10, b=10),
      paper_bgcolor='rgba(0,0,0,0)',
      plot_bgcolor='rgba(0,0,0,0)',
      font={'color': chart_text_color}
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown(f"""
      <div style="text-align: center; margin-top: 4px;">
        <span class="{'status-pill status-pill-green' if score_val >= 70 else ('status-pill status-pill-amber' if score_val >= 45 else 'status-pill status-pill-red')}" style="padding: 4px 12px; font-size: 0.80rem;">
          {score_badge}
        </span>
        <div style="font-size: 0.74rem; color: var(--text-muted); margin-top: 6px;">
          Calibrated to statutory quotas, circular metrics & emission density.
        </div>
      </div>
      </div>
    """, unsafe_allow_html=True)

  st.markdown("<div style='margin-bottom: 18px;'></div>", unsafe_allow_html=True)

  # =========================================================================
  # 6. SECONDARY INTELLIGENCE: 3 Columns
  # =========================================================================
  col_donut, col_recs, col_activity = st.columns([1.0, 1.15, 0.95], gap="medium")

  with col_donut:
    pie_icon = feather_icon("pie-chart", color="#D97706", size=18, margin_right=6)
    st.markdown(f"""
      <div class="saas-card" style="height: 100%;">
        <div class="saas-card-title" style="display: flex; align-items: center;">
          {pie_icon} Distribution by Pillar
        </div>
        <div class="saas-card-subtitle">Operational stream proportion:</div>
    """, unsafe_allow_html=True)

    if res["total_co2"] <= 0.0:
      st.markdown("""
        <div style="background: var(--bg-subtle); border: 1px dashed var(--border-color); border-radius: 10px; padding: 48px 16px; text-align: center; margin-top: 10px;">
          <div style="font-size: 2.2rem; margin-bottom: 8px;">🍩</div>
          <div style="font-weight: 700; font-size: 0.90rem; color: var(--text-primary); margin-bottom: 4px;">No Stream Distribution</div>
          <div style="font-size: 0.78rem; color: var(--text-muted);">
            Emissions are at 0.0 t CO₂ across all 5 operational pillars.
          </div>
        </div>
      """, unsafe_allow_html=True)
    else:
      pie_labels = list(res["pillar_co2"].keys())
      pie_values = list(res["pillar_co2"].values())
      pillar_palette = ["#10B981", "#F59E0B", "#EF4444", "#3B82F6", "#8B5CF6", "#06B6D4"]

      fig_donut = go.Figure(data=[go.Pie(
        labels=pie_labels,
        values=pie_values,
        hole=0.60,
        marker=dict(colors=pillar_palette, line=dict(color='var(--bg-card)', width=2)),
        textinfo='percent',
        hovertemplate='<b>%{label}</b><br>%{value:,.1f} t CO₂ (%{percent})<extra></extra>'
      )])
      fig_donut.update_layout(
        height=270,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="top", y=-0.05, xanchor="center", x=0.5, font=dict(size=10, color=chart_text_color)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        annotations=[dict(
          text=f"<b>{res['total_co2']:,.0f} t</b><br><span style='font-size:10px;color:#64748B'>Total CO₂</span>",
          x=0.5, y=0.5, font_size=13, showarrow=False, font_color=chart_text_color
        )]
      )
      st.plotly_chart(fig_donut, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

  with col_recs:
    recom_head_icon = feather_icon("lightbulb", color="#D97706", size=18, margin_right=6)
    st.markdown(f"""
      <div class="saas-card" style="height: 100%;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
          <div>
            <div class="saas-card-title" style="display: flex; align-items: center;">
              {recom_head_icon} Top 3 Green Recommendations
            </div>
            <div class="saas-card-subtitle">Prioritized high-ROI decarbonization fixes:</div>
          </div>
        </div>
    """, unsafe_allow_html=True)

    hotspot_recs = generate_hotspot_recommendations(res, user)
    top_3_recs = hotspot_recs[:3]

    if not top_3_recs:
      st.info("No recommendations available for current profile.")
    else:
      for r in top_3_recs:
        diff_class = "status-pill-green" if r["difficulty"] == "Easy" else ("status-pill-amber" if r["difficulty"] == "Medium" else "status-pill-red")
        st.markdown(f"""
          <div style="background: var(--bg-subtle); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px 12px; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
              <span style="font-size: 0.72rem; font-weight: 700; color: #047857; text-transform: uppercase;">
                #{r['targeted_hotspot_rank']} {r['targeted_hotspot_source']}
              </span>
              <span class="status-pill {diff_class}">{r['difficulty']}</span>
            </div>
            <div style="font-size: 0.86rem; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; line-height: 1.3;">
              {r['title']}
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.78rem; color: var(--text-secondary);">
              <span>CO₂: <strong style="color: #059669;">-{r['co2_saved_t']:,.1f} t/yr</strong></span>
              <span>Savings: <strong style="color: #059669;">+₹{r['annual_savings_inr']:,.0f}/yr</strong></span>
              <span>ROI: <strong>{r['expected_roi']}%</strong></span>
            </div>
          </div>
        """, unsafe_allow_html=True)

    if st.button("Explore All Recommendations →", key="dash_explore_recs_btn", type="primary", use_container_width=True):
      st.session_state["current_step"] = 8
      st.session_state["nav_section"] = "recommendations"
      st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

  with col_activity:
    act_icon = feather_icon("clock", color="#64748B", size=18, margin_right=6)

    timeline_items = []
    if user_logs:
      for l in user_logs[:4]:
        note_text = f" • {l['notes']}" if l.get("notes") else ""
        timeline_items.append({
          "title": f"Shift Activity Logged ({l.get('frequency', 'daily').capitalize()})",
          "time": l.get("log_date", "Recent"),
          "detail": f"+{l.get('calculated_total_co2', 0.0):.2f} t CO₂e recorded{note_text}",
          "color": "#10B981"
        })

    if len(timeline_items) < 2:
      timeline_items.append({
        "title": "BEE PAT Quota Benchmarked",
        "time": "Statutory Review",
        "detail": f"Annual allowance ceiling of {res['govt_credits']:,.0f} credits verified",
        "color": "#3B82F6"
      })
      timeline_items.append({
        "title": "Operational Baseline Calibrated",
        "time": "Assessment Sync",
        "detail": f"Facility baseline anchored at {res['total_co2']:,.1f} t CO₂e/yr",
        "color": "#10B981"
      })

    timeline_items_html = []
    for t in timeline_items[:4]:
      timeline_items_html.append(
        f'<div class="timeline-item">'
        f'<div class="timeline-dot" style="background-color: {t["color"]};"></div>'
        f'<div class="timeline-title">{t["title"]}</div>'
        f'<div class="timeline-time">{t["time"]}</div>'
        f'<div class="timeline-detail">{t["detail"]}</div>'
        f'</div>'
      )
    timeline_body = "".join(timeline_items_html)

    card_html = (
      f'<div class="saas-card" style="height: 100%;">'
      f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">'
      f'<div>'
      f'<div class="saas-card-title" style="display: flex; align-items: center;">'
      f'{act_icon} Recent Activity'
      f'</div>'
      f'<div class="saas-card-subtitle">Operational shift & ledger events:</div>'
      f'</div>'
      f'</div>'
      f'<div class="activity-timeline">{timeline_body}</div>'
      f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    if st.button("View Activity Logs Ledger →", type="primary", key="dash_view_logs_btn", use_container_width=True):
      st.session_state["nav_section"] = "activity_logs"
      st.session_state["current_step"] = 4
      st.rerun()

  # =========================================================================
  # 7. BOTTOM QUICK ACTIONS: 4 Shortcuts to Existing Features
  # =========================================================================
  st.markdown("<hr style='margin: 20px 0 14px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)
  c_act1, c_act2, c_act3, c_act4 = st.columns(4)
  with c_act1:
    if st.button("Inspect Emission Leak Hotspots →", type="primary", use_container_width=True, key="dash_btm_leaks"):
      st.session_state["current_step"] = 6
      st.session_state["nav_section"] = "leak_detection"
      st.rerun()
  with c_act2:
    if st.button("Reconcile Carbon Credits →", type="primary", use_container_width=True, key="dash_btm_credits"):
      st.session_state["current_step"] = 7
      st.session_state["nav_section"] = "carbon_credits"
      st.rerun()
  with c_act3:
    if st.button("Open Activity Logs →", type="primary", use_container_width=True, key="dash_btm_logs"):
      st.session_state["nav_section"] = "activity_logs"
      st.session_state["current_step"] = 4
      st.rerun()
  with c_act4:
    if st.button("Launch Decarbonization Simulator →", type="primary", use_container_width=True, key="dash_btm_sim"):
      st.session_state["current_step"] = 9
      st.session_state["nav_section"] = "simulator"
      st.rerun()

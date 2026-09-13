"""
Operational Activity Log View (Daily & Weekly Emission Tracking).
Collects daily and weekly operational metrics for fuel, waste streams, electricity,
and production units, dynamically updating the database and dashboard visualizations.
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import io

from database.db_manager import (
  save_activity_log, get_activity_logs, delete_activity_log, update_activity_log,
  get_aggregated_activity_summary, save_emissions_assessment,
  sync_activity_logs_to_dashboard, ACTIVITY_EMISSION_FACTORS
)
from components.auth import is_demo_session
from components.calculations import calculate_detailed_emissions
from components.csv_importer import import_past_data_from_csv
from components.icons import (

  feather_icon, render_icon_heading, COLOR_WARNING, COLOR_SUCCESS,
  COLOR_NEUTRAL, COLOR_INFO, COLOR_PRIMARY
)

def render_activity_log_view():
  """Renders the Daily & Weekly Activity Logger interface."""
  user = st.session_state.get("current_user", {})
  user_email = user.get("email", "guest@enterprise.com")
  comp_name = user.get("company_name", "Enterprise Facility")
  is_demo = is_demo_session()

  c_top_back, c_top_space = st.columns([1.5, 4.5])
  with c_top_back:
    if st.button("← Back to Dashboard", key="act_top_back_dash"):
      st.session_state["current_step"] = 5
      st.session_state["nav_section"] = "dashboard"
      st.rerun()

  st.markdown("""
    <div style="margin-bottom: 8px;">
      <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #5A8766; font-weight: 700;">
        High-Frequency Operational Monitoring
      </span>
    </div>
  """, unsafe_allow_html=True)

  header_icon = feather_icon("calendar", color="#5A8766", size=30, margin_right=10)
  st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px; flex-wrap: wrap; gap: 10px;">
      <div>
        <h1 style="font-size: 2.0rem; font-weight: 800; margin: 0; letter-spacing: -0.02em; display: flex; align-items: center;">
          {header_icon} Daily & Weekly Operational Activity Logger
        </h1>
        <p style="font-size: 0.95rem; color: var(--text-muted); margin-top: 4px; margin-bottom: 0;">
          Log shift-level fuel consumption, waste disposals, and meter readings for {comp_name}.
        </p>
      </div>
      <div>
        <span class="{'badge-low' if not is_demo else 'badge-medium'}" style="font-size: 0.85rem; padding: 6px 14px;">
          {'PRODUCTION WORKSPACE' if not is_demo else 'DEMO SANDBOX (ISOLATED)'}
        </span>
      </div>
    </div>
  """, unsafe_allow_html=True)

  # Activity Summary Metrics
  agg = get_aggregated_activity_summary(user_email)
  # Activity Summary Metrics - 4 Equal-Sized Balanced Cards
  agg = get_aggregated_activity_summary(user_email)
  
  m1, m2, m3, m4 = st.columns(4)
  with m1:
    st.markdown(f"""
      <div class="kpi-card">
        <div class="kpi-title">
          {feather_icon("list", color=COLOR_NEUTRAL, size=15, margin_right=5)} Total Logged
        </div>
        <div class="kpi-value">{agg['total_entries']}</div>
        <div class="kpi-subtext">{agg['date_range']}</div>
      </div>
    """, unsafe_allow_html=True)

  with m2:
    st.markdown(f"""
      <div class="kpi-card">
        <div class="kpi-title">
          {feather_icon("leaf", color=COLOR_SUCCESS, size=15, margin_right=5)} Total Footprint
        </div>
        <div class="kpi-value">{agg['total_co2']:,.2f}</div>
        <div class="kpi-subtext">tonnes CO₂e logged</div>
      </div>
    """, unsafe_allow_html=True)

  with m3:
    st.markdown(f"""
      <div class="kpi-card warning">
        <div class="kpi-title">
          {feather_icon("droplet", color=COLOR_WARNING, size=15, margin_right=5)} Fuel & Gas CO₂
        </div>
        <div class="kpi-value">{agg['total_fuel_co2']:,.2f}</div>
        <div class="kpi-subtext">{agg['total_diesel_liters']:,.0f} L diesel &bull; {agg['total_gas_m3']:,.0f} m³ gas</div>
      </div>
    """, unsafe_allow_html=True)

  with m4:
    st.markdown(f"""
      <div class="kpi-card deficit">
        <div class="kpi-title">
          {feather_icon("trash-2", color="#EF4444", size=15, margin_right=5)} Waste & Power CO₂
        </div>
        <div class="kpi-value">{(agg['total_waste_co2'] + agg['total_electricity_co2']):,.2f}</div>
        <div class="kpi-subtext">{agg['total_waste_kg']:,.0f} kg waste &bull; {agg['total_electricity_kwh']:,.0f} kWh</div>
      </div>
    """, unsafe_allow_html=True)

  st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

  tab_entry, tab_history, tab_batch = st.tabs([
    "New Activity Entry", "Activity Ledger & History", "Bulk Ingestion & Export"
  ])

  # 1. New Activity Entry Tab
  with tab_entry:
    # Action Banner for Just-Logged Entry
    just_logged = st.session_state.get("just_logged_record")
    if just_logged:
      next_day_val = just_logged.get("next_date", date.today() + timedelta(days=1))
      st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid #6EE7B7; border-radius: 10px; padding: 12px 16px; margin-bottom: 16px;">
          <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
            <div style="display: flex; align-items: center;">
              {feather_icon('check-circle', color='#6B8E7D', size=20, margin_right=8)}
              <div>
                <span style="font-weight: 800; color: #065F46; font-size: 0.95rem;">
                  Record #{just_logged['id']} Logged for {just_logged['date']} ({just_logged['co2']:,.2f} t CO₂e)
                </span>
                <span style="font-size: 0.78rem; color: #047857; margin-left: 8px; background: rgba(16, 185, 129, 0.25); padding: 2px 8px; border-radius: 4px; font-weight: 700;">
                  Executive Dashboard Synced
                </span>
              </div>
            </div>
          </div>
        </div>
      """, unsafe_allow_html=True)

      col_act1, col_act2, col_act3 = st.columns([1.5, 1.3, 1.4])
      with col_act1:
        if st.button(f"Log Next Day ({next_day_val.strftime('%b %d, %Y')})", key="act_log_next_day_btn", type="primary", use_container_width=True):
          st.session_state["activity_log_next_date"] = next_day_val
          st.session_state["activity_log_label_preset"] = next_day_val.strftime("%Y-%m-%d")
          st.session_state["just_logged_record"] = None
          st.rerun()
      with col_act2:
        if st.button(f"Delete Entry #{just_logged['id']}", key=f"act_del_just_{just_logged['id']}", type="secondary", use_container_width=True):
          del_id = just_logged["id"]
          delete_activity_log(del_id, user_email)
          sync_activity_logs_to_dashboard(user_email, is_demo=is_demo)
          st.session_state["just_logged_record"] = None
          st.success(f"Entry #{del_id} deleted! Executive Dashboard recalculated.")
          st.rerun()
      with col_act3:
        if st.button("View Executive Dashboard →", key="act_view_dash_btn", use_container_width=True):
          st.session_state["nav_section"] = "dashboard"
          st.session_state["current_step"] = 5
          st.rerun()

      st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    with st.form("activity_entry_form"):
      st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; padding-bottom: 10px; border-bottom: 1px solid var(--border-color);">
          <div>
            <div style="font-weight: 800; font-size: 1.15rem; color: var(--text-primary);">
              Shift & Operational Activity Data Entry
            </div>
            <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 2px;">
              Enter measured fuel receipts, waste weights, and utility invoices. Automatically recalculates your Executive Dashboard.
            </div>
          </div>
          <span style="font-size: 0.78rem; background: #DCFCE7; color: #166534; padding: 4px 10px; border-radius: 6px; font-weight: 700;">
            Live Sync Active
          </span>
        </div>
      """, unsafe_allow_html=True)

      # Metadata Row with dynamic next-day preset
      default_entry_date = st.session_state.get("activity_log_next_date", date.today())
      preset_lbl = st.session_state.get("activity_log_label_preset", default_entry_date.strftime("%Y-%m-%d"))

      c_meta1, c_meta2, c_meta3 = st.columns([1, 1, 1.5])
      with c_meta1:
        in_freq = st.selectbox("Frequency", ["Daily", "Weekly"], index=0, key="act_freq_select")
      with c_meta2:
        in_date = st.date_input("Activity Date", value=default_entry_date, key="act_date_input")
      with c_meta3:
        in_label = st.text_input("Period Label / Shift ID", value=preset_lbl, help="e.g. Morning Shift, Generator Test, Week 37", key="act_shift_label_input")

      st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

      # Section 1: Fuel & Gas (Crisp Group Card)
      st.markdown(f"""
        <div class="input-section-card">
          <div class="input-section-header">
            <span style="font-weight: 700; font-size: 0.95rem; color: var(--text-primary); display: flex; align-items: center;">
              {feather_icon('droplet', color=COLOR_WARNING, size=16, margin_right=6)} 1. Liquid & Gaseous Fuels
            </span>
            <span style="font-size: 0.75rem; background: #FEF3C7; color: #92400E; padding: 2px 8px; border-radius: 6px; font-weight: 700;">
              Scope 1 Direct
            </span>
          </div>
      """, unsafe_allow_html=True)
      c_f1, c_f2, c_f3 = st.columns(3)
      with c_f1:
        in_diesel = st.number_input("⛽ Diesel Fuel (Liters)", min_value=0.0, value=0.0, step=10.0, help="Backup gensets, forklifts, plant boilers", key="act_diesel_inp")
      with c_f2:
        in_petrol = st.number_input("🚗 Petrol / Gasoline (Liters)", min_value=0.0, value=0.0, step=5.0, help="Company fleet vehicles & utility machinery", key="act_petrol_inp")
      with c_f3:
        in_gas = st.number_input("Natural Gas (m³)", min_value=0.0, value=0.0, step=25.0, help="Thermal process heating & furnaces", key="act_gas_inp")
      st.markdown("</div>", unsafe_allow_html=True)

      # Section 2: Waste Streams (Crisp Group Card)
      st.markdown(f"""
        <div class="input-section-card">
          <div class="input-section-header">
            <span style="font-weight: 700; font-size: 0.95rem; color: var(--text-primary); display: flex; align-items: center;">
              {feather_icon('trash-2', color='#EF4444', size=16, margin_right=6)} 2. Solid & Hazardous Waste Streams (kg)
            </span>
            <span style="font-size: 0.75rem; background: #FEE2E2; color: #991B1B; padding: 2px 8px; border-radius: 6px; font-weight: 700;">
              Scope 3 Disposal
            </span>
          </div>
      """, unsafe_allow_html=True)
      c_w1, c_w2, c_w3, c_w4, c_w5 = st.columns(5)
      with c_w1:
        in_org = st.number_input("🍃 Organic Waste (kg)", min_value=0.0, value=0.0, step=20.0, key="act_org_inp")
      with c_w2:
        in_plas = st.number_input("🥤 Plastic Waste (kg)", min_value=0.0, value=0.0, step=10.0, key="act_plas_inp")
      with c_w3:
        in_met = st.number_input("🔩 Metal Scrap (kg)", min_value=0.0, value=0.0, step=10.0, key="act_met_inp")
      with c_w4:
        in_pap = st.number_input("📦 Paper & Board (kg)", min_value=0.0, value=0.0, step=10.0, key="act_pap_inp")
      with c_w5:
        in_haz = st.number_input("Hazardous Waste (kg)", min_value=0.0, value=0.0, step=5.0, key="act_haz_inp")
      st.markdown("</div>", unsafe_allow_html=True)

      # Section 3: Electricity, Freight & Utilities (Crisp Group Card)
      st.markdown(f"""
        <div class="input-section-card">
          <div class="input-section-header">
            <span style="font-weight: 700; font-size: 0.95rem; color: var(--text-primary); display: flex; align-items: center;">
              {feather_icon('zap', color=COLOR_INFO, size=16, margin_right=6)} 3. Electricity, Logistics Freight & Production Output
            </span>
            <span style="font-size: 0.75rem; background: #E0F2FE; color: #0369A1; padding: 2px 8px; border-radius: 6px; font-weight: 700;">
              Scope 2 & 3
            </span>
          </div>
      """, unsafe_allow_html=True)
      c_u1, c_u2, c_u3, c_u4 = st.columns(4)
      with c_u1:
        in_elec = st.number_input("⚡ Metered Electricity (kWh)", min_value=0.0, value=0.0, step=100.0, key="act_elec_inp")
      with c_u2:
        in_truck = st.number_input("🚚 Freight Transport (km)", min_value=0.0, value=0.0, step=50.0, key="act_truck_inp")
      with c_u3:
        in_water = st.number_input("💧 Freshwater Metered (m³)", min_value=0.0, value=0.0, step=10.0, key="act_water_inp")
      with c_u4:
        in_prod = st.number_input("🏭 Production Output (units)", min_value=0.0, value=0.0, step=50.0, key="act_prod_inp")
      st.markdown("</div>", unsafe_allow_html=True)

      in_notes = st.text_input("Operational Context / Notes", placeholder="e.g. Scheduled boiler blowout; packaging surge for holiday delivery", key="act_notes_inp")

      st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
      submit_log = st.form_submit_button("💾 Save Activity Log & Recalculate Dashboard", type="primary", use_container_width=True)

      if submit_log:
        total_activity = in_diesel + in_petrol + in_gas + in_org + in_plas + in_met + in_pap + in_haz + in_elec + in_truck
        if total_activity <= 0:
          st.error("Please enter at least one positive operational quantity (fuel, waste, electricity, or transport).")
        else:
          log_payload = {
            "log_date": in_date.isoformat(),
            "frequency": in_freq.lower(),
            "period_label": in_label,
            "diesel_liters": in_diesel,
            "petrol_liters": in_petrol,
            "gas_m3": in_gas,
            "electricity_kwh": in_elec,
            "organic_waste_kg": in_org,
            "plastic_waste_kg": in_plas,
            "metal_waste_kg": in_met,
            "paper_waste_kg": in_pap,
            "hazardous_waste_kg": in_haz,
            "truck_km": in_truck,
            "water_m3": in_water,
            "production_units": in_prod,
            "notes": in_notes
          }
          record_id = save_activity_log(user_email, log_payload, is_demo=is_demo)
          
          f_co2 = (in_diesel * ACTIVITY_EMISSION_FACTORS["diesel"]) + (in_petrol * ACTIVITY_EMISSION_FACTORS["petrol"]) + (in_gas * ACTIVITY_EMISSION_FACTORS["gas"])
          w_co2 = (in_org * ACTIVITY_EMISSION_FACTORS["waste_organic"]) + (in_plas * ACTIVITY_EMISSION_FACTORS["waste_plastic"]) + (in_met * ACTIVITY_EMISSION_FACTORS["waste_metal"]) + (in_pap * ACTIVITY_EMISSION_FACTORS["waste_paper"]) + (in_haz * ACTIVITY_EMISSION_FACTORS["waste_hazardous"])
          tot_co2 = f_co2 + w_co2 + (in_elec * ACTIVITY_EMISSION_FACTORS["electricity"]) + (in_truck * ACTIVITY_EMISSION_FACTORS["truck"])

          # Date progression to next day
          next_d = in_date + timedelta(days=1)
          st.session_state["activity_log_next_date"] = next_d
          st.session_state["activity_log_label_preset"] = next_d.strftime("%Y-%m-%d") if in_freq == "Daily" else f"Week {(next_d).strftime('%U, %Y')}"
          st.session_state["just_logged_record"] = {
            "id": record_id,
            "date": in_date.strftime("%Y-%m-%d"),
            "next_date": next_d,
            "co2": tot_co2,
            "label": in_label
          }

          # Explicitly ensure dashboard is recalculated
          st.session_state["manual_setup_override"] = False
          sync_activity_logs_to_dashboard(user_email, is_demo=is_demo)

          st.success(f"✅ Successfully logged record #{record_id}! Generated {tot_co2:,.3f} tonnes CO₂e. Executive Dashboard updated!")
          st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

  # 2. Activity Ledger & History Tab
  with tab_history:
    st.markdown(f"""
      <div class="saas-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; flex-wrap: wrap; gap: 10px;">
          <div>
            <div class="saas-card-title">{feather_icon('list', color=COLOR_NEUTRAL, size=18)} Recorded Operational Logs History</div>
            <div class="saas-card-subtitle">Complete chronological audit ledger stored in SQLite:</div>
          </div>
        </div>
    """, unsafe_allow_html=True)

    c_filt1, c_filt2 = st.columns([1, 2])
    with c_filt1:
      freq_filter = st.selectbox("Filter Frequency", ["All Records", "Daily Only", "Weekly Only"], index=0, key="hist_freq_filter")
    
    filter_val = None if freq_filter == "All Records" else ("daily" if "Daily" in freq_filter else "weekly")
    logs = get_activity_logs(user_email, limit=200, frequency=filter_val)

    if not logs:
      st.info("No activity logs recorded yet. Use the 'New Activity Entry' tab to record your first daily or weekly log.")
    else:
      table_rows = []
      for l in logs:
        table_rows.append({
          "ID": l["id"],
          "Date": l["log_date"],
          "Freq": l["frequency"].capitalize(),
          "Label": l["period_label"],
          "Fuel CO₂ (t)": round(l["calculated_fuel_co2"], 3),
          "Waste CO₂ (t)": round(l["calculated_waste_co2"], 3),
          "Elec CO₂ (t)": round(l["calculated_electricity_co2"], 3),
          "Total CO₂ (t)": round(l["calculated_total_co2"], 3),
          "Notes": l["notes"]
        })
      df_logs = pd.DataFrame(table_rows)
      st.dataframe(df_logs, use_container_width=True, height=280)

      # Direct 1-Click Inline Record Deletion
      st.markdown(f"""
        <div style="margin-top: 18px; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between;">
          <div style="font-weight: 800; font-size: 0.95rem; color: var(--text-primary); display: flex; align-items: center;">
            {feather_icon('trash-2', color='#EF4444', size=16, margin_right=6)} Recent Recorded Shifts — 1-Click Deletion
          </div>
          <span style="font-size: 0.78rem; color: var(--text-muted);">
            Deleting an entry immediately recalculates the Executive Dashboard
          </span>
        </div>
      """, unsafe_allow_html=True)

      for l in logs[:8]:
        c_desc, c_stat, c_del = st.columns([2.5, 2.2, 0.9])
        with c_desc:
          st.markdown(f"""
            <div style="font-size: 0.88rem; font-weight: 700; color: var(--text-primary);">
              #{l['id']} &bull; {l['log_date']} <span style="font-weight: 400; color: var(--text-muted);">({l['period_label']})</span>
            </div>
          """, unsafe_allow_html=True)
        with c_stat:
          st.markdown(f"""
            <div style="font-size: 0.82rem; color: var(--text-muted);">
              Fuel: <strong>{l['calculated_fuel_co2']:.2f}t</strong> | Waste: <strong>{l['calculated_waste_co2']:.2f}t</strong> | Total: <strong style="color: #5A8766;">{l['calculated_total_co2']:.2f}t CO₂e</strong>
            </div>
          """, unsafe_allow_html=True)
        with c_del:
          if st.button("Delete", key=f"inline_del_log_{l['id']}", type="secondary", use_container_width=True):
            delete_activity_log(l["id"], user_email)
            sync_activity_logs_to_dashboard(user_email, is_demo=is_demo)
            st.success(f"Record #{l['id']} deleted! Executive Dashboard recalculated.")
            st.rerun()

      # Action: Roll up logs into Annual Baseline
      st.markdown("<hr style='margin: 18px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)
      c_roll1, c_roll2 = st.columns([1.5, 1])
      with c_roll1:
        st.markdown(f"""
          <div style="font-weight: 700; font-size: 0.95rem; margin-bottom: 4px;">
            Synchronize Logs with Enterprise Annual Baseline
          </div>
          <div style="font-size: 0.82rem; color: var(--text-muted);">
            Annualizes your recorded daily/weekly operational run-rate across 365 days and updates your enterprise compliance assessment in SQLite.
          </div>
        """, unsafe_allow_html=True)

      with c_roll2:
        if st.button("Roll Up Logs to Annual Baseline", type="primary", use_container_width=True, key="act_rollup_btn"):
          daily_logs = [l for l in logs if l["frequency"] == "daily"]
          if len(daily_logs) >= 1:
            sync_activity_logs_to_dashboard(user_email, is_demo=is_demo)
            st.success(f"✅ Baseline synchronized from {len(daily_logs)} daily logs! Executive Dashboard updated.")
            st.rerun()
          else:
            st.warning("Please record at least 1 daily log before calculating an annualized run-rate.")

      # Edit an Operational Log Entry
      with st.expander("Edit an Operational Log Entry"):
        log_map = {f"#{l['id']} - {l['log_date']} ({l['period_label']})": l for l in logs}
        selected_log_label = st.selectbox("Select Log Entry to Edit", list(log_map.keys()), key="edit_log_selector")
        target_log = log_map[selected_log_label]
        
        with st.form(f"edit_log_form_{target_log['id']}"):
          ce1, ce2, ce3 = st.columns(3)
          with ce1:
            ed_diesel = st.number_input("⛽ Diesel (L)", min_value=0.0, value=float(target_log.get("diesel_liters", 0.0)), step=10.0, key=f"ed_d_{target_log['id']}")
            ed_petrol = st.number_input("🚗 Petrol (L)", min_value=0.0, value=float(target_log.get("petrol_liters", 0.0)), step=5.0, key=f"ed_p_{target_log['id']}")
            ed_gas = st.number_input("Gas (m³)", min_value=0.0, value=float(target_log.get("gas_m3", 0.0)), step=25.0, key=f"ed_g_{target_log['id']}")
          with ce2:
            ed_elec = st.number_input("⚡ Electricity (kWh)", min_value=0.0, value=float(target_log.get("electricity_kwh", 0.0)), step=100.0, key=f"ed_e_{target_log['id']}")
            ed_waste_org = st.number_input("🍃 Organic Waste (kg)", min_value=0.0, value=float(target_log.get("organic_waste_kg", 0.0)), step=10.0, key=f"ed_wo_{target_log['id']}")
            ed_waste_plas = st.number_input("🥤 Plastic Waste (kg)", min_value=0.0, value=float(target_log.get("plastic_waste_kg", 0.0)), step=10.0, key=f"ed_wp_{target_log['id']}")
          with ce3:
            ed_waste_met = st.number_input("🔩 Metal Scrap (kg)", min_value=0.0, value=float(target_log.get("metal_waste_kg", 0.0)), step=10.0, key=f"ed_wm_{target_log['id']}")
            ed_waste_pap = st.number_input("📦 Paper/Cardboard (kg)", min_value=0.0, value=float(target_log.get("paper_waste_kg", 0.0)), step=10.0, key=f"ed_wpa_{target_log['id']}")
            ed_truck = st.number_input("🚚 Freight Distance (km)", min_value=0.0, value=float(target_log.get("truck_km", 0.0)), step=50.0, key=f"ed_t_{target_log['id']}")
          
          ed_notes = st.text_input("Operational Shift Notes", value=str(target_log.get("notes") or ""), key=f"ed_n_{target_log['id']}")
          ed_submit = st.form_submit_button("💾 Save Changes & Recalculate Dashboard", type="primary", use_container_width=True)
          if ed_submit:
            updated_payload = {
              "log_date": target_log["log_date"],
              "frequency": target_log["frequency"],
              "period_label": target_log["period_label"],
              "diesel_liters": ed_diesel,
              "petrol_liters": ed_petrol,
              "gas_m3": ed_gas,
              "electricity_kwh": ed_elec,
              "organic_waste_kg": ed_waste_org,
              "plastic_waste_kg": ed_waste_plas,
              "metal_waste_kg": ed_waste_met,
              "paper_waste_kg": ed_waste_pap,
              "hazardous_waste_kg": float(target_log.get("hazardous_waste_kg", 0.0)),
              "truck_km": ed_truck,
              "water_m3": float(target_log.get("water_m3", 0.0)),
              "production_units": float(target_log.get("production_units", 0.0)),
              "notes": ed_notes
            }
            update_activity_log(target_log["id"], user_email, updated_payload, is_demo=is_demo)
            st.session_state["manual_setup_override"] = False
            st.success(f"Entry #{target_log['id']} updated! Dashboard recalculated.")
            st.rerun()

      # Individual Log Deletion Option by ID
      with st.expander("Delete a Log Record by ID"):
        log_ids = [l["id"] for l in logs]
        selected_del_id = st.selectbox("Select Log ID to Delete", log_ids, key="del_select_box")
        if st.button("Confirm Delete Record", key="del_log_btn_confirm"):
          if delete_activity_log(selected_del_id, user_email):
            st.session_state["manual_setup_override"] = False
            sync_activity_logs_to_dashboard(user_email, is_demo=is_demo)
            st.success(f"Record #{selected_del_id} deleted successfully.")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

  # 3. Bulk Ingestion & CSV Export Tab
  with tab_batch:
    c_b1, c_b2 = st.columns([1, 1], gap="large")
    
    with c_b1:
      st.markdown(f"""
        <div class="saas-card">
          <div class="saas-card-title">{feather_icon('download', color=COLOR_SUCCESS, size=18)} Export Activity Logs to CSV</div>
          <div class="saas-card-subtitle" style="margin-bottom: 14px;">
            Download complete logged history for audit compliance or ERP spreadsheet backup:
          </div>
      """, unsafe_allow_html=True)

      all_logs = get_activity_logs(user_email, limit=1000)
      if all_logs:
        df_exp = pd.DataFrame(all_logs)
        csv_bytes = df_exp.to_csv(index=False).encode('utf-8')
        st.download_button(
          label="📄 Download All Logs (.CSV)",
          data=csv_bytes,
          file_name=f"{comp_name.replace(' ', '_').lower()}_activity_logs.csv",
          mime="text/csv",
          use_container_width=True
        )
      else:
        st.info("No records to export yet.")
      st.markdown("</div>", unsafe_allow_html=True)

    with c_b2:
      st.markdown(f"""
        <div class="saas-card">
          <div class="saas-card-title">{feather_icon('upload', color=COLOR_INFO, size=18)} Batch CSV Ingestion</div>
          <div class="saas-card-subtitle" style="margin-bottom: 14px;">
            Import multiple days or weeks of operational entries at once via CSV:
          </div>
      """, unsafe_allow_html=True)

      sample_batch = {
        "log_date": [date.today().isoformat(), (date.today() - timedelta(days=1)).isoformat()],
        "frequency": ["daily", "daily"],
        "period_label": ["Shift A", "Shift B"],
        "diesel_liters": [45.0, 52.0],
        "petrol_liters": [10.0, 12.0],
        "gas_m3": [110.0, 115.0],
        "electricity_kwh": [850.0, 920.0],
        "organic_waste_kg": [60.0, 75.0],
        "plastic_waste_kg": [35.0, 40.0],
        "metal_waste_kg": [15.0, 20.0],
        "paper_waste_kg": [25.0, 30.0],
        "hazardous_waste_kg": [5.0, 6.0],
        "truck_km": [120.0, 140.0],
        "notes": ["Batch upload A", "Batch upload B"]
      }
      batch_template_df = pd.DataFrame(sample_batch)
      st.download_button(
        label="Download Batch CSV Format Template",
        data=batch_template_df.to_csv(index=False).encode('utf-8'),
        file_name="activity_batch_template.csv",
        mime="text/csv",
        use_container_width=True
      )

      uploaded_batch = st.file_uploader("Upload Completed Activity CSV", type=["csv", "xlsx", "xls"], key="activity_batch_file_uploader")
      if uploaded_batch is not None:
        last_file = st.session_state.get("activity_last_uploaded_file")
        if last_file != uploaded_batch.name:
          with st.spinner("Processing batch activity spreadsheet..."):
            import_res = import_past_data_from_csv(uploaded_batch, user_email, is_demo=is_demo)
            st.session_state["activity_last_uploaded_file"] = uploaded_batch.name
            if import_res.get("success"):
              st.success(f"🎉 {import_res.get('message', 'Successfully imported activity records!')}")
              st.rerun()
            else:
              st.error(import_res.get("error", "Error importing batch file."))

      st.markdown("</div>", unsafe_allow_html=True)


  # Navigation
  st.markdown("<hr style='margin: 24px 0 16px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)
  if st.button("← Back to Dashboard", key="act_bottom_back_dash"):
    st.session_state["current_step"] = 5
    st.session_state["nav_section"] = "dashboard"
    st.rerun()

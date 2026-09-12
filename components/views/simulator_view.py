"""
Step 9: Before vs After Simulation View.
Interactive real-time sliders for Electricity, Fuel, Waste, Transport, Water, Production, and Renewable %.
Instantly recalculates and updates KPIs, comparison charts, and carbon credit deficits with zero latency.
"""

import streamlit as st
import plotly.graph_objects as go
from components.calculations import calculate_detailed_emissions
from components.icons import feather_icon, render_icon_heading, COLOR_WARNING, COLOR_SUCCESS, COLOR_NEUTRAL, COLOR_AMBER, COLOR_ORANGE

def render_simulator_view():
  """Renders Step 9 Before vs After Simulator."""
  res = st.session_state.get("emissions_results")
  if not res:
    st.warning("Please complete Step 3 Setup or load a preset first.")
    return

  baseline_inputs = res.get("raw_inputs", {})
  baseline_co2 = res["total_co2"]
  baseline_cost = res["total_cost"]
  chart_text_color = "#1E293B"

  st.markdown("""
    <div style="margin-bottom: 8px;">
      <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #10B981; font-weight: 700;">
        Step 9 — Interactive What-If Scenario Simulator
      </span>
    </div>
  """, unsafe_allow_html=True)
  st.markdown(render_icon_heading(
    "sliders",
    "Before vs. After Decarbonization Sandbox",
    level="h2",
    color=COLOR_NEUTRAL,
    subtitle="Drag operational reduction sliders and renewable % targets below. Observe instant live updates to emissions, savings, and credit status."
  ), unsafe_allow_html=True)

  # Preset Simulation Buttons
  sim_icon = feather_icon("sliders", color=COLOR_NEUTRAL, size=16, margin_right=6)
  st.markdown(f"""
    <div class="saas-card" style="padding: 12px 18px; margin-bottom: 20px;">
      <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
        <span style="font-weight: 700; font-size: 0.9rem; display: flex; align-items: center;">{sim_icon} Quick Simulation Scenarios:</span>
  """, unsafe_allow_html=True)

  c_s1, c_s2, c_s3 = st.columns(3)
  with c_s1:
    if st.button("🌱 Conservative Quick-Wins (-15%)", use_container_width=True):
      st.session_state["sim_elec"] = 15
      st.session_state["sim_fuel"] = 10
      st.session_state["sim_trans"] = 15
      st.session_state["sim_waste"] = 25
      st.session_state["sim_water"] = 15
      st.session_state["sim_renew"] = max(30, int(baseline_inputs.get("renewable_pct", 15)))
      st.rerun()
  with c_s2:
    if st.button("🚀 Aggressive Circular Upgrade (-35%)", use_container_width=True):
      st.session_state["sim_elec"] = 35
      st.session_state["sim_fuel"] = 30
      st.session_state["sim_trans"] = 35
      st.session_state["sim_waste"] = 55
      st.session_state["sim_water"] = 35
      st.session_state["sim_renew"] = 65
      st.rerun()
  with c_s3:
    if st.button("🌍 Net-Zero Transformation (-60%)", use_container_width=True):
      st.session_state["sim_elec"] = 60
      st.session_state["sim_fuel"] = 55
      st.session_state["sim_trans"] = 65
      st.session_state["sim_waste"] = 75
      st.session_state["sim_water"] = 50
      st.session_state["sim_renew"] = 100
      st.rerun()

  st.markdown("</div>", unsafe_allow_html=True)

  col_sliders, col_results = st.columns([1.1, 1.3], gap="large")

  with col_sliders:
    slider_icon = feather_icon("sliders", color=COLOR_NEUTRAL, size=20, margin_right=8)
    st.markdown(f"<div style='display: flex; align-items: center; margin-bottom: 12px;'>{slider_icon} <h4 style='margin: 0;'>Live Operational Sliders</h4></div>", unsafe_allow_html=True)

    sim_elec = st.slider(
      "⚡ Electricity Efficiency Cut (%)", min_value=0, max_value=80,
      value=st.session_state.get("sim_elec", 20), step=5,
      help="LED retrofits, HVAC smart scheduling, VFD variable speed drives"
    )
    st.session_state["sim_elec"] = sim_elec

    sim_renew = st.slider(
      "On-Site Renewable Energy Target (%)", min_value=0, max_value=100,
      value=st.session_state.get("sim_renew", int(baseline_inputs.get("renewable_pct", 15))), step=5,
      help="Rooftop solar PV installation or 100% green PPA contracting"
    )
    st.session_state["sim_renew"] = sim_renew

    sim_fuel = st.slider(
      "Thermal Fuel & Gas Cut (%)", min_value=0, max_value=80,
      value=st.session_state.get("sim_fuel", 20), step=5,
      help="Boiler jacket insulation, flue gas heat recovery, heat pump electrification"
    )
    st.session_state["sim_fuel"] = sim_fuel

    sim_trans = st.slider(
      "🚚 Transport & Fleet Mileage Reduction (%)", min_value=0, max_value=80,
      value=st.session_state.get("sim_trans", 25), step=5,
      help="AI routing software, anti-idling limits, delivery consolidation"
    )
    st.session_state["sim_trans"] = sim_trans

    sim_waste = st.slider(
      "Landfill Waste Diversion (%)", min_value=0, max_value=90,
      value=st.session_state.get("sim_waste", 40), step=5,
      help="Closed-loop plastic regrind, food composting, cardboard shredding"
    )
    st.session_state["sim_waste"] = sim_waste

    sim_water = st.slider(
      "💧 Water & Effluent Recycling (%)", min_value=0, max_value=75,
      value=st.session_state.get("sim_water", 25), step=5,
      help="Cooling tower greywater reuse and membrane filtration"
    )
    st.session_state["sim_water"] = sim_water

    sim_prod = st.slider(
      "📦 Production Output Scale (+/- %)", min_value=-30, max_value=50,
      value=st.session_state.get("sim_prod", 0), step=5,
      help="Model future plant output growth without proportional emissions growth"
    )
    st.session_state["sim_prod"] = sim_prod

  # Compute Simulated Footprint Live
  simulated_inputs = baseline_inputs.copy()
  simulated_inputs["electricity_kwh"] = float(baseline_inputs.get("electricity_kwh", 350000.0)) * (1.0 - sim_elec / 100.0)
  simulated_inputs["renewable_pct"] = float(sim_renew)
  simulated_inputs["diesel_liters"] = float(baseline_inputs.get("diesel_liters", 12000.0)) * (1.0 - sim_fuel / 100.0)
  simulated_inputs["petrol_liters"] = float(baseline_inputs.get("petrol_liters", 4500.0)) * (1.0 - sim_fuel / 100.0)
  simulated_inputs["gas_m3"] = float(baseline_inputs.get("gas_m3", 32000.0)) * (1.0 - sim_fuel / 100.0)
  simulated_inputs["truck_km"] = float(baseline_inputs.get("truck_km", 55000.0)) * (1.0 - sim_trans / 100.0)
  simulated_inputs["car_km"] = float(baseline_inputs.get("car_km", 18000.0)) * (1.0 - sim_trans / 100.0)
  simulated_inputs["commute_km"] = float(baseline_inputs.get("commute_km", 75000.0)) * (1.0 - sim_trans * 0.5 / 100.0)
  
  simulated_inputs["organic_waste_kg"] = float(baseline_inputs.get("organic_waste_kg", 24000.0)) * (1.0 - sim_waste / 100.0)
  simulated_inputs["plastic_waste_kg"] = float(baseline_inputs.get("plastic_waste_kg", 16000.0)) * (1.0 - sim_waste / 100.0)
  simulated_inputs["metal_waste_kg"] = float(baseline_inputs.get("metal_waste_kg", 8500.0)) * (1.0 - sim_waste / 100.0)
  simulated_inputs["paper_waste_kg"] = float(baseline_inputs.get("paper_waste_kg", 14000.0)) * (1.0 - sim_waste / 100.0)
  simulated_inputs["hazardous_waste_kg"] = float(baseline_inputs.get("hazardous_waste_kg", 1200.0)) * (1.0 - sim_waste * 0.8 / 100.0)

  simulated_inputs["water_m3"] = float(baseline_inputs.get("water_m3", 6400.0)) * (1.0 - sim_water / 100.0)
  simulated_inputs["wastewater_m3"] = float(baseline_inputs.get("wastewater_m3", 5200.0)) * (1.0 - sim_water / 100.0)

  prod_factor = 1.0 + (sim_prod / 100.0)
  simulated_inputs["production_units"] = float(baseline_inputs.get("production_units", 150000.0)) * prod_factor

  sim_res = calculate_detailed_emissions(simulated_inputs)

  # Deltas
  diff_co2 = round(baseline_co2 - sim_res["total_co2"], 1)
  diff_pct = round((diff_co2 / baseline_co2 * 100.0), 1) if baseline_co2 > 0 else 0.0
  diff_cost = round(baseline_cost - sim_res["total_cost"], 0)

  with col_results:
    impact_icon = feather_icon("columns", color=COLOR_SUCCESS, size=20, margin_right=8)
    st.markdown(f"<div style='display: flex; align-items: center; margin-bottom: 12px;'>{impact_icon} <h4 style='margin: 0;'>Projected Decarbonization Impact</h4></div>", unsafe_allow_html=True)

    # Metric cards
    m1, m2, m3 = st.columns(3)
    with m1:
      st.metric(
        label="Simulated Footprint",
        value=f"{sim_res['total_co2']:,.1f} t",
        delta=f"-{diff_co2} t ({diff_pct}% cut)",
        delta_color="normal"
      )
    with m2:
      st.metric(
        label="Annual Cost Savings",
        value=f"₹{diff_cost:,.0f} / yr",
        delta=f"₹{diff_cost:,.0f} recovered",
        delta_color="normal"
      )
    with m3:
      st.metric(
        label="New Eco Score",
        value=f"{sim_res['sustainability_score']:.0f}/100",
        delta=f"+{round(sim_res['sustainability_score'] - res['sustainability_score'], 1)} pts",
        delta_color="normal"
      )

    # Before vs After Grouped Bar Chart
    categories = list(res["pillar_co2"].keys())
    baseline_values = [res["pillar_co2"].get(c, 0) for c in categories]
    simulated_values = [sim_res["pillar_co2"].get(c, 0) for c in categories]

    fig_sim = go.Figure(data=[
      go.Bar(name='Current Baseline', x=categories, y=baseline_values, marker_color='#EF4444'),
      go.Bar(name='Projected with Fixes', x=categories, y=simulated_values, marker_color='#10B981')
    ])
    fig_sim.update_layout(
      barmode='group',
      height=280,
      margin=dict(l=10, r=10, t=10, b=20),
      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=chart_text_color)),
      paper_bgcolor='rgba(0,0,0,0)',
      plot_bgcolor='rgba(0,0,0,0)',
      xaxis=dict(tickfont=dict(color=chart_text_color)),
      yaxis=dict(title=dict(text="Tonnes CO₂e", font=dict(color=chart_text_color)), tickfont=dict(color=chart_text_color), showgrid=True, gridcolor='rgba(128,128,128,0.15)')
    )
    st.plotly_chart(fig_sim, use_container_width=True)

    # Projected Carbon Credit Shift Callout
    st.markdown(f"""
      <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 14px 18px; margin-top: 10px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <strong style="font-size: 0.95rem;">New Net Carbon Status:</strong>
            <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 2px;">
              {'Surplus of ' + str(sim_res['credits_remaining']) + ' credits available to sell (+₹' + f"{sim_res['est_revenue']:,.0f}" + ')' if not sim_res['is_deficit'] else 'Deficit reduced to ' + str(sim_res['credits_required']) + ' credits'}
            </div>
          </div>
          <span class="{'badge-low' if not sim_res['is_deficit'] else 'badge-critical'}">
            {sim_res['net_carbon_status']}
          </span>
        </div>
      </div>
    """, unsafe_allow_html=True)

  # Navigation
  st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)
  c_b1, c_b2 = st.columns([1, 1])
  with c_b1:
    if st.button("← Back to Recommendations", key="sim_back_recom"):
      st.session_state["current_step"] = 8
      st.session_state["nav_section"] = "recommendations"
      st.rerun()
  with c_b2:
    if st.button("Proceed to Circular Alternatives (4R Framework) →", type="primary", key="sim_next_circ", use_container_width=True):
      st.session_state["current_step"] = 10
      st.session_state["nav_section"] = "circular"
      st.rerun()

"""
Step 6: Action Plan View.
Groups prioritized initiatives into:
1. Quick Wins (0–3 months)
2. Mid-term (3–12 months)
3. Long-term (1+ years)
Allows tracking completion and assigning operational owners.
"""

import streamlit as st
from components.data_presets import CATEGORY_FIXES
from components.calculations import CATEGORY_METADATA

def get_selected_fix_objects():
  """Gathers all fix objects currently selected by user across all categories."""
  selected_ids = st.session_state.get("selected_fixes") or st.session_state.get("selected_action_recs")
  if not selected_ids:
    selected_ids = {
      "elec_led", "elec_sensor", "solar_pv",
      "fuel_insulate", "fuel_boiler_tune",
      "trans_route", "waste_segregation"
    }
  all_fixes = []
  for cat, fixes in CATEGORY_FIXES.items():
    for fix in fixes:
      if fix["id"] in selected_ids:
        fix_copy = fix.copy()
        fix_copy["category"] = cat
        all_fixes.append(fix_copy)
  return all_fixes

def render_action_plan_view():
  user = st.session_state.get("current_user", {})
  inputs = st.session_state.get("form_inputs", {})
  business_name = inputs.get("business_name", user.get("company_name", user.get("company", "Your Business")))

  # Data guard: auto-calculate emissions if missing from inputs or database
  results = st.session_state.get("emissions_results")
  if not results:
    if inputs and any(v for k, v in inputs.items() if isinstance(v, (int, float)) and v > 0):
      from components.calculations import calculate_detailed_emissions
      results = calculate_detailed_emissions(inputs)
      st.session_state["emissions_results"] = results
    else:
      email = user.get("email", "")
      if email:
        from database.db_manager import get_latest_emissions
        from components.calculations import calculate_detailed_emissions
        db_data = get_latest_emissions(email)
        if db_data:
          results = calculate_detailed_emissions(db_data)
          st.session_state["form_inputs"] = dict(db_data)
          st.session_state["emissions_results"] = results

  sim_outcomes = st.session_state.get("simulated_outcomes", {})
  co2_t = results.get("total_co2", 0.0) if results else 0.0
  cost_t = results.get("total_cost", 0.0) if results else 0.0
  co2_saved = sim_outcomes.get("co2_saved", round(co2_t * 0.26, 1) if co2_t > 0 else 28.5)
  cost_saved = sim_outcomes.get("cost_saved", round(cost_t * 0.22, 0) if cost_t > 0 else 8400)
  co2_pct = sim_outcomes.get("co2_pct", 26.0)

  st.markdown(f"""
    <div style="margin-bottom: 20px;">
      <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #6B8E7D; font-weight: 700;">
        Implementation Roadmap
      </span>
      <h2 style="font-size: 1.8rem; font-weight: 800; color: #0F172A; margin: 4px 0 6px 0;">
        {business_name} Green Action Plan
      </h2>
      <p style="font-size: 0.95rem; color: #64748B;">
        A clear, staged roadmap designed for small business operations. Grouped into manageable execution phases.
      </p>
    </div>
  """, unsafe_allow_html=True)

  if not results or co2_t == 0.0:
    st.info("ℹ️ Baseline emissions data not yet recorded. Showing projected roadmap based on typical facility benchmarks. You can customize your facility inputs under **Business Profile & Setup**.")

  # Summary metric highlights
  c1, c2, c3 = st.columns(3)

  with c1:
    st.markdown(f"""
      <div class="clean-card" style="padding: 16px;">
        <div style="font-size: 0.8rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Total Carbon Cut Target</div>
        <div style="font-size: 1.6rem; font-weight: 800; color: #6B8E7D;">-{co2_saved} tonnes / yr</div>
        <div style="font-size: 0.8rem; color: #047857;">{co2_pct}% overall reduction</div>
      </div>
    """, unsafe_allow_html=True)
  with c2:
    st.markdown(f"""
      <div class="clean-card" style="padding: 16px;">
        <div style="font-size: 0.8rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Annual Cost Recovery</div>
        <div style="font-size: 1.6rem; font-weight: 800; color: #0F172A;">₹{cost_saved:,.0f} / yr</div>
        <div style="font-size: 0.8rem; color: #64748B;">Direct utility & fuel savings</div>
      </div>
    """, unsafe_allow_html=True)
  with c3:
    fixes = get_selected_fix_objects()
    st.markdown(f"""
      <div class="clean-card" style="padding: 16px;">
        <div style="font-size: 0.8rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Active Initiatives</div>
        <div style="font-size: 1.6rem; font-weight: 800; color: #2563EB;">{len(fixes)} Projects</div>
        <div style="font-size: 0.8rem; color: #64748B;">Selected across 3 phases</div>
      </div>
    """, unsafe_allow_html=True)

  st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

  # 3 Staged Groups
  phases = [
    {
      "key": "quick_win",
      "title": "⚡ Stage 1: Quick Wins (0–3 Months)",
      "badge": "IMMEDIATE ROI",
      "badge_color": "#ECFDF5",
      "text_color": "#065F46",
      "desc": "Low-to-no CapEx tweaks, employee behavioral changes, sensor controls, and pipe insulation."
    },
    {
      "key": "mid_term",
      "title": "Stage 2: Mid-Term Optimization (3–12 Months)",
      "badge": "HIGH IMPACT",
      "badge_color": "#FEF3C7",
      "text_color": "#92400E",
      "desc": "Equipment retrofits, route optimization software, motor drives, and recycling partnerships."
    },
    {
      "key": "long_term",
      "title": "🌳 Stage 3: Long-Term Transformation (1+ Years)",
      "badge": "FUTURE-PROOF",
      "badge_color": "#EFF6FF",
      "text_color": "#1E40AF",
      "desc": "Commercial solar PV installations, commercial heat pump electrification, and electric fleet vehicles."
    }
  ]

  for phase in phases:
    phase_fixes = [f for f in fixes if f.get("timeframe") == phase["key"]]
    
    st.markdown(f"""
      <div style="background: white; border: 1px solid #E2E8F0; border-radius: 14px; padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
          <h3 style="font-size: 1.15rem; font-weight: 800; color: #0F172A; margin: 0;">{phase['title']}</h3>
          <span style="background: {phase['badge_color']}; color: {phase['text_color']}; font-size: 0.75rem; font-weight: 700; padding: 3px 8px; border-radius: 6px;">
            {phase['badge']}
          </span>
        </div>
        <p style="font-size: 0.85rem; color: #64748B; margin-bottom: 14px;">{phase['desc']}</p>
    """, unsafe_allow_html=True)

    if not phase_fixes:
      st.info("No initiatives currently selected for this timeframe. You can toggle them in the Recommendations tab.")
    else:
      for fix in phase_fixes:
        cat_meta = CATEGORY_METADATA.get(fix["category"], {})
        st.markdown(f"""
          <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 14px 16px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
              <div>
                <span style="font-size: 0.78rem; font-weight: 700; color: #475569;">
                  {cat_meta.get('icon', '🌱')} {cat_meta.get('label', 'General')} &bull; {fix['difficulty']} Effort
                </span>
                <div style="font-weight: 700; color: #0F172A; font-size: 1rem; margin-top: 2px;">
                  {fix['name']}
                </div>
                <div style="font-size: 0.85rem; color: #64748B; margin-top: 4px;">
                  {fix['description']}
                </div>
              </div>
              <div style="text-align: right; min-width: 140px;">
                <div style="font-size: 0.88rem; font-weight: 700; color: #6B8E7D;">
                  ~{fix['co2_saved_pct']}% CO₂ Cut
                </div>
                <div style="font-size: 0.8rem; color: #64748B;">
                  ROI: {fix['payback_time']}
                </div>
              </div>
            </div>
          </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

  st.markdown("<hr style='margin: 30px 0 20px 0; border: none; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)

  # Navigation buttons
  col_nav_left, col_nav_right = st.columns([1, 1])
  with col_nav_left:
    if st.button("← Back to Simulator", key="plan_back"):
      st.session_state["nav_section"] = "simulator"
      st.session_state["current_step"] = 9
      st.rerun()

  with col_nav_right:
    if st.button("Proceed to Export & Share →", type="primary", key="plan_next", use_container_width=True):
      st.session_state["nav_section"] = "export"
      st.session_state["current_step"] = 13
      st.rerun()

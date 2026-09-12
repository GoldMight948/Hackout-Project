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
  selected_ids = st.session_state.get("selected_fixes", set())
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
  business_name = st.session_state.get("form_inputs", {}).get("business_name", "Your Business")
  sim_outcomes = st.session_state.get("simulated_outcomes", {})

  st.markdown(f"""
    <div style="margin-bottom: 20px;">
      <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #059669; font-weight: 700;">
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

  # Summary metric highlights
  c1, c2, c3 = st.columns(3)
  co2_saved = sim_outcomes.get("co2_saved", 28.5)
  cost_saved = sim_outcomes.get("cost_saved", 8400)
  co2_pct = sim_outcomes.get("co2_pct", 26.0)

  with c1:
    st.markdown(f"""
      <div class="clean-card" style="padding: 16px;">
        <div style="font-size: 0.8rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Total Carbon Cut Target</div>
        <div style="font-size: 1.6rem; font-weight: 800; color: #059669;">-{co2_saved} tonnes / yr</div>
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
                <div style="font-size: 0.88rem; font-weight: 700; color: #059669;">
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
      st.session_state["current_step"] = 5
      st.rerun()

  with col_nav_right:
    if st.button("Proceed to Export & Share →", type="primary", key="plan_next", use_container_width=True):
      st.session_state["current_step"] = 7
      st.rerun()

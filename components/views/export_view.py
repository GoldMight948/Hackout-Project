"""
Step 7: Export and Share View.
Provides:
- CSV Action Plan Download
- Printable Executive Summary for board / stakeholders
- Shareable copy-to-clipboard text
- Option to reset or perform new assessment
"""

import streamlit as st
import pandas as pd
from components.views.action_plan_view import get_selected_fix_objects
from components.calculations import CATEGORY_METADATA

def render_export_view():
  inputs = st.session_state.get("form_inputs", {})
  user = st.session_state.get("current_user", {})
  business_name = inputs.get("business_name", user.get("company_name", user.get("company", "Your Enterprise")))
  user_lead = user.get("owner_name", user.get("name", "Management"))

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

  results = results or {}
  sim_outcomes = st.session_state.get("simulated_outcomes", {})

  st.markdown(f"""
    <div style="margin-bottom: 20px;">
      <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #6B8E7D; font-weight: 700;">
        Export & Share
      </span>
      <h2 style="font-size: 1.8rem; font-weight: 800; color: #0F172A; margin: 4px 0 6px 0;">
        Download Your Green Action Roadmap
      </h2>
      <p style="font-size: 0.95rem; color: #64748B;">
        Share your tailored carbon reduction strategy with company leadership, investors, or operational teams.
      </p>
    </div>
  """, unsafe_allow_html=True)

  # Prepare DataFrame for CSV Export
  fixes = get_selected_fix_objects()
  data_rows = []
  for f in fixes:
    cat_meta = CATEGORY_METADATA.get(f.get("category"), {})
    data_rows.append({
      "Business Name": business_name,
      "Execution Stage": f.get("timeframe_label"),
      "Category": cat_meta.get("label", f.get("category")),
      "Initiative Name": f.get("name"),
      "Description": f.get("description"),
      "CO2 Reduction (%)": f.get("co2_saved_pct"),
      "Estimated Cost": f.get("cost_estimate"),
      "Difficulty": f.get("difficulty"),
      "Payback Period": f.get("payback_time"),
    })

  df = pd.DataFrame(data_rows)
  csv_bytes = df.to_csv(index=False).encode('utf-8')

  col_csv, col_summary = st.columns([1, 1], gap="large")

  with col_csv:
    st.markdown("""
      <div class="clean-card">
        <div style="font-size: 1.8rem; margin-bottom: 8px;"></div>
        <h3 style="font-size: 1.2rem; font-weight: 800; color: #0F172A; margin-bottom: 8px;">
          Download Action Plan as CSV
        </h3>
        <p style="font-size: 0.88rem; color: #64748B; margin-bottom: 16px;">
          Compatible with Microsoft Excel, Google Sheets, and project management tools (Asana, Jira, Notion).
        </p>
    """, unsafe_allow_html=True)

    st.download_button(
      label="📄 Download Action Plan (.CSV)",
      data=csv_bytes,
      file_name=f"{business_name.lower().replace(' ', '_')}_green_action_plan.csv",
      mime="text/csv",
      type="primary",
      use_container_width=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
      <div class="clean-card" style="margin-top: 16px;">
        <div style="font-size: 1.8rem; margin-bottom: 8px;"></div>
        <h3 style="font-size: 1.2rem; font-weight: 800; color: #0F172A; margin-bottom: 8px;">
          Copyable Executive Brief
        </h3>
        <p style="font-size: 0.88rem; color: #64748B; margin-bottom: 12px;">
          Quick summary text ready to paste into team Slack or board emails:
        </p>
    """, unsafe_allow_html=True)

    co2_t = results.get('total_co2', 0.0)
    cost_total = results.get('total_cost', 0.0)
    co2_s = sim_outcomes.get('co2_saved', round(co2_t * 0.26, 1) if co2_t > 0 else 28.5)
    cost_s = sim_outcomes.get('cost_saved', round(cost_total * 0.22, 0) if cost_total > 0 else 8400.0)
    top_cat = results.get('top_leak', {}).get('label', 'Electricity & Thermal Utilities')
    
    brief_text = (
      f"🌿 {business_name} Sustainability Brief:\n"
      f"• Baseline Footprint: {co2_t} tonnes CO₂e/yr\n"
      f"• Primary Leak Identified: #{results.get('top_leak', {}).get('rank', 1)} {top_cat}\n"
      f"• Projected Carbon Cut: -{co2_s} tonnes/yr ({sim_outcomes.get('co2_pct', 26.0)}% cut)\n"
      f"• Projected Cost Recovery: ₹{cost_s:,.0f} saved annually\n"
      f"• Active Initiatives Planned: {len(fixes)} projects across Quick Wins, Mid-Term, and Long-Term."
    )
    st.code(brief_text, language="text")
    st.markdown("</div>", unsafe_allow_html=True)

  with col_summary:
    st.markdown("""
      <div class="clean-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <h3 style="font-size: 1.15rem; font-weight: 800; color: #0F172A; margin: 0;">
            Printable Executive Summary
          </h3>
          <span style="font-size: 0.75rem; background: #ECFDF5; color: #047857; font-weight: 700; padding: 2px 8px; border-radius: 4px;">
            PDF / PRINT READY
          </span>
        </div>
        <p style="font-size: 0.85rem; color: #64748B; margin-bottom: 14px;">
          Use your browser's Print command (<strong>Ctrl+P</strong> or <strong>Cmd+P</strong>) to save as a clean PDF.
        </p>
        <div style="border: 1px solid #CBD5E1; border-radius: 8px; padding: 18px; background: #FFFFFF; font-size: 0.88rem;">
          <div style="border-bottom: 2px solid #5A8766; padding-bottom: 8px; margin-bottom: 12px;">
            <h4 style="margin: 0; color: #065F46; font-size: 1.1rem;">EMISSION LEAK DETECTOR & GREEN ACTION PLAN</h4>
            <div style="color: #64748B; font-size: 0.8rem;">Prepared for: <strong>""" + business_name + """</strong> &bull; Lead: """ + user_lead + """</div>
          </div>
          <div style="margin-bottom: 10px;">
            <strong>Key Diagnoses:</strong>
            <ul style="margin: 4px 0 10px 18px; padding: 0;">
              <li>Total Baseline: <strong>""" + str(co2_t) + """ tonnes CO₂e</strong> (₹""" + f"{results.get('total_cost', 0):,.0f}" + """/yr)</li>
              <li>Primary Hotspot: <strong>""" + top_cat + """</strong> (""" + str(results.get('top_leak', {}).get('share_pct', 0)) + """% of footprint)</li>
              <li>Target Reduction: <strong>-""" + str(co2_s) + """ tonnes</strong> with estimated savings of <strong>₹""" + f"{cost_s:,.0f}" + """/yr</strong></li>
            </ul>
          </div>
          <div>
            <strong>Selected Action Plan:</strong>
            <ol style="margin: 4px 0 0 18px; padding: 0;">
    """, unsafe_allow_html=True)

    if not fixes:
      st.markdown("<li>No active initiatives selected yet.</li>", unsafe_allow_html=True)
    else:
      for fix in fixes[:5]:
        st.markdown(f"<li><strong>{fix['name']}</strong> — {fix.get('timeframe_label', 'Active')} (Payback: {fix.get('payback_time', 'N/A')})</li>", unsafe_allow_html=True)

    st.markdown("""
            </ol>
          </div>
        </div>
      </div>
    """, unsafe_allow_html=True)

  st.markdown("<hr style='margin: 30px 0 20px 0; border: none; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)

  # Navigation buttons
  col_nav_left, col_nav_right = st.columns([1, 1])
  with col_nav_left:
    if st.button("← Back to Action Plan", key="export_back"):
      st.session_state["nav_section"] = "action_plan"
      st.session_state["current_step"] = 11
      st.rerun()

  with col_nav_right:
    if st.button("Start New Assessment / Go to Setup", key="export_restart", use_container_width=True):
      st.session_state["nav_section"] = "setup"
      st.session_state["current_step"] = 3
      st.rerun()

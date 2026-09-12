"""
Step 8: AI Recommendation Engine View.
Identifies the highest emission hotspot and serves 10 prioritized decarbonization interventions.
Features modern expandable cards with CO2 saved, capital investment, expected ROI,
payback periods, difficulty ratings, circular benefits, and government incentives.
"""

import streamlit as st
from components.data_presets import AI_RECOMMENDATIONS
from components.icons import feather_icon, render_icon_heading, COLOR_WARNING, COLOR_SUCCESS, COLOR_NEUTRAL, COLOR_AMBER, COLOR_SECONDARY, COLOR_INFO

def render_recommendations_view():
    """Renders Step 8 AI Decarbonization Recommendations."""
    res = st.session_state.get("emissions_results")
    if not res:
        st.warning("Please complete Step 3 Setup or load a demo dataset.")
        return

    top_leak = res.get("top_leak")
    highest_category = top_leak["category"] if top_leak else "Electricity"

    if "selected_action_recs" not in st.session_state:
        st.session_state["selected_action_recs"] = {"rec_led", "rec_insulation", "rec_route_opt", "rec_water_recycle"}

    st.markdown("""
        <div style="margin-bottom: 8px;">
            <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #10B981; font-weight: 700;">
                Step 8 — AI Recommendation Engine
            </span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(render_icon_heading(
        "lightbulb",
        "Actionable Decarbonization & Circular Interventions",
        level="h2",
        color=COLOR_AMBER,
        subtitle=f"Targeting your primary operational leak hotspot: {highest_category} ({top_leak['share_pct'] if top_leak else 0}% of footprint)."
    ), unsafe_allow_html=True)

    # Filter & Search Controls
    c_search, c_filter_cat, c_filter_diff = st.columns([1.5, 1, 1], gap="medium")
    with c_search:
        search_query = st.text_input("Search Interventions", placeholder="e.g. Solar, LED, Insulation, VFD, Water")
    with c_filter_cat:
        cat_filter = st.selectbox("Filter Category", ["All Categories", "Electricity", "Fuel", "Transport", "Water", "Manufacturing"])
    with c_filter_diff:
        diff_filter = st.selectbox("Effort Level", ["All Difficulties", "Easy", "Medium", "Hard"])

    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    # Filter recommendations
    filtered_recs = []
    for rec in AI_RECOMMENDATIONS:
        if search_query.lower() and (search_query.lower() not in rec["title"].lower() and search_query.lower() not in rec["description"].lower()):
            continue
        if cat_filter != "All Categories" and rec["category"].lower() != cat_filter.lower():
            continue
        if diff_filter != "All Difficulties" and rec["difficulty"].lower() != diff_filter.lower():
            continue
        filtered_recs.append(rec)

    st.markdown(f"##### Displaying {len(filtered_recs)} Actionable AI Recommendations:")

    cat_icon_map = {
        "electricity": "zap",
        "fuel": "droplet",
        "transport": "truck",
        "water": "droplet",
        "manufacturing": "settings"
    }

    for idx, rec in enumerate(filtered_recs):
        is_selected = rec["id"] in st.session_state["selected_action_recs"]
        diff_badge = "badge-low" if rec["difficulty"] == "Easy" else ("badge-medium" if rec["difficulty"] == "Medium" else "badge-critical")
        rec_f_icon = cat_icon_map.get(rec["category"].lower(), "lightbulb")
        card_icon = feather_icon(rec_f_icon, color="#10B981", size=16, margin_right=5)
        
        with st.container():
            st.markdown(f"""
                <div class="saas-card" style="margin-bottom: 14px; border-left: 5px solid {'#10B981' if rec['difficulty'] == 'Easy' else ('#F59E0B' if rec['difficulty'] == 'Medium' else '#EF4444')};">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
                        <div>
                            <span style="font-size: 0.78rem; font-weight: 700; color: #10B981; text-transform: uppercase; display: flex; align-items: center;">
                                {card_icon} {rec['category']} &bull; Impact: {rec['impact_level']}
                            </span>
                            <div style="font-size: 1.15rem; font-weight: 800; margin-top: 4px; color: var(--text-primary);">
                                {rec['title']}
                            </div>
                        </div>
                        <div style="display: flex; gap: 8px; align-items: center;">
                            <span class="{diff_badge}">{rec['difficulty']} Effort</span>
                        </div>
                    </div>
                    <p style="font-size: 0.9rem; color: var(--text-secondary); margin: 8px 0 14px 0; line-height: 1.5;">
                        {rec['description']}
                    </p>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 12px; padding: 12px; background: var(--bg-subtle); border-radius: 10px; border: 1px solid var(--border-color); font-size: 0.85rem;">
                        <div>
                            <span style="color: var(--text-muted); display: flex; align-items: center;">{feather_icon('leaf', color=COLOR_SUCCESS, size=13, margin_right=4)} CO₂ Saved:</span>
                            <strong style="color: #10B981; font-size: 0.95rem;">-{rec['co2_saved_t']} t/yr ({rec['co2_saved_pct']}%)</strong>
                        </div>
                        <div>
                            <span style="color: var(--text-muted); display: flex; align-items: center;">{feather_icon('dollar-sign', color=COLOR_NEUTRAL, size=13, margin_right=4)} Est. Investment:</span>
                            <strong>{rec['cost_estimate']}</strong>
                        </div>
                        <div>
                            <span style="color: var(--text-muted); display: flex; align-items: center;">{feather_icon('trending-up', color=COLOR_SUCCESS, size=13, margin_right=4)} Expected ROI:</span>
                            <strong style="color: #2563EB;">+{rec['expected_roi']}%</strong>
                        </div>
                        <div>
                            <span style="color: var(--text-muted); display: flex; align-items: center;">{feather_icon('calendar', color=COLOR_SECONDARY, size=13, margin_right=4)} Payback Period:</span>
                            <strong style="color: #059669;">{rec['payback_time']}</strong>
                        </div>
                        <div>
                            <span style="color: var(--text-muted); display: flex; align-items: center;">{feather_icon('shield', color=COLOR_INFO, size=13, margin_right=4)} Credits Saved:</span>
                            <strong>+{rec['credits_saved']} credits</strong>
                        </div>
                    </div>
            """, unsafe_allow_html=True)

            with st.expander(f"📖 Detailed Engineering, Circular Benefits & Government Grants"):
                c_exp1, c_exp2 = st.columns(2)
                with c_exp1:
                    st.markdown(f"**♻️ Circular Economy Benefit:**")
                    st.write(rec["circular_benefit"])
                with c_exp2:
                    st.markdown(f"**🏛️ Government Incentives & Subsidies:**")
                    st.write(rec["govt_incentives"])

            # Checkbox to add to customized roadmap
            chk_val = st.checkbox(
                f"Include '{rec['title']}' in My Formal Decarbonization Action Plan",
                value=is_selected,
                key=f"chk_rec_{rec['id']}"
            )
            if chk_val:
                st.session_state["selected_action_recs"].add(rec["id"])
            else:
                st.session_state["selected_action_recs"].discard(rec["id"])

            st.markdown("</div>", unsafe_allow_html=True)

    # Navigation
    st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)
    c_b1, c_b2 = st.columns([1, 1])
    with c_b1:
        if st.button("← Back to Carbon Credits", key="recom_back_credits"):
            st.session_state["current_step"] = 7
            st.session_state["nav_section"] = "carbon_credits"
            st.rerun()
    with c_b2:
        if st.button("Test These Changes in Before vs After Simulator →", type="primary", key="recom_next_sim", use_container_width=True):
            st.session_state["current_step"] = 9
            st.session_state["nav_section"] = "simulator"
            st.rerun()

"""
Step 8: AI Recommendation Engine View.
Identifies the highest emission hotspot and serves 10 prioritized decarbonization interventions.
Features modern expandable cards with CO2 saved, capital investment, expected ROI,
payback periods, difficulty ratings, circular benefits, and government incentives.
"""

import streamlit as st
from components.data_presets import AI_RECOMMENDATIONS
from components.calculations import generate_hotspot_recommendations
from components.icons import feather_icon, render_icon_heading, COLOR_WARNING, COLOR_SUCCESS, COLOR_NEUTRAL, COLOR_AMBER, COLOR_SECONDARY, COLOR_INFO

def render_recommendations_view():
    """Renders Step 8 AI Decarbonization Recommendations based on actual emission leak hotspots."""
    res = st.session_state.get("emissions_results")
    if not res:
        st.warning("Please complete Step 3 Setup or load a demo dataset.")
        return

    user = st.session_state.get("current_user", {})
    top_leak = res.get("top_leak")
    highest_source = top_leak["source"] if top_leak else "Operations"
    highest_category = top_leak["category"] if top_leak else "Electricity"
    highest_co2 = top_leak["current_co2"] if top_leak else 0.0
    highest_share = top_leak["share_pct"] if top_leak else 0.0

    # Dynamically generate recommendations prioritized by the business's actual leak hotspots
    dynamic_recs = generate_hotspot_recommendations(res, user)
    master_recs = dynamic_recs if dynamic_recs else AI_RECOMMENDATIONS

    if "selected_action_recs" not in st.session_state:
        st.session_state["selected_action_recs"] = {r["id"] for r in master_recs[:3]}

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
        subtitle="Browse proven decarbonization interventions with verified ROI and circular benefits. Once operational data is entered, solutions will dynamically re-order around your facility's biggest carbon leaks." if highest_co2 == 0.0 else f"Directly targeting your facility's primary leak hotspot: <strong>{highest_source}</strong> ({highest_co2:,.1f} t CO₂e, {highest_share}% of footprint)."
    ), unsafe_allow_html=True)

    # Hotspot Context Alert Banner
    if highest_co2 > 0:
        st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 14px 18px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
                <div style="display: flex; align-items: center;">
                    {feather_icon('target', color='#10B981', size=22, margin_right=10)}
                    <div>
                        <div style="font-size: 0.95rem; font-weight: 800; color: #065F46;">
                            🎯 Hotspot-Driven Recommendations Active: Prioritizing Solutions for #{top_leak['rank'] if top_leak else 1} {highest_source}
                        </div>
                        <div style="font-size: 0.84rem; color: #047857; margin-top: 2px;">
                            Interventions below are mathematically calibrated to your measured consumption volume ({highest_co2:,.1f} t CO₂e) and current carbon credit quota balance.
                        </div>
                    </div>
                </div>
                <span class="badge-low" style="padding: 6px 12px; font-size: 0.8rem;">
                    🟢 100% TAILORED TO YOUR DATA
                </span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 14px 18px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
                <div style="display: flex; align-items: center;">
                    {feather_icon('compass', color='#10B981', size=22, margin_right=10)}
                    <div>
                        <div style="font-size: 0.95rem; font-weight: 800; color: #065F46;">
                            🌱 Decarbonization Catalog Ready
                        </div>
                        <div style="font-size: 0.84rem; color: #047857; margin-top: 2px;">
                            Explore high-ROI engineering solutions and circular loops. Once you enter facility data or log shifts, this engine will automatically calibrate payback calculations to your measured emissions.
                        </div>
                    </div>
                </div>
                <span class="badge-low" style="padding: 6px 12px; font-size: 0.8rem;">
                    READY FOR DATA
                </span>
            </div>
        """, unsafe_allow_html=True)

    # Filter & Search Controls
    c_search, c_filter_hot, c_filter_diff = st.columns([1.5, 1.2, 1], gap="medium")
    with c_search:
        search_query = st.text_input("Search Interventions", placeholder="e.g. Solar, Economizer, Insulation, Regrind, VFD")
    with c_filter_hot:
        hotspot_filter = st.selectbox("Filter by Target", ["All Recommendations", "🎯 Hotspot #1 Fixes", "🎯 Top 3 Hotspots", "High ROI (>100%)"])
    with c_filter_diff:
        diff_filter = st.selectbox("Effort Level", ["All Difficulties", "Easy", "Medium", "Hard"])

    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    # Filter recommendations
    filtered_recs = []
    for rec in master_recs:
        if search_query.lower() and (search_query.lower() not in rec["title"].lower() and search_query.lower() not in rec["description"].lower()):
            continue
        if hotspot_filter == "🎯 Hotspot #1 Fixes" and rec.get("targeted_hotspot_rank") != 1:
            continue
        if hotspot_filter == "🎯 Top 3 Hotspots" and rec.get("targeted_hotspot_rank", 99) > 3:
            continue
        if hotspot_filter == "High ROI (>100%)" and rec.get("expected_roi", 0.0) < 100.0:
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
        
        hotspot_badge = f"<span style='font-size: 0.76rem; background: rgba(16,185,129,0.15); color: #047857; padding: 3px 8px; border-radius: 6px; font-weight: 800; margin-right: 8px;'>{rec.get('hotspot_priority_tag', '')}</span>" if rec.get("hotspot_priority_tag") else ""
        hotspot_sub = f"<div style='font-size: 0.82rem; color: var(--text-muted); margin-top: 2px;'>{rec.get('targeted_hotspot_label', '')} ({rec.get('targeted_hotspot_co2', 0):,.1f} t CO₂e)</div>" if rec.get("targeted_hotspot_label") else ""
        
        with st.container():
            st.markdown(f"""
                <div class="saas-card" style="margin-bottom: 14px; border-left: 5px solid {'#10B981' if rec.get('targeted_hotspot_rank', 99) == 1 else ('#F59E0B' if rec.get('targeted_hotspot_rank', 99) == 2 else ('#3B82F6' if rec.get('targeted_hotspot_rank', 99) == 3 else '#64748B'))};">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
                        <div>
                            <div style="display: flex; align-items: center; flex-wrap: wrap; gap: 6px;">
                                {hotspot_badge}
                                <span style="font-size: 0.78rem; font-weight: 700; color: #10B981; text-transform: uppercase; display: flex; align-items: center;">
                                    {card_icon} {rec['category']} &bull; Impact: {rec['impact_level']}
                                </span>
                            </div>
                            <div style="font-size: 1.15rem; font-weight: 800; margin-top: 4px; color: var(--text-primary);">
                                {rec['title']}
                            </div>
                            {hotspot_sub}
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
                            <span style="color: var(--text-muted); display: flex; align-items: center;">{feather_icon('dollar-sign', color=COLOR_SUCCESS, size=13, margin_right=4)} Annual Savings:</span>
                            <strong style="color: #059669; font-size: 0.95rem;">+₹{rec.get('annual_savings_inr', 0):,.0f}/yr</strong>
                        </div>
                        <div>
                            <span style="color: var(--text-muted); display: flex; align-items: center;">{feather_icon('briefcase', color=COLOR_NEUTRAL, size=13, margin_right=4)} Est. Investment:</span>
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

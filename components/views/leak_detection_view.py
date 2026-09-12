"""
Step 6: Emission Leak Detection & Hotspot Diagnostics View.
Ranks the Top 10 operational leak points across CO2 volume, cost impact, and severity score.
Displays colored priority badges, potential savings, and direct drill-downs into targeted fixes.
"""

import streamlit as st
import pandas as pd
from components.icons import feather_icon, render_icon_heading, COLOR_WARNING, COLOR_SUCCESS, COLOR_NEUTRAL

def render_leak_detection_view():
    """Renders Step 6 Top 10 Leak Points ranking table and diagnostic cards."""
    res = st.session_state.get("emissions_results")
    if not res:
        st.warning("Please enter data in Step 3 or load a demo dataset.")
        return

    top_10 = res.get("top_10_leaks", [])

    st.markdown("""
        <div style="margin-bottom: 8px;">
            <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #10B981; font-weight: 700;">
                Step 6 — Automated Operational Leak Detection
            </span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(render_icon_heading(
        "alert-triangle",
        "Top 10 Emission Hotspots & Financial Waste Points",
        level="h2",
        color=COLOR_WARNING,
        subtitle="Our multi-factor diagnostic algorithm ranked all operational activities by greenhouse gas volume, annual dollar spend, and urgency index."
    ), unsafe_allow_html=True)

    # Top Leak Diagnosis Alert Banner
    if top_10 and res.get("total_co2", 0.0) > 0 and top_10[0]["current_co2"] > 0:
        worst_leak = top_10[0]
        banner_icon = feather_icon("alert-triangle", color="#DC2626", size=32, margin_right=14)
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(220, 38, 38, 0.1) 0%, rgba(249, 115, 22, 0.08) 100%); border: 1px solid #FCA5A5; border-radius: 14px; padding: 20px 24px; margin-bottom: 24px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px;">
                <div style="display: flex; align-items: center;">
                    {banner_icon}
                    <div>
                        <div style="font-weight: 800; font-size: 1.15rem; color: #991B1B;">
                            #1 Primary Leak Hotspot: {worst_leak['source']}
                        </div>
                        <div style="font-size: 0.9rem; color: #7F1D1D; margin-top: 4px;">
                            Accounts for <strong>{worst_leak['current_co2']:,.1f} tonnes CO₂e</strong> ({worst_leak['share_pct']}% of total footprint) and ~<strong>₹{worst_leak['cost_impact']:,.0f}/yr</strong> in utility/operational spend.
                        </div>
                    </div>
                </div>
                <span class="badge-critical" style="font-size: 0.85rem; padding: 6px 14px;">
                    {worst_leak['priority']}
                </span>
            </div>
        """, unsafe_allow_html=True)
    else:
        clean_icon = feather_icon("check-circle", color="#10B981", size=32, margin_right=14)
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.08) 100%); border: 1px solid #6EE7B7; border-radius: 14px; padding: 20px 24px; margin-bottom: 24px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px;">
                <div style="display: flex; align-items: center;">
                    {clean_icon}
                    <div>
                        <div style="font-weight: 800; font-size: 1.15rem; color: #065F46;">
                            🌱 Zero Active Emission Leaks Detected
                        </div>
                        <div style="font-size: 0.9rem; color: #047857; margin-top: 4px;">
                            Your facility emissions are currently at <strong>0.0 tonnes CO₂e</strong>. Log operational shifts or input utility data in Setup to run automated hotspot diagnostics.
                        </div>
                    </div>
                </div>
                <span class="badge-low" style="font-size: 0.85rem; padding: 6px 14px;">
                    100% DECARBONIZED / ZERO BASELINE
                </span>
            </div>
        """, unsafe_allow_html=True)

    # Top 10 Table Header / Filter
    matrix_icon = feather_icon("list", color=COLOR_NEUTRAL, size=18, margin_right=6)
    st.markdown(f"""
        <div class="saas-card">
            <div class="saas-card-title" style="margin-bottom: 6px; display: flex; align-items: center;">{matrix_icon} Ranked Leak Points Matrix (1–10)</div>
            <div class="saas-card-subtitle" style="margin-bottom: 16px;">
                Click any hotspot below to inspect engineering solutions, circular substitutions, and payback calculations:
            </div>
    """, unsafe_allow_html=True)

    for leak in top_10:
        leak_icon = feather_icon(leak.get("feather_icon", "alert-triangle"), color=COLOR_WARNING if leak['rank'] <= 3 else COLOR_NEUTRAL, size=18, margin_right=6)
        with st.container():
            st.markdown(f"""
                <div style="background: var(--bg-subtle); border: 1px solid var(--border-color); border-radius: 12px; padding: 16px 20px; margin-bottom: 12px; transition: all 0.2s ease;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
                        <div style="display: flex; align-items: center; gap: 14px;">
                            <div style="width: 36px; height: 36px; border-radius: 10px; background: {'rgba(220, 38, 38, 0.15)' if leak['rank'] <= 3 else 'var(--bg-card)'}; color: {'#DC2626' if leak['rank'] <= 3 else 'var(--text-primary)'}; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.05rem; border: 1px solid var(--border-color);">
                                #{leak['rank']}
                            </div>
                            <div>
                                <div style="font-weight: 700; font-size: 1.05rem; display: flex; align-items: center;">
                                    {leak_icon} {leak['source']}
                                </div>
                                <div style="font-size: 0.82rem; color: var(--text-muted); margin-top: 2px;">
                                    Category: <strong>{leak['category']}</strong> &bull; Share: <strong>{leak['share_pct']}%</strong> &bull; Current Activity: {leak['activity_val']:,.0f} {leak['unit']}
                                </div>
                            </div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span class="{leak['badge_class']}">
                                {leak['priority']}
                            </span>
                            <span style="background: var(--bg-card); border: 1px solid var(--border-color); padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.8rem;">
                                Impact: {leak['impact_score']}/100
                            </span>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--border-color); font-size: 0.86rem;">
                        <div>
                            <span style="color: var(--text-muted);">Current Footprint:</span><br/>
                            <strong style="color: #DC2626; font-size: 0.95rem;">{leak['current_co2']:,.1f} t CO₂</strong>
                        </div>
                        <div>
                            <span style="color: var(--text-muted);">Annual Financial Cost:</span><br/>
                            <strong>₹{leak['cost_impact']:,.0f} / yr</strong>
                        </div>
                        <div>
                            <span style="color: var(--text-muted);">Potential Carbon Cut:</span><br/>
                            <strong style="color: #10B981; font-size: 0.95rem;">-{leak['potential_saving_co2']:,.1f} t ({leak['potential_saving_pct']}%)</strong>
                        </div>
                        <div>
                            <span style="color: var(--text-muted);">Est. Cost Recovery:</span><br/>
                            <strong style="color: #059669;">₹{leak['potential_saving_cost']:,.0f} / yr</strong>
                        </div>
                        <div>
                            <span style="color: var(--text-muted);">Diagnostic Status:</span><br/>
                            <strong>{leak['status']}</strong>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            c_btn_l, c_btn_r = st.columns([1.5, 1])
            with c_btn_l:
                if st.button(f"🔍 Inspect AI Fixes for #{leak['rank']} {leak['source']}", key=f"fix_btn_{leak['rank']}", use_container_width=True):
                    st.session_state["selected_leak_category"] = leak["category"]
                    st.session_state["current_step"] = 8
                    st.session_state["nav_section"] = "recommendations"
                    st.rerun()
            with c_btn_r:
                if st.button(f"♻️ Circular Alternative →", key=f"circ_btn_{leak['rank']}", use_container_width=True):
                    st.session_state["current_step"] = 10
                    st.session_state["nav_section"] = "circular"
                    st.rerun()

            st.markdown("<div style='margin-bottom: 6px;'></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Navigation
    st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)
    c_n1, c_n2 = st.columns([1, 1])
    with c_n1:
        if st.button("← Back to Dashboard", key="leak_back_dash"):
            st.session_state["current_step"] = 5
            st.session_state["nav_section"] = "dashboard"
            st.rerun()
    with c_n2:
        if st.button("Proceed to Carbon Credit Analysis →", type="primary", key="leak_next_credits", use_container_width=True):
            st.session_state["current_step"] = 7
            st.session_state["nav_section"] = "carbon_credits"
            st.rerun()

"""
Step 10: Circular Economy Alternatives View.
Implements the 4R Framework (Reuse, Recycle, Recover, Replace) across industrial waste streams:
Plastics, Organics, Metals, and Water Effluent.
Connects businesses with circular supplier loops, cost savings, and verified carbon abatement.
"""

import streamlit as st
from components.data_presets import CIRCULAR_ALTERNATIVES
from components.icons import feather_icon, render_icon_heading, COLOR_SUCCESS, COLOR_PRIMARY, COLOR_WARNING, COLOR_INFO, COLOR_NEUTRAL

def render_circular_view():
    """Renders Step 10 Circular Alternatives Matrix."""
    st.markdown("""
        <div style="margin-bottom: 8px;">
            <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #10B981; font-weight: 700;">
                Step 10 — Circular Economy Transformation
            </span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(render_icon_heading(
        "refresh-cw",
        "4R Closed-Loop Resource & Waste Alternatives",
        level="h2",
        color=COLOR_SUCCESS,
        subtitle="Shift from linear 'take-make-waste' disposal to closed circular economy loops: <strong>Reuse</strong>, <strong>Recycle</strong>, <strong>Recover</strong>, and <strong>Replace</strong>."
    ), unsafe_allow_html=True)

    # Tab selection for waste streams
    tab_keys = list(CIRCULAR_ALTERNATIVES.keys())
    tab_titles = [f"{CIRCULAR_ALTERNATIVES[k]['title'].split()[0]} Waste" if "Effluent" not in CIRCULAR_ALTERNATIVES[k]['title'] else "Water Effluent" for k in tab_keys]
    
    tabs = st.tabs(tab_titles)

    for idx, key in enumerate(tab_keys):
        stream = CIRCULAR_ALTERNATIVES[key]
        f_icon = stream.get('feather_icon', 'box')
        with tabs[idx]:
            st.markdown(f"""
                <div class="saas-card" style="margin-bottom: 20px;">
                    <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 6px;">
                        <div style="background: rgba(16, 185, 129, 0.12); padding: 10px; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                            {feather_icon(f_icon, color=COLOR_SUCCESS, size=28, margin_right=0)}
                        </div>
                        <div>
                            <div style="font-size: 1.3rem; font-weight: 800; color: var(--text-primary);">{stream['title']}</div>
                            <div style="font-size: 0.85rem; color: #DC2626; font-weight: 600;">Baseline Challenge: {stream['current_impact']}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # 4R Grid
            r_cols = st.columns(4, gap="medium")
            four_rs = [
                ("1. REUSE", stream["reuse"], "#059669", "repeat"),
                ("2. RECYCLE", stream["recycle"], "#10B981", "refresh-cw"),
                ("3. RECOVER", stream["recover"], "#F59E0B", "zap"),
                ("4. REPLACE", stream["replace"], "#6366F1", "leaf")
            ]

            for r_idx, (r_label, r_data, r_color, r_icon) in enumerate(four_rs):
                with r_cols[r_idx]:
                    st.markdown(f"""
                        <div class="saas-card" style="height: 100%; border-top: 4px solid {r_color}; padding: 18px; display: flex; flex-direction: column; justify-content: space-between;">
                            <div>
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                    <span style="font-size: 0.78rem; font-weight: 800; color: {r_color}; letter-spacing: 0.06em; display: flex; align-items: center;">
                                        {feather_icon(r_icon, color=r_color, size=15)} <span>{r_label}</span>
                                    </span>
                                </div>
                                <div style="font-size: 1.05rem; font-weight: 700; margin-bottom: 6px; color: var(--text-primary);">
                                    {r_data['title']}
                                </div>
                                <div style="font-size: 0.8rem; color: #10B981; font-weight: 600; margin-bottom: 8px; display: flex; align-items: center;">
                                    {feather_icon('user-check', color='#10B981', size=14)} <span>Partner: {r_data['partner']}</span>
                                </div>
                                <p style="font-size: 0.84rem; color: var(--text-secondary); line-height: 1.45; margin-bottom: 12px;">
                                    {r_data['mechanism']}
                                </p>
                            </div>
                            <div style="background: var(--bg-subtle); padding: 10px; border-radius: 8px; border: 1px solid var(--border-color); font-size: 0.82rem; margin-top: 10px;">
                                <div>
                                    <span style="color: var(--text-muted);">Est. Cost Saving:</span> 
                                    <strong style="color: #059669;">{r_data['cost_saving']}</strong>
                                </div>
                                <div style="margin-top: 2px;">
                                    <span style="color: var(--text-muted);">Carbon Abatement:</span> 
                                    <strong style="color: #10B981;">{r_data['carbon_saving']}</strong>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

    # Interactive Circular Flow Example Callout
    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class="saas-card">
            <div class="saas-card-title">{feather_icon('refresh-cw', color=COLOR_SUCCESS, size=18)} Circular Economy Transformation Flow Example</div>
            <div class="saas-card-subtitle" style="margin-bottom: 14px;">
                How industrial waste is transformed from a disposal liability into a valuable operational asset:
            </div>
            <div style="display: flex; align-items: center; justify-content: space-around; flex-wrap: wrap; gap: 10px; text-align: center;">
                <div style="background: var(--bg-subtle); border: 1px solid var(--border-color); padding: 14px 18px; border-radius: 12px; min-width: 160px;">
                    <div style="margin-bottom: 6px;">{feather_icon('trash-2', color='#EF4444', size=28, margin_right=0)}</div>
                    <strong style="font-size: 0.95rem;">Industrial Waste</strong>
                    <div style="font-size: 0.8rem; color: #EF4444; margin-top: 2px;">Landfill Liability</div>
                </div>
                <div style="font-size: 1.4rem; color: var(--text-muted);">{feather_icon('arrow-right', color='var(--text-muted)', size=20, margin_right=0)}</div>
                <div style="background: var(--bg-subtle); border: 1px solid var(--border-color); padding: 14px 18px; border-radius: 12px; min-width: 160px;">
                    <div style="margin-bottom: 6px;">{feather_icon('refresh-cw', color='#3B82F6', size=28, margin_right=0)}</div>
                    <strong style="font-size: 0.95rem;">Circular Supplier</strong>
                    <div style="font-size: 0.8rem; color: #3B82F6; margin-top: 2px;">Certified Regrind / Recycler</div>
                </div>
                <div style="font-size: 1.4rem; color: var(--text-muted);">{feather_icon('arrow-right', color='var(--text-muted)', size=20, margin_right=0)}</div>
                <div style="background: var(--bg-subtle); border: 1px solid var(--border-color); padding: 14px 18px; border-radius: 12px; min-width: 160px;">
                    <div style="margin-bottom: 6px;">{feather_icon('dollar-sign', color='#059669', size=28, margin_right=0)}</div>
                    <strong style="font-size: 0.95rem;">Cost Recovery</strong>
                    <div style="font-size: 0.8rem; color: #059669; margin-top: 2px;">Up to ₹680,600/yr Saved</div>
                </div>
                <div style="font-size: 1.4rem; color: var(--text-muted);">{feather_icon('arrow-right', color='var(--text-muted)', size=20, margin_right=0)}</div>
                <div style="background: var(--bg-subtle); border: 1px solid var(--border-color); padding: 14px 18px; border-radius: 12px; min-width: 160px;">
                    <div style="margin-bottom: 6px;">{feather_icon('leaf', color='#10B981', size=28, margin_right=0)}</div>
                    <strong style="font-size: 0.95rem;">Carbon Abated</strong>
                    <div style="font-size: 0.8rem; color: #10B981; margin-top: 2px;">Permanent Footprint Cut</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Navigation
    st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)
    c_b1, c_b2 = st.columns([1, 1])
    with c_b1:
        if st.button("← Back to Simulator", key="circ_back_sim"):
            st.session_state["current_step"] = 9
            st.session_state["nav_section"] = "simulator"
            st.rerun()
    with c_b2:
        if st.button("Proceed to Platform Settings →", type="primary", key="circ_next_rep", use_container_width=True):
            st.session_state["current_step"] = 12
            st.session_state["nav_section"] = "settings"
            st.rerun()

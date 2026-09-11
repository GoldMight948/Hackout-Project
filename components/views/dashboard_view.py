"""
Step 3: Emissions Dashboard View.
Strictly adheres to the Dashboard Checklist:
1. Headline number (Total tonnes CO2/yr)
2. Emissions breakdown chart (Donut/pie)
3. Category breakdown (numeric shares & tonnes)
4. Leak-point ranking (worst to least)
5. Cost equivalent ($/year estimated utility & operational impact)
6. Emissions per unit produced (efficiency metric)
7. Entry point into each leak point (routes directly to suggestions)
8. Visual priority tags (Very High, High, Medium, Low)
"""

import streamlit as st
import plotly.graph_objects as go
from components.calculations import calculate_emissions, CATEGORY_METADATA

def render_dashboard_view():
    # Retrieve or compute emissions results
    if "emissions_results" not in st.session_state or st.session_state["emissions_results"] is None:
        inputs = st.session_state.get("form_inputs", {})
        if not inputs:
            st.warning("No data found. Please complete the data entry form first.")
            if st.button("Go to Data Entry"):
                st.session_state["current_step"] = 2
                st.rerun()
            return
        st.session_state["emissions_results"] = calculate_emissions(inputs)

    results = st.session_state["emissions_results"]
    total_co2 = results["total_co2"]
    total_cost = results["total_cost"]
    ranked_cats = results["ranked_categories"]
    top_leak = results.get("top_leak")
    per_unit = results.get("emissions_per_unit")
    business_name = st.session_state.get("form_inputs", {}).get("business_name", "Your Enterprise")

    # Header title
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;">
            <div>
                <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #059669; font-weight: 700;">
                    Emissions Diagnosis & Leak Ranking
                </span>
                <h2 style="font-size: 1.8rem; font-weight: 800; color: #0F172A; margin: 4px 0 0 0;">
                    {business_name} Footprint Overview
                </h2>
            </div>
            <div>
                <span style="background: #F1F5F9; color: #475569; padding: 6px 12px; border-radius: 8px; font-size: 0.82rem; font-weight: 600;">
                    📅 12-Month Operational Period
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 1. Headline Number & 5. Cost Equivalent & 6. Emissions Per Unit Produced
    col_headline, col_cost, col_unit = st.columns([1.6, 1.2, 1.2], gap="medium")

    with col_headline:
        st.markdown(f"""
            <div class="headline-card">
                <div class="headline-title">1. Total Annual Footprint</div>
                <div class="headline-number">{total_co2:,.1f} <span style="font-size: 1.2rem; font-weight: 500; color: #A7F3D0;">tonnes CO₂e</span></div>
                <div class="headline-subtitle">
                    Equivalent to driving ~{int(total_co2 * 5800):,} km in an average gasoline car.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_cost:
        st.markdown(f"""
            <div class="clean-card" style="height: 100%; border-top: 4px solid #F59E0B;">
                <div style="font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.06em; color: #64748B; font-weight: 700; margin-bottom: 6px;">
                    5. Cost Equivalent
                </div>
                <div style="font-size: 2.1rem; font-weight: 800; color: #0F172A; line-height: 1.1; margin-bottom: 6px;">
                    ${total_cost:,.0f} <span style="font-size: 0.9rem; font-weight: 500; color: #64748B;">/ yr</span>
                </div>
                <p style="font-size: 0.82rem; color: #64748B; margin: 0; line-height: 1.4;">
                    Estimated annual utility, fuel, and disposal expenses contributing to these emissions.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with col_unit:
        unit_text = f"{per_unit['kg_co2_per_unit']} kg CO₂" if per_unit else "Not specified"
        unit_sub = f"Across {int(per_unit['units']):,} units produced" if per_unit else "Add units in data entry"
        st.markdown(f"""
            <div class="clean-card" style="height: 100%; border-top: 4px solid #10B981;">
                <div style="font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.06em; color: #64748B; font-weight: 700; margin-bottom: 6px;">
                    6. Emissions Intensity
                </div>
                <div style="font-size: 2.1rem; font-weight: 800; color: #0F172A; line-height: 1.1; margin-bottom: 6px;">
                    {unit_text}
                </div>
                <p style="font-size: 0.82rem; color: #64748B; margin: 0; line-height: 1.4;">
                    {unit_sub} — key efficiency metric to track as you scale.
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # 2. Emissions Breakdown Chart & 3. Numeric Breakdown
    col_chart, col_ranks = st.columns([1.15, 1.35], gap="large")

    with col_chart:
        st.markdown("#### 2. Emissions Breakdown")
        
        # Prepare Plotly Donut Chart
        labels = [cat["label"] for cat in ranked_cats]
        values = [cat["co2_tonnes"] for cat in ranked_cats]
        icons = [cat["icon"] for cat in ranked_cats]
        # Colors corresponding to categories
        cat_colors = [cat["priority_color"] for cat in ranked_cats]

        fig = go.Figure(data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.56,
                marker=dict(colors=cat_colors, line=dict(color='#FFFFFF', width=2)),
                textinfo='label+percent',
                textposition='inside',
                hoverinfo='label+value+percent',
                hovertemplate='<b>%{label}</b><br>Emissions: %{value} t CO₂<br>Share: %{percent}<extra></extra>'
            )
        ])
        fig.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            height=300,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            annotations=[dict(text=f'<b>{total_co2} t</b><br>Total', x=0.5, y=0.5, font_size=15, showarrow=False)]
        )
        st.plotly_chart(fig, use_container_width=True)

        # 3. Category Breakdown (numeric shares)
        st.markdown("##### 3. Exact Category Share")
        for cat in ranked_cats:
            st.markdown(f"""
                <div style="display: flex; justify-content: space-between; font-size: 0.88rem; padding: 4px 0; border-bottom: 1px dotted #E2E8F0;">
                    <span>{cat['icon']} <strong>{cat['label']}</strong></span>
                    <span><strong>{cat['share_pct']}%</strong> &bull; {cat['co2_tonnes']} t &bull; ${cat['cost_dollars']:,.0f}</span>
                </div>
            """, unsafe_allow_html=True)

    # 4. Leak-Point Ranking & 7. Entry Point into each leak point & 8. Visual Priority Tags
    with col_ranks:
        st.markdown("#### 4. Ranked Leak Points (Worst to Least)")
        st.caption("Click any leak category below to jump straight to targeted green fixes:")

        for cat in ranked_cats:
            priority_class = f"badge-priority-{cat['priority'].lower().replace(' ', '-')}"
            
            # Row container with styling
            st.markdown(f"""
                <div class="leak-row">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div class="leak-rank-badge" style="background: {'#FEE2E2' if cat['rank'] == 1 else '#F1F5F9'}; color: {'#DC2626' if cat['rank'] == 1 else '#475569'};">
                            #{cat['rank']}
                        </div>
                        <div>
                            <div style="font-weight: 700; font-size: 1rem; color: #0F172A;">
                                {cat['icon']} {cat['label']}
                            </div>
                            <div style="font-size: 0.8rem; color: #64748B;">
                                {cat['co2_tonnes']} tonnes CO₂ ({cat['share_pct']}%) &bull; est. ${cat['cost_dollars']:,.0f}/yr
                            </div>
                        </div>
                    </div>
                    <div>
                        <span class="{priority_class}">8. {cat['priority']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # 7. Entry Point button for each leak point
            btn_label = f"Inspect #{cat['rank']} {cat['label']} Fixes →" if cat['rank'] == 1 else f"View {cat['label']} Fixes →"
            if st.button(btn_label, key=f"route_leak_{cat['category']}", use_container_width=True):
                st.session_state["selected_leak_category"] = cat["category"]
                st.session_state["current_step"] = 4 # Navigate to recommendations
                st.rerun()

            st.markdown("<div style='margin-bottom: 6px;'></div>", unsafe_allow_html=True)

    st.markdown("<hr style='margin: 30px 0 20px 0; border: none; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)

    # Top leak callout banner
    if top_leak:
        st.markdown(f"""
            <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 12px; padding: 16px 20px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 1.6rem;">🎯</span>
                    <div>
                        <strong style="color: #92400E; font-size: 0.95rem;">Primary Leak Diagnosis: {top_leak['label']}</strong>
                        <div style="color: #B45309; font-size: 0.85rem;">
                            Accounts for <strong>{top_leak['share_pct']}%</strong> of your total emissions and ~${top_leak['cost_dollars']:,.0f}/year. Prioritizing fixes here will give your business the highest return.
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Navigation buttons
    col_nav_left, col_nav_right = st.columns([1, 1])
    with col_nav_left:
        if st.button("← Back to Data Entry", key="dash_back"):
            st.session_state["current_step"] = 2
            st.rerun()

    with col_nav_right:
        if st.button("Proceed to Recommendations & Fixes →", type="primary", key="dash_next", use_container_width=True):
            if "selected_leak_category" not in st.session_state or not st.session_state["selected_leak_category"]:
                st.session_state["selected_leak_category"] = top_leak["category"] if top_leak else "electricity"
            st.session_state["current_step"] = 4
            st.rerun()

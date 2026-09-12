"""
Step 5: Executive Dashboard View.
Delivers a modern SaaS analytics interface (similar to Microsoft Power BI & Tableau).
Includes Top KPI cards, Gauge chart, Donut chart, Pie chart, Bar chart,
Stacked Bar chart, Line chart, Area chart, and quick links to Analytics.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from components.calculations import calculate_detailed_emissions
from components.ml_forecast import generate_monthly_timeseries, forecast_emissions_ml
from components.icons import (
    feather_icon, COLOR_WARNING, COLOR_SUCCESS, COLOR_NEUTRAL,
    COLOR_SECONDARY, COLOR_INFO, COLOR_AMBER
)

def render_dashboard_view():
    """Renders executive KPI cards and core Plotly visualizations."""
    if "emissions_results" not in st.session_state or st.session_state["emissions_results"] is None:
        inputs = st.session_state.get("form_inputs", {})
        if not inputs:
            st.warning("No data found. Please complete Setup or load a demo dataset.")
            if st.button("Go to Setup"):
                st.session_state["current_step"] = 3
                st.rerun()
            return
        st.session_state["emissions_results"] = calculate_detailed_emissions(inputs)

    res = st.session_state["emissions_results"]
    user = st.session_state.get("current_user", {})
    comp_name = user.get("company_name", res.get("raw_inputs", {}).get("business_name", "Enterprise Facility"))
    theme_mode = st.session_state.get("theme_mode", "light")
    chart_text_color = "#F8FAFC" if theme_mode == "dark" else "#1E293B"

    # Header section with Feather Icon
    head_icon = feather_icon("pie-chart", color="#10B981", size=30, margin_right=10)
    cal_icon = feather_icon("calendar", color="var(--text-muted)", size=15, margin_right=6)
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px; flex-wrap: wrap; gap: 10px;">
            <div>
                <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #10B981; font-weight: 700;">
                    Executive Overview & Carbon Intelligence
                </span>
                <h1 style="font-size: 2.1rem; font-weight: 800; margin: 4px 0 0 0; letter-spacing: -0.02em; display: flex; align-items: center;">
                    {head_icon} {comp_name} Carbon Dashboard
                </h1>
            </div>
            <div style="display: flex; gap: 10px; align-items: center;">
                <span style="background: var(--bg-card); border: 1px solid var(--border-color); padding: 6px 14px; border-radius: 8px; font-size: 0.85rem; font-weight: 600; display: flex; align-items: center;">
                    {cal_icon} 12-Month Compliance Period
                </span>
                <span class="{'badge-low' if not res['is_deficit'] else 'badge-critical'}">
                    {res['net_carbon_status']}
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Top 7 KPIs Cards with Feather Icons
    k1, k2, k3, k4, k5, k6, k7 = st.columns(7)
    
    with k1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title" style="display: flex; align-items: center;">
                    {feather_icon("leaf", color=COLOR_SUCCESS, size=15, margin_right=5)} Total Emissions
                </div>
                <div class="kpi-value">{res['total_co2']:,.1f}</div>
                <div class="kpi-subtext">tonnes CO₂e / yr</div>
            </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
            <div class="kpi-card info">
                <div class="kpi-title" style="display: flex; align-items: center;">
                    {feather_icon("award", color=COLOR_INFO, size=15, margin_right=5)} Govt Credits
                </div>
                <div class="kpi-value">{res['govt_credits']:,.0f}</div>
                <div class="kpi-subtext">credits allocated</div>
            </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
            <div class="kpi-card warning">
                <div class="kpi-title" style="display: flex; align-items: center;">
                    {feather_icon("activity", color=COLOR_AMBER, size=15, margin_right=5)} Credits Used
                </div>
                <div class="kpi-value">{res['credits_used']:,.1f}</div>
                <div class="kpi-subtext">1 credit = 1 t CO₂</div>
            </div>
        """, unsafe_allow_html=True)

    with k4:
        deficit_class = "deficit" if res['is_deficit'] else "low"
        def_icon = feather_icon("alert-triangle", color=COLOR_WARNING if res['is_deficit'] else COLOR_SUCCESS, size=15, margin_right=5)
        st.markdown(f"""
            <div class="kpi-card {deficit_class}">
                <div class="kpi-title" style="display: flex; align-items: center;">
                    {def_icon} Credit Deficit
                </div>
                <div class="kpi-value" style="color: {'#EF4444' if res['is_deficit'] else '#10B981'};">
                    {res['credits_required']:,.1f}
                </div>
                <div class="kpi-subtext">{'required to buy' if res['is_deficit'] else 'no deficit'}</div>
            </div>
        """, unsafe_allow_html=True)

    with k5:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title" style="display: flex; align-items: center;">
                    {feather_icon("shield", color=COLOR_SUCCESS, size=15, margin_right=5)} Remaining Credits
                </div>
                <div class="kpi-value">{res['credits_remaining']:,.1f}</div>
                <div class="kpi-subtext">surplus balance</div>
            </div>
        """, unsafe_allow_html=True)

    with k6:
        st.markdown(f"""
            <div class="kpi-card {'deficit' if res['compliance_cost'] > 0 else ''}">
                <div class="kpi-title" style="display: flex; align-items: center;">
                    {feather_icon("dollar-sign", color=COLOR_NEUTRAL, size=15, margin_right=5)} Compliance Cost
                </div>
                <div class="kpi-value">${res['compliance_cost']:,.0f}</div>
                <div class="kpi-subtext">@ ${res['credit_price']:.0f}/tonne</div>
            </div>
        """, unsafe_allow_html=True)

    with k7:
        score_val = res['sustainability_score']
        score_color = "#10B981" if score_val >= 70 else ("#F59E0B" if score_val >= 45 else "#EF4444")
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title" style="display: flex; align-items: center;">
                    {feather_icon("target", color=score_color, size=15, margin_right=5)} Eco Score
                </div>
                <div class="kpi-value" style="color: {score_color};">{score_val:.0f}</div>
                <div class="kpi-subtext">scale 0–100</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # Monthly Timeseries Data for Visuals
    monthly_df = generate_monthly_timeseries(res["pillar_co2"])

    # Row 1 Charts: Gauge Chart (Sustainability Score) & Donut Chart (Carbon Credits) & Pie Chart (Pillars)
    col_gauge, col_donut, col_pie = st.columns([1, 1, 1], gap="medium")

    with col_gauge:
        gauge_title = feather_icon("target", color=COLOR_SUCCESS, size=18, margin_right=6)
        st.markdown(f"""
            <div class="saas-card">
                <div class="saas-card-title" style="display: flex; align-items: center;">{gauge_title} Overall Sustainability Score (0–100)</div>
                <div class="saas-card-subtitle">Multi-factor operational green efficiency index</div>
        """, unsafe_allow_html=True)

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=res["sustainability_score"],
            number={'suffix': "/100", 'font': {'size': 28, 'color': chart_text_color}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': chart_text_color},
                'bar': {'color': "#10B981", 'thickness': 0.28},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 1,
                'bordercolor': "var(--border-color)",
                'steps': [
                    {'range': [0, 45], 'color': 'rgba(239, 68, 68, 0.25)'},
                    {'range': [45, 70], 'color': 'rgba(245, 158, 11, 0.25)'},
                    {'range': [70, 100], 'color': 'rgba(16, 185, 129, 0.25)'}
                ],
                'threshold': {
                    'line': {'color': "#065F46", 'width': 4},
                    'thickness': 0.75,
                    'value': 85
                }
            }
        ))
        fig_gauge.update_layout(
            height=240,
            margin=dict(l=20, r=20, t=20, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': chart_text_color}
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_donut:
        donut_icon = feather_icon("pie-chart", color=COLOR_INFO, size=18, margin_right=6)
        st.markdown(f"""
            <div class="saas-card">
                <div class="saas-card-title" style="display: flex; align-items: center;">{donut_icon} Carbon Credits: Used vs. Remaining</div>
                <div class="saas-card-subtitle">Statutory compliance balance</div>
        """, unsafe_allow_html=True)

        donut_labels = ["Credits Used", "Credits Remaining"]
        donut_vals = [res["credits_used"], res["credits_remaining"]]
        donut_colors = ["#F97316", "#10B981"] if not res["is_deficit"] else ["#EF4444", "#3B82F6"]

        fig_donut = go.Figure(data=[go.Pie(
            labels=donut_labels,
            values=donut_vals,
            hole=0.62,
            marker=dict(colors=donut_colors, line=dict(color='var(--bg-card)', width=2)),
            textinfo='label+percent',
            textposition='inside',
            hovertemplate='<b>%{label}</b><br>%{value:,.1f} tonnes (%{percent})<extra></extra>'
        )])
        fig_donut.update_layout(
            height=240,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            annotations=[dict(
                text=f"<b>{res['govt_credits']:,.0f} t</b><br>Quota",
                x=0.5, y=0.5, font_size=13, showarrow=False, font_color=chart_text_color
            )]
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_pie:
        pie_icon = feather_icon("pie-chart", color=COLOR_AMBER, size=18, margin_right=6)
        st.markdown(f"""
            <div class="saas-card">
                <div class="saas-card-title" style="display: flex; align-items: center;">{pie_icon} Emission Contribution by Pillar</div>
                <div class="saas-card-subtitle">Operational source distribution</div>
        """, unsafe_allow_html=True)

        pie_labels = list(res["pillar_co2"].keys())
        pie_values = list(res["pillar_co2"].values())
        pillar_palette = ["#F59E0B", "#EF4444", "#F97316", "#10B981", "#06B6D4", "#6366F1"]

        fig_pie = go.Figure(data=[go.Pie(
            labels=pie_labels,
            values=pie_values,
            marker=dict(colors=pillar_palette, line=dict(color='var(--bg-card)', width=2)),
            textinfo='percent',
            hovertemplate='<b>%{label}</b><br>Emissions: %{value:,.1f} t CO₂<br>Share: %{percent}<extra></extra>'
        )])
        fig_pie.update_layout(
            height=240,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, font=dict(size=10, color=chart_text_color)),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # Row 2 Charts: Bar Chart (Top Categories) & Stacked Bar Chart (Monthly Trajectory)
    col_bar, col_stacked = st.columns([1.1, 1.3], gap="large")

    with col_bar:
        bar_icon = feather_icon("bar-chart-2", color=COLOR_WARNING, size=18, margin_right=6)
        st.markdown(f"""
            <div class="saas-card">
                <div class="saas-card-title" style="display: flex; align-items: center;">{bar_icon} Top Emission Categories (tonnes CO₂e)</div>
                <div class="saas-card-subtitle">Highest volume industrial sources</div>
        """, unsafe_allow_html=True)

        sorted_cats = sorted(res["pillar_co2"].items(), key=lambda x: x[1], reverse=True)
        cat_names = [k for k, v in sorted_cats]
        cat_vals = [v for k, v in sorted_cats]

        fig_bar = go.Figure(data=[go.Bar(
            x=cat_vals,
            y=cat_names,
            orientation='h',
            marker=dict(
                color=cat_vals,
                colorscale=[[0, '#10B981'], [0.5, '#F59E0B'], [1.0, '#DC2626']],
                line=dict(width=0)
            ),
            text=[f"{v:,.1f} t" for v in cat_vals],
            textposition='auto',
            hovertemplate='<b>%{y}</b>: %{x:,.1f} tonnes CO₂e<extra></extra>'
        )])
        fig_bar.update_layout(
            height=290,
            margin=dict(l=10, r=20, t=10, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.15)', tickfont=dict(size=12, color=chart_text_color)),
            yaxis=dict(autorange="reversed", tickfont=dict(size=12, color=chart_text_color))
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_stacked:
        stack_icon = feather_icon("columns", color=COLOR_NEUTRAL, size=18, margin_right=6)
        st.markdown(f"""
            <div class="saas-card">
                <div class="saas-card-title" style="display: flex; align-items: center;">{stack_icon} Stacked 12-Month Emission Breakdown</div>
                <div class="saas-card-subtitle">Seasonal monthly operational trajectory across all pillars</div>
        """, unsafe_allow_html=True)

        fig_stacked = go.Figure()
        pillars = [c for c in monthly_df.columns if c not in ["Month", "Month_Num", "Total_Monthly_CO2"]]
        palette = ["#F59E0B", "#EF4444", "#F97316", "#10B981", "#06B6D4", "#6366F1"]

        for idx, pillar in enumerate(pillars):
            fig_stacked.add_trace(go.Bar(
                name=pillar,
                x=monthly_df["Month"],
                y=monthly_df[pillar],
                marker_color=palette[idx % len(palette)],
                hovertemplate=f'<b>{pillar}</b>: %{{y:,.1f}} t<extra></extra>'
            ))

        fig_stacked.update_layout(
            barmode='stack',
            height=290,
            margin=dict(l=10, r=10, t=10, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color=chart_text_color)),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickfont=dict(size=11, color=chart_text_color)),
            yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.15)', tickfont=dict(size=11, color=chart_text_color))
        )
        st.plotly_chart(fig_stacked, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # Row 3 Charts: Line Chart (Trends) & Area Chart (Cumulative Carbon Footprint)
    col_line, col_area = st.columns([1, 1], gap="large")

    with col_line:
        trend_icon = feather_icon("trending-down", color=COLOR_SUCCESS, size=18, margin_right=6)
        st.markdown(f"""
            <div class="saas-card">
                <div class="saas-card-title" style="display: flex; align-items: center;">{trend_icon} Emission Trends Over Months (Line Chart)</div>
                <div class="saas-card-subtitle">Monthly profile with peak operational variance</div>
        """, unsafe_allow_html=True)

        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=monthly_df["Month"],
            y=monthly_df["Total_Monthly_CO2"],
            mode='lines+markers',
            name='Total Monthly CO₂',
            line=dict(color='#059669', width=3),
            marker=dict(size=7, color='#10B981'),
            hovertemplate='<b>%{x}</b>: %{y:,.1f} tonnes CO₂<extra></extra>'
        ))
        fig_line.update_layout(
            height=260,
            margin=dict(l=10, r=10, t=10, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickfont=dict(size=11, color=chart_text_color)),
            yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.15)', tickfont=dict(size=11, color=chart_text_color))
        )
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_area:
        st.markdown("""
            <div class="saas-card">
                <div class="saas-card-title">Cumulative Carbon Footprint (Area Chart)</div>
                <div class="saas-card-subtitle">Accrued compliance footprint against carbon allowance</div>
        """, unsafe_allow_html=True)

        cumulative_vals = monthly_df["Total_Monthly_CO2"].cumsum()
        quota_runrate = [(res["govt_credits"] / 12.0) * (i + 1) for i in range(12)]

        fig_area = go.Figure()
        fig_area.add_trace(go.Scatter(
            x=monthly_df["Month"],
            y=cumulative_vals,
            fill='tozeroy',
            name='Cumulative Emitted',
            line=dict(color='#3B82F6', width=2),
            fillcolor='rgba(59, 130, 246, 0.2)',
            hovertemplate='Cumulative: %{y:,.1f} t<extra></extra>'
        ))
        fig_area.add_trace(go.Scatter(
            x=monthly_df["Month"],
            y=quota_runrate,
            mode='lines',
            name='Credit Allocation Trajectory',
            line=dict(color='#10B981', dash='dash', width=2),
            hovertemplate='Quota Target: %{y:,.1f} t<extra></extra>'
        ))
        fig_area.update_layout(
            height=260,
            margin=dict(l=10, r=10, t=10, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color=chart_text_color)),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickfont=dict(size=11, color=chart_text_color)),
            yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.15)', tickfont=dict(size=11, color=chart_text_color))
        )
        st.plotly_chart(fig_area, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Call-to-actions to Deep-Dive Analytics & Leak Points
    st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)
    c_act1, c_act2, c_act3 = st.columns(3)
    with c_act1:
        if st.button("📊 View Deep-Dive Analytics (Sankey, Treemap, Heatmap) →", use_container_width=True):
            st.session_state["nav_section"] = "analytics"
            st.rerun()
    with c_act2:
        if st.button("🔥 Inspect Top 10 Emission Leak Points →", type="primary", use_container_width=True):
            st.session_state["current_step"] = 6
            st.session_state["nav_section"] = "leak_detection"
            st.rerun()
    with c_act3:
        if st.button("🌍 Reconcile Carbon Credits & Marketplace →", use_container_width=True):
            st.session_state["current_step"] = 7
            st.session_state["nav_section"] = "carbon_credits"
            st.rerun()

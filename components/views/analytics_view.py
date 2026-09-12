"""
Deep-Dive Analytics View.
Delivers advanced Plotly visualizations:
1. Sankey Diagram for Material Flow (Input -> Production -> Waste -> Recycling -> Recovered Material)
2. Treemap of Emission Contribution by Department
3. Heatmap of Monthly Emission Intensity
4. Scatter Plot of Production Units vs Emissions (with OLS Trendline)
5. ML 12-Month Emission Forecast (BAU vs Decarbonization Pathway)
6. Industry Benchmarking Comparison
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from components.ml_forecast import generate_monthly_timeseries, forecast_emissions_ml, get_emission_intensity_matrix
from components.calculations import INDUSTRY_BENCHMARKS
from components.icons import feather_icon, render_icon_heading, COLOR_NEUTRAL, COLOR_INFO, COLOR_SUCCESS, COLOR_WARNING

def render_analytics_view():
  """Renders advanced Plotly diagrams & predictive analytics."""
  res = st.session_state.get("emissions_results")
  if not res:
    st.warning("Please complete Step 3 Setup or load a preset first.")
    return

  chart_text_color = "#1E293B"
  monthly_df = generate_monthly_timeseries(res["pillar_co2"])
  forecast_df = forecast_emissions_ml(monthly_df, target_reduction_pct=30.0)

  st.markdown("""
    <div style="margin-bottom: 8px;">
      <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #CBDED3; font-weight: 700;">
        Advanced Analytics & Systems Modeling
      </span>
    </div>
  """, unsafe_allow_html=True)
  st.markdown(render_icon_heading(
    "bar-chart-2",
    "Deep-Dive Visualizations & Circular Flow Dynamics",
    level="h2",
    color=COLOR_NEUTRAL,
    subtitle="High-fidelity Sankey material flow, departmental treemaps, intensity heatmaps, and predictive machine learning models."
  ), unsafe_allow_html=True)

  # 1. Sankey Diagram: Industrial Material Flow
  st.markdown(f"""
    <div class="saas-card">
      <div class="saas-card-title">{feather_icon('refresh-cw', color=COLOR_SUCCESS, size=18)} 1. Industrial Material Flow (Sankey Diagram)</div>
      <div class="saas-card-subtitle">
        Tracks virgin material input through production, scrap generation, circular recycling, and recovered raw feedstock:
      </div>
  """, unsafe_allow_html=True)

  raw_mat = float(res["raw_inputs"].get("raw_material_tonnes", 450.0))
  prod_mat = round(raw_mat * 0.72, 1)
  scrap_mat = round(raw_mat * 0.28, 1)
  recycled_mat = round(scrap_mat * 0.65, 1)
  landfill_mat = round(scrap_mat * 0.35, 1)
  recovered_mat = round(recycled_mat * 0.90, 1)

  sankey_node_labels = [
    f"Raw Material Input ({raw_mat:,.0f} t)",   # 0
    f"Active Production ({prod_mat:,.0f} t)",    # 1
    f"Industrial Scrap & Waste ({scrap_mat:,.0f} t)",# 2
    f"Finished Goods ({prod_mat:,.0f} t)",     # 3
    f"Circular Recycling ({recycled_mat:,.0f} t)",  # 4
    f"Municipal Landfill ({landfill_mat:,.0f} t)",  # 5
    f"Recovered Secondary Material ({recovered_mat:,.0f} t)" # 6
  ]

  sankey_sources = [0, 0, 1, 2, 2, 4]
  sankey_targets = [1, 2, 3, 4, 5, 6]
  sankey_values = [prod_mat, scrap_mat, prod_mat, recycled_mat, landfill_mat, recovered_mat]
  sankey_colors = [
    "rgba(16, 185, 129, 0.4)",
    "rgba(239, 68, 68, 0.4)",
    "rgba(16, 185, 129, 0.5)",
    "rgba(59, 130, 246, 0.4)",
    "rgba(239, 68, 68, 0.5)",
    "rgba(16, 185, 129, 0.6)"
  ]

  fig_sankey = go.Figure(data=[go.Sankey(
    node=dict(
      pad=18,
      thickness=22,
      line=dict(color="var(--border-color)", width=1),
      label=sankey_node_labels,
      color=["#B0C5BA", "#CBDED3", "#EF4444", "#CBDED3", "#3B82F6", "#DC2626", "#047857"]
    ),
    link=dict(
      source=sankey_sources,
      target=sankey_targets,
      value=sankey_values,
      color=sankey_colors
    )
  )])

  fig_sankey.update_layout(
    height=320,
    margin=dict(l=10, r=10, t=20, b=10),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(size=11, color=chart_text_color)
  )
  st.plotly_chart(fig_sankey, use_container_width=True)
  st.markdown("</div>", unsafe_allow_html=True)

  # Row 2: Treemap & Heatmap
  c_tree, c_heat = st.columns([1, 1], gap="large")

  with c_tree:
    st.markdown(f"""
      <div class="saas-card">
        <div class="saas-card-title">{feather_icon('pie-chart', color=COLOR_INFO, size=18)} 2. Departmental Emission Treemap</div>
        <div class="saas-card-subtitle">Hierarchical footprint allocation across plant divisions</div>
    """, unsafe_allow_html=True)

    dept_data = [
      {"Department": "Facility Infrastructure", "Category": "Facility", "CO2": round(res["total_co2"] * 0.34, 1)},
      {"Department": "Production Line Operations", "Category": "Production", "CO2": round(res["total_co2"] * 0.28, 1)},
      {"Department": "Fleet Logistics & Shipping", "Category": "Supply Chain", "CO2": round(res["total_co2"] * 0.22, 1)},
      {"Department": "Packaging & Solid Waste", "Category": "Materials", "CO2": round(res["total_co2"] * 0.10, 1)},
      {"Department": "Corporate Admin & Commute", "Category": "Office", "CO2": round(res["total_co2"] * 0.06, 1)}
    ]
    df_dept = pd.DataFrame(dept_data)

    fig_tree = px.treemap(
      df_dept,
      path=['Category', 'Department'],
      values='CO2',
      color='CO2',
      color_continuous_scale='Mint',
      hover_data={'CO2': ':.1f'}
    )
    fig_tree.update_layout(
      height=300,
      margin=dict(l=10, r=10, t=10, b=10),
      paper_bgcolor='rgba(0,0,0,0)',
      font=dict(color=chart_text_color)
    )
    fig_tree.update_traces(textinfo="label+value+percent parent")
    st.plotly_chart(fig_tree, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

  with c_heat:
    st.markdown(f"""
      <div class="saas-card">
        <div class="saas-card-title">{feather_icon('activity', color=COLOR_WARNING, size=18)} 3. Monthly Emission Intensity Heatmap</div>
        <div class="saas-card-subtitle">Operational hotspot matrix across 12 months & sources</div>
    """, unsafe_allow_html=True)

    heatmap_df = get_emission_intensity_matrix(monthly_df)

    fig_heat = go.Figure(data=go.Heatmap(
      z=heatmap_df.values,
      x=heatmap_df.columns,
      y=heatmap_df.index,
      colorscale='YlOrRd',
      hovertemplate='<b>%{y} - %{x}</b><br>Emissions: %{z:,.1f} t CO₂<extra></extra>'
    ))
    fig_heat.update_layout(
      height=300,
      margin=dict(l=10, r=10, t=10, b=20),
      paper_bgcolor='rgba(0,0,0,0)',
      plot_bgcolor='rgba(0,0,0,0)',
      xaxis=dict(tickfont=dict(color=chart_text_color)),
      yaxis=dict(tickfont=dict(color=chart_text_color))
    )
    st.plotly_chart(fig_heat, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

  # Row 3: Scatter Plot (Production vs Emissions) & ML 12-Month Forecast
  c_scatter, c_forecast = st.columns([1, 1.2], gap="large")

  with c_scatter:
    st.markdown(f"""
      <div class="saas-card">
        <div class="saas-card-title">{feather_icon('trending-up', color=COLOR_NEUTRAL, size=18)} 4. Emission vs Production Output (Scatter Plot)</div>
        <div class="saas-card-subtitle">Correlation between manufacturing volume and carbon footprint</div>
    """, unsafe_allow_html=True)

    # Generate synthetic production data correlating with monthly emissions
    base_units = float(res["production_units"]) / 12.0
    scatter_units = [base_units * (1 + (m_co2 - monthly_df["Total_Monthly_CO2"].mean()) / monthly_df["Total_Monthly_CO2"].mean() * 0.7) for m_co2 in monthly_df["Total_Monthly_CO2"]]

    df_scatter = pd.DataFrame({
      "Month": monthly_df["Month"],
      "Production_Units": scatter_units,
      "Monthly_CO2": monthly_df["Total_Monthly_CO2"]
    })

    fig_scatter = px.scatter(
      df_scatter,
      x="Production_Units",
      y="Monthly_CO2",
      text="Month",
      labels={"Production_Units": "Units Produced", "Monthly_CO2": "Monthly CO₂ (t)"},
      color="Monthly_CO2",
      color_continuous_scale="Viridis"
    )
    try:
      m, b = np.polyfit(df_scatter["Production_Units"], df_scatter["Monthly_CO2"], 1)
      x_line = np.linspace(df_scatter["Production_Units"].min(), df_scatter["Production_Units"].max(), 50)
      y_line = m * x_line + b
      fig_scatter.add_trace(go.Scatter(
        x=x_line,
        y=y_line,
        mode="lines",
        name="OLS Trendline",
        line=dict(color="#EF4444", dash="dash", width=2),
        hoverinfo="skip"
      ))
    except Exception:
      pass

    fig_scatter.update_traces(textposition='top center', selector=dict(mode='markers+text'))
    fig_scatter.update_layout(
      height=300,
      margin=dict(l=10, r=10, t=10, b=20),
      paper_bgcolor='rgba(0,0,0,0)',
      plot_bgcolor='rgba(0,0,0,0)',
      xaxis=dict(tickfont=dict(color=chart_text_color), showgrid=True, gridcolor='rgba(128,128,128,0.15)'),
      yaxis=dict(tickfont=dict(color=chart_text_color), showgrid=True, gridcolor='rgba(128,128,128,0.15)')
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

  with c_forecast:
    st.markdown(f"""
      <div class="saas-card">
        <div class="saas-card-title">{feather_icon('sliders', color=COLOR_SUCCESS, size=18)} 5. ML 12-Month Trajectory Forecasting</div>
        <div class="saas-card-subtitle">Business-As-Usual (BAU) vs Decarbonization Pathway (-30% Target)</div>
    """, unsafe_allow_html=True)

    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Scatter(
      x=forecast_df["Month_Label"],
      y=forecast_df["BAU_Forecast"],
      mode='lines+markers',
      name='BAU Trajectory',
      line=dict(color='#EF4444', width=2, dash='dash')
    ))
    fig_forecast.add_trace(go.Scatter(
      x=forecast_df["Month_Label"],
      y=forecast_df["Decarbonization_Pathway"],
      mode='lines+markers',
      name='Decarbonization Target (-30%)',
      line=dict(color='#CBDED3', width=3)
    ))

    fig_forecast.update_layout(
      height=300,
      margin=dict(l=10, r=10, t=10, b=20),
      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color=chart_text_color)),
      paper_bgcolor='rgba(0,0,0,0)',
      plot_bgcolor='rgba(0,0,0,0)',
      xaxis=dict(tickfont=dict(color=chart_text_color)),
      yaxis=dict(tickfont=dict(color=chart_text_color), showgrid=True, gridcolor='rgba(128,128,128,0.15)')
    )
    st.plotly_chart(fig_forecast, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

  # 6. Industry Benchmarking Table
  st.markdown(f"""
    <div class="saas-card">
      <div class="saas-card-title">{feather_icon('award', color=COLOR_INFO, size=18)} 6. Peer Industry Benchmark Comparison</div>
      <div class="saas-card-subtitle">
        How your facility compares to average sector peers across renewable share, waste diversion, and emission intensity:
      </div>
  """, unsafe_allow_html=True)

  bench_rows = []
  user_ind = res["raw_inputs"].get("industry", "Manufacturing Plant")
  for ind, b_data in INDUSTRY_BENCHMARKS.items():
    is_user = (ind.lower() == user_ind.lower())
    bench_rows.append({
      "Industry Sector": f"{ind} {'(Your Facility)' if is_user else ''}",
      "Emission Intensity (kg CO₂ / unit)": f"{b_data['intensity_kg_per_unit']} kg",
      "Avg Renewable Energy (%)": f"{b_data['avg_renewable_pct']}%",
      "Waste Diversion Rate (%)": f"{b_data['waste_divert_pct']}%",
      "ESG Rating Tier": "Tier A (Leading)" if b_data['avg_renewable_pct'] >= 20 else "Tier B (Compliant)"
    })

  st.table(pd.DataFrame(bench_rows))
  st.markdown("</div>", unsafe_allow_html=True)

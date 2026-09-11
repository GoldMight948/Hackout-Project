"""
Step 5: Before / After Simulator View.
Interactive sliders to adjust each emission category and watch pie/bar charts and numbers update live.
"""

import streamlit as st
import plotly.graph_objects as go
from components.calculations import calculate_emissions, CATEGORY_METADATA

def render_simulator_view():
    inputs = st.session_state.get("form_inputs", {})
    results = st.session_state.get("emissions_results", {})
    baseline_co2 = results.get("total_co2", 0.0)
    baseline_cost = results.get("total_cost", 0.0)

    st.markdown("""
        <div style="margin-bottom: 20px;">
            <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #059669; font-weight: 700;">
                Live Interactive What-If Tool
            </span>
            <h2 style="font-size: 1.8rem; font-weight: 800; color: #0F172A; margin: 4px 0 6px 0;">
                Before vs. After Emission Simulator
            </h2>
            <p style="font-size: 0.95rem; color: #64748B;">
                Drag the reduction sliders below to test different green initiatives. Watch your projected carbon footprint and annual dollar savings update instantly!
            </p>
        </div>
    """, unsafe_allow_html=True)

    col_sliders, col_visuals = st.columns([1.1, 1.3], gap="large")

    with col_sliders:
        st.markdown("#### 🎛️ Adjust Operational Reductions")
        st.caption("Targeted percentage cuts through efficiency and green upgrades:")

        red_elec = st.slider(
            "⚡ Electricity Efficiency Cut (%)",
            min_value=0, max_value=70, value=st.session_state.get("sim_elec", 20), step=5,
            help="Achieved via LED retrofits, HVAC setbacks, solar arrays, and high-efficiency motors."
        )
        st.session_state["sim_elec"] = red_elec

        red_fuel = st.slider(
            "🔥 On-Site Fuel Reduction (%)",
            min_value=0, max_value=70, value=st.session_state.get("sim_fuel", 15), step=5,
            help="Achieved via pipe insulation, burner tuning, waste heat recovery, or heat pump electrification."
        )
        st.session_state["sim_fuel"] = red_fuel

        red_trans = st.slider(
            "🚗 Transport & Mileage Cut (%)",
            min_value=0, max_value=70, value=st.session_state.get("sim_trans", 25), step=5,
            help="Achieved via route optimization, telematics anti-idling, and delivery consolidation."
        )
        st.session_state["sim_trans"] = red_trans

        red_waste = st.slider(
            "♻️ Landfill Waste Diversion (%)",
            min_value=0, max_value=85, value=st.session_state.get("sim_waste", 35), step=5,
            help="Achieved via on-site sorting bins, cardboard balers, and food waste composting."
        )
        st.session_state["sim_waste"] = red_waste

        # Quick preset buttons for simulation
        st.markdown("<p style='font-size: 0.82rem; color: #64748B; margin-top: 12px;'>Quick Simulation Scenarios:</p>", unsafe_allow_html=True)
        q1, q2, q3 = st.columns(3)
        with q1:
            if st.button("🌱 Conservative (-15%)", use_container_width=True):
                st.session_state["sim_elec"] = 15
                st.session_state["sim_fuel"] = 10
                st.session_state["sim_trans"] = 15
                st.session_state["sim_waste"] = 20
                st.rerun()
        with q2:
            if st.button("🚀 Moderate (-30%)", use_container_width=True):
                st.session_state["sim_elec"] = 30
                st.session_state["sim_fuel"] = 25
                st.session_state["sim_trans"] = 30
                st.session_state["sim_waste"] = 40
                st.rerun()
        with q3:
            if st.button("🌍 Net-Zero Push (-55%)", use_container_width=True):
                st.session_state["sim_elec"] = 55
                st.session_state["sim_fuel"] = 50
                st.session_state["sim_trans"] = 60
                st.session_state["sim_waste"] = 70
                st.rerun()

    # Compute simulated post-reduction values
    sim_inputs = {
        "business_name": inputs.get("business_name", ""),
        "business_type": inputs.get("business_type", ""),
        "electricity": inputs.get("electricity", 0.0) * (1.0 - red_elec / 100.0),
        "fuel": inputs.get("fuel", 0.0) * (1.0 - red_fuel / 100.0),
        "transport": inputs.get("transport", 0.0) * (1.0 - red_trans / 100.0),
        "waste": inputs.get("waste", 0.0) * (1.0 - red_waste / 100.0),
        "production_units": inputs.get("production_units", 0.0)
    }
    sim_results = calculate_emissions(sim_inputs)
    projected_co2 = sim_results["total_co2"]
    projected_cost = sim_results["total_cost"]

    co2_diff = round(baseline_co2 - projected_co2, 1)
    co2_pct_reduction = round((co2_diff / baseline_co2 * 100), 1) if baseline_co2 > 0 else 0.0
    cost_diff = round(baseline_cost - projected_cost, 0)

    # Store simulated outcomes in session state for action plan
    st.session_state["simulated_outcomes"] = {
        "co2_saved": co2_diff,
        "co2_pct": co2_pct_reduction,
        "cost_saved": cost_diff,
        "projected_co2": projected_co2
    }

    with col_visuals:
        st.markdown("#### 🎯 Real-Time Impact Projection")

        # Top metric callout boxes
        m1, m2 = st.columns(2)
        with m1:
            st.metric(
                label="Projected Annual CO₂",
                value=f"{projected_co2:,.1f} tonnes",
                delta=f"-{co2_diff} t ({co2_pct_reduction}% cut)",
                delta_color="normal"
            )
        with m2:
            st.metric(
                label="Estimated Dollar Savings",
                value=f"${cost_diff:,.0f} / yr",
                delta=f"${cost_diff:,.0f} saved annually",
                delta_color="normal"
            )

        # Before vs After Comparison Chart
        categories = ["Electricity", "Fuel", "Transport", "Waste"]
        baseline_vals = [
            results.get("co2_by_category", {}).get("electricity", 0),
            results.get("co2_by_category", {}).get("fuel", 0),
            results.get("co2_by_category", {}).get("transport", 0),
            results.get("co2_by_category", {}).get("waste", 0)
        ]
        projected_vals = [
            sim_results.get("co2_by_category", {}).get("electricity", 0),
            sim_results.get("co2_by_category", {}).get("fuel", 0),
            sim_results.get("co2_by_category", {}).get("transport", 0),
            sim_results.get("co2_by_category", {}).get("waste", 0)
        ]

        fig_compare = go.Figure(data=[
            go.Bar(name='Current Baseline', x=categories, y=baseline_vals, marker_color='#EF4444'),
            go.Bar(name='Projected with Fixes', x=categories, y=projected_vals, marker_color='#10B981')
        ])
        fig_compare.update_layout(
            barmode='group',
            margin=dict(t=20, b=20, l=10, r=10),
            height=280,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis_title="Tonnes CO₂ / Year"
        )
        st.plotly_chart(fig_compare, use_container_width=True)

    st.markdown("<hr style='margin: 30px 0 20px 0; border: none; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)

    # Navigation buttons
    col_nav_left, col_nav_right = st.columns([1, 1])
    with col_nav_left:
        if st.button("← Back to Recommendations", key="sim_back"):
            st.session_state["current_step"] = 4
            st.rerun()

    with col_nav_right:
        if st.button("Lock In & View Action Plan →", type="primary", key="sim_next", use_container_width=True):
            st.session_state["current_step"] = 6
            st.rerun()

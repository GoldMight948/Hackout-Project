"""
Step 2: Data Entry Form View.
Collects electricity, fuel, waste, transport, and production volume with validation and tooltips.
"""

import streamlit as st
from components.data_presets import DEMO_BUSINESSES
from components.calculations import calculate_emissions

def render_data_entry_view():
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <h2 style="font-size: 1.6rem; font-weight: 800; color: #0F172A; margin-bottom: 6px;">
                Enter Your Annual Operational Activity
            </h2>
            <p style="font-size: 0.95rem; color: #64748B;">
                Input your 12-month totals from utility bills and receipts. If you don't have exact figures, good approximations work great!
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Quick preset loader pills
    p_cols = st.columns([1.2, 1, 1, 1])
    with p_cols[0]:
        st.markdown("<p style='font-size: 0.88rem; font-weight: 600; color: #475569; padding-top: 6px;'>Fill from sample:</p>", unsafe_allow_html=True)
    with p_cols[1]:
        if st.button("🥪 Food Processor", key="fill_food", use_container_width=True):
            st.session_state["form_inputs"] = DEMO_BUSINESSES["food_processor"]["data"].copy()
            st.rerun()
    with p_cols[2]:
        if st.button("🏪 Small Retail", key="fill_retail", use_container_width=True):
            st.session_state["form_inputs"] = DEMO_BUSINESSES["small_retail"]["data"].copy()
            st.rerun()
    with p_cols[3]:
        if st.button("🚚 Logistics Fleet", key="fill_logistics", use_container_width=True):
            st.session_state["form_inputs"] = DEMO_BUSINESSES["logistics"]["data"].copy()
            st.rerun()

    st.markdown("<div style='margin-bottom: 18px;'></div>", unsafe_allow_html=True)

    # Existing values from session state
    inputs = st.session_state.get("form_inputs", {})
    def_bname = inputs.get("business_name", "My Enterprise")
    def_btype = inputs.get("business_type", "Food Processing")
    def_elec = float(inputs.get("electricity", 45000.0))
    def_fuel = float(inputs.get("fuel", 5000.0))
    def_waste = float(inputs.get("waste", 6000.0))
    def_trans = float(inputs.get("transport", 18000.0))
    def_prod = float(inputs.get("production_units", 25000.0))

    with st.form("emissions_data_form"):
        # Section 1: Business Overview
        st.markdown("#### 🏢 Business Profile")
        col_name, col_type = st.columns(2)
        with col_name:
            bname = st.text_input("Facility or Enterprise Name", value=def_bname, help="Used for your generated action plan and reports")
        with col_type:
            btype = st.selectbox(
                "Operating Sector",
                ["Food Processing", "Retail Store", "Logistics & Delivery", "Hospitality / Cafe", "Manufacturing", "Office Services"],
                index=0 if "Food" in def_btype else (1 if "Retail" in def_btype else 2)
            )

        st.markdown("<hr style='margin: 16px 0; border: none; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)
        st.markdown("#### 📊 Annual Activity Volumes (Last 12 Months)")

        # Section 2: Core Utility inputs
        col1, col2 = st.columns(2, gap="large")

        with col1:
            elec_val = st.number_input(
                "⚡ Electricity Consumption (kWh / year)",
                min_value=0.0,
                max_value=10000000.0,
                value=def_elec,
                step=1000.0,
                help="Check your 12 monthly electric bills for total kilowatt-hours (kWh). Covers lighting, cooling, computers, and facility machinery."
            )

            fuel_val = st.number_input(
                "🔥 On-Site Fuel & Gas (Liters / year)",
                min_value=0.0,
                max_value=5000000.0,
                value=def_fuel,
                step=500.0,
                help="Total liters of natural gas equivalent, diesel for backup generators, LPG cylinders, or heating oil consumed on premises."
            )

        with col2:
            trans_val = st.number_input(
                "🚗 Vehicle & Fleet Transport (km / year)",
                min_value=0.0,
                max_value=10000000.0,
                value=def_trans,
                step=1000.0,
                help="Total kilometers logged across company delivery vans, service vehicles, sales cars, or dedicated local couriers."
            )

            waste_val = st.number_input(
                "♻️ Solid Landfill Waste (kg / year)",
                min_value=0.0,
                max_value=5000000.0,
                value=def_waste,
                step=250.0,
                help="Estimated annual weight of non-recycled landfill trash collected by your commercial waste service."
            )

        st.markdown("<hr style='margin: 16px 0; border: none; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)
        st.markdown("#### 📦 Efficiency Benchmark (Optional)")
        
        prod_val = st.number_input(
            "Total Output / Production Units per Year",
            min_value=0.0,
            max_value=100000000.0,
            value=def_prod,
            step=1000.0,
            help="Number of products packaged, customers served, or parcels shipped. Allows computing emission intensity per product."
        )

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

        # Form action buttons
        c_sub_left, c_sub_right = st.columns([1, 1])
        with c_sub_left:
            submit_btn = st.form_submit_button(
                "Calculate Emissions & Detect Leaks →",
                type="primary",
                use_container_width=True
            )

    # Form Validation & Processing
    if submit_btn:
        total_activity = elec_val + fuel_val + trans_val + waste_val
        if total_activity <= 0:
            st.error("⚠️ Please enter at least one positive activity value above zero to calculate emissions.")
            return

        if elec_val == 0 and ("Retail" in btype or "Food" in btype):
            st.warning("ℹ️ Notice: Electricity is set to 0. Most retail and food facilities have baseline electric refrigeration and lighting.")

        # Save to session state
        updated_data = {
            "business_name": bname,
            "business_type": btype,
            "electricity": elec_val,
            "fuel": fuel_val,
            "waste": waste_val,
            "transport": trans_val,
            "production_units": prod_val
        }
        st.session_state["form_inputs"] = updated_data
        
        # Calculate emissions and store in persistent results
        results = calculate_emissions(updated_data)
        st.session_state["emissions_results"] = results
        
        # Default selected leak point to the #1 worst leak
        if results.get("top_leak"):
            st.session_state["selected_leak_category"] = results["top_leak"]["category"]

        st.success("✅ Emissions calculated successfully! Proceeding to Dashboard...")
        st.session_state["current_step"] = 3
        st.rerun()

    # Helpful collapsible explainer guides
    with st.expander("❓ Where do I find these numbers if I don't have utility bills handy?"):
        st.markdown("""
        - **Electricity (kWh)**: Look at the line marked "Total Metered Usage (kWh)" on your quarterly or monthly energy invoice. Multiply an average monthly bill by 12.
        - **Fuel (Liters)**: Check your fuel card statements, delivery receipts for heating oil or propane tanks.
        - **Transport (km)**: Check vehicle odometer logs or annual fleet maintenance service reports.
        - **Waste (kg)**: Commercial bins typically hold:
          - Small 240L wheelie bin ≈ 25–35 kg per pickup
          - Large 1100L metal dumpster ≈ 110–140 kg per pickup
        """)

    with st.expander("🌱 How does this tool calculate carbon emissions and dollars?"):
        st.markdown("""
        We use established GHG Protocol and EPA international greenhouse gas emission factors:
        - **Electricity**: 0.42 kg CO₂e / kWh (grid average)
        - **Fuel**: 2.68 kg CO₂e / liter (combustion)
        - **Transport**: 0.171 kg CO₂e / km (mixed delivery vans)
        - **Waste**: 0.52 kg CO₂e / kg (methane generation in landfill)
        """)

    # Back navigation
    col_back, _ = st.columns([1, 3])
    with col_back:
        if st.button("← Back to Welcome", key="back_to_welcome"):
            st.session_state["current_step"] = 1
            st.rerun()

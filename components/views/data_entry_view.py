"""
Step 3 / Data Entry: Operational Activity Entry View.
Supports Dual Modes:
  - Quick Mode: 4 coarse utility fields with EPA/GHG benchmark estimated category splits.
  - Detailed Mode: Granular operational breakdown across 5 pillars (Energy, Transport, Waste, Water, Manufacturing) & Government Carbon Credits.
Includes inline benchmark validation, verified industry presets, source help guides, and transparent defaults handling.
"""

import streamlit as st
from database.db_manager import save_emissions_assessment
from components.data_presets import DEMO_BUSINESSES
from components.calculations import calculate_detailed_emissions, calculate_emissions, INDUSTRY_BENCHMARKS
from components.auth import is_demo_session
from components.icons import (
    feather_icon, render_icon_heading, COLOR_SECONDARY,
    COLOR_NEUTRAL, COLOR_SUCCESS, COLOR_WARNING, COLOR_INFO
)

def render_data_entry_view():
    """Renders the comprehensive Activity Data Entry view with Quick and Detailed modes."""
    user = st.session_state.get("current_user", {})
    user_email = user.get("email", "guest@enterprise.com")
    comp_name = user.get("company_name", "Enterprise Facility")
    is_demo = is_demo_session()

    st.markdown("""
        <div style="margin-bottom: 8px;">
            <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #10B981; font-weight: 700;">
                Data Entry & Activity Intake
            </span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(render_icon_heading(
        "edit-3",
        f"Operational Activity Entry — {comp_name}",
        level="h2",
        color=COLOR_NEUTRAL,
        subtitle="Input 12-month operational consumption data. Choose Quick Mode for estimated category splits or Detailed Mode for granular sub-meter precision."
    ), unsafe_allow_html=True)

    # 1. Preset Loader Bar
    st.markdown(f"""
        <div class="saas-card" style="padding: 14px 20px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
                <span style="font-weight: 700; font-size: 0.9rem; display: flex; align-items: center;">
                    {feather_icon('zap', color=COLOR_WARNING, size=16, margin_right=6)} Quick Pre-Fill from Verified Industry Benchmarks:
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        if st.button("🥪 Food Processing", key="fill_food_preset", use_container_width=True):
            st.session_state["form_inputs"] = DEMO_BUSINESSES["food_processing"]["data"].copy()
            st.rerun()
    with col_p2:
        if st.button("🏪 Retail Store", key="fill_retail_preset", use_container_width=True):
            st.session_state["form_inputs"] = DEMO_BUSINESSES["retail_store"]["data"].copy()
            st.rerun()
    with col_p3:
        if st.button("🚚 Logistics Hub", key="fill_logistics_preset", use_container_width=True):
            st.session_state["form_inputs"] = DEMO_BUSINESSES["logistics_company"]["data"].copy()
            st.rerun()
    with col_p4:
        if st.button("🏭 Manufacturing Plant", key="fill_mfg_preset", use_container_width=True):
            st.session_state["form_inputs"] = DEMO_BUSINESSES["manufacturing_plant"]["data"].copy()
            st.rerun()

    # Current form inputs from session state
    inputs = st.session_state.get("form_inputs", {})
    def_bname = inputs.get("business_name") or user.get("company_name", "Enterprise Facility")
    def_btype = inputs.get("industry") or inputs.get("business_type", "Manufacturing Plant")

    # Mode Selection (Quick Mode vs Detailed Mode)
    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    entry_mode = st.radio(
        "Select Data Entry Depth:",
        [
            "⚡ Quick Mode (Estimated Category Splits)",
            "🔬 Detailed Mode (Granular Operational Breakdown)"
        ],
        index=0 if st.session_state.get("data_entry_mode") != "detailed" else 1,
        horizontal=True,
        key="data_entry_mode_selector"
    )
    is_quick_mode = "Quick Mode" in entry_mode
    st.session_state["data_entry_mode"] = "quick" if is_quick_mode else "detailed"

    sector_options = list(INDUSTRY_BENCHMARKS.keys())
    matched_idx = 0
    for idx, sec in enumerate(sector_options):
        if sec.lower() in def_btype.lower() or def_btype.lower() in sec.lower():
            matched_idx = idx
            break

    with st.form("operational_data_entry_form"):
        # Section A: Business Profile
        st.markdown("#### 🏢 Facility & Sector Profile")
        c_prof1, c_prof2 = st.columns(2)
        with c_prof1:
            bname = st.text_input("Facility or Enterprise Name", value=def_bname, help="Used for generated reports and action plans")
        with c_prof2:
            btype = st.selectbox("Operating Industry Sector", sector_options, index=matched_idx, help="Calibrates statutory carbon quotas and efficiency benchmarks")

        st.markdown("<hr style='margin: 16px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)

        if is_quick_mode:
            # ─────────────────────────────────────────────────────────────
            # QUICK MODE: 4 Coarse Fields + Renewable % + Output
            # ─────────────────────────────────────────────────────────────
            st.info(
                "⚡ **Quick Mode Active:** Input your 4 primary operational utility totals. "
                "The engine will automatically apply standard GHG Protocol category ratios "
                "(Fuel: 70% Diesel / 30% Petrol; Transport: 60% Freight / 30% Fleet / 10% Commute; "
                "Waste: 40% Organic / 30% Plastic / 10% Metal / 15% Paper / 5% Hazardous). "
                "Switch to **Detailed Mode** above if you have granular sub-meter numbers."
            )

            def_elec = float(inputs.get("electricity_kwh", inputs.get("electricity", 120000.0)))
            def_fuel = float(inputs.get("fuel", inputs.get("diesel_liters", 8000.0) + inputs.get("petrol_liters", 2000.0)))
            def_trans = float(inputs.get("transport", inputs.get("truck_km", 25000.0) + inputs.get("car_km", 10000.0)))
            def_waste = float(inputs.get("waste", inputs.get("organic_waste_kg", 5000.0) + inputs.get("plastic_waste_kg", 3000.0)))
            def_renew = float(inputs.get("renewable_pct", 10.0))
            def_prod = float(inputs.get("production_units", 25000.0))

            c_q1, c_q2 = st.columns(2, gap="large")
            with c_q1:
                q_elec = st.number_input(
                    "⚡ Electricity Consumption (kWh / yr)",
                    min_value=0.0,
                    max_value=50000000.0,
                    value=def_elec,
                    step=5000.0,
                    help="Total kilowatt-hours from 12 monthly electric bills."
                )
                q_renew = st.slider(
                    "🌱 On-Site Renewable Energy Share (%)",
                    min_value=0,
                    max_value=100,
                    value=int(def_renew),
                    step=1,
                    help="Percentage of electric power supplied by rooftop solar, wind, or green PPA."
                )
                q_fuel = st.number_input(
                    "🔥 Total Thermal Fuel & Heating (Liters / yr)",
                    min_value=0.0,
                    max_value=10000000.0,
                    value=def_fuel,
                    step=1000.0,
                    help="Combined liters of fuel oil, generator diesel, LPG cylinders, or heating fuels."
                )
            with c_q2:
                q_trans = st.number_input(
                    "🚗 Total Transport & Fleet Travel (km / yr)",
                    min_value=0.0,
                    max_value=25000000.0,
                    value=def_trans,
                    step=5000.0,
                    help="Total kilometers traveled by company delivery vans, freight trucks, and sales cars."
                )
                q_waste = st.number_input(
                    "♻️ Total Solid Waste Generated (kg / yr)",
                    min_value=0.0,
                    max_value=10000000.0,
                    value=def_waste,
                    step=500.0,
                    help="Estimated annual weight of non-recycled waste sent to landfill."
                )
                q_prod = st.number_input(
                    "📦 Annual Production / Output Units (Optional)",
                    min_value=0.0,
                    max_value=100000000.0,
                    value=def_prod,
                    step=2500.0,
                    help="Finished product units, shipments, or customers served. Enables carbon intensity per unit."
                )

        else:
            # ─────────────────────────────────────────────────────────────
            # DETAILED MODE: Granular 5 Pillars + Carbon Credits
            # ─────────────────────────────────────────────────────────────
            def_elec = float(inputs.get("electricity_kwh", inputs.get("electricity", 350000.0)))
            def_renew = float(inputs.get("renewable_pct", 15.0))
            def_diesel = float(inputs.get("diesel_liters", inputs.get("fuel", 12000.0)))
            def_petrol = float(inputs.get("petrol_liters", 4500.0))
            def_gas = float(inputs.get("gas_m3", 32000.0))

            def_truck = float(inputs.get("truck_km", inputs.get("transport", 55000.0)))
            def_car = float(inputs.get("car_km", 18000.0))
            def_commute = float(inputs.get("commute_km", 75000.0))
            def_vehs = int(inputs.get("delivery_vehicles", 6))

            def_org_waste = float(inputs.get("organic_waste_kg", inputs.get("waste", 24000.0)))
            def_plas_waste = float(inputs.get("plastic_waste_kg", 16000.0))
            def_met_waste = float(inputs.get("metal_waste_kg", 8500.0))
            def_pap_waste = float(inputs.get("paper_waste_kg", 14000.0))
            def_haz_waste = float(inputs.get("hazardous_waste_kg", 1200.0))

            def_water = float(inputs.get("water_m3", 6400.0))
            def_wastewater = float(inputs.get("wastewater_m3", 5200.0))

            def_raw_mat = float(inputs.get("raw_material_tonnes", 380.0))
            def_prod_qty = float(inputs.get("production_units", 150000.0))
            def_mach_hours = float(inputs.get("machine_hours", inputs.get("machine_running_hours", 3200.0)))

            def_credits = float(inputs.get("total_credits") or inputs.get("total_carbon_credits", 250.0))
            def_price = float(inputs.get("credit_price") or inputs.get("carbon_credit_price", 2905.0))

            # Pillar 1: Energy
            st.markdown(f"<div style='font-size: 1.1rem; font-weight: 700; margin-bottom: 8px; display: flex; align-items: center;'>{feather_icon('zap', color=COLOR_WARNING, size=18, margin_right=6)} 1. Energy & Thermal Fuels</div>", unsafe_allow_html=True)
            c_d_e1, c_d_e2, c_d_e3 = st.columns(3)
            with c_d_e1:
                d_elec = st.number_input("Electricity (kWh / yr)", min_value=0.0, value=def_elec, step=5000.0)
                d_renew = st.slider("Renewable Share (%)", min_value=0, max_value=100, value=int(def_renew), step=1)
            with c_d_e2:
                d_diesel = st.number_input("Diesel (Liters / yr)", min_value=0.0, value=def_diesel, step=500.0)
                d_petrol = st.number_input("Petrol / Gasoline (Liters / yr)", min_value=0.0, value=def_petrol, step=500.0)
            with c_d_e3:
                d_gas = st.number_input("Natural Gas (m³ / yr)", min_value=0.0, value=def_gas, step=1000.0)

            st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)

            # Pillar 2: Transport
            st.markdown(f"<div style='font-size: 1.1rem; font-weight: 700; margin-bottom: 8px; display: flex; align-items: center;'>{feather_icon('truck', color=COLOR_INFO, size=18, margin_right=6)} 2. Transport & Logistics</div>", unsafe_allow_html=True)
            c_d_t1, c_d_t2, c_d_t3, c_d_t4 = st.columns(4)
            with c_d_t1:
                d_truck = st.number_input("Freight Trucks (km)", min_value=0.0, value=def_truck, step=2500.0)
            with c_d_t2:
                d_car = st.number_input("Company Cars (km)", min_value=0.0, value=def_car, step=1000.0)
            with c_d_t3:
                d_commute = st.number_input("Staff Commute (km)", min_value=0.0, value=def_commute, step=5000.0)
            with c_d_t4:
                d_vehs = st.number_input("Delivery Fleet Size", min_value=0, max_value=500, value=def_vehs, step=1)

            st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)

            # Pillar 3: Waste
            st.markdown(f"<div style='font-size: 1.1rem; font-weight: 700; margin-bottom: 8px; display: flex; align-items: center;'>{feather_icon('trash-2', color='#EF4444', size=18, margin_right=6)} 3. Waste Streams (kg / yr)</div>", unsafe_allow_html=True)
            c_d_w1, c_d_w2, c_d_w3, c_d_w4, c_d_w5 = st.columns(5)
            with c_d_w1:
                d_org = st.number_input("Organic (kg)", min_value=0.0, value=def_org_waste, step=500.0)
            with c_d_w2:
                d_plas = st.number_input("Plastic (kg)", min_value=0.0, value=def_plas_waste, step=500.0)
            with c_d_w3:
                d_met = st.number_input("Metal (kg)", min_value=0.0, value=def_met_waste, step=250.0)
            with c_d_w4:
                d_pap = st.number_input("Paper (kg)", min_value=0.0, value=def_pap_waste, step=500.0)
            with c_d_w5:
                d_haz = st.number_input("Hazardous (kg)", min_value=0.0, value=def_haz_waste, step=100.0)

            st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)

            # Pillar 4: Water & Manufacturing
            st.markdown(f"<div style='font-size: 1.1rem; font-weight: 700; margin-bottom: 8px; display: flex; align-items: center;'>{feather_icon('droplet', color=COLOR_INFO, size=18, margin_right=6)} 4. Water, Materials & Production</div>", unsafe_allow_html=True)
            c_d_m1, c_d_m2, c_d_m3 = st.columns(3)
            with c_d_m1:
                d_water = st.number_input("Water (m³ / yr)", min_value=0.0, value=def_water, step=500.0)
                d_wastewater = st.number_input("Wastewater (m³ / yr)", min_value=0.0, value=def_wastewater, step=500.0)
            with c_d_m2:
                d_raw = st.number_input("Raw Materials (tonnes / yr)", min_value=0.0, value=def_raw_mat, step=25.0)
                d_prod_m = st.number_input("Production Output (units / yr)", min_value=0.0, value=def_prod_qty, step=5000.0)
            with c_d_m3:
                d_mach = st.number_input("Machine Running (hours / yr)", min_value=0.0, value=def_mach_hours, step=200.0)

            st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)

            # Pillar 5: Carbon Credits
            st.markdown(f"<div style='font-size: 1.1rem; font-weight: 700; margin-bottom: 8px; display: flex; align-items: center;'>{feather_icon('dollar-sign', color=COLOR_SUCCESS, size=18, margin_right=6)} 5. Statutory Carbon Credits</div>", unsafe_allow_html=True)
            c_d_c1, c_d_c2 = st.columns(2)
            with c_d_c1:
                d_cred = st.number_input("Statutory Carbon Quota (tonnes allowance)", min_value=0.0, value=def_credits, step=25.0)
            with c_d_c2:
                d_cprice = st.number_input("Market Trading Price (₹ / tonne)", min_value=1.0, value=def_price, step=1.0)

        st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button(
            "Calculate Footprint, Diagnose Leaks & Open Dashboard →",
            type="primary",
            use_container_width=True
        )

    # ─────────────────────────────────────────────────────────────
    # Form Processing & Inline Validation
    # ─────────────────────────────────────────────────────────────
    if submit_btn:
        if is_quick_mode:
            tot_act = q_elec + q_fuel + q_trans + q_waste
            if tot_act <= 0:
                st.error("⚠️ Please enter at least one operational activity volume above zero.")
                return

            if q_elec == 0 and ("Retail" in btype or "Food" in btype):
                st.warning("⚠️ Warning: Electricity is set to 0. Commercial facilities typically have refrigeration/lighting baseline.")

            if q_renew < 0 or q_renew > 100:
                st.error("⚠️ Renewable energy share must be between 0% and 100%.")
                return

            updated_data = {
                "business_name": bname,
                "business_type": btype,
                "industry": btype,
                # Coarse fields
                "electricity": q_elec,
                "fuel": q_fuel,
                "transport": q_trans,
                "waste": q_waste,
                # Granular derivations using EPA standard category splits
                "electricity_kwh": q_elec,
                "renewable_pct": float(q_renew),
                "diesel_liters": round(q_fuel * 0.70, 1),
                "petrol_liters": round(q_fuel * 0.30, 1),
                "gas_m3": 0.0,
                "truck_km": round(q_trans * 0.60, 1),
                "car_km": round(q_trans * 0.30, 1),
                "commute_km": round(q_trans * 0.10, 1),
                "delivery_vehicles": max(1, int(q_trans / 20000.0)) if q_trans > 0 else 0,
                "organic_waste_kg": round(q_waste * 0.40, 1),
                "plastic_waste_kg": round(q_waste * 0.30, 1),
                "metal_waste_kg": round(q_waste * 0.10, 1),
                "paper_waste_kg": round(q_waste * 0.15, 1),
                "hazardous_waste_kg": round(q_waste * 0.05, 1),
                "production_units": q_prod,
                # Leave unentered parameters as None so calculations.py tracks them as defaulted
                "water_m3": None,
                "wastewater_m3": None,
                "raw_material_tonnes": None,
                "machine_hours": None,
                "total_credits": None,
                "credit_price": 2905.0
            }
        else:
            tot_act = d_elec + d_diesel + d_petrol + d_gas + d_truck + d_car + d_commute + d_org + d_plas
            if tot_act <= 0:
                st.error("⚠️ Please enter at least one operational activity volume above zero.")
                return

            if d_renew < 0 or d_renew > 100:
                st.error("⚠️ Renewable energy share must be between 0% and 100%.")
                return

            updated_data = {
                "business_name": bname,
                "business_type": btype,
                "industry": btype,
                # Granular fields
                "electricity_kwh": d_elec,
                "renewable_pct": float(d_renew),
                "diesel_liters": d_diesel,
                "petrol_liters": d_petrol,
                "gas_m3": d_gas,
                "truck_km": d_truck,
                "car_km": d_car,
                "commute_km": d_commute,
                "delivery_vehicles": d_vehs,
                "organic_waste_kg": d_org,
                "plastic_waste_kg": d_plas,
                "metal_waste_kg": d_met,
                "paper_waste_kg": d_pap,
                "hazardous_waste_kg": d_haz,
                "water_m3": d_water,
                "wastewater_m3": d_wastewater,
                "raw_material_tonnes": d_raw,
                "production_units": d_prod_m,
                "machine_hours": d_mach,
                "machine_running_hours": d_mach,
                "total_credits": d_cred,
                "credit_price": d_cprice,
                # Backwards compatible coarse keys
                "electricity": d_elec,
                "fuel": d_diesel + d_petrol,
                "transport": d_truck + d_car + d_commute,
                "waste": d_org + d_plas + d_met + d_pap + d_haz
            }

        # Save to session state
        st.session_state["form_inputs"] = updated_data
        st.session_state["manual_setup_override"] = True

        # Calculate detailed emissions
        results = calculate_detailed_emissions(updated_data)
        st.session_state["emissions_results"] = results

        # Set default selected leak
        if results.get("top_leak"):
            st.session_state["selected_leak_category"] = results["top_leak"]["category"]

        # Persist to database if authenticated
        if user_email:
            try:
                save_emissions_assessment(user_email, updated_data, is_demo=1 if is_demo else 0)
                st.session_state["dash_synced_email"] = user_email
            except Exception:
                pass

        st.success("✅ Operational footprint saved & calculated! Redirecting to Executive Dashboard...")
        st.session_state["current_step"] = 5
        st.session_state["nav_section"] = "dashboard"
        st.rerun()

    # ─────────────────────────────────────────────────────────────
    # Detailed "Where do I find these numbers?" Expander Guides
    # ─────────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    with st.expander("❓ Where do I find these operational numbers if I don't have exact bills handy?"):
        st.markdown("""
        - **⚡ Electricity & Solar (kWh)**: Check the "Total Billed kWh" on your 12 monthly electric bills. If you have rooftop solar, check your inverter telemetry portal for total kWh generated and self-consumed.
        - **🔥 Fuels & Thermal Gas (Liters & m³)**:
          - **Diesel & Petrol**: Check your company fleet fuel card statements or receipts for backup generator bulk tank refills.
          - **Natural Gas (m³)**: Found on utility gas invoices. 1 Therm ≈ 2.83 m³; 100 cubic feet (CCF) ≈ 2.83 m³.
        - **🚗 Transport & Logistics (km)**:
          - Check odometer logs recorded during annual vehicle safety inspections.
          - Review freight waybills or dispatch manifests for shipping delivery routes.
        - **♻️ Waste Streams (kg)**:
          - Standard commercial wheelie bin (240 Liters) ≈ 25–35 kg per pickup.
          - Large commercial front-load metal dumpster (1,100 Liters) ≈ 110–140 kg per pickup.
          - Multiply the number of weekly bin collections by 52 to calculate annual weight.
        - **💧 Water & Wastewater (m³)**: Check municipal water utility bills for "Billed Consumption (m³ or kGal)". (1,000 Gallons ≈ 3.785 m³).
        - **📦 Manufacturing Output & Materials**: Consult your ERP/MES production summary reports for total units finished and raw material inventory consumption.
        - **💰 Statutory Carbon Quota**: Refer to your compliance registration letter from the environmental regulator (EPA, CARB, EU ETS, or national registry) for your annual free carbon allowance credits.
        """)

    with st.expander("🌱 How does this system calculate greenhouse gas emissions and financial impacts?"):
        st.markdown("""
        This platform adheres to the **GHG Protocol Corporate Accounting and Reporting Standard** and EPA greenhouse gas emission factors:
        - **Grid Electricity**: 0.42 kg CO₂e / kWh (international grid average)
        - **Diesel Combustion**: 2.68 kg CO₂e / Liter
        - **Petrol / Gasoline**: 2.31 kg CO₂e / Liter
        - **Natural Gas**: 2.03 kg CO₂e / m³
        - **Heavy Freight Truck**: 0.62 kg CO₂e / km
        - **Company Passenger Car**: 0.171 kg CO₂e / km
        - **Organic Landfill Waste**: 0.45 kg CO₂e / kg (methane emissions from anaerobic breakdown)
        - **Plastic Waste**: 2.10 kg CO₂e / kg (embedded petrochemical footprint and disposal)
        - **Water Supply & Treatment**: 0.34 kg CO₂e / m³
        """)

    # Back navigation
    col_back, _ = st.columns([1, 4])
    with col_back:
        if st.button("← Back to Dashboard", key="back_to_dash_from_data_entry"):
            st.session_state["nav_section"] = "dashboard"
            st.session_state["current_step"] = 5
            st.rerun()

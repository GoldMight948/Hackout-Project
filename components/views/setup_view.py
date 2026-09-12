"""
Step 3: Business Setup & Comprehensive Emission Sources Entry View.
Collects activity data across 5 pillars: Energy, Transport, Waste, Water, and Manufacturing,
alongside Government Carbon Credits allocation.
"""

import streamlit as st
from database.db_manager import save_emissions_assessment
from components.data_presets import DEMO_BUSINESSES
from components.calculations import calculate_detailed_emissions
from components.auth import is_demo_session
from components.icons import feather_icon, render_icon_heading, COLOR_SECONDARY, COLOR_NEUTRAL, COLOR_SUCCESS, COLOR_WARNING, COLOR_INFO

def render_setup_view():
    """Renders Step 3 complete emissions activity inputs."""
    user = st.session_state.get("current_user", {})
    user_email = user.get("email", "guest@enterprise.com")
    comp_name = user.get("company_name", "Enterprise Facility")
    is_demo = is_demo_session()

    st.markdown("""
        <div style="margin-bottom: 8px;">
            <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #10B981; font-weight: 700;">
                Step 3 — Operational Activity Entry
            </span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(render_icon_heading(
        "settings",
        f"Configure Emission Sources for {comp_name}",
        level="h2",
        color=COLOR_NEUTRAL,
        subtitle="Input your 12-month operational volumes. You can also load benchmark figures from our verified industry presets."
    ), unsafe_allow_html=True)

    # Preset Loader Bar
    st.markdown(f"""
        <div class="saas-card" style="padding: 14px 20px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
                <span style="font-weight: 700; font-size: 0.9rem; display: flex; align-items: center;">
                    {feather_icon('zap', color=COLOR_WARNING, size=16)} Quick Pre-Fill from Verified Industry Benchmarks:
                </span>
    """, unsafe_allow_html=True)

    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        if st.button("Food Processing Bakery", key="fill_food", use_container_width=True):
            st.session_state["form_inputs"] = DEMO_BUSINESSES["food_processing"]["data"].copy()
            st.rerun()
    with col_p2:
        if st.button("Retail Boutique", key="fill_retail", use_container_width=True):
            st.session_state["form_inputs"] = DEMO_BUSINESSES["retail_store"]["data"].copy()
            st.rerun()
    with col_p3:
        if st.button("Logistics Fleet Hub", key="fill_logistics", use_container_width=True):
            st.session_state["form_inputs"] = DEMO_BUSINESSES["logistics_company"]["data"].copy()
            st.rerun()
    with col_p4:
        if st.button("Manufacturing Plant", key="fill_mfg", use_container_width=True):
            st.session_state["form_inputs"] = DEMO_BUSINESSES["manufacturing_plant"]["data"].copy()
            st.rerun()

    # Current form values
    inputs = st.session_state.get("form_inputs", {})
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

    user = st.session_state.get("current_user", {})
    from components.calculations import get_statutory_carbon_quota
    quota_calc = get_statutory_carbon_quota(
        industry=user.get("industry", inputs.get("industry", "Manufacturing Plant")),
        company_type=user.get("company_type", "SME / Mid-Sized Business"),
        employees=user.get("employees", 50)
    )
    def_credits = float(inputs.get("total_credits") or inputs.get("total_carbon_credits") or quota_calc["quota_credits"])
    def_price = float(inputs.get("credit_price") or quota_calc["benchmark_price"])
    def_bal = float(inputs.get("current_balance", def_credits))

    with st.form("setup_emission_form"):
        # Section 1: Energy & Fuel
        st.markdown(f"<div style='font-size: 1.2rem; font-weight: 700; margin-bottom: 12px; display: flex; align-items: center;'>{feather_icon('zap', color=COLOR_WARNING, size=20)} <span>1. Energy & Thermal Fuel Consumption</span></div>", unsafe_allow_html=True)
        c_e1, c_e2, c_e3 = st.columns(3)
        with c_e1:
            inp_elec = st.number_input("Electricity Consumption (kWh / yr)", min_value=0.0, value=def_elec, step=5000.0, help="Grid metered electric power")
            inp_renew = st.slider("On-Site Renewable Energy (%)", min_value=0, max_value=100, value=int(def_renew), step=1, help="Share covered by rooftop solar or green PPA")
        with c_e2:
            inp_diesel = st.number_input("Diesel Consumption (Liters / yr)", min_value=0.0, value=def_diesel, step=500.0, help="Stationary generators, heavy forklifts, boiler oil")
            inp_petrol = st.number_input("Petrol / Gasoline (Liters / yr)", min_value=0.0, value=def_petrol, step=500.0, help="Company small utility vehicles & equipment")
        with c_e3:
            inp_gas = st.number_input("Natural Gas Consumption (m³ / yr)", min_value=0.0, value=def_gas, step=1000.0, help="Facility thermal ovens, furnaces, space heating")

        st.markdown("<hr style='margin: 18px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)

        # Section 2: Transport & Fleet Logistics
        st.markdown(f"<div style='font-size: 1.2rem; font-weight: 700; margin-bottom: 12px; display: flex; align-items: center;'>{feather_icon('truck', color=COLOR_INFO, size=20)} <span>2. Transport & Fleet Logistics</span></div>", unsafe_allow_html=True)
        c_t1, c_t2, c_t3, c_t4 = st.columns(4)
        with c_t1:
            inp_truck = st.number_input("Truck Freight Distance (km / yr)", min_value=0.0, value=def_truck, step=2500.0, help="Heavy freight & distribution shipping")
        with c_t2:
            inp_car = st.number_input("Company Car Distance (km / yr)", min_value=0.0, value=def_car, step=1000.0, help="Sales team and executive travel")
        with c_t3:
            inp_commute = st.number_input("Employee Commute (km / yr)", min_value=0.0, value=def_commute, step=5000.0, help="Staff daily transit footprint")
        with c_t4:
            inp_vehs = st.number_input("Dedicated Delivery Vehicles", min_value=0, max_value=500, value=def_vehs, step=1, help="Number of active fleet delivery vans")

        st.markdown("<hr style='margin: 18px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)

        # Section 3: Waste Generation & Streams
        st.markdown(f"<div style='font-size: 1.2rem; font-weight: 700; margin-bottom: 12px; display: flex; align-items: center;'>{feather_icon('trash-2', color='#EF4444', size=20)} <span>3. Industrial Solid Waste Streams (kg / yr)</span></div>", unsafe_allow_html=True)
        c_w1, c_w2, c_w3, c_w4, c_w5 = st.columns(5)
        with c_w1:
            inp_org_waste = st.number_input("Organic Waste (kg)", min_value=0.0, value=def_org_waste, step=500.0)
        with c_w2:
            inp_plas_waste = st.number_input("Plastic Waste (kg)", min_value=0.0, value=def_plas_waste, step=500.0)
        with c_w3:
            inp_met_waste = st.number_input("Metal Waste (kg)", min_value=0.0, value=def_met_waste, step=250.0)
        with c_w4:
            inp_pap_waste = st.number_input("Paper & Cardboard (kg)", min_value=0.0, value=def_pap_waste, step=500.0)
        with c_w5:
            inp_haz_waste = st.number_input("Hazardous Waste (kg)", min_value=0.0, value=def_haz_waste, step=100.0)

        st.markdown("<hr style='margin: 18px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)

        # Section 4: Water & Manufacturing Production
        st.markdown(f"<div style='font-size: 1.2rem; font-weight: 700; margin-bottom: 12px; display: flex; align-items: center;'>{feather_icon('droplet', color=COLOR_INFO, size=20)} <span>4. Water, Effluent & Manufacturing Output</span></div>", unsafe_allow_html=True)
        c_m1, c_m2, c_m3 = st.columns(3)
        with c_m1:
            inp_water = st.number_input("Water Consumption (m³ / yr)", min_value=0.0, value=def_water, step=500.0, help="Freshwater municipal meter volume")
            inp_wastewater = st.number_input("Wastewater Generated (m³ / yr)", min_value=0.0, value=def_wastewater, step=500.0, help="Effluent sent to municipal sewer or treatment plant")
        with c_m2:
            inp_raw_mat = st.number_input("Raw Material Used (tonnes / yr)", min_value=0.0, value=def_raw_mat, step=25.0, help="Virgin metal, plastic, flour, or textiles")
            inp_prod_qty = st.number_input("Production Quantity (units / yr)", min_value=0.0, value=def_prod_qty, step=5000.0, help="Finished goods manufactured or parcels delivered")
        with c_m3:
            inp_mach_hours = st.number_input("Machine Running Hours (hrs / yr)", min_value=0.0, value=def_mach_hours, step=200.0, help="Total active operating hours across manufacturing equipment")

        st.markdown("<hr style='margin: 18px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)

        # Section 5: Government Carbon Credits
        st.markdown(f"<div style='font-size: 1.2rem; font-weight: 700; margin-bottom: 12px; display: flex; align-items: center;'>{feather_icon('dollar-sign', color=COLOR_SUCCESS, size=20)} <span>5. Government Carbon Credits & Market Pricing</span></div>", unsafe_allow_html=True)
        c_c1, c_c2, c_c3 = st.columns(3)
        with c_c1:
            inp_credits = st.number_input("Total Carbon Credits Allocated (tonnes)", min_value=0.0, value=def_credits, step=25.0, help="Statutory compliance allowance assigned by environmental agency")
        with c_c2:
            inp_price = st.number_input("Carbon Credit Market Price ($ / tonne)", min_value=1.0, value=def_price, step=1.0, help="Prevailing spot carbon trading price")
        with c_c3:
            inp_bal = st.number_input("Current Credit Balance (tonnes)", min_value=0.0, value=def_bal, step=25.0, help="Current available credit reserve in registry")

        st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

        submit_setup = st.form_submit_button("Calculate Emissions, Diagnose Leaks & Save", type="primary", use_container_width=True)

        if submit_setup:
            updated_data = {
                "business_name": comp_name,
                "electricity_kwh": inp_elec,
                "renewable_pct": inp_renew,
                "diesel_liters": inp_diesel,
                "petrol_liters": inp_petrol,
                "gas_m3": inp_gas,
                "truck_km": inp_truck,
                "car_km": inp_car,
                "commute_km": inp_commute,
                "delivery_vehicles": inp_vehs,
                "organic_waste_kg": inp_org_waste,
                "plastic_waste_kg": inp_plas_waste,
                "metal_waste_kg": inp_met_waste,
                "paper_waste_kg": inp_pap_waste,
                "hazardous_waste_kg": inp_haz_waste,
                "water_m3": inp_water,
                "wastewater_m3": inp_wastewater,
                "raw_material_tonnes": inp_raw_mat,
                "production_units": inp_prod_qty,
                "machine_running_hours": inp_mach_hours,
                "total_credits": inp_credits,
                "credit_price": inp_price,
                "current_balance": inp_bal
            }

            results = calculate_detailed_emissions(updated_data)
            updated_data["total_co2"] = results["total_co2"]
            updated_data["total_cost"] = results["total_cost"]
            updated_data["sustainability_score"] = results["sustainability_score"]

            st.session_state["form_inputs"] = updated_data
            st.session_state["emissions_results"] = results

            # Persist to SQLite with demo isolation tag
            save_emissions_assessment(user_email, updated_data, is_demo=1 if is_demo else 0)

            st.success("Operational footprint saved & calculated! Redirecting to Dashboard...")
            st.session_state["current_step"] = 5
            st.rerun()

    # Back navigation
    col_back, _ = st.columns([1, 4])
    with col_back:
        if st.button("← Back to Step 2", key="setup_back"):
            st.session_state["current_step"] = 2
            st.rerun()

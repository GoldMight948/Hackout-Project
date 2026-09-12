import streamlit as st
import pandas as pd
import io
from components.data_presets import DEMO_BUSINESSES
from components.calculations import calculate_detailed_emissions
from components.auth import is_demo_session
from database.db_manager import save_emissions_assessment, log_audit
from components.icons import feather_icon, render_icon_heading, COLOR_WARNING, COLOR_SUCCESS, COLOR_NEUTRAL, COLOR_INFO

def render_upload_view():
    """Renders Step 4 Upload & Data Editor screen."""
    user = st.session_state.get("current_user", {})
    user_email = user.get("email", "guest@enterprise.com")
    is_demo = is_demo_session()

    st.markdown("""
        <div style="margin-bottom: 8px;">
            <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #10B981; font-weight: 700;">
                Step 4 — Data Ingestion & Live Table Editor
            </span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(render_icon_heading(
        "upload",
        "Upload Operational Spreadsheet or Use Demo Datasets",
        level="h2",
        color="#10B981",
        subtitle="Import existing utility records via CSV or Excel (.xlsx). You can also edit and fine-tune figures directly in the interactive grid below."
    ), unsafe_allow_html=True)

    # Demo Datasets Quick Switcher
    folder_icon = feather_icon("box", color=COLOR_NEUTRAL, size=16, margin_right=6)
    st.markdown(f"""
        <div class="saas-card" style="margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="font-weight: 700; font-size: 0.95rem; display: flex; align-items: center;">{folder_icon} 1-Click Load Calibrated Demo Industry Datasets:</span>
                <span class="badge-low">PRE-LOADED</span>
            </div>
    """, unsafe_allow_html=True)

    c_d1, c_d2, c_d3, c_d4 = st.columns(4)
    with c_d1:
        if st.button("Food Processing Demo", key="upload_demo_food", use_container_width=True):
            st.session_state["form_inputs"] = DEMO_BUSINESSES["food_processing"]["data"].copy()
            st.session_state["emissions_results"] = calculate_detailed_emissions(st.session_state["form_inputs"])
            st.success("Loaded Food Processing dataset!")
            st.rerun()
    with c_d2:
        if st.button("Retail Store Demo", key="upload_demo_retail", use_container_width=True):
            st.session_state["form_inputs"] = DEMO_BUSINESSES["retail_store"]["data"].copy()
            st.session_state["emissions_results"] = calculate_detailed_emissions(st.session_state["form_inputs"])
            st.success("Loaded Retail Store dataset!")
            st.rerun()
    with c_d3:
        if st.button("Logistics Company Demo", key="upload_demo_log", use_container_width=True):
            st.session_state["form_inputs"] = DEMO_BUSINESSES["logistics_company"]["data"].copy()
            st.session_state["emissions_results"] = calculate_detailed_emissions(st.session_state["form_inputs"])
            st.success("Loaded Logistics Fleet dataset!")
            st.rerun()
    with c_d4:
        if st.button("Manufacturing Plant Demo", key="upload_demo_mfg", use_container_width=True):
            st.session_state["form_inputs"] = DEMO_BUSINESSES["manufacturing_plant"]["data"].copy()
            st.session_state["emissions_results"] = calculate_detailed_emissions(st.session_state["form_inputs"])
            st.success("Loaded Manufacturing Plant dataset!")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # File Upload Section
    c_up1, c_up2 = st.columns([1.2, 0.8], gap="large")

    with c_up1:
        up_title = feather_icon("upload", color=COLOR_NEUTRAL, size=18, margin_right=6)
        st.markdown(f"""
            <div class="saas-card">
                <div class="saas-card-title" style="display: flex; align-items: center;">{up_title} Upload CSV or Excel Workbook</div>
                <div class="saas-card-subtitle">
                    Select a CSV or .xlsx file containing utility metrics, transport mileage, and waste weights:
                </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["csv", "xlsx", "xls"],
            help="File should contain activity headers (electricity_kwh, diesel_liters, truck_km, etc.)"
        )

        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df_uploaded = pd.read_csv(uploaded_file)
                else:
                    df_uploaded = pd.read_excel(uploaded_file)

                st.success(f"Successfully read `{uploaded_file.name}` ({len(df_uploaded)} rows)!")
                
                # If dataframe has records, take first row or column mappings
                first_row = df_uploaded.iloc[0].to_dict()
                curr_inputs = st.session_state.get("form_inputs", {})
                for k, v in first_row.items():
                    clean_k = str(k).lower().strip().replace(" ", "_")
                    if clean_k in curr_inputs or any(sub in clean_k for sub in ["elec", "diesel", "fuel", "gas", "truck", "waste", "water", "credit", "prod"]):
                        try:
                            curr_inputs[clean_k] = float(v)
                        except (ValueError, TypeError):
                            pass
                
                st.session_state["form_inputs"] = curr_inputs
                st.session_state["emissions_results"] = calculate_detailed_emissions(curr_inputs)
                log_audit(user_email, "FILE_UPLOAD", uploaded_file.name, "", f"{len(df_uploaded)} rows processed")
            except Exception as e:
                st.error(f"Error parsing file: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    with c_up2:
        dl_title = feather_icon("download", color=COLOR_NEUTRAL, size=18, margin_right=6)
        st.markdown(f"""
            <div class="saas-card">
                <div class="saas-card-title" style="display: flex; align-items: center;">{dl_title} Template Download</div>
                <div class="saas-card-subtitle">
                    Download an empty pre-formatted spreadsheet template with the required columns:
                </div>
        """, unsafe_allow_html=True)

        template_data = {
            "period_year": [2025],
            "electricity_kwh": [350000.0],
            "renewable_pct": [15.0],
            "diesel_liters": [12000.0],
            "petrol_liters": [4500.0],
            "gas_m3": [32000.0],
            "truck_km": [55000.0],
            "car_km": [18000.0],
            "commute_km": [75000.0],
            "delivery_vehicles": [6],
            "organic_waste_kg": [24000.0],
            "plastic_waste_kg": [16000.0],
            "metal_waste_kg": [8500.0],
            "paper_waste_kg": [14000.0],
            "hazardous_waste_kg": [1200.0],
            "water_m3": [6400.0],
            "wastewater_m3": [5200.0],
            "raw_material_tonnes": [380.0],
            "production_units": [150000.0],
            "machine_hours": [3200.0],
            "total_credits": [350.0],
            "credit_price": [38.0]
        }
        df_template = pd.DataFrame(template_data)
        csv_buffer = df_template.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📄 Download Blank CSV Template",
            data=csv_buffer,
            file_name="industrial_emissions_template.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

    # st.data_editor Section
    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
    st.markdown("""
        <div class="saas-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div>
                    <div class="saas-card-title">📝 Live Interactive Data Grid (st.data_editor)</div>
                    <div class="saas-card-subtitle">
                        Double-click any cell below to modify values directly. Changes will instantly update your carbon calculations.
                    </div>
                </div>
                <span class="badge-medium">EDITABLE GRID</span>
            </div>
    """, unsafe_allow_html=True)

    # Format current form inputs into a structured DataFrame for st.data_editor
    current_inputs = st.session_state.get("form_inputs", DEMO_BUSINESSES["manufacturing_plant"]["data"].copy())
    
    grid_rows = [
        {"Category": "Energy", "Metric": "Electricity Consumption", "Value": float(current_inputs.get("electricity_kwh", 350000.0)), "Unit": "kWh / yr"},
        {"Category": "Energy", "Metric": "On-Site Renewable Energy", "Value": float(current_inputs.get("renewable_pct", 15.0)), "Unit": "% Share"},
        {"Category": "Energy", "Metric": "Diesel Consumption", "Value": float(current_inputs.get("diesel_liters", 12000.0)), "Unit": "Liters / yr"},
        {"Category": "Energy", "Metric": "Petrol / Gasoline", "Value": float(current_inputs.get("petrol_liters", 4500.0)), "Unit": "Liters / yr"},
        {"Category": "Energy", "Metric": "Natural Gas Consumption", "Value": float(current_inputs.get("gas_m3", 32000.0)), "Unit": "m³ / yr"},
        {"Category": "Transport", "Metric": "Truck Freight Distance", "Value": float(current_inputs.get("truck_km", 55000.0)), "Unit": "km / yr"},
        {"Category": "Transport", "Metric": "Company Car Distance", "Value": float(current_inputs.get("car_km", 18000.0)), "Unit": "km / yr"},
        {"Category": "Transport", "Metric": "Employee Commute", "Value": float(current_inputs.get("commute_km", 75000.0)), "Unit": "km / yr"},
        {"Category": "Transport", "Metric": "Delivery Fleet Vehicles", "Value": float(current_inputs.get("delivery_vehicles", 6)), "Unit": "Count"},
        {"Category": "Waste", "Metric": "Organic Waste", "Value": float(current_inputs.get("organic_waste_kg", 24000.0)), "Unit": "kg / yr"},
        {"Category": "Waste", "Metric": "Plastic Waste", "Value": float(current_inputs.get("plastic_waste_kg", 16000.0)), "Unit": "kg / yr"},
        {"Category": "Waste", "Metric": "Metal Waste", "Value": float(current_inputs.get("metal_waste_kg", 8500.0)), "Unit": "kg / yr"},
        {"Category": "Waste", "Metric": "Paper & Cardboard", "Value": float(current_inputs.get("paper_waste_kg", 14000.0)), "Unit": "kg / yr"},
        {"Category": "Waste", "Metric": "Hazardous Waste", "Value": float(current_inputs.get("hazardous_waste_kg", 1200.0)), "Unit": "kg / yr"},
        {"Category": "Water", "Metric": "Water Consumption", "Value": float(current_inputs.get("water_m3", 6400.0)), "Unit": "m³ / yr"},
        {"Category": "Water", "Metric": "Wastewater Generated", "Value": float(current_inputs.get("wastewater_m3", 5200.0)), "Unit": "m³ / yr"},
        {"Category": "Manufacturing", "Metric": "Raw Material Used", "Value": float(current_inputs.get("raw_material_tonnes", 380.0)), "Unit": "tonnes / yr"},
        {"Category": "Manufacturing", "Metric": "Production Output Units", "Value": float(current_inputs.get("production_units", 150000.0)), "Unit": "units / yr"},
        {"Category": "Manufacturing", "Metric": "Machine Running Hours", "Value": float(current_inputs.get("machine_hours", 3200.0)), "Unit": "hrs / yr"},
        {"Category": "Carbon Credits", "Metric": "Allocated Carbon Credits", "Value": float(current_inputs.get("total_credits", 350.0)), "Unit": "Credits (t CO2)"},
        {"Category": "Carbon Credits", "Metric": "Carbon Credit Price", "Value": float(current_inputs.get("credit_price", 38.0)), "Unit": "$ / Credit"}
    ]

    df_editor = pd.DataFrame(grid_rows)
    edited_df = st.data_editor(
        df_editor,
        disabled=["Category", "Metric", "Unit"],
        column_config={
            "Value": st.column_config.NumberColumn("Reported Value", required=True, format="%.1f")
        },
        use_container_width=True,
        num_rows="fixed",
        key="data_editor_component"
    )

    c_save, c_dash = st.columns([1, 1])
    with c_save:
        if st.button("💾 Apply Grid Edits to Baseline", type="primary", use_container_width=True):
            # Parse edited_df back to form_inputs
            val_map = dict(zip(edited_df["Metric"], edited_df["Value"]))
            new_inputs = current_inputs.copy()
            new_inputs["electricity_kwh"] = val_map.get("Electricity Consumption", 350000.0)
            new_inputs["renewable_pct"] = val_map.get("On-Site Renewable Energy", 15.0)
            new_inputs["diesel_liters"] = val_map.get("Diesel Consumption", 12000.0)
            new_inputs["petrol_liters"] = val_map.get("Petrol / Gasoline", 4500.0)
            new_inputs["gas_m3"] = val_map.get("Natural Gas Consumption", 32000.0)
            new_inputs["truck_km"] = val_map.get("Truck Freight Distance", 55000.0)
            new_inputs["car_km"] = val_map.get("Company Car Distance", 18000.0)
            new_inputs["commute_km"] = val_map.get("Employee Commute", 75000.0)
            new_inputs["delivery_vehicles"] = int(val_map.get("Delivery Fleet Vehicles", 6))
            new_inputs["organic_waste_kg"] = val_map.get("Organic Waste", 24000.0)
            new_inputs["plastic_waste_kg"] = val_map.get("Plastic Waste", 16000.0)
            new_inputs["metal_waste_kg"] = val_map.get("Metal Waste", 8500.0)
            new_inputs["paper_waste_kg"] = val_map.get("Paper & Cardboard", 14000.0)
            new_inputs["hazardous_waste_kg"] = val_map.get("Hazardous Waste", 1200.0)
            new_inputs["water_m3"] = val_map.get("Water Consumption", 6400.0)
            new_inputs["wastewater_m3"] = val_map.get("Wastewater Generated", 5200.0)
            new_inputs["raw_material_tonnes"] = val_map.get("Raw Material Used", 380.0)
            new_inputs["production_units"] = val_map.get("Production Output Units", 150000.0)
            new_inputs["machine_hours"] = val_map.get("Machine Running Hours", 3200.0)
            new_inputs["total_credits"] = val_map.get("Allocated Carbon Credits", 350.0)
            new_inputs["credit_price"] = val_map.get("Carbon Credit Price", 38.0)

            st.session_state["form_inputs"] = new_inputs
            st.session_state["emissions_results"] = calculate_detailed_emissions(new_inputs)
            save_emissions_assessment(user_email, new_inputs, is_demo=1 if is_demo else 0)
            st.success("✅ Changes saved to database and recalculations completed!")
            st.rerun()

    with c_dash:
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("📅 Daily & Weekly Logs →", use_container_width=True):
                st.session_state["nav_section"] = "activity_logs"
                st.rerun()
        with col_btn2:
            if st.button("Proceed to Dashboard →", type="primary", use_container_width=True):
                st.session_state["current_step"] = 5
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

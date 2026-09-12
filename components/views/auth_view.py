"""
Step 2: Authentication View.
Supports User Login, Business Profile Creation stored in SQLite,
multi-user role assignment (Admin/Employee), and 1-click verified enterprise demo access.
"""

import streamlit as st
from database.db_manager import authenticate_user, register_user, save_emissions_assessment
from components.auth import login_user_session, quick_demo_login
from components.data_presets import DEMO_USERS, DEMO_BUSINESSES
from components.icons import feather_icon, render_icon_heading, COLOR_PRIMARY, COLOR_NEUTRAL, COLOR_SUCCESS, COLOR_WARNING
from components.geo_data import get_country_list, get_states_for_country
from components.calculations import get_statutory_carbon_quota, calculate_detailed_emissions

def render_auth_view():
    """Renders Login & Create Business Profile screen."""
    
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 24px;">
            <div style="display: flex; justify-content: center; margin-bottom: 10px;">
                <div style="background: rgba(16, 185, 129, 0.12); padding: 16px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center;">
                    {feather_icon('lock', color=COLOR_PRIMARY, size=36, margin_right=0)}
                </div>
            </div>
            <h2 style="font-size: 1.85rem; font-weight: 800; margin-top: 4px; margin-bottom: 6px;">
                Enterprise Sustainability Portal
            </h2>
            <p style="font-size: 0.95rem; color: var(--text-muted); max-width: 600px; margin: 0 auto;">
                Securely log in to manage your facility's emissions or register your business to start tracking carbon leaks and government credits.
            </p>
        </div>
    """, unsafe_allow_html=True)

    default_tab_idx = 1 if st.session_state.get("auth_tab") == "register" else 0
    tab_login, tab_register, tab_demo = st.tabs(["Sign In", "Create Business Profile", "1-Click Demo Profiles"])

    # 1. Sign In Tab
    with tab_login:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown(f"""
                <div class="saas-card">
                    <div class="saas-card-title" style="margin-bottom: 12px;">{feather_icon('user', color=COLOR_NEUTRAL, size=18)} Sign In to Your Account</div>
            """, unsafe_allow_html=True)

            with st.form("login_form"):
                login_email = st.text_input("Work Email Address", placeholder="e.g. alex@greenbite.com")
                login_password = st.text_input("Password", type="password", placeholder="••••••••")
                submit_login = st.form_submit_button("Sign In", type="primary", use_container_width=True)

                if submit_login:
                    if not login_email or not login_password:
                        st.error("Please enter both email and password.")
                    else:
                        user = authenticate_user(login_email, login_password)
                        if user:
                            st.success(f"Welcome back, {user['owner_name']}! Loading workspace...")
                            login_user_session(user)
                        else:
                            st.error("Invalid credentials. Please verify your email and password, or use a 1-Click Demo profile.")

            st.markdown("</div>", unsafe_allow_html=True)

    # 2. Create Business Profile Tab
    with tab_register:
        st.markdown(f"""
            <div class="saas-card">
                <div class="saas-card-title" style="margin-bottom: 6px;">{feather_icon('user', color=COLOR_NEUTRAL, size=18)} Register Facility & Production Workspace</div>
                <div class="saas-card-subtitle" style="margin-bottom: 16px;">
                    Stored securely in your local SQLite database. <strong>Production workspaces are completely isolated from demo sandbox data.</strong>
                </div>
        """, unsafe_allow_html=True)

        col_p1, col_p2 = st.columns(2, gap="medium")
        
        with col_p1:
            p_comp_name = st.text_input("Company / Business Name *", placeholder="e.g. Apex Precision Metalworks", key="reg_comp_name")
            p_owner_name = st.text_input("Primary Contact / Lead Name *", placeholder="e.g. David Kovac", key="reg_owner_name")
            p_email = st.text_input("Corporate Email Address *", placeholder="e.g. d.kovac@apexmetal.com", key="reg_email")
            p_password = st.text_input("Password *", type="password", placeholder="Create secure password", key="reg_password")
            p_role = st.selectbox("Your Role in Organization", ["Admin (Full Access & Settings)", "Sustainability Lead", "Facility Engineer", "Employee (Read & Submit)"], key="reg_role")
            p_comp_type = st.selectbox("Company Type", [
                "SME / Mid-Sized Business",
                "Heavy Industrial Manufacturer",
                "Retail / Distribution",
                "Logistics Fleet Operator",
                "Enterprise / Corporation"
            ], key="reg_comp_type")

        with col_p2:
            p_industry = st.selectbox("Primary Sector / Industry *", [
                "Manufacturing Plant",
                "Heavy Industrial Manufacturer",
                "Chemicals & Plastics",
                "Food Processing",
                "Logistics Company",
                "Retail Store",
                "Hospitality & Cafe",
                "Other Commercial"
            ], key="reg_industry")
            p_employees = st.number_input("Number of Employees", min_value=1, max_value=50000, value=65, step=5, key="reg_employees")
            p_revenue = st.number_input("Annual Revenue ($ USD, Optional)", min_value=0.0, max_value=1000000000.0, value=4500000.0, step=100000.0, key="reg_revenue")
            
            # Dynamic Country & State dropdowns
            country_options = get_country_list()
            default_country_idx = country_options.index("India") if "India" in country_options else 0
            p_country = st.selectbox("Country *", country_options, index=default_country_idx, key="reg_country_select")
            
            state_options = get_states_for_country(p_country)
            p_state = st.selectbox("State / Province / Region *", state_options, key=f"reg_state_select_{p_country}")
            
            p_location = st.text_input("Factory / Facility Location", placeholder="e.g. Plant #3 - Industrial Zone", key="reg_location")

        # Dynamic Research-Backed Statutory Carbon Quota Live Indicator
        quota_info = get_statutory_carbon_quota(p_industry, p_comp_type, int(p_employees))
        st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.28); border-radius: 10px; padding: 14px 18px; margin: 18px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                    <div>
                        <div style="font-weight: 700; font-size: 0.95rem; color: #065F46; display: flex; align-items: center;">
                            {feather_icon('award', color='#10B981', size=16, margin_right=6)} Statutory Carbon Credit Quota (EPA / CARB / CCTS Calibrated)
                        </div>
                        <div style="font-size: 0.83rem; color: #047857; margin-top: 3px;">
                            Regulatory Regime: <strong>{quota_info['regulatory_regime']}</strong>
                        </div>
                        <div style="font-size: 0.80rem; color: var(--text-muted); margin-top: 2px;">
                            {quota_info['description']} • Base {quota_info['annual_per_employee_co2']} t/emp × {quota_info['type_multiplier']}x type multiplier
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.65rem; font-weight: 800; color: #10B981; line-height: 1.1;">
                            {quota_info['quota_credits']:,.0f}
                        </div>
                        <div style="font-size: 0.75rem; color: #065F46; font-weight: 600;">Government Carbon Credits</div>
                        <div style="font-size: 0.74rem; color: var(--text-muted);">Benchmark Price: ${quota_info['benchmark_price']:.0f}/tonne</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        submit_reg = st.button("Create Business Profile & Enter Workspace", type="primary", use_container_width=True, key="btn_create_profile_submit")

        if submit_reg:
            if not p_comp_name.strip() or not p_owner_name.strip() or not p_email.strip() or not p_password.strip():
                st.error("Please fill in all required fields (marked with *).")
            else:
                success = register_user(
                    email=p_email,
                    password=p_password,
                    company_name=p_comp_name,
                    owner_name=p_owner_name,
                    role="Admin" if "Admin" in p_role else "Employee",
                    company_type=p_comp_type,
                    industry=p_industry,
                    employees=int(p_employees),
                    annual_revenue=float(p_revenue),
                    country=p_country,
                    state=p_state,
                    location=p_location,
                    is_demo=0
                )
                if success:
                    # Save initial baseline assessment with calibrated statutory carbon credits
                    init_inputs = {
                        "business_name": p_comp_name,
                        "industry": p_industry,
                        "company_type": p_comp_type,
                        "employees": int(p_employees),
                        "annual_revenue": float(p_revenue),
                        "country": p_country,
                        "state": p_state,
                        "location": p_location,
                        "total_credits": quota_info["quota_credits"],
                        "credit_price": quota_info["benchmark_price"],
                        "electricity_kwh": 0.0,
                        "renewable_pct": 0.0,
                        "diesel_liters": 0.0,
                        "petrol_liters": 0.0,
                        "gas_m3": 0.0,
                        "truck_km": 0.0,
                        "car_km": 0.0,
                        "commute_km": 0.0,
                        "delivery_vehicles": 0,
                        "organic_waste_kg": 0.0,
                        "plastic_waste_kg": 0.0,
                        "metal_waste_kg": 0.0,
                        "paper_waste_kg": 0.0,
                        "hazardous_waste_kg": 0.0,
                        "water_m3": 0.0,
                        "wastewater_m3": 0.0,
                        "raw_material_tonnes": 0.0,
                        "production_units": 0.0,
                        "machine_hours": 0.0,
                    }
                    res_init = calculate_detailed_emissions(init_inputs)
                    init_inputs["total_co2"] = res_init["total_co2"]
                    init_inputs["total_cost"] = res_init["total_cost"]
                    init_inputs["sustainability_score"] = res_init["sustainability_score"]
                    save_emissions_assessment(p_email, init_inputs, is_demo=0)

                    st.success("Business profile created successfully! Initializing production workspace...")
                    user = authenticate_user(p_email, p_password)
                    if user:
                        login_user_session(user)
                else:
                    st.error("An account with this email address already exists. Please sign in instead.")

        st.markdown("</div>", unsafe_allow_html=True)


    # 3. Quick Demo Login Tab (Isolated Sandbox)
    with tab_demo:
        st.markdown(f"""
            <div class="saas-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <div>
                        <div class="saas-card-title">{feather_icon('zap', color=COLOR_WARNING, size=18)} Isolated Demo Sandbox Profiles</div>
                        <div class="saas-card-subtitle">
                            Instantly test the full platform with realistic operational data across 4 core industries. Demo data is sandboxed and can be reset at any time:
                        </div>
                    </div>
                    <span class="badge-medium">SANDBOX MODE</span>
                </div>
        """, unsafe_allow_html=True)

        d_cols = st.columns(4, gap="medium")
        for idx, (email, user) in enumerate(DEMO_USERS.items()):
            preset = DEMO_BUSINESSES[user["preset_key"]]
            with d_cols[idx]:
                st.markdown(f"""
                    <div style="background: var(--bg-subtle); border: 1px solid var(--border-color); border-radius: 12px; padding: 14px; height: 170px; display: flex; flex-direction: column; justify-content: space-between;">
                        <div>
                            <div style="margin-bottom: 8px;">{feather_icon('user', color=COLOR_PRIMARY, size=24, margin_right=0)}</div>
                            <div style="font-weight: 700; font-size: 0.95rem;">{user['name']}</div>
                            <div style="font-size: 0.78rem; color: var(--text-muted);">{user['company']}</div>
                            <div style="font-size: 0.74rem; color: #10B981; font-weight: 600; margin-top: 4px;">{preset['type_label']}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                if st.button(f"Sign In as {user['name'].split()[0]}", key=f"demo_btn_{email}", use_container_width=True):
                    quick_demo_login(email)

        st.markdown("</div>", unsafe_allow_html=True)

    # Back navigation
    col_b, _ = st.columns([1, 4])
    with col_b:
        if st.button("← Back to Landing", key="auth_back_landing"):
            st.session_state["current_step"] = 1
            st.rerun()

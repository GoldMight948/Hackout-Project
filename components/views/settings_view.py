"""
Step 12: Settings & Administration View.
Enables user profile editing, updating carbon credit spot prices,
customizing GHG Protocol emission factors, and managing user roles.
"""

import streamlit as st
from database.db_manager import update_user_profile, get_user_profile
from components.auth import logout_user
from components.calculations import EMISSION_FACTORS, COST_FACTORS, calculate_detailed_emissions
from components.icons import feather_icon, render_icon_heading, COLOR_SECONDARY, COLOR_NEUTRAL, COLOR_SUCCESS

def render_settings_view():
  """Renders Step 12 Settings screen."""
  user = st.session_state.get("current_user", {})
  user_email = user.get("email", "guest@enterprise.com")
  db_profile = get_user_profile(user_email) or user

  st.markdown("""
    <div style="margin-bottom: 8px;">
      <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #CBDED3; font-weight: 700;">
        Step 12 — Platform Settings & Enterprise Configuration
      </span>
    </div>
  """, unsafe_allow_html=True)
  st.markdown(render_icon_heading(
    "settings",
    "Configuration & Emission Factor Settings",
    level="h2",
    color=COLOR_SECONDARY,
    subtitle="Update organization details, calibrate regional carbon market prices, and manage user roles."
  ), unsafe_allow_html=True)

  tab_profile, tab_factors, tab_account = st.tabs([
    "Business Profile", "Emission Factors & Pricing", "Account & Role"
  ])

  # Tab 1: Business Profile
  with tab_profile:
    st.markdown(f"""
      <div class="saas-card">
        <div class="saas-card-title">{feather_icon('user', color=COLOR_NEUTRAL, size=18)} Edit Company Information</div>
        <div class="saas-card-subtitle" style="margin-bottom: 16px;">
          Update your facility name, operational address, and industry taxonomy:
        </div>
    """, unsafe_allow_html=True)

    with st.form("edit_profile_form"):
      cp1, cp2 = st.columns(2)
      with cp1:
        e_comp = st.text_input("Company Name", value=db_profile.get("company_name", ""))
        e_owner = st.text_input("Lead / Contact Name", value=db_profile.get("owner_name", ""))
        e_emp = st.number_input("Employees", min_value=1, value=int(db_profile.get("employees", 50)))
      with cp2:
        e_ind = st.selectbox("Industry", ["Manufacturing Plant", "Food Processing", "Logistics Company", "Retail Store", "Hospitality & Cafe", "Other"], index=0)
        e_state = st.text_input("State / Province", value=db_profile.get("state", "California"))
        e_loc = st.text_input("Facility Plant Location", value=db_profile.get("location", "Plant #1"))

      save_profile_btn = st.form_submit_button("Save Profile Changes", type="primary", use_container_width=True)
      if save_profile_btn:
        updates = {
          "company_name": e_comp,
          "owner_name": e_owner,
          "employees": int(e_emp),
          "industry": e_ind,
          "state": e_state,
          "location": e_loc
        }
        update_user_profile(user_email, updates)
        # Update current_user in session
        st.session_state["current_user"].update(updates)
        st.success("Profile updated successfully in SQLite!")
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

  # Tab 3: Emission Factors & Carbon Price
  with tab_factors:
    st.markdown(f"""
      <div class="saas-card">
        <div class="saas-card-title">{feather_icon('sliders', color=COLOR_NEUTRAL, size=18)} GHG Protocol Emission Factors & Spot Carbon Price</div>
        <div class="saas-card-subtitle" style="margin-bottom: 16px;">
          Fine-tune regional emission coefficients (e.g. state grid intensity or localized fuel blends):
        </div>
    """, unsafe_allow_html=True)

    with st.form("factors_form"):
      cf1, cf2 = st.columns(2)
      with cf1:
        f_price = st.number_input("Carbon Credit Market Price (₹/tonne)", min_value=1.0, value=float(st.session_state.get("form_inputs", {}).get("credit_price", 38.0)), step=1.0)
        f_elec = st.number_input("Grid Electricity Factor (t CO₂e/kWh)", min_value=0.00001, max_value=0.005, value=float(EMISSION_FACTORS["electricity_grid"]), format="%.5f")
        f_diesel = st.number_input("Diesel Combustion Factor (t CO₂e/L)", min_value=0.0001, max_value=0.01, value=float(EMISSION_FACTORS["diesel"]), format="%.5f")
      with cf2:
        f_truck = st.number_input("Truck Transport Factor (t CO₂e/km)", min_value=0.0001, max_value=0.01, value=float(EMISSION_FACTORS["truck"]), format="%.5f")
        f_plas = st.number_input("Plastic Waste Factor (t CO₂e/kg)", min_value=0.0001, max_value=0.01, value=float(EMISSION_FACTORS["waste_plastic"]), format="%.5f")
        f_gas = st.number_input("Natural Gas Factor (t CO₂e/m³)", min_value=0.0001, max_value=0.01, value=float(EMISSION_FACTORS["natural_gas"]), format="%.5f")

      save_factors_btn = st.form_submit_button("Update Emission Coefficients & Recalculate", type="primary", use_container_width=True)
      if save_factors_btn:
        EMISSION_FACTORS["electricity_grid"] = f_elec
        EMISSION_FACTORS["diesel"] = f_diesel
        EMISSION_FACTORS["truck"] = f_truck
        EMISSION_FACTORS["waste_plastic"] = f_plas
        EMISSION_FACTORS["natural_gas"] = f_gas

        if "form_inputs" in st.session_state and st.session_state["form_inputs"]:
          st.session_state["form_inputs"]["credit_price"] = f_price
          st.session_state["emissions_results"] = calculate_detailed_emissions(st.session_state["form_inputs"])
        st.success("Emission factors and credit pricing updated! Baseline recalculated.")
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

  # Tab 4: Account & Multi-User Roles
  with tab_account:
    st.markdown(f"""
      <div class="saas-card">
        <div class="saas-card-title">{feather_icon('shield', color=COLOR_NEUTRAL, size=18)} User Account & Permission Role</div>
        <div style="margin-top: 10px; font-size: 0.9rem;">
          <div>Signed in as: <strong>{db_profile.get('owner_name', 'User')}</strong> ({user_email})</div>
          <div style="margin-top: 4px;">Assigned Role: <span class="badge-low">{db_profile.get('role', 'Admin')}</span></div>
          <div style="margin-top: 4px; color: var(--text-muted); font-size: 0.82rem;">
            Admin privileges enable editing emission factors, saving assessments, and executing carbon market orders.
          </div>
        </div>
        <hr style="margin: 20px 0; border: none; border-top: 1px solid var(--border-color);"/>
    """, unsafe_allow_html=True)

    if st.button("Sign Out of Platform", key="settings_logout_btn", type="primary", use_container_width=True):
      logout_user()

    st.markdown("</div>", unsafe_allow_html=True)

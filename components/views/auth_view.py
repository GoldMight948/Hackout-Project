"""
Step 2: Authentication View.
Supports User Login, Business Profile Creation stored in SQLite,
multi-user role assignment (Admin/Employee), and 1-click verified enterprise demo access.
"""

import streamlit as st
from database.db_manager import authenticate_user, register_user
from components.auth import login_user_session, quick_demo_login
from components.data_presets import DEMO_USERS, DEMO_BUSINESSES

def render_auth_view():
    """Renders Login & Create Business Profile screen."""
    
    st.markdown("""
        <div style="text-align: center; margin-bottom: 24px;">
            <span style="font-size: 2.4rem;">🔐</span>
            <h2 style="font-size: 1.85rem; font-weight: 800; margin-top: 4px; margin-bottom: 6px;">
                Enterprise Sustainability Portal
            </h2>
            <p style="font-size: 0.95rem; color: var(--text-muted); max-width: 600px; margin: 0 auto;">
                Securely log in to manage your facility's emissions or register your business to start tracking carbon leaks and government credits.
            </p>
        </div>
    """, unsafe_allow_html=True)

    default_tab_idx = 1 if st.session_state.get("auth_tab") == "register" else 0
    tab_login, tab_register, tab_demo = st.tabs(["🔑 Sign In", "🏢 Create Business Profile", "⚡ 1-Click Demo Profiles"])

    # 1. Sign In Tab
    with tab_login:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("""
                <div class="saas-card">
                    <div class="saas-card-title" style="margin-bottom: 12px;">Sign In to Your Account</div>
            """, unsafe_allow_html=True)

            with st.form("login_form"):
                login_email = st.text_input("Work Email Address", placeholder="e.g. alex@greenbite.com")
                login_password = st.text_input("Password", type="password", placeholder="••••••••")
                submit_login = st.form_submit_button("Sign In →", type="primary", use_container_width=True)

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
        st.markdown("""
            <div class="saas-card">
                <div class="saas-card-title" style="margin-bottom: 6px;">Register Facility & Business Profile</div>
                <div class="saas-card-subtitle" style="margin-bottom: 16px;">
                    Stored securely in the local SQLite persistence layer. This information calibrates your emissions baseline.
                </div>
        """, unsafe_allow_html=True)

        with st.form("create_profile_form"):
            col_p1, col_p2 = st.columns(2, gap="medium")
            
            with col_p1:
                p_comp_name = st.text_input("Company / Business Name *", placeholder="e.g. Apex Precision Metalworks")
                p_owner_name = st.text_input("Primary Contact / Lead Name *", placeholder="e.g. David Kovac")
                p_email = st.text_input("Corporate Email Address *", placeholder="e.g. d.kovac@apexmetal.com")
                p_password = st.text_input("Password *", type="password", placeholder="Create secure password")
                p_role = st.selectbox("Your Role in Organization", ["Admin (Full Access & Settings)", "Sustainability Lead", "Facility Engineer", "Employee (Read & Submit)"])
                p_comp_type = st.selectbox("Company Type", ["SME / Mid-Sized Business", "Heavy Industrial Manufacturer", "Retail / Distribution", "Logistics Fleet Operator", "Enterprise / Corporation"])

            with col_p2:
                p_industry = st.selectbox("Primary Sector / Industry *", ["Manufacturing Plant", "Food Processing", "Logistics Company", "Retail Store", "Hospitality & Cafe", "Chemicals & Plastics", "Other Commercial"])
                p_employees = st.number_input("Number of Employees", min_value=1, max_value=50000, value=65, step=5)
                p_revenue = st.number_input("Annual Revenue ($ USD, Optional)", min_value=0.0, max_value=1000000000.0, value=4500000.0, step=100000.0)
                p_country = st.text_input("Country", value="United States")
                p_state = st.text_input("State / Region", value="Ohio")
                p_location = st.text_input("Factory / Facility Location", placeholder="e.g. Plant #3 - Cleveland West Park")

            submit_reg = st.form_submit_button("Create Business Profile & Enter Setup →", type="primary", use_container_width=True)

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
                        location=p_location
                    )
                    if success:
                        st.success("Business profile created successfully! Initializing workspace...")
                        user = authenticate_user(p_email, p_password)
                        if user:
                            login_user_session(user)
                    else:
                        st.error("An account with this email address already exists. Please sign in instead.")

        st.markdown("</div>", unsafe_allow_html=True)

    # 3. Quick Demo Login Tab
    with tab_demo:
        st.markdown("""
            <div class="saas-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <div>
                        <div class="saas-card-title">Instant 1-Click Verified Demo Accounts</div>
                        <div class="saas-card-subtitle">
                            Instantly test the full platform with realistic operational data across 4 core industries:
                        </div>
                    </div>
                    <span class="badge-low">NO SETUP REQUIRED</span>
                </div>
        """, unsafe_allow_html=True)

        d_cols = st.columns(4, gap="medium")
        for idx, (email, user) in enumerate(DEMO_USERS.items()):
            preset = DEMO_BUSINESSES[user["preset_key"]]
            with d_cols[idx]:
                st.markdown(f"""
                    <div style="background: var(--bg-subtle); border: 1px solid var(--border-color); border-radius: 12px; padding: 14px; height: 170px; display: flex; flex-direction: column; justify-content: space-between;">
                        <div>
                            <div style="font-size: 1.6rem; margin-bottom: 4px;">{user['avatar']}</div>
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

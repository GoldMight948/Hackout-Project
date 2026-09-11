"""
Authentication and Demo User Switcher module for Streamlit.
Supports one-click login as pre-configured business personas or custom credentials.
"""

import streamlit as st
from components.data_presets import DEMO_USERS, DEMO_BUSINESSES

def init_auth_state():
    """Ensures authentication state variables exist."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "current_user" not in st.session_state:
        st.session_state["current_user"] = None

def login_as_user(email: str):
    """Logs in using a demo user preset and automatically loads their business baseline."""
    user_info = DEMO_USERS.get(email)
    if user_info:
        st.session_state["authenticated"] = True
        st.session_state["current_user"] = user_info
        
        # Auto-populate the form data for this persona if not already populated
        preset_key = user_info.get("preset_key")
        if preset_key and preset_key in DEMO_BUSINESSES:
            preset = DEMO_BUSINESSES[preset_key]["data"]
            st.session_state["form_inputs"] = preset.copy()
            st.session_state["active_preset"] = preset_key
        st.rerun()

def login_custom(name: str, company: str, business_type: str):
    """Logs in with custom entered credentials."""
    st.session_state["authenticated"] = True
    st.session_state["current_user"] = {
        "name": name.strip() or "Guest Business",
        "company": company.strip() or "My Enterprise",
        "role": "Sustainability Lead",
        "avatar": "🌱",
        "preset_key": "custom"
    }
    if "form_inputs" not in st.session_state:
        st.session_state["form_inputs"] = {
            "business_name": company.strip() or "My Enterprise",
            "business_type": business_type,
            "electricity": 45000.0,
            "fuel": 4000.0,
            "waste": 5000.0,
            "transport": 20000.0,
            "production_units": 10000.0
        }
    st.rerun()

def logout_user():
    """Logs out current user and resets session."""
    st.session_state["authenticated"] = False
    st.session_state["current_user"] = None
    st.rerun()

def render_login_view():
    """Renders clean, minimal, non-technical login screen with 1-click demo profiles."""
    st.markdown("""
        <div style="text-align: center; margin-top: 20px; margin-bottom: 30px;">
            <span style="font-size: 3rem;">🌿</span>
            <h1 style="font-size: 2.2rem; font-weight: 800; color: #065F46; margin-top: 8px; margin-bottom: 6px;">
                Emission Leak Detector
            </h1>
            <p style="font-size: 1.05rem; color: #64748B; max-width: 550px; margin: 0 auto;">
                Find hidden energy & carbon leaks in your business operations, unlock green fixes, and calculate instant cost savings.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.1, 0.9], gap="large")

    with col1:
        st.markdown("""
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 14px; padding: 22px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
                    <h3 style="font-size: 1.15rem; font-weight: 700; color: #0F172A; margin: 0;">⚡ Quick Demo Login</h3>
                    <span style="background: #ECFDF5; color: #047857; font-size: 0.75rem; font-weight: 700; padding: 3px 8px; border-radius: 6px;">1-CLICK ACCESS</span>
                </div>
                <p style="font-size: 0.88rem; color: #64748B; margin-bottom: 18px;">
                    Select any pre-configured small business profile to test the dashboard with realistic operational numbers:
                </p>
        """, unsafe_allow_html=True)

        for email, user in DEMO_USERS.items():
            b_info = DEMO_BUSINESSES[user["preset_key"]]
            c_left, c_btn = st.columns([2.2, 1.0])
            with c_left:
                st.markdown(f"""
                    <div style="padding: 6px 0;">
                        <span style="font-size: 1.2rem; margin-right: 6px;">{user['avatar']}</span>
                        <strong style="font-size: 0.95rem; color: #1E293B;">{user['name']}</strong>
                        <div style="font-size: 0.8rem; color: #64748B; padding-left: 28px;">{user['company']} &bull; <em>{b_info['type_label']}</em></div>
                    </div>
                """, unsafe_allow_html=True)
            with c_btn:
                if st.button(f"Sign In as {user['name'].split()[0]}", key=f"btn_login_{email}", use_container_width=True):
                    login_as_user(email)
            st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px solid #F1F5F9;'/>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 14px; padding: 22px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                <h3 style="font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-bottom: 8px;">🏢 Custom Business Login</h3>
                <p style="font-size: 0.88rem; color: #64748B; margin-bottom: 16px;">
                    Or enter your own team name to start a custom assessment from scratch.
                </p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("custom_login_form"):
            c_name = st.text_input("Your Full Name", value="Elena Rostova", placeholder="e.g. Jordan Miller")
            c_comp = st.text_input("Business or Facility Name", value="Peak Craft Bakery & Cafe", placeholder="e.g. Acme Manufacturing")
            c_type = st.selectbox(
                "Primary Industry / Sector",
                ["Food Processing / Bakery", "Retail / Boutique", "Logistics & Transport", "Hospitality & Restaurant", "Light Manufacturing", "Office / Professional Services"]
            )
            submit_custom = st.form_submit_button("Enter App & Start Assessment →", type="primary", use_container_width=True)
            if submit_custom:
                login_custom(c_name, c_comp, c_type)

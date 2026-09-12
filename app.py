"""
Main Application Entry Point: Industrial Emission Leak-Point Detector & Circular Alternative Recommender
Built with Streamlit, Plotly, Pandas, NumPy, and SQLite.
Designed as an enterprise-grade SaaS analytics platform (similar to Microsoft Power BI & Tableau).
"""

import streamlit as st

# Streamlit Page Configuration must be the first command
st.set_page_config(
    page_title="Industrial Emission Leak-Point Detector & Circular OS",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

from components.styles import inject_custom_css
from components.auth import init_auth_state, logout_user, quick_demo_login
from components.data_presets import DEMO_BUSINESSES
from components.calculations import calculate_detailed_emissions

# Import all 12 views
from components.views.landing_view import render_landing_view
from components.views.auth_view import render_auth_view
from components.views.setup_view import render_setup_view
from components.views.upload_view import render_upload_view
from components.views.dashboard_view import render_dashboard_view
from components.views.analytics_view import render_analytics_view
from components.views.leak_detection_view import render_leak_detection_view
from components.views.carbon_credits_view import render_carbon_credits_view
from components.views.recommendations_view import render_recommendations_view
from components.views.simulator_view import render_simulator_view
from components.views.circular_view import render_circular_view
from components.views.reports_view import render_reports_view
from components.views.settings_view import render_settings_view

# 12-Step Guided Stages
STEPS = [
    {"num": 1, "id": "landing", "name": "Landing", "icon": "🌐"},
    {"num": 2, "id": "auth", "name": "Auth", "icon": "🔐"},
    {"num": 3, "id": "setup", "name": "Setup", "icon": "🏢"},
    {"num": 4, "id": "upload", "name": "Upload", "icon": "📥"},
    {"num": 5, "id": "dashboard", "name": "Dashboard", "icon": "🏠"},
    {"num": 6, "id": "leak_detection", "name": "Leaks", "icon": "🔥"},
    {"num": 7, "id": "carbon_credits", "name": "Credits", "icon": "🌍"},
    {"num": 8, "id": "recommendations", "name": "AI Fixes", "icon": "💡"},
    {"num": 9, "id": "simulator", "name": "Simulator", "icon": "📈"},
    {"num": 10, "id": "circular", "name": "Circular", "icon": "♻️"},
    {"num": 11, "id": "reports", "name": "Reports", "icon": "📄"},
    {"num": 12, "id": "settings", "name": "Settings", "icon": "⚙️"},
]

def init_app_state():
    """Initializes global session state keys."""
    init_auth_state()
    if "current_step" not in st.session_state:
        st.session_state["current_step"] = 1
    if "nav_section" not in st.session_state:
        st.session_state["nav_section"] = "dashboard"
    if "form_inputs" not in st.session_state:
        st.session_state["form_inputs"] = {}
    if "emissions_results" not in st.session_state:
        st.session_state["emissions_results"] = None
    if "theme_mode" not in st.session_state:
        st.session_state["theme_mode"] = "light"

def render_top_stepper():
    """Renders sleek top breadcrumbs progress bar."""
    cur = st.session_state.get("current_step", 1)
    
    pills_html = ""
    for s in STEPS:
        num = s["num"]
        icon = s["icon"]
        name = s["name"]
        if num == cur:
            css_class = "step-pill active"
        elif num < cur:
            css_class = "step-pill completed"
        else:
            css_class = "step-pill upcoming"
        pills_html += f'<span class="{css_class}">{icon} {num}. {name}</span>'

    st.markdown(f"""
        <div class="step-indicator-wrapper">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.4rem;">🌍</span>
                <span style="font-weight: 800; font-size: 1.05rem; letter-spacing: -0.01em;">Industrial Emission Leak Detector</span>
                <span class="step-badge">Stage {cur} of {len(STEPS)}: {STEPS[cur-1]['name']}</span>
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 4px;">
                {pills_html}
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Renders modern SaaS sidebar with navigation icons, notifications, and presets."""
    user = st.session_state.get("current_user", {})
    user_name = user.get("owner_name", user.get("name", "David Kovac"))
    user_company = user.get("company_name", user.get("company", "Apex Precision Metalworks"))
    user_role = user.get("role", "Admin")
    user_avatar = user.get("avatar", "🏭")
    
    with st.sidebar:
        # Organization Card
        st.markdown(f"""
            <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 14px; margin-bottom: 16px; box-shadow: var(--shadow-card);">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 2rem;">{user_avatar}</span>
                    <div>
                        <div style="font-weight: 800; font-size: 0.95rem; color: var(--text-primary);">{user_company}</div>
                        <div style="font-size: 0.78rem; color: var(--text-muted);">{user_name} &bull; <span style="color: #10B981; font-weight: 700;">{user_role}</span></div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Main Navigation List (as requested in spec)
        st.markdown("##### 📌 Platform Navigation")

        nav_items = [
            ("🏠 Dashboard", "dashboard", 5),
            ("🏢 Company Profile", "setup", 3),
            ("📥 Upload Data", "upload", 4),
            ("📊 Analytics", "analytics", 5),
            ("🌍 Carbon Credits", "carbon_credits", 7),
            ("🔥 Leak Detection", "leak_detection", 6),
            ("♻ Recommendations", "recommendations", 8),
            ("📈 Simulator", "simulator", 9),
            ("📄 Reports", "reports", 11),
            ("⚙ Settings", "settings", 12),
        ]

        cur_nav = st.session_state.get("nav_section", "dashboard")

        for label, section_key, step_target in nav_items:
            is_active = (cur_nav == section_key)
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_btn_{section_key}", type=btn_type, use_container_width=True):
                st.session_state["nav_section"] = section_key
                st.session_state["current_step"] = step_target
                st.rerun()

        st.markdown("<hr style='margin: 16px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)

        # Quick Theme Mode Toggle
        curr_th = st.session_state.get("theme_mode", "light")
        th_label = "🌙 Dark Mode" if curr_th == "light" else "☀️ Light Mode"
        if st.button(th_label, key="quick_theme_toggle", use_container_width=True):
            st.session_state["theme_mode"] = "dark" if curr_th == "light" else "light"
            st.rerun()

        # Notification Panel
        st.markdown("##### 🔔 Compliance Notifications")
        st.markdown("""
            <div style="background: var(--bg-subtle); border: 1px solid var(--border-color); border-radius: 10px; padding: 10px 12px; font-size: 0.8rem; margin-bottom: 8px;">
                <div style="font-weight: 700; color: #D97706;">⚠️ Annual Cap Deadline</div>
                <div style="color: var(--text-muted); margin-top: 2px;">Statutory carbon audit filing due in 45 days.</div>
            </div>
            <div style="background: var(--bg-subtle); border: 1px solid var(--border-color); border-radius: 10px; padding: 10px 12px; font-size: 0.8rem; margin-bottom: 8px;">
                <div style="font-weight: 700; color: #10B981;">🟢 Q3 Solar Credit Verified</div>
                <div style="color: var(--text-muted); margin-top: 2px;">18.5 tonnes carbon offset recognized by registry.</div>
            </div>
        """, unsafe_allow_html=True)

        # Achievement Badges
        st.markdown("##### 🏅 Achievement Badges")
        st.markdown("""
            <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px;">
                <span class="badge-low" title="Energy audited">⚡ Green Plant</span>
                <span class="badge-low" title="Over 40% waste diverted">♻️ Circular Champ</span>
                <span class="badge-medium" title="Tracking Scope 1-3">🌍 Scope Master</span>
            </div>
        """, unsafe_allow_html=True)

        # Logout button
        if st.button("🚪 Logout", key="sidebar_logout_btn", use_container_width=True):
            logout_user()

def main():
    # Inject high-contrast custom CSS & initialize state
    inject_custom_css()
    init_app_state()

    # If unauthenticated, show Step 1 (Landing) or Step 2 (Auth)
    if not st.session_state.get("authenticated", False):
        step = st.session_state.get("current_step", 1)
        if step == 1:
            render_landing_view()
        else:
            render_auth_view()
        return

    # Authenticated Frame
    render_sidebar()
    render_top_stepper()

    # Route based on navigation section & step
    nav_sec = st.session_state.get("nav_section", "dashboard")
    step = st.session_state.get("current_step", 5)

    if nav_sec == "analytics":
        render_analytics_view()
    elif nav_sec == "circular" or step == 10:
        render_circular_view()
    elif nav_sec == "leak_detection" or step == 6:
        render_leak_detection_view()
    elif nav_sec == "carbon_credits" or step == 7:
        render_carbon_credits_view()
    elif nav_sec == "recommendations" or step == 8:
        render_recommendations_view()
    elif nav_sec == "simulator" or step == 9:
        render_simulator_view()
    elif nav_sec == "reports" or step == 11:
        render_reports_view()
    elif nav_sec == "settings" or step == 12:
        render_settings_view()
    elif nav_sec == "setup" or step == 3:
        render_setup_view()
    elif nav_sec == "upload" or step == 4:
        render_upload_view()
    else: # Default dashboard (Step 5)
        render_dashboard_view()

if __name__ == "__main__":
    main()

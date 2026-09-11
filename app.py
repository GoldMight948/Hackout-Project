"""
Main Application Entry Point: Emission Leak Detector & Green Fix Recommender
Built with Streamlit. Designed for small businesses to diagnose emission leaks and implement green fixes.
"""

import streamlit as st

# Streamlit Page Configuration must be the first Streamlit command
st.set_page_config(
    page_title="Emission Leak Detector & Green Fix Recommender",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

from components.styles import inject_custom_css
from components.auth import init_auth_state, render_login_view, logout_user
from components.data_presets import DEMO_BUSINESSES
from components.views.welcome_view import render_welcome_view
from components.views.data_entry_view import render_data_entry_view
from components.views.dashboard_view import render_dashboard_view
from components.views.recommendations_view import render_recommendations_view
from components.views.simulator_view import render_simulator_view
from components.views.action_plan_view import render_action_plan_view
from components.views.export_view import render_export_view

STEPS = [
    {"num": 1, "name": "Welcome", "icon": "👋"},
    {"num": 2, "name": "Data Entry", "icon": "📝"},
    {"num": 3, "name": "Dashboard", "icon": "📊"},
    {"num": 4, "name": "Leak Fixes & Ideas", "icon": "💡"},
    {"num": 5, "name": "Simulator", "icon": "🎛️"},
    {"num": 6, "name": "Action Plan", "icon": "📋"},
    {"num": 7, "name": "Export & Share", "icon": "📥"},
]

def init_app_state():
    """Initializes global session state keys."""
    init_auth_state()
    if "current_step" not in st.session_state:
        st.session_state["current_step"] = 1
    if "form_inputs" not in st.session_state:
        st.session_state["form_inputs"] = {}
    if "emissions_results" not in st.session_state:
        st.session_state["emissions_results"] = None
    if "selected_leak_category" not in st.session_state:
        st.session_state["selected_leak_category"] = "electricity"

def render_top_stepper():
    """Renders clean progress bar indicator showing current stage."""
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
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.4rem;">🌿</span>
                <span style="font-weight: 800; font-size: 1.05rem; color: #064E3B;">Emission Leak Detector</span>
                <span class="step-badge">Step {cur} of {len(STEPS)}: {STEPS[cur-1]['name']}</span>
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 4px;">
                {pills_html}
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Sidebar with user profile, stage navigation, and preset switcher."""
    user = st.session_state.get("current_user", {})
    user_name = user.get("name", "User")
    user_company = user.get("company", "Small Business")
    user_avatar = user.get("avatar", "🌱")
    
    with st.sidebar:
        # Profile header
        st.markdown(f"""
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.8rem;">{user_avatar}</span>
                    <div>
                        <div style="font-weight: 700; color: #0F172A; font-size: 0.95rem;">{user_name}</div>
                        <div style="font-size: 0.8rem; color: #64748B;">{user_company}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Switch User / Sign Out", key="sidebar_logout", use_container_width=True):
            logout_user()

        st.markdown("<hr style='margin: 16px 0; border: none; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)

        # Stage Navigator
        st.markdown("#### 🗺️ Journey Navigation")
        cur_step = st.session_state.get("current_step", 1)
        results = st.session_state.get("emissions_results")

        for s in STEPS:
            num = s["num"]
            icon = s["icon"]
            name = s["name"]
            is_active = (num == cur_step)
            
            # Allow navigation if step is accessible
            btn_type = "primary" if is_active else "secondary"
            btn_label = f"{icon} Step {num}: {name}"
            
            # Disable steps 3-7 if data hasn't been submitted yet
            disabled = (num >= 3 and results is None)
            
            if st.button(btn_label, key=f"nav_step_{num}", type=btn_type, disabled=disabled, use_container_width=True):
                st.session_state["current_step"] = num
                st.rerun()

        # Mini live status card if emissions computed
        if results is not None:
            st.markdown("<hr style='margin: 16px 0; border: none; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)
            st.markdown("#### 📌 Live Footprint Summary")
            st.markdown(f"""
                <div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 10px; padding: 12px; font-size: 0.85rem;">
                    <div>Baseline: <strong>{results['total_co2']} tonnes</strong></div>
                    <div>Est. Spend: <strong>${results['total_cost']:,.0f}/yr</strong></div>
                    <div style="margin-top: 4px; color: #B91C1C;">
                        Top Leak: <strong>{results['top_leak']['label']} ({results['top_leak']['share_pct']}%)</strong>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # Presets quick switch
        st.markdown("<hr style='margin: 16px 0; border: none; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)
        st.caption("Load Quick Benchmark:")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            if st.button("🥪 Bakery", key="side_food", use_container_width=True):
                st.session_state["form_inputs"] = DEMO_BUSINESSES["food_processor"]["data"].copy()
                st.session_state["emissions_results"] = None
                st.session_state["current_step"] = 2
                st.rerun()
        with col_p2:
            if st.button("🚚 Fleet", key="side_log", use_container_width=True):
                st.session_state["form_inputs"] = DEMO_BUSINESSES["logistics"]["data"].copy()
                st.session_state["emissions_results"] = None
                st.session_state["current_step"] = 2
                st.rerun()

def main():
    # Inject CSS & initialize state
    inject_custom_css()
    init_app_state()

    # If user is not authenticated, show login screen
    if not st.session_state.get("authenticated", False):
        render_login_view()
        return

    # Render authenticated frame
    render_sidebar()
    render_top_stepper()

    # Route based on current step
    step = st.session_state.get("current_step", 1)

    if step == 1:
        render_welcome_view()
    elif step == 2:
        render_data_entry_view()
    elif step == 3:
        render_dashboard_view()
    elif step == 4:
        render_recommendations_view()
    elif step == 5:
        render_simulator_view()
    elif step == 6:
        render_action_plan_view()
    elif step == 7:
        render_export_view()
    else:
        st.session_state["current_step"] = 1
        st.rerun()

if __name__ == "__main__":
    main()

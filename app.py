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
from components.auth import init_auth_state, logout_user, quick_demo_login, is_demo_session, reset_current_demo_profile
from components.data_presets import DEMO_BUSINESSES
from components.calculations import calculate_detailed_emissions
from components.icons import feather_icon, render_icon_heading, COLOR_WARNING, COLOR_SUCCESS, COLOR_NEUTRAL, COLOR_SECONDARY

# Import views
from components.views.landing_view import render_landing_view
from components.views.auth_view import render_auth_view
from components.views.setup_view import render_setup_view
from components.views.upload_view import render_upload_view
from components.views.activity_log_view import render_activity_log_view
from components.views.dashboard_view import render_dashboard_view
from components.views.analytics_view import render_analytics_view
from components.views.leak_detection_view import render_leak_detection_view
from components.views.carbon_credits_view import render_carbon_credits_view
from components.views.recommendations_view import render_recommendations_view
from components.views.simulator_view import render_simulator_view
from components.views.circular_view import render_circular_view
from components.views.settings_view import render_settings_view
from components.chatbot import render_copilot_chat

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

def render_sidebar():
  """Renders modern SaaS sidebar with navigation icons, notifications, and presets."""
  user = st.session_state.get("current_user", {})
  user_name = user.get("owner_name", user.get("name", "David Kovac"))
  user_company = user.get("company_name", user.get("company", "Apex Precision Metalworks"))
  user_role = user.get("role", "Admin")
  user_avatar = user.get("avatar", "🏭")
  
  with st.sidebar:
    # Organization Card with Feather Icon and Demo / Production Mode Indicator
    is_demo = is_demo_session()
    org_icon = feather_icon("box", color="#F59E0B" if is_demo else "#10B981", size=24, margin_right=10)
    mode_badge = '<span style="background: rgba(245,158,11,0.2); color: #B45309; padding: 2px 8px; border-radius: 4px; font-weight: 800; font-size: 0.7rem; border: 1px solid #FCD34D;">DEMO SANDBOX</span>' if is_demo else '<span style="background: rgba(16,185,129,0.2); color: #047857; padding: 2px 8px; border-radius: 4px; font-weight: 800; font-size: 0.7rem; border: 1px solid #6EE7B7;">VERIFIED ORG</span>'
    
    st.markdown(f"""
      <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 14px; margin-bottom: 16px; box-shadow: var(--shadow-card);">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
          <span style="font-size: 0.75rem; color: var(--text-muted); font-weight: 700;">WORKSPACE</span>
          {mode_badge}
        </div>
        <div style="display: flex; align-items: center;">
          {org_icon}
          <div>
            <div style="font-weight: 800; font-size: 0.95rem; color: var(--text-primary);">{user_company}</div>
            <div style="font-size: 0.78rem; color: var(--text-muted);">{user_name} &bull; <span style="color: #10B981; font-weight: 700;">{user_role}</span></div>
          </div>
        </div>
      </div>
    """, unsafe_allow_html=True)

    if is_demo:
      if st.button("Reset Demo Data", icon=":material/refresh:", key="sidebar_reset_demo_btn", use_container_width=True):
        reset_current_demo_profile()
        st.success("Demo profile restored!")
        st.rerun()

    # Main Navigation Grouped by Function
    cur_nav = st.session_state.get("nav_section", "dashboard")

    # Group 1: Operations
    st.markdown(f"""
      <div style="font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin: 12px 0 6px 4px;">
        {feather_icon('activity', size=14, margin_right=6)} Operations
      </div>
    """, unsafe_allow_html=True)
    op_items = [
        ("Executive Dashboard", "dashboard", 5, "dashboard"),
        ("Daily & Weekly Logs", "activity_logs", 4, "calendar_today"),
        ("Carbon Copilot AI", "copilot", 99, "smart_toy"),
    ]
    for label, section_key, step_target, icon_name in op_items:
        is_active = (cur_nav == section_key)
        btn_type = "primary" if is_active else "secondary"
        
        # Use columns to put feather icon next to button
        if st.button(label, icon=f":material/{icon_name}:", key=f"nav_btn_{section_key}", type=btn_type, use_container_width=True):
            st.session_state["nav_section"] = section_key
            st.session_state["current_step"] = step_target
            st.rerun()

    # Group 2: Carbon Intelligence & Diagnostics
    st.markdown(f"""
      <div style="font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin: 16px 0 6px 4px;">
    {feather_icon('zap', size=14, margin_right=6)} Intelligence & Diagnostics
      </div>
    """, unsafe_allow_html=True)
    diag_items = [
        ("Emission Leak Hotspots", "leak_detection", 6, "search"),
        ("Carbon Credits & Market", "carbon_credits", 7, "monetization_on"),
        ("Green Recommendations", "recommendations", 8, "lightbulb"),
        ("Decarbonization Simulator", "simulator", 9, "science"),
        ("Circular Economy (4R)", "circular", 10, "recycling"),
    ]
    for label, section_key, step_target, icon_name in diag_items:
        is_active = (cur_nav == section_key)
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, icon=f":material/{icon_name}:", key=f"nav_btn_{section_key}", type=btn_type, use_container_width=True):
            st.session_state["nav_section"] = section_key
            st.session_state["current_step"] = step_target
            st.rerun()

    # Group 3: Data & Administration
    st.markdown(f"""
      <div style="font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin: 16px 0 6px 4px;">
    {feather_icon('folder', size=14, margin_right=6)} Data & Administration
      </div>
    """, unsafe_allow_html=True)
    admin_items = [
        ("Business Profile & Setup", "setup", 3, "settings"),
        ("Activity Data Entry", "data_entry", 3, "edit_document"),
        ("Upload Historical Data", "upload_file", 4, "upload_file"),
        ("Platform Settings", "settings", 12, "build"),
    ]
    for label, section_key, step_target, icon_name in admin_items:
        is_active = (cur_nav == section_key)
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, icon=f":material/{icon_name}:", key=f"nav_btn_{section_key}", type=btn_type, use_container_width=True):
            st.session_state["nav_section"] = section_key
            st.session_state["current_step"] = step_target
            st.rerun()

    st.markdown("<hr style='margin: 16px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)

    # Notification Panel with Feather Icons
    notif_header = feather_icon("alert-triangle", color="#95A5A6", size=18, margin_right=6)
    warn_icon = feather_icon("alert-triangle", color="#FF6B6B", size=16, margin_right=6)
    check_icon = feather_icon("check-circle", color="#2ECC71", size=16, margin_right=6)
    st.markdown(f"""
      <div style="display: flex; align-items: center; margin-bottom: 8px; margin-top: 10px;">
    {notif_header}
    <span style="font-weight: 700; font-size: 0.9rem; color: var(--text-primary);">Compliance Alerts</span>
      </div>
      <div style="background: var(--bg-subtle); border: 1px solid var(--border-color); border-radius: 10px; padding: 10px 12px; font-size: 0.8rem; margin-bottom: 8px;">
    <div style="font-weight: 700; color: #D97706; display: flex; align-items: center;">{warn_icon} Annual Cap Deadline</div>
    <div style="color: var(--text-muted); margin-top: 2px;">Statutory carbon audit filing due in 45 days.</div>
      </div>
      <div style="background: var(--bg-subtle); border: 1px solid var(--border-color); border-radius: 10px; padding: 10px 12px; font-size: 0.8rem; margin-bottom: 8px;">
    <div style="font-weight: 700; color: #10B981; display: flex; align-items: center;">{check_icon} Q3 Solar Credit Verified</div>
    <div style="color: var(--text-muted); margin-top: 2px;">18.5 tonnes carbon offset recognized by registry.</div>
      </div>
    """, unsafe_allow_html=True)

    # Logout button
    if st.button("Sign Out", icon=":material/logout:", key="sidebar_logout_btn", use_container_width=True):
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

  # Authenticated Frame (Top Stepper Bar is completely removed for clean SaaS layout)
  render_sidebar()

  # Route based on navigation section & step
  nav_sec = st.session_state.get("nav_section", "dashboard")
  step = st.session_state.get("current_step", 5)

  # Sync nav_section if step was set directly to dashboard
  if step == 5 and nav_sec in ["setup", "upload_file"]:
    nav_sec = "dashboard"
    st.session_state["nav_section"] = "dashboard"

  if nav_sec == "copilot":
    from components.chatbot import render_copilot_view
    render_copilot_view()
  elif nav_sec == "activity_logs":
    render_activity_log_view()
  elif nav_sec == "analytics":
    render_analytics_view()
  elif nav_sec == "recommendations" or step == 8:
    render_recommendations_view()
  elif nav_sec == "circular" or step == 10:
    render_circular_view()
  elif nav_sec == "leak_detection" or step == 6:
    render_leak_detection_view()
  elif nav_sec == "carbon_credits" or step == 7:
    render_carbon_credits_view()
  elif nav_sec == "simulator" or step == 9:
    render_simulator_view()
  elif nav_sec == "settings" or step == 12:
    render_settings_view()
  elif nav_sec == "setup" or (step == 3 and nav_sec != "data_entry"):
    render_setup_view()
  elif nav_sec == "data_entry":
    from components.views.data_entry_view import render_data_entry_view
    render_data_entry_view()
  elif nav_sec == "upload_file" or step == 4:
    render_upload_view()
  else: # Default dashboard (Step 5)
    render_dashboard_view()

if __name__ == "__main__":
  main()

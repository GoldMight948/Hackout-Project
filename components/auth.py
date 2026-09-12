"""
Authentication and Session State Management.
Integrates SQLite persistence with multi-user role support (Admin/Employee),
custom business profile creation, and one-click demo personas.
"""

import streamlit as st
from typing import Optional, Dict, Any
from database.db_manager import authenticate_user, register_user, get_user_profile
from components.data_presets import DEMO_USERS, DEMO_BUSINESSES
from components.calculations import calculate_detailed_emissions

def init_auth_state():
    """Ensures core authentication and user state exists."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "current_user" not in st.session_state:
        st.session_state["current_user"] = None
    if "theme_mode" not in st.session_state:
        st.session_state["theme_mode"] = "light"

def login_user_session(user_dict: Dict[str, Any]):
    """Establishes logged-in session state and loads user's enterprise baseline."""
    st.session_state["authenticated"] = True
    st.session_state["current_user"] = user_dict
    
    # Check if there is a preset key or matched industry
    industry = user_dict.get("industry", "Manufacturing Plant")
    preset_key = "manufacturing_plant"
    for key, data in DEMO_BUSINESSES.items():
        if data.get("industry", "").lower() == industry.lower() or key in user_dict.get("email", ""):
            preset_key = key
            break

    # If form_inputs not yet set or empty, load baseline
    if "form_inputs" not in st.session_state or not st.session_state["form_inputs"]:
        preset_data = DEMO_BUSINESSES[preset_key]["data"].copy()
        preset_data["business_name"] = user_dict.get("company_name", preset_data["business_name"])
        st.session_state["form_inputs"] = preset_data
        st.session_state["emissions_results"] = calculate_detailed_emissions(preset_data)

    st.rerun()

def logout_user():
    """Clears user session and logs out."""
    st.session_state["authenticated"] = False
    st.session_state["current_user"] = None
    st.session_state["form_inputs"] = {}
    st.session_state["emissions_results"] = None
    st.session_state["current_step"] = 1
    st.rerun()

def quick_demo_login(email: str):
    """One-click instant login as a pre-configured verified enterprise persona."""
    user_meta = DEMO_USERS.get(email)
    if user_meta:
        preset_key = user_meta["preset_key"]
        preset_info = DEMO_BUSINESSES[preset_key]
        
        user_record = {
            "email": email,
            "owner_name": user_meta["name"],
            "company_name": user_meta["company"],
            "role": user_meta.get("role", "Admin"),
            "industry": user_meta["industry"],
            "avatar": user_meta["avatar"],
            "company_type": preset_info["type_label"],
            "employees": preset_info["employees"],
            "annual_revenue": preset_info["revenue"],
            "country": "United States",
            "state": preset_info["location"].split(",")[-1].strip(),
            "location": preset_info["location"]
        }
        st.session_state["form_inputs"] = preset_info["data"].copy()
        st.session_state["emissions_results"] = calculate_detailed_emissions(st.session_state["form_inputs"])
        st.session_state["authenticated"] = True
        st.session_state["current_user"] = user_record
        st.session_state["current_step"] = 5 # Route straight to Dashboard
        st.rerun()

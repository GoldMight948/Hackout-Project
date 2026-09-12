"""
Authentication and Session State Management.
Integrates SQLite persistence with multi-user role support (Admin/Employee),
custom business profile creation, and one-click demo personas.
Isolates demo sandbox accounts from real enterprise profiles and cross-references SQLite backend.
"""

import streamlit as st
from typing import Optional, Dict, Any
from database.db_manager import (
  authenticate_user, register_user, get_user_profile, get_latest_emissions,
  is_demo_user, reset_demo_account, get_activity_logs, sync_activity_logs_to_dashboard,
  save_emissions_assessment
)
from components.data_presets import DEMO_USERS, DEMO_BUSINESSES
from components.calculations import calculate_detailed_emissions, get_statutory_carbon_quota

def init_auth_state():
  """Ensures core authentication, demo isolation, and user state exists."""
  if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
  if "current_user" not in st.session_state:
    st.session_state["current_user"] = None
  if "is_demo" not in st.session_state:
    st.session_state["is_demo"] = False
  if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "light"

def is_demo_session() -> bool:
  """Returns True if the currently logged-in user is an isolated demo sandbox account."""
  if not st.session_state.get("authenticated", False):
    return False
  return bool(st.session_state.get("is_demo", False))

def login_user_session(user_dict: Dict[str, Any]):
  """
  Establishes logged-in session state.
  Cross-references existing SQLite database to dynamically load user's actual stored assessment.
  Syncs operational daily/weekly activity logs, calibrates statutory carbon credit quotas,
  and isolates demo accounts from real production workspaces.
  """
  st.session_state["authenticated"] = True
  st.session_state["current_user"] = user_dict
  
  email = user_dict.get("email", "").lower().strip()
  is_demo = bool(user_dict.get("is_demo", False)) or is_demo_user(email) or (email in DEMO_USERS)
  st.session_state["is_demo"] = is_demo

  # Automatically check if user has high-frequency activity logs in SQLite to sync
  activity_entries = get_activity_logs(email, limit=1)
  if activity_entries:
    sync_activity_logs_to_dashboard(email, is_demo=is_demo)

  # Cross-reference existing SQLite backend for saved assessments
  latest_db_data = get_latest_emissions(email)
  
  if latest_db_data:
    # User has real persistent emissions records in SQLite - load dynamically!
    loaded_inputs = dict(latest_db_data)
    loaded_inputs["business_name"] = user_dict.get("company_name", loaded_inputs.get("business_name", "Enterprise Facility"))
    
    # Apply research-backed statutory quota if credits are unset or default
    industry = user_dict.get("industry", loaded_inputs.get("industry", "Manufacturing Plant"))
    comp_type = user_dict.get("company_type", "SME / Mid-Sized Business")
    employees = user_dict.get("employees", 50)
    quota_calc = get_statutory_carbon_quota(industry, comp_type, employees)
    
    curr_credits = float(loaded_inputs.get("total_credits", 0.0))
    if curr_credits in [0.0, 100.0]:
      loaded_inputs["total_credits"] = quota_calc["quota_credits"]
      loaded_inputs["credit_price"] = quota_calc["benchmark_price"]
      
    st.session_state["form_inputs"] = loaded_inputs
    st.session_state["emissions_results"] = calculate_detailed_emissions(loaded_inputs)
  elif is_demo:
    # Demo account fallback to calibrated preset
    industry = user_dict.get("industry", "Manufacturing Plant")
    preset_key = "manufacturing_plant"
    for key, data in DEMO_BUSINESSES.items():
      if data.get("industry", "").lower() == industry.lower() or key in email:
        preset_key = key
        break
    preset_data = DEMO_BUSINESSES[preset_key]["data"].copy()
    preset_data["business_name"] = user_dict.get("company_name", preset_data["business_name"])
    st.session_state["form_inputs"] = preset_data
    st.session_state["emissions_results"] = calculate_detailed_emissions(preset_data)
  else:
    # Clean real user account with no prior assessments - provide research-backed statutory quota
    industry = user_dict.get("industry", "Manufacturing Plant")
    comp_type = user_dict.get("company_type", "SME / Mid-Sized Business")
    employees = user_dict.get("employees", 50)
    quota_calc = get_statutory_carbon_quota(industry, comp_type, employees)

    clean_profile = {
      "business_name": user_dict.get("company_name", "My Enterprise"),
      "industry": industry,
      "company_type": comp_type,
      "employees": employees,
      "annual_revenue": user_dict.get("annual_revenue", 0.0),
      "country": user_dict.get("country", "United States"),
      "state": user_dict.get("state", "California"),
      "factory_location": user_dict.get("location", "Plant #1"),
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
      "total_credits": quota_calc["quota_credits"],
      "credit_price": quota_calc["benchmark_price"],
      "current_balance": quota_calc["quota_credits"]
    }
    res_clean = calculate_detailed_emissions(clean_profile)
    clean_profile["total_co2"] = res_clean["total_co2"]
    clean_profile["total_cost"] = res_clean["total_cost"]
    clean_profile["sustainability_score"] = res_clean["sustainability_score"]
    save_emissions_assessment(email, clean_profile, is_demo=0)
    
    st.session_state["form_inputs"] = clean_profile
    st.session_state["emissions_results"] = res_clean

  st.rerun()

def logout_user():
  """Clears user session and logs out."""
  st.session_state["authenticated"] = False
  st.session_state["current_user"] = None
  st.session_state["is_demo"] = False
  st.session_state["form_inputs"] = {}
  st.session_state["emissions_results"] = None
  st.session_state["current_step"] = 1
  st.rerun()

def quick_demo_login(email: str):
  """One-click instant login as a pre-configured verified enterprise persona (isolated in demo mode)."""
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
      "location": preset_info["location"],
      "is_demo": 1
    }
    st.session_state["form_inputs"] = preset_info["data"].copy()
    st.session_state["emissions_results"] = calculate_detailed_emissions(st.session_state["form_inputs"])
    st.session_state["authenticated"] = True
    st.session_state["is_demo"] = True
    st.session_state["current_user"] = user_record
    st.session_state["current_step"] = 5 # Route straight to Dashboard
    st.rerun()

def reset_current_demo_profile():
  """Resets the currently active demo profile to original factory preset without touching real data."""
  user = st.session_state.get("current_user", {})
  email = user.get("email", "")
  if is_demo_session() and email in DEMO_USERS:
    reset_demo_account(email)
    preset_key = DEMO_USERS[email]["preset_key"]
    st.session_state["form_inputs"] = DEMO_BUSINESSES[preset_key]["data"].copy()
    st.session_state["emissions_results"] = calculate_detailed_emissions(st.session_state["form_inputs"])
    return True
  return False


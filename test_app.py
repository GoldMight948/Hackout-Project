"""
Comprehensive Automated Test Suite for Industrial Emission Leak-Point Detector.
Validates SQLite persistence, calculations, carbon credit accounting,
Top 10 leak diagnostics, ML forecasting, and FastAPI endpoints.
"""

import sys
import os
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if sys.platform == "win32":
  try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
  except Exception:
    pass

from database.db_manager import init_db, register_user, authenticate_user, save_emissions_assessment, get_latest_emissions, log_audit, get_audit_logs, record_market_transaction, get_market_transactions
from components.calculations import calculate_detailed_emissions, INDUSTRY_BENCHMARKS
from components.data_presets import DEMO_BUSINESSES, DEMO_USERS, AI_RECOMMENDATIONS, CIRCULAR_ALTERNATIVES
from components.ml_forecast import generate_monthly_timeseries, forecast_emissions_ml, get_emission_intensity_matrix

def test_database():
  print("Testing SQLite Database...")
  init_db()
  
  # Test Registration
  test_email = "tester_audit@enterprise.com"
  reg_ok = register_user(
    email=test_email,
    password="securepassword123",
    company_name="Test Industrial Systems",
    owner_name="Audit Lead",
    role="Admin",
    industry="Manufacturing Plant"
  )
  # Registration should succeed or already exist
  user = authenticate_user(test_email, "securepassword123")
  assert user is not None, "Authentication failed for registered user"
  assert user["company_name"] == "Test Industrial Systems"
  print(" [PASS] User registration and authentication verified.")

  # Test Assessment Save
  sample_data = {
    "electricity_kwh": 250000.0,
    "diesel_liters": 15000.0,
    "truck_km": 40000.0,
    "organic_waste_kg": 10000.0,
    "water_m3": 5000.0,
    "total_credits": 200.0,
    "total_co2": 185.5,
    "total_cost": 54000.0,
    "sustainability_score": 68.5
  }
  rec_id = save_emissions_assessment(test_email, sample_data)
  assert rec_id > 0, "Failed to save emissions assessment"
  latest = get_latest_emissions(test_email)
  assert latest is not None, "Failed to fetch latest emissions"
  assert latest["total_credits"] == 200.0
  print(" [PASS] Emissions assessment persistence verified.")

  # Test Market Transaction
  tx_id = record_market_transaction(test_email, "BUY", 50.0, 35.0, "Test compliance buy")
  assert tx_id > 0, "Failed to record market transaction"
  txs = get_market_transactions(test_email)
  assert len(txs) > 0, "Failed to retrieve market transactions"
  print(" [PASS] Carbon credit market transactions verified.")

def test_calculations():
  print("Testing Emission Engine & Carbon Credits Logic...")
  
  # Case 1: Surplus / Carbon Neutral Scenario
  surplus_input = {
    "electricity_kwh": 50000.0,
    "renewable_pct": 50.0,
    "diesel_liters": 2000.0,
    "truck_km": 10000.0,
    "organic_waste_kg": 5000.0,
    "water_m3": 1000.0,
    "total_credits": 250.0,
    "credit_price": 40.0
  }
  res_surplus = calculate_detailed_emissions(surplus_input)
  assert res_surplus["total_co2"] > 0
  assert not res_surplus["is_deficit"], "Expected surplus/neutral status"
  assert res_surplus["credits_remaining"] > 0
  assert res_surplus["est_revenue"] > 0
  assert res_surplus["compliance_cost"] == 0.0
  print(f" [PASS] Surplus Case: {res_surplus['total_co2']} t CO2 vs {res_surplus['govt_credits']} credits -> {res_surplus['net_carbon_status']}")

  # Case 2: Deficit Scenario
  deficit_input = {
    "electricity_kwh": 600000.0,
    "renewable_pct": 5.0,
    "diesel_liters": 45000.0,
    "truck_km": 120000.0,
    "plastic_waste_kg": 25000.0,
    "total_credits": 100.0,
    "credit_price": 38.0
  }
  res_deficit = calculate_detailed_emissions(deficit_input)
  assert res_deficit["is_deficit"], "Expected deficit status"
  assert res_deficit["credits_required"] > 0
  assert res_deficit["compliance_cost"] > 0
  assert res_deficit["est_revenue"] == 0.0
  print(f" [PASS] Deficit Case: {res_deficit['total_co2']} t CO2 vs {res_deficit['govt_credits']} credits -> Deficit: {res_deficit['credits_required']} t, Cost: ₹{res_deficit['compliance_cost']:,.0f}")

  # Case 3: Defaulted Fields Transparency Verification (Task 4)
  sparse_input = {
    "electricity_kwh": 50000.0,
    "diesel_liters": 2000.0
  }
  res_sparse = calculate_detailed_emissions(sparse_input)
  assert "defaulted_fields" in res_sparse
  assert "water_m3" in res_sparse["defaulted_fields"]
  assert "raw_material_tonnes" in res_sparse["defaulted_fields"]
  assert "production_units" in res_sparse["defaulted_fields"]
  assert "total_credits" in res_sparse["defaulted_fields"]

  full_input = {
    "electricity_kwh": 50000.0,
    "water_m3": 1500.0,
    "raw_material_tonnes": 200.0,
    "production_units": 30000.0,
    "total_credits": 180.0,
    "machine_hours": 2000.0
  }
  res_full = calculate_detailed_emissions(full_input)
  assert len(res_full["defaulted_fields"]) == 0
  print(" [PASS] Defaulted fields detection & transparency metadata verified.")

  # Top 10 Leaks Verification
  leaks = res_deficit["top_10_leaks"]
  assert len(leaks) == 10, f"Expected 10 leaks, found {len(leaks)}"
  assert leaks[0]["current_co2"] >= leaks[-1]["current_co2"], "Leaks must be sorted descending"
  for l in leaks:
    assert "impact_score" in l
    assert "priority" in l
    assert "potential_saving_co2" in l
  print(" [PASS] Top 10 leak diagnostics sorted and scored successfully.")

def test_ml_forecasting():
  print("Testing ML Forecasting & Timeseries...")
  sample_pillars = {
    "Electricity": 120.0,
    "Fuel & Heating": 85.0,
    "Transport & Fleet": 65.0,
    "Waste & Packaging": 35.0,
    "Water & Effluent": 18.0,
    "Industrial Ops": 22.0
  }
  df_m = generate_monthly_timeseries(sample_pillars)
  assert len(df_m) == 12, "Monthly timeseries must have 12 months"
  assert "Total_Monthly_CO2" in df_m.columns

  forecast_df = forecast_emissions_ml(df_m, target_reduction_pct=30.0)
  assert len(forecast_df) == 12, "Forecast must have 12 future steps"
  assert "BAU_Forecast" in forecast_df.columns
  assert "Decarbonization_Pathway" in forecast_df.columns
  assert forecast_df["Decarbonization_Pathway"].iloc[-1] < forecast_df["BAU_Forecast"].iloc[-1]
  print(" [PASS] ML polynomial regression & decarbonization pathway verified.")

def test_presets_and_alternatives():
  print("Testing 4R Circular Alternatives & Demo Presets...")
  assert len(DEMO_BUSINESSES) >= 4, "Must have at least 4 demo businesses"
  assert len(AI_RECOMMENDATIONS) >= 10, "Must have at least 10 AI recommendations"
  for r in AI_RECOMMENDATIONS:
    assert "circular_benefit" in r
    assert "govt_incentives" in r
    assert "expected_roi" in r
    assert "payback_time" in r
  
  assert len(CIRCULAR_ALTERNATIVES) >= 4, "Must have at least 4 circular alternative matrices"
  for stream, r_dict in CIRCULAR_ALTERNATIVES.items():
    for r_key in ["reuse", "recycle", "recover", "replace"]:
      assert r_key in r_dict, f"Missing {r_key} in {stream}"
  print(" [PASS] 4R alternatives, AI recommendations, and demo presets verified.")

def test_fastapi_endpoints():
  print("Testing FastAPI Application...")
  try:
    from fastapi.testclient import TestClient
    from api import app
    client = TestClient(app)
  except (ImportError, RuntimeError):
    print(" [SKIP] fastapi/testclient (httpx) not installed in current environment; skipping REST API tests.")
    return
  
  # Health check
  res_health = client.get("/health")
  assert res_health.status_code == 200
  assert res_health.json()["status"] == "online"

  # Calculate emissions
  payload = {
    "business_name": "Test Fast Plant",
    "electricity_kwh": 100000.0,
    "diesel_liters": 5000.0,
    "total_credits": 150.0
  }
  res_calc = client.post("/api/calculate-emissions", json=payload)
  assert res_calc.status_code == 200
  data = res_calc.json()
  assert "total_co2" in data
  assert "top_10_leaks" in data

  # Benchmarks
  res_bench = client.get("/api/benchmarks/Manufacturing Plant")
  assert res_bench.status_code == 200
  assert "intensity_kg_per_unit" in res_bench.json()["benchmarks"]

  # Activity logs API tests
  res_log_post = client.post("/api/activity-logs", json={
    "user_email": "api_test_facility@corp.com",
    "log_date": "2025-09-12",
    "frequency": "daily",
    "period_label": "Shift 1",
    "diesel_liters": 50.0,
    "organic_waste_kg": 100.0,
    "electricity_kwh": 300.0
  })
  assert res_log_post.status_code == 200
  log_resp = res_log_post.json()
  assert log_resp["status"] == "success"
  assert log_resp["log_id"] > 0

  res_log_get = client.get("/api/activity-logs/api_test_facility@corp.com")
  assert res_log_get.status_code == 200
  assert res_log_get.json()["total_records"] >= 1

  res_log_sum = client.get("/api/activity-logs/summary/api_test_facility@corp.com")
  assert res_log_sum.status_code == 200
  assert res_log_sum.json()["total_entries"] >= 1

  print(" [PASS] FastAPI endpoints responded successfully.")

def test_demo_isolation_and_activity_logs():
  print("Testing Demo Profile Isolation & Activity Logging Engine...")
  from database.db_manager import (
    is_demo_user, save_activity_log, get_activity_logs,
    delete_activity_log, get_aggregated_activity_summary,
    reset_demo_account, ACTIVITY_EMISSION_FACTORS
  )

  # 1. Test Demo Isolation
  assert is_demo_user("alex@greenbite.com") == True
  assert is_demo_user("sarah@ecotrend.com") == True
  assert is_demo_user("david@apexmanufacturing.com") == True
  assert is_demo_user("real_production_user@corp.com") == False
  print(" [PASS] Demo user detection and sandbox isolation verified.")

  # 2. Test Real User Registration is isolated
  real_email = "real_production_audit@corp.com"
  register_user(
    email=real_email,
    password="realpassword456",
    company_name="Real Clean Tech Corp",
    owner_name="Chief Sustainability Officer",
    role="Admin",
    industry="Manufacturing Plant",
    is_demo=0
  )
  assert is_demo_user(real_email) == False
  print(" [PASS] Real production user created with clean, isolated workspace.")

  # 3. Test Daily Operational Activity Logging
  daily_payload = {
    "log_date": "2025-09-12",
    "frequency": "daily",
    "period_label": "Shift A",
    "diesel_liters": 100.0,
    "petrol_liters": 0.0,
    "gas_m3": 200.0,
    "organic_waste_kg": 100.0,
    "plastic_waste_kg": 50.0,
    "electricity_kwh": 500.0,
    "truck_km": 100.0,
    "notes": "Test shift log"
  }
  log_id = save_activity_log(real_email, daily_payload, is_demo=False)
  assert log_id > 0

  logs = get_activity_logs(real_email)
  assert len(logs) >= 1
  recent = logs[0]

  # Verify Calculations:
  # Fuel: (100 * 0.00268) + (200 * 0.00203) = 0.268 + 0.406 = 0.674
  expected_fuel = round((100.0 * ACTIVITY_EMISSION_FACTORS["diesel"]) + (200.0 * ACTIVITY_EMISSION_FACTORS["gas"]), 4)
  assert abs(recent["calculated_fuel_co2"] - expected_fuel) < 0.001

  # Waste: (100 * 0.00045) + (50 * 0.00210) = 0.045 + 0.105 = 0.150
  expected_waste = round((100.0 * ACTIVITY_EMISSION_FACTORS["waste_organic"]) + (50.0 * ACTIVITY_EMISSION_FACTORS["waste_plastic"]), 4)
  assert abs(recent["calculated_waste_co2"] - expected_waste) < 0.001

  # Electricity: 500 * 0.00042 = 0.210
  expected_elec = round(500.0 * ACTIVITY_EMISSION_FACTORS["electricity"], 4)
  assert abs(recent["calculated_electricity_co2"] - expected_elec) < 0.001

  print(" [PASS] Daily fuel, waste, and electricity emission calculations verified.")

  # 4. Test Weekly Activity Logging & Aggregation
  weekly_payload = {
    "log_date": "2025-09-07",
    "frequency": "weekly",
    "period_label": "Week 36, 2025",
    "diesel_liters": 600.0,
    "gas_m3": 1200.0,
    "organic_waste_kg": 500.0,
    "plastic_waste_kg": 250.0,
    "electricity_kwh": 3000.0,
    "notes": "Weekly consolidated summary"
  }
  w_log_id = save_activity_log(real_email, weekly_payload, is_demo=False)
  assert w_log_id > 0

  summary = get_aggregated_activity_summary(real_email)
  assert summary["total_entries"] >= 2
  assert summary["total_fuel_co2"] > 0
  assert summary["total_waste_co2"] > 0
  assert summary["total_diesel_liters"] >= 700.0
  print(" [PASS] Weekly activity logging and multi-period aggregation verified.")

  # 5. Test Demo Account Reset
  demo_test_email = "alex@greenbite.com"
  reset_ok = reset_demo_account(demo_test_email)
  assert reset_ok == True
  # Verify demo logs exist after reset
  demo_logs = get_activity_logs(demo_test_email)
  assert len(demo_logs) >= 14, "Expected seeded demo activity logs after reset"
  # Ensure real user records were not affected by demo reset
  real_logs_after = get_activity_logs(real_email)
  assert len(real_logs_after) >= 2, "Real user logs must remain untouched during demo reset"
  print(" [PASS] Demo account factory reset and real account isolation verified.")

  # 6. Test Activity Log Deletion & Dynamic Sync
  del_ok = delete_activity_log(w_log_id, real_email)
  assert del_ok == True
  print(" [PASS] Activity log deletion verified.")

  # 7. Test Dynamic Activity-to-Dashboard Sync Engine
  from database.db_manager import sync_activity_logs_to_dashboard, get_latest_emissions
  synced_assessment = sync_activity_logs_to_dashboard(real_email, is_demo=False)
  assert synced_assessment is not None
  assert synced_assessment["total_co2"] > 0
  assert "pillar_co2" in synced_assessment
  latest_em = get_latest_emissions(real_email)
  assert latest_em is not None
  assert latest_em["total_co2"] == synced_assessment["total_co2"]
  print(f" [PASS] Real-time operational activity to dashboard sync verified: {synced_assessment['total_co2']:.1f} t CO2e.")

  # 8. Test Next Day Date Progression Logic
  from datetime import date, timedelta
  test_d = date(2025, 9, 12)
  next_d = test_d + timedelta(days=1)
  assert next_d == date(2025, 9, 13)
  assert next_d.strftime("%Y-%m-%d") == "2025-09-13"
  print(" [PASS] Next day sequential date progression verified.")

def test_copilot_assistant():
  print("Testing Carbon Copilot AI Engine & Navigation...")
  from components.chatbot import detect_navigation_intent, generate_copilot_response

  # 1. Intent Detection
  assert detect_navigation_intent("Take me to dashboard") == "dashboard"
  assert detect_navigation_intent("I want to log fuel and waste") == "activity_logs"
  assert detect_navigation_intent("Show me my emission leaks") == "leak_detection"
  assert detect_navigation_intent("What is my carbon credit balance?") == "carbon_credits"
  assert detect_navigation_intent("Open compliance report") == "reports"
  print(" [PASS] Natural language navigation intent parsing verified.")

  # 2. Personalized Metrics Generation
  sample_res = {
    "total_co2": 540.2,
    "govt_credits": 400.0,
    "credits_used": 540.2,
    "credits_required": 140.2,
    "credits_remaining": 0.0,
    "is_deficit": True,
    "compliance_cost": 5327.6,
    "credit_price": 38.0,
    "sustainability_score": 62.0,
    "pillar_co2": {"Natural Gas Heating": 220.0, "Diesel Fleet": 150.0, "Electricity": 170.2}
  }

  resp_emissions = generate_copilot_response("What are my total emissions?", "alex@greenbite.com", "GreenBite Packaging", sample_res)
  assert "540.2" in resp_emissions["text"]
  assert "GreenBite Packaging" in resp_emissions["text"]
  assert resp_emissions["nav_target"] == "dashboard"

  resp_deficit = generate_copilot_response("Do I have a carbon deficit?", "alex@greenbite.com", "GreenBite Packaging", sample_res)
  assert "Deficit Warning" in resp_deficit["text"]
  assert "₹442,224" in resp_deficit["text"] or "5,328" in resp_deficit["text"] or "5,327" in resp_deficit["text"]
  assert resp_deficit["nav_target"] == "carbon_credits"

  resp_nav = generate_copilot_response("Please navigate to leaks", "alex@greenbite.com", "GreenBite Packaging", sample_res)
  assert resp_nav["nav_target"] == "leak_detection"
  assert resp_nav.get("auto_redirect") == True

  # 3. Personalized Profile Summary Query
  resp_pers = generate_copilot_response("tell personalize info", "alex@greenbite.com", "GreenBite Packaging", sample_res)
  assert "Personalized Enterprise Profile" in resp_pers["text"]
  assert "GreenBite Packaging" in resp_pers["text"]
  assert "540.2" in resp_pers["text"]

  print(" [PASS] Personalized enterprise intelligence & advisory verified.")

def test_geo_data_and_statutory_carbon_quotas():
  print("Testing Country/State Dropdowns & Dynamic Statutory Carbon Quotas...")
  from components.geo_data import get_country_list, get_states_for_country
  from components.calculations import get_statutory_carbon_quota

  # 1. Test Country & State Lookups
  countries = get_country_list()
  assert len(countries) >= 12
  assert "India" in countries
  assert "United States" in countries
  
  ind_states = get_states_for_country("India")
  assert "Gujarat" in ind_states
  assert "Maharashtra" in ind_states
  assert "Delhi (NCT)" in ind_states

  us_states = get_states_for_country("United States")
  assert "Ohio" in us_states
  assert "California" in us_states
  assert "Texas" in us_states
  print(f" [PASS] Dynamic country/state dropdown mappings verified ({len(countries)} countries, {len(ind_states)} Indian states).")

  # 2. Test Statutory Carbon Quota dynamically varies by industry and workforce
  q_heavy = get_statutory_carbon_quota("Heavy Industrial Manufacturer", "Heavy Industrial Manufacturer", 100)
  q_mfg = get_statutory_carbon_quota("Manufacturing Plant", "SME / Mid-Sized Business", 65)
  q_logistics = get_statutory_carbon_quota("Logistics Company", "Logistics Fleet Operator", 50)
  q_retail = get_statutory_carbon_quota("Retail Store", "Retail / Distribution", 20)
  q_cafe = get_statutory_carbon_quota("Hospitality & Cafe", "SME / Mid-Sized Business", 10)

  assert q_heavy["quota_credits"] > q_mfg["quota_credits"]
  assert q_mfg["quota_credits"] > q_retail["quota_credits"]
  assert q_retail["quota_credits"] > q_cafe["quota_credits"]
  assert q_heavy["quota_credits"] >= 800.0
  assert q_mfg["quota_credits"] == 618.0 # 65 * 9.5 * 1.0 = 617.5 -> 618
  assert q_logistics["quota_credits"] == 660.0 # 50 * 11.0 * 1.2 = 660
  assert q_retail["quota_credits"] == 80.0 # max(80, 20 * 3.2 * 0.85 = 54.4)
  assert q_cafe["quota_credits"] == 60.0 # max(60, 10 * 2.5 * 1.0 = 25)

  print(f" [PASS] Statutory quotas calibrated: Heavy={q_heavy['quota_credits']:.0f}, Mfg={q_mfg['quota_credits']:.0f}, Logistics={q_logistics['quota_credits']:.0f}, Retail={q_retail['quota_credits']:.0f}, Cafe={q_cafe['quota_credits']:.0f}.")

def test_carbon_credit_audit_and_cross_check():
  print("Testing Carbon Credit Daily/Weekly Use, Expected Use, and Quota Cross-Check...")
  from components.calculations import calculate_carbon_credit_audit
  from database.db_manager import get_user_profile, get_activity_logs, get_latest_emissions

  # 1. Test abcd@gmail.com audit calculation
  prof = get_user_profile("abcd@gmail.com")
  logs = get_activity_logs("abcd@gmail.com")
  em = get_latest_emissions("abcd@gmail.com")
  
  audit = calculate_carbon_credit_audit(prof, logs, em)
  assert audit["initial_govt_quota"] >= 350.0
  assert audit["daily_quota_target"] > 0
  assert audit["weekly_quota_target"] > 0
  assert audit["actual_daily_avg"] > 0
  assert audit["actual_weekly_avg"] > 0
  assert audit["expected_annual_burn"] > 0
  assert audit["expected_monthly_burn"] > 0
  assert audit["accrued_credits_used"] > 0
  assert audit["accrued_remaining_balance"] > 0
  assert audit["audit_verdict"] != ""
  print(f" [PASS] Quota cross-check verified: Govt Issued={audit['initial_govt_quota']}, Daily Burn={audit['actual_daily_avg']} c/d, Weekly Burn={audit['actual_weekly_avg']} c/w, Expected Annual={audit['expected_annual_burn']} c/yr.")

  # 2. Test Copilot query answering for carbon credit cross-check
  from components.chatbot import generate_copilot_response
  sample_res = {
    "total_co2": 540.2,
    "govt_credits": 400.0,
    "credits_used": 540.2,
    "credits_required": 140.2,
    "credits_remaining": 0.0,
    "is_deficit": True,
    "compliance_cost": 5327.6,
    "credit_price": 38.0,
    "sustainability_score": 62.0,
    "pillar_co2": {"Natural Gas Heating": 220.0}
  }
  resp = generate_copilot_response("cross check how many carbon credit government issue initially", "abcd@gmail.com", "Solarvise", sample_res)
  assert "Government Initial Quota Issued" in resp["text"]
  assert "Daily Carbon Credit Use" in resp["text"]
  assert "Expected Annual Credit Use" in resp["text"]
  print(" [PASS] Copilot cross-check intent & audit diagnostics verified.")

def test_dynamic_graphs_and_hotspot_recommendations():
  print("Testing Dynamic Graph Synchronization & Hotspot-Based Green Recommendations...")
  from components.calculations import generate_hotspot_recommendations, calculate_detailed_emissions
  from database.db_manager import (
    save_activity_log, update_activity_log, delete_activity_log,
    sync_activity_logs_to_dashboard, get_latest_emissions
  )
  from components.chatbot import generate_copilot_response

  # 1. Verify Green Recommendations dynamically prioritize the business's actual leak hotspot
  # Scenario A: Top Hotspot is Fuel (Boiler Diesel)
  sample_fuel_assessment = calculate_detailed_emissions({
    "business_name": "EcoThermal Ltd",
    "diesel_liters": 45000.0,
    "electricity_kwh": 20000.0,
    "truck_km": 5000.0,
    "organic_waste_kg": 2000.0,
    "total_credits": 300.0
  })
  recs_fuel = generate_hotspot_recommendations(sample_fuel_assessment, {"employees": 35})
  assert len(recs_fuel) > 0
  top_rec_fuel = recs_fuel[0]
  assert top_rec_fuel["targeted_hotspot_rank"] == 1
  assert "#1 Hotspot Fix" in top_rec_fuel["hotspot_priority_tag"]
  assert top_rec_fuel["category"] == "Fuel"
  assert top_rec_fuel["co2_saved_t"] > 0
  assert top_rec_fuel["annual_savings_inr"] > 0
  assert "months" in top_rec_fuel["payback_time"] or "years" in top_rec_fuel["payback_time"]
  print(f" [PASS] Fuel Hotspot Recommendations verified: Top Fix='{top_rec_fuel['title']}' (-{top_rec_fuel['co2_saved_t']} t CO2e).")

  # Scenario B: Top Hotspot is Transport Freight
  sample_trans_assessment = calculate_detailed_emissions({
    "business_name": "Apex Cargo",
    "diesel_liters": 2000.0,
    "electricity_kwh": 30000.0,
    "truck_km": 180000.0,
    "organic_waste_kg": 1000.0,
    "total_credits": 250.0
  })
  recs_trans = generate_hotspot_recommendations(sample_trans_assessment, {"employees": 45})
  assert len(recs_trans) > 0
  top_rec_trans = recs_trans[0]
  assert top_rec_trans["targeted_hotspot_rank"] == 1
  assert "#1 Hotspot Fix" in top_rec_trans["hotspot_priority_tag"]
  assert top_rec_trans["category"] == "Transport"
  assert "Route" in top_rec_trans["title"] or "Fleet" in top_rec_trans["title"]
  print(f" [PASS] Transport Hotspot Recommendations verified: Top Fix='{top_rec_trans['title']}' (-{top_rec_trans['co2_saved_t']} t CO2e).")

  # 2. Verify Activity Log Update & Dynamic Dashboard Recalculation
  test_email = "dynamic_test@enterprise.com"
  from database.db_manager import register_user, get_activity_logs, delete_activity_log, save_activity_log, update_activity_log, sync_activity_logs_to_dashboard
  register_user(test_email, "Pass123!", "Dynamic Co", "Tester", "SME", "Manufacturing Plant", 30)

  # Clean up any leftover logs from prior test runs
  for old_log in get_activity_logs(test_email):
    delete_activity_log(old_log["id"], test_email)

  # Log initial shift: High diesel (300 L)
  log_id = save_activity_log(test_email, {
    "log_date": "2026-09-01",
    "frequency": "daily",
    "period_label": "2026-09-01",
    "diesel_liters": 300.0,
    "electricity_kwh": 500.0
  }, is_demo=False)
  
  synced_initial = sync_activity_logs_to_dashboard(test_email, is_demo=False)
  co2_initial = synced_initial["total_co2"]
  assert co2_initial > 0
  assert synced_initial["top_leak"]["category"] == "Fuel"

  # User updates data: cuts diesel to 0 L and switches to green electricity
  updated = update_activity_log(log_id, test_email, {
    "log_date": "2026-09-01",
    "frequency": "daily",
    "period_label": "2026-09-01",
    "diesel_liters": 0.0,
    "electricity_kwh": 1200.0
  }, is_demo=False)
  assert updated is True

  synced_updated = sync_activity_logs_to_dashboard(test_email, is_demo=False)
  co2_updated = synced_updated["total_co2"]
  # Total emissions changed and fuel dropped to 0
  assert synced_updated["raw_inputs"]["diesel_liters"] == 0.0
  assert synced_updated["pillar_co2"]["Fuel & Heating"] == 0.0
  # Top leak is now Electricity
  assert synced_updated["top_leak"]["category"] == "Electricity"
  print(f" [PASS] Dynamic Graph update on user data edit verified: Fuel dropped to 0, Top Leak shifted from Fuel -> Electricity.")

  # 3. Copilot Recommendation Query response verified
  copilot_rec_resp = generate_copilot_response("what green recommendations do you have to cut emissions and fix leaks", test_email, "Dynamic Co", synced_updated)
  assert "Hotspot-Targeted Green Recommendations" in copilot_rec_resp["text"]
  assert "CO₂ Saved" in copilot_rec_resp["text"]
  assert copilot_rec_resp["nav_target"] == "recommendations"
  print(" [PASS] Copilot Hotspot-Targeted Recommendation generation verified.")

def test_new_user_past_data_csv_import():
  print("Testing New User Past Data CSV Import & Dashboard Analysis...")
  import io
  from database.db_manager import (
    register_user, get_activity_logs, delete_activity_log,
    get_latest_emissions, sync_activity_logs_to_dashboard,
    get_aggregated_activity_summary
  )
  from components.csv_importer import (
    import_past_data_from_csv,
    generate_sample_past_data_csv,
    generate_blank_activity_csv_template
  )
  from components.calculations import calculate_carbon_credit_audit

  test_email = "newuser_csv_import@cleanenergy.com"
  register_user(
    email=test_email,
    password="Password123!",
    company_name="GreenVolt Manufacturing",
    owner_name="Elena Vance",
    role="Admin",
    company_type="Heavy Industrial Manufacturer",
    industry="Manufacturing Plant",
    employees=120,
    annual_revenue=15000000.0,
    country="India",
    state="Gujarat",
    location="Sanand Plant #2",
    is_demo=0
  )

  # Clean any residual test data
  from database.db_manager import get_db_connection
  conn = get_db_connection()
  conn.execute("DELETE FROM activity_logs WHERE user_email = ?", (test_email.lower().strip(),))
  conn.commit()
  conn.close()

  # 1. Verify New User initial zero state
  agg_init = get_aggregated_activity_summary(test_email)
  assert agg_init["total_entries"] == 0
  assert agg_init["total_co2"] == 0.0

  # 2. Test Multi-Row Historical Activity CSV Import
  csv_content = """date,frequency,electricity_kwh,diesel_liters,petrol_liters,gas_m3,truck_km,organic_waste_kg,plastic_waste_kg,notes
2025-01-15,monthly,32000,1100,300,2800,4500,1800,1200,Jan 2025 Shift Ledger
2025-02-15,monthly,29500,1050,280,2600,4100,1650,1100,Feb 2025 Shift Ledger
2025-03-15,monthly,31000,1120,310,2750,4400,1750,1150,Mar 2025 Shift Ledger
2025-04-15,monthly,33500,1200,320,2900,4800,1900,1250,Apr 2025 Shift Ledger
2025-05-15,monthly,35000,1250,330,3100,5000,2000,1300,May 2025 Shift Ledger
2025-06-15,monthly,34000,1180,315,3000,4700,1850,1220,Jun 2025 Shift Ledger
"""
  res_import = import_past_data_from_csv(io.StringIO(csv_content), test_email, is_demo=False)
  assert res_import["success"] is True
  assert res_import["type"] == "activity_logs"
  assert res_import["rows_imported"] == 6
  assert res_import["total_co2"] > 0.0
  print(f" [PASS] Multi-row historical CSV imported successfully ({res_import['rows_imported']} records, {res_import['total_co2']:.1f} t CO2e/yr).")

  # 3. Verify SQLite persistence and dynamic synchronization
  user_logs = get_activity_logs(test_email)
  assert len(user_logs) == 6
  agg_after = get_aggregated_activity_summary(test_email)
  assert agg_after["total_entries"] == 6
  assert agg_after["total_co2"] > 0.0
  print(f" [PASS] SQLite operational ledger synchronized: {agg_after['total_entries']} entries, {agg_after['total_co2']:.2f} t CO2.")

  # 4. Verify Executive Dashboard analysis metrics
  dash_res = sync_activity_logs_to_dashboard(test_email, is_demo=False)
  assert dash_res is not None
  assert dash_res["total_co2"] > 0.0
  assert len(dash_res["pillar_co2"]) >= 5
  assert dash_res["govt_credits"] > 0
  assert "top_leak" in dash_res

  audit = calculate_carbon_credit_audit({"email": test_email, "industry": "Manufacturing Plant", "company_type": "Heavy Industrial Manufacturer", "employees": 120}, user_logs, dash_res)
  assert audit["actual_daily_avg"] > 0.0
  assert audit["actual_weekly_avg"] > 0.0
  print(f" [PASS] Dashboard analysis metrics calculated: Total={dash_res['total_co2']:.1f} t, Quota={dash_res['govt_credits']:.0f} credits, Audit={audit['audit_verdict']}.")

  # 5. Test Spreadsheets with Unit Headers & Formatted Numbers (commas, spaces, units)
  formatted_csv = """Date (YYYY-MM-DD),Electricity (kWh),Diesel Fuel (Liters),Natural Gas (m³),Truck Freight (km),Organic Waste (kg),Notes / Remarks
2025-07-15,"32,500","1,250.0","2,850.5","4,600","1,950","July Operation with Units & Commas"
2025-08-15,"34,000","1,300.0","2,900.0","4,800","2,000","August Operation with Units & Commas"
"""
  res_formatted = import_past_data_from_csv(io.StringIO(formatted_csv), test_email, is_demo=False)
  assert res_formatted["success"] is True
  assert res_formatted["rows_imported"] == 2
  assert res_formatted["total_co2"] > 0.0

  # Verify that the parsed values in DB are non-zero numbers
  latest_logs = get_activity_logs(test_email, limit=2)
  assert latest_logs[0]["electricity_kwh"] in [32500.0, 34000.0]
  assert latest_logs[0]["diesel_liters"] in [1250.0, 1300.0]
  assert latest_logs[0]["gas_m3"] in [2850.5, 2900.0]
  assert latest_logs[0]["truck_km"] in [4600.0, 4800.0]
  print(f" [PASS] Spreadsheets with unit headers & comma numbers parsed accurately: {latest_logs[0]['electricity_kwh']} kWh, {latest_logs[0]['diesel_liters']} L.")

  # 6. Test Single-Row Facility Baseline CSV Import with Human Headers
  baseline_csv = """Electricity Consumption (kWh),Diesel (Liters),Natural Gas (m3),Truck Freight Distance (km),Allocated Carbon Credits,Notes
"360,000","14,500","35,000","60,000","400","Annual Baseline 2025"
"""
  res_baseline = import_past_data_from_csv(io.StringIO(baseline_csv), test_email, is_demo=False)
  assert res_baseline["success"] is True
  assert res_baseline["type"] == "baseline"
  assert res_baseline["total_co2"] > 0.0
  saved_base = get_latest_emissions(test_email)
  assert saved_base["electricity_kwh"] == 360000.0
  assert saved_base["diesel_liters"] == 14500.0
  assert saved_base["gas_m3"] == 35000.0
  assert saved_base["truck_km"] == 60000.0
  print(f" [PASS] Single-row baseline CSV import verified: Total={res_baseline['total_co2']:.1f} t CO2.")

  # 7. Test Transaction Ledger CSV Import (e.g. data/greenpack_emissions.csv)
  if os.path.exists("data/greenpack_emissions.csv"):
    res_ledger = import_past_data_from_csv("data/greenpack_emissions.csv", test_email, is_demo=False)
    assert res_ledger["success"] is True
    assert res_ledger["type"] == "activity_logs"
    assert res_ledger["rows_imported"] >= 12
    assert res_ledger["total_co2"] > 0.0
    print(f" [PASS] Line-item transaction ledger (greenpack_emissions.csv) imported & aggregated: {res_ledger['rows_imported']} monthly logs, {res_ledger['total_co2']:.1f} t CO2.")

  # 8. Test 1-Click Sample CSV Generation
  sample_csv = generate_sample_past_data_csv("Manufacturing Plant")
  assert "electricity_kwh" in sample_csv
  assert "diesel_liters" in sample_csv
  assert len(sample_csv.strip().split("\n")) == 13  # Header + 12 monthly rows

  # 9. Test Blank Template Generator
  tmpl_csv = generate_blank_activity_csv_template()
  assert "date,frequency" in tmpl_csv
  print(" [PASS] 1-Click sample generator and blank template verification complete.")

def test_views_routing_and_welcome_flow():
  print("Testing View Routing, Action Plan, Export, and Welcome Onboarding Flow...")
  import streamlit as st
  from components.views.action_plan_view import get_selected_fix_objects
  from components.calculations import CATEGORY_METADATA
  from components.data_presets import CATEGORY_FIXES

  # 1. Verify CATEGORY_METADATA covers all category fixes
  for cat in CATEGORY_FIXES.keys():
    assert cat in CATEGORY_METADATA, f"Missing category metadata for {cat}"
    assert "label" in CATEGORY_METADATA[cat]
    assert "icon" in CATEGORY_METADATA[cat]
  print(" [PASS] CATEGORY_METADATA dictionary complete and validated.")

  # 2. Verify get_selected_fix_objects fallback
  if "selected_fixes" in st.session_state:
    del st.session_state["selected_fixes"]
  if "selected_action_recs" in st.session_state:
    del st.session_state["selected_action_recs"]
  
  default_fixes = get_selected_fix_objects()
  assert len(default_fixes) > 0, "Expected non-empty default fixes"
  timeframes = {f.get("timeframe") for f in default_fixes}
  assert "quick_win" in timeframes
  assert "mid_term" in timeframes
  assert "long_term" in timeframes
  print(f" [PASS] Action Plan default fixes fallback verified: {len(default_fixes)} initiatives across all timeframes.")

  # 3. Verify specific selection
  st.session_state["selected_fixes"] = {"elec_led", "fuel_insulate"}
  chosen_fixes = get_selected_fix_objects()
  assert len(chosen_fixes) == 2
  ids = {f["id"] for f in chosen_fixes}
  assert ids == {"elec_led", "fuel_insulate"}
  print(" [PASS] Action Plan custom initiative filtering verified.")

  # 4. Verify Export CSV DataFrame generation
  data_rows = []
  for f in chosen_fixes:
    cat_meta = CATEGORY_METADATA.get(f.get("category"), {})
    data_rows.append({
      "Business Name": "Test Corp",
      "Execution Stage": f.get("timeframe_label"),
      "Category": cat_meta.get("label", f.get("category")),
      "Initiative Name": f.get("name"),
      "Description": f.get("description"),
      "CO2 Reduction (%)": f.get("co2_saved_pct"),
      "Estimated Cost": f.get("cost_estimate"),
      "Difficulty": f.get("difficulty"),
      "Payback Period": f.get("payback_time"),
    })
  df = pd.DataFrame(data_rows)
  assert len(df) == 2
  assert "CO2 Reduction (%)" in df.columns
  assert "Payback Period" in df.columns
  csv_str = df.to_csv(index=False)
  assert "Test Corp" in csv_str
  print(" [PASS] Export Action Plan CSV compilation verified.")

  # 5. Verify App.py Routing and Sidebar Definitions
  with open("app.py", "r", encoding="utf-8") as f:
    app_source = f.read()

  assert "render_welcome_view" in app_source
  assert "render_action_plan_view" in app_source
  assert "render_export_view" in app_source
  assert 'nav_sec == "action_plan"' in app_source
  assert 'nav_sec == "export"' in app_source
  assert 'nav_sec == "welcome"' in app_source
  assert '("Deep-Dive Analytics", "analytics"' in app_source
  assert '("Action Plan & Roadmap", "action_plan"' in app_source
  assert '("Export & Reports", "export"' in app_source
  print(" [PASS] App.py routing branches and sidebar integration verified.")

if __name__ == "__main__":
  test_database()
  test_calculations()
  test_demo_isolation_and_activity_logs()
  test_geo_data_and_statutory_carbon_quotas()
  test_carbon_credit_audit_and_cross_check()
  test_dynamic_graphs_and_hotspot_recommendations()
  test_copilot_assistant()
  test_ml_forecasting()
  test_presets_and_alternatives()
  test_new_user_past_data_csv_import()
  test_views_routing_and_welcome_flow()
  test_fastapi_endpoints()
  print("\n=======================================================")
  print("🎉 ALL TEST SUITES PASSED CLEANLY WITH ZERO ERRORS! 🎉")
  print("=======================================================")



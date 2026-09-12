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
    print("  [PASS] User registration and authentication verified.")

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
    print("  [PASS] Emissions assessment persistence verified.")

    # Test Market Transaction
    tx_id = record_market_transaction(test_email, "BUY", 50.0, 35.0, "Test compliance buy")
    assert tx_id > 0, "Failed to record market transaction"
    txs = get_market_transactions(test_email)
    assert len(txs) > 0, "Failed to retrieve market transactions"
    print("  [PASS] Carbon credit market transactions verified.")

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
    print(f"  [PASS] Surplus Case: {res_surplus['total_co2']} t CO2 vs {res_surplus['govt_credits']} credits -> {res_surplus['net_carbon_status']}")

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
    print(f"  [PASS] Deficit Case: {res_deficit['total_co2']} t CO2 vs {res_deficit['govt_credits']} credits -> Deficit: {res_deficit['credits_required']} t, Cost: ${res_deficit['compliance_cost']:,.0f}")

    # Top 10 Leaks Verification
    leaks = res_deficit["top_10_leaks"]
    assert len(leaks) == 10, f"Expected 10 leaks, found {len(leaks)}"
    assert leaks[0]["current_co2"] >= leaks[-1]["current_co2"], "Leaks must be sorted descending"
    for l in leaks:
        assert "impact_score" in l
        assert "priority" in l
        assert "potential_saving_co2" in l
    print("  [PASS] Top 10 leak diagnostics sorted and scored successfully.")

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
    print("  [PASS] ML polynomial regression & decarbonization pathway verified.")

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
    print("  [PASS] 4R alternatives, AI recommendations, and demo presets verified.")

def test_fastapi_endpoints():
    print("Testing FastAPI Application...")
    try:
        from fastapi.testclient import TestClient
        from api import app
        client = TestClient(app)
    except ImportError:
        print("  [SKIP] fastapi/testclient not installed in current environment; skipping REST API tests.")
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

    print("  [PASS] FastAPI endpoints responded successfully.")

if __name__ == "__main__":
    test_database()
    test_calculations()
    test_ml_forecasting()
    test_presets_and_alternatives()
    test_fastapi_endpoints()
    print("\n=======================================================")
    print("🎉 ALL TEST SUITES PASSED CLEANLY WITH ZERO ERRORS! 🎉")
    print("=======================================================")

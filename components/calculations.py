"""
Comprehensive GHG Protocol Emission Calculations Engine.
Computes Scope 1, Scope 2, Scope 3 emissions, cost equivalents, Top 10 leak point diagnostics,
carbon credit balance/deficit accounting, and multi-factor sustainability scoring (0–100).
"""

from typing import Dict, List, Any, Optional

# Standard GHG Protocol Emission Factors (metric tonnes of CO2e per input unit)
EMISSION_FACTORS = {
    # Energy
    "electricity_grid": 0.00042,     # 0.42 kg CO2e / kWh
    "diesel": 0.00268,               # 2.68 kg CO2e / Liter
    "petrol": 0.00231,               # 2.31 kg CO2e / Liter
    "natural_gas": 0.00203,          # 2.03 kg CO2e / m³
    
    # Transport
    "truck": 0.00085,                # 0.85 kg CO2e / km
    "car": 0.000171,                 # 0.171 kg CO2e / km
    "commute": 0.00012,              # 0.12 kg CO2e / km
    "delivery_vehicle_base": 1.25,   # baseline annual tonnes per delivery van
    
    # Waste
    "waste_organic": 0.00045,        # 0.45 kg CO2e / kg
    "waste_plastic": 0.00210,        # 2.10 kg CO2e / kg (high lifecycle footprint)
    "waste_metal": 0.00180,          # 1.80 kg CO2e / kg
    "waste_paper": 0.00095,          # 0.95 kg CO2e / kg
    "waste_hazardous": 0.00320,      # 3.20 kg CO2e / kg
    
    # Water
    "water_supply": 0.000344,        # 0.344 kg CO2e / m³ (pumping & treatment)
    "wastewater": 0.000708,          # 0.708 kg CO2e / m³ (aeration & biological treatment)
    
    # Manufacturing
    "raw_material": 0.45,            # 0.45 t CO2e / tonne embodied material
    "machine_hour": 0.0085,          # 8.5 kg CO2e / machine running hour (idle & wear)
}

# Standard Commercial Cost Factors (₹ INR per unit)
COST_FACTORS = {
"electricity": 12.87,       # ₹ / kWh
"diesel": 117.9,             # ₹ / Liter
"petrol": 112.1,             # ₹ / Liter
"natural_gas": 53.95,        # ₹ / m³
"truck": 70.55,              # ₹ / km (fuel, maintenance, wear)
"car": 29.05,                # ₹ / km
"commute": 16.60,            # ₹ / km
"delivery_vehicle": 348600.0, # ₹ / vehicle annual service overhead
"waste_organic": 6.64,      # ₹ / kg tipping fee
"waste_plastic": 14.94,      # ₹ / kg
"waste_metal": 18.26,        # ₹ / kg
"waste_paper": 9.13,        # ₹ / kg
"waste_hazardous": 62.25,    # ₹ / kg specialized disposal
"water_supply": 203.4,       # ₹ / m³
"wastewater": 315.4,         # ₹ / m³ sewer surcharge
"raw_material": 39840.0,      # ₹ / tonne
"machine_hour": 2656.0,       # ₹ / hour operating overhead
}

# Industry Benchmarks (average t CO2e per 1,000 units or normalized turnover)
INDUSTRY_BENCHMARKS = {
    "Food Processing": {"intensity_kg_per_unit": 0.95, "avg_renewable_pct": 18.0, "waste_divert_pct": 35.0},
    "Retail Store": {"intensity_kg_per_unit": 0.42, "avg_renewable_pct": 22.0, "waste_divert_pct": 52.0},
    "Logistics Company": {"intensity_kg_per_unit": 1.45, "avg_renewable_pct": 12.0, "waste_divert_pct": 28.0},
    "Manufacturing Plant": {"intensity_kg_per_unit": 2.80, "avg_renewable_pct": 15.0, "waste_divert_pct": 40.0},
    "Chemicals & Plastics": {"intensity_kg_per_unit": 3.40, "avg_renewable_pct": 10.0, "waste_divert_pct": 32.0},
    "Heavy Industrial Manufacturer": {"intensity_kg_per_unit": 4.10, "avg_renewable_pct": 10.0, "waste_divert_pct": 25.0},
    "Hospitality & Cafe": {"intensity_kg_per_unit": 0.60, "avg_renewable_pct": 20.0, "waste_divert_pct": 45.0},
    "Other Commercial": {"intensity_kg_per_unit": 1.10, "avg_renewable_pct": 15.0, "waste_divert_pct": 35.0},
    "Other": {"intensity_kg_per_unit": 1.10, "avg_renewable_pct": 15.0, "waste_divert_pct": 35.0}
}

# Statutory Carbon Allowance Allocation Benchmarks (EPA, CARB, EU ETS, CCTS Regulatory Standards)
INDUSTRY_QUOTA_BENCHMARKS = {
    "Heavy Industrial Manufacturer": {
        "annual_per_employee_co2": 18.5,
        "min_credits": 800.0,
        "benchmark_price": 42.0,
        "regulatory_regime": "EU ETS / EPA Subpart C Mandatory Cap",
        "description": "Heavy industrial manufacturing with intensive thermal processing & smelting"
    },
    "Chemicals & Plastics": {
        "annual_per_employee_co2": 15.0,
        "min_credits": 600.0,
        "benchmark_price": 40.0,
        "regulatory_regime": "Chemicals Sector Cap-and-Trade",
        "description": "Chemical synthesis, polymer polymerization, and process reaction lines"
    },
    "Manufacturing Plant": {
        "annual_per_employee_co2": 9.5,
        "min_credits": 350.0,
        "benchmark_price": 38.0,
        "regulatory_regime": "CCTS / EPA Subpart W Benchmark",
        "description": "Machining, assembly, fabrication, and industrial tooling facilities"
    },
    "Logistics Company": {
        "annual_per_employee_co2": 11.0,
        "min_credits": 400.0,
        "benchmark_price": 36.0,
        "regulatory_regime": "Commercial Transport & Fleet Cap",
        "description": "Heavy freight, regional distribution centers, and commercial fleet networks"
    },
    "Food Processing": {
        "annual_per_employee_co2": 6.8,
        "min_credits": 250.0,
        "benchmark_price": 2905.0,
        "regulatory_regime": "Agri-Industrial Processing Quota",
        "description": "Commercial refrigeration, industrial ovens, steam boilers, and food canning"
    },
    "Retail Store": {
        "annual_per_employee_co2": 3.2,
        "min_credits": 80.0,
        "benchmark_price": 32.0,
        "regulatory_regime": "Commercial Building Energy Standard",
        "description": "Retail storefronts, retail HVAC load, and light merchandise logistics"
    },
    "Hospitality & Cafe": {
        "annual_per_employee_co2": 2.5,
        "min_credits": 60.0,
        "benchmark_price": 30.0,
        "regulatory_regime": "Light Commercial Hospitality Standard",
        "description": "Commercial kitchens, dining HVAC, customer refrigeration, and food waste"
    },
    "Other Commercial": {
        "annual_per_employee_co2": 4.5,
        "min_credits": 120.0,
        "benchmark_price": 34.0,
        "regulatory_regime": "General Commercial Benchmark",
        "description": "Multi-tenant commercial buildings, professional campuses, and data hubs"
    }
}

COMPANY_TYPE_MULTIPLIERS = {
    "Heavy Industrial Manufacturer": 1.50,
    "Enterprise / Corporation": 1.35,
    "Logistics Fleet Operator": 1.20,
    "SME / Mid-Sized Business": 1.00,
    "Retail / Distribution": 0.85,
    "Mid-Sized Enterprise": 1.15,
    "Mid-Sized Manufacturer": 1.15,
    "SME Retailer": 0.85,
    "Logistics Fleet": 1.20,
    "Heavy Manufacturing": 1.50,
    "SME": 1.00
}

def get_statutory_carbon_quota(
    industry: str,
    company_type: str = "SME / Mid-Sized Business",
    employees: int = 50
) -> Dict[str, Any]:
    """
    Calculates research-backed statutory carbon credit quota and benchmark trading price
    calibrated to EPA, EU ETS, California CARB, and Indian CCTS compliance benchmarks.
    Allocation varies dynamically by industry sector, company type classification, and workforce headcount.
    """
    matched_data = INDUSTRY_QUOTA_BENCHMARKS.get(industry)
    if not matched_data:
        for ind_key, data in INDUSTRY_QUOTA_BENCHMARKS.items():
            if ind_key.lower() in (industry or "").lower() or (industry or "").lower() in ind_key.lower():
                matched_data = data
                break
    if not matched_data:
        matched_data = INDUSTRY_QUOTA_BENCHMARKS["Other Commercial"]

    multiplier = 1.0
    for ct_key, mult in COMPANY_TYPE_MULTIPLIERS.items():
        if ct_key.lower() in (company_type or "").lower():
            multiplier = mult
            break

    emp = max(1, int(employees if employees is not None else 50))
    per_emp = matched_data["annual_per_employee_co2"]
    min_cred = matched_data["min_credits"]
    raw_quota = emp * per_emp * multiplier
    final_quota = round(max(min_cred, raw_quota), 0)

    return {
        "quota_credits": final_quota,
        "benchmark_price": matched_data["benchmark_price"],
        "annual_per_employee_co2": per_emp,
        "min_credits": min_cred,
        "type_multiplier": multiplier,
        "regulatory_regime": matched_data["regulatory_regime"],
        "description": matched_data["description"]
    }


def calculate_carbon_credit_audit(
    user_prof: Dict[str, Any],
    activity_logs: List[Dict[str, Any]],
    latest_assessment: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Performs a rigorous cross-check audit between initial government statutory quotas and
    operational carbon credit usage across daily, weekly, and projected annual timeframes.
    """
    industry = user_prof.get("industry", "Manufacturing Plant")
    company_type = user_prof.get("company_type", "SME / Mid-Sized Business")
    employees = user_prof.get("employees", 50)
    
    statutory_info = get_statutory_carbon_quota(industry, company_type, employees)
    latest = latest_assessment or {}
    
    # Initial Government Issued Quota
    initial_govt_quota = float(latest.get("total_credits") or statutory_info["quota_credits"])
    benchmark_price = float(latest.get("credit_price") or statutory_info["benchmark_price"])
    
    daily_quota_target = round(initial_govt_quota / 365.0, 3)
    weekly_quota_target = round(initial_govt_quota / 52.0, 2)
    monthly_quota_target = round(initial_govt_quota / 12.0, 2)
    
    # Categorize logs by frequency
    daily_logs = [l for l in activity_logs if l.get("frequency") == "daily"]
    weekly_logs = [l for l in activity_logs if l.get("frequency") == "weekly"]
    
    # Actual daily usage
    daily_credits_sum = sum(l.get("calculated_total_co2", 0.0) for l in daily_logs)
    actual_daily_avg = round(daily_credits_sum / len(daily_logs), 3) if daily_logs else 0.0
    actual_daily_latest = round(daily_logs[0].get("calculated_total_co2", 0.0), 3) if daily_logs else 0.0
    daily_pct_of_allowance = round((actual_daily_avg / daily_quota_target) * 100, 1) if daily_quota_target > 0 else 0.0
    
    # Actual weekly usage
    weekly_credits_sum = sum(l.get("calculated_total_co2", 0.0) for l in weekly_logs)
    actual_weekly_avg = round(weekly_credits_sum / len(weekly_logs), 2) if weekly_logs else 0.0
    actual_weekly_latest = round(weekly_logs[0].get("calculated_total_co2", 0.0), 2) if weekly_logs else 0.0
    weekly_pct_of_allowance = round((actual_weekly_avg / weekly_quota_target) * 100, 1) if weekly_quota_target > 0 else 0.0
    
    # Accrued credits used to date
    accrued_credits_used = round(sum(l.get("calculated_total_co2", 0.0) for l in activity_logs), 2)
    accrued_remaining_balance = round(initial_govt_quota - accrued_credits_used, 2)
    accrued_balance_pct = round((accrued_remaining_balance / initial_govt_quota) * 100, 1) if initial_govt_quota > 0 else 0.0
    
    # Expected Carbon Credit Use (Annualized run-rate forecast)
    if latest.get("total_co2") is not None and float(latest.get("total_co2", 0)) > 0:
        expected_annual_burn = round(float(latest.get("total_co2", 0)), 1)
    elif activity_logs:
        annual_from_daily = actual_daily_avg * 365.0
        annual_from_weekly = actual_weekly_avg * 52.0
        expected_annual_burn = round(annual_from_daily + annual_from_weekly, 1)
    else:
        expected_annual_burn = initial_govt_quota
        
    expected_daily_burn = round(expected_annual_burn / 365.0, 3)
    expected_weekly_burn = round(expected_annual_burn / 52.0, 2)
    expected_monthly_burn = round(expected_annual_burn / 12.0, 2)
    
    # Net Projected Position
    projected_net_balance = round(initial_govt_quota - expected_annual_burn, 1)
    is_projected_deficit = projected_net_balance < 0
    projected_credits_needed = abs(projected_net_balance) if is_projected_deficit else 0.0
    projected_surplus_credits = projected_net_balance if not is_projected_deficit else 0.0
    projected_compliance_cost = round(projected_credits_needed * benchmark_price, 0)
    
    # Quota Runway (Days until initial quota is exhausted at expected daily burn)
    if expected_daily_burn > 0:
        quota_runway_days = max(0, int(accrued_remaining_balance / expected_daily_burn))
    else:
        quota_runway_days = 365
        
    # Compliance Verdict & Summary
    if not activity_logs:
        audit_verdict = "INITIAL ALLOCATION RECORDED"
        audit_status_color = "#3B82F6"
        audit_summary_text = f"Government allocated {initial_govt_quota:,.0f} carbon credits under {statutory_info['regulatory_regime']} framework. Awaiting operational activity logging."
    elif not is_projected_deficit:
        audit_verdict = "COMPLIANT — SURPLUS FORECAST 🟢"
        audit_status_color = "#10B981"
        audit_summary_text = f"Operating safely within statutory quota. Projected annual surplus of {projected_surplus_credits:,.1f} credits available for trading reserve."
    else:
        audit_verdict = "QUOTA DEFICIT WARNING 🔴"
        audit_status_color = "#EF4444"
        audit_summary_text = f"Operational run-rate ({expected_annual_burn:,.1f} t) exceeds initial government quota ({initial_govt_quota:,.0f} t). Projected deficit: {projected_credits_needed:,.1f} credits (₹{projected_compliance_cost:,.0f} liability)."
        
    return {
        # Government Quota
        "initial_govt_quota": initial_govt_quota,
        "benchmark_price": benchmark_price,
        "regulatory_regime": statutory_info["regulatory_regime"],
        "industry": industry,
        "company_type": company_type,
        "employees": employees,
        "annual_per_employee_co2": statutory_info["annual_per_employee_co2"],
        "daily_quota_target": daily_quota_target,
        "weekly_quota_target": weekly_quota_target,
        "monthly_quota_target": monthly_quota_target,
        
        # Actual Usage
        "daily_entries_count": len(daily_logs),
        "actual_daily_avg": actual_daily_avg,
        "actual_daily_latest": actual_daily_latest,
        "daily_pct_of_allowance": daily_pct_of_allowance,
        "weekly_entries_count": len(weekly_logs),
        "actual_weekly_avg": actual_weekly_avg,
        "actual_weekly_latest": actual_weekly_latest,
        "weekly_pct_of_allowance": weekly_pct_of_allowance,
        "total_entries_count": len(activity_logs),
        "accrued_credits_used": accrued_credits_used,
        "accrued_remaining_balance": accrued_remaining_balance,
        "accrued_balance_pct": accrued_balance_pct,
        
        # Expected Usage
        "expected_daily_burn": expected_daily_burn,
        "expected_weekly_burn": expected_weekly_burn,
        "expected_monthly_burn": expected_monthly_burn,
        "expected_annual_burn": expected_annual_burn,
        "projected_net_balance": projected_net_balance,
        "is_projected_deficit": is_projected_deficit,
        "projected_credits_needed": projected_credits_needed,
        "projected_surplus_credits": projected_surplus_credits,
        "projected_compliance_cost": projected_compliance_cost,
        "quota_runway_days": quota_runway_days,
        
        # Verdict & Diagnostics
        "audit_verdict": audit_verdict,
        "audit_status_color": audit_status_color,
        "audit_summary_text": audit_summary_text
    }



def safe_float(val: Any, default: float = 0.0) -> float:
    """Safely converts a value to float, returning default if None, empty string, NaN, or invalid."""
    if val is None or val == "":
        return float(default)
    try:
        f = float(val)
        import math
        if math.isnan(f):
            return float(default)
        return f
    except (ValueError, TypeError):
        return float(default)

def calculate_detailed_emissions(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs end-to-end greenhouse gas and cost computations across 5 pillars:
    Energy, Transport, Waste, Water, and Manufacturing.
    """
    # 1. Extract inputs with defaults
    elec_val = inputs.get("electricity_kwh") if inputs.get("electricity_kwh") is not None else inputs.get("electricity")
    elec_kwh = max(0.0, safe_float(elec_val, 0.0))
    renew_pct = min(100.0, max(0.0, safe_float(inputs.get("renewable_pct"), 0.0)))
    diesel_val = inputs.get("diesel_liters") if inputs.get("diesel_liters") is not None else (safe_float(inputs.get("fuel"), 0.0) * 0.7)
    diesel_l = max(0.0, safe_float(diesel_val, 0.0))
    petrol_val = inputs.get("petrol_liters") if inputs.get("petrol_liters") is not None else (safe_float(inputs.get("fuel"), 0.0) * 0.3)
    petrol_l = max(0.0, safe_float(petrol_val, 0.0))
    gas_m3 = max(0.0, safe_float(inputs.get("gas_m3"), 0.0))

    truck_val = inputs.get("truck_km") if inputs.get("truck_km") is not None else (safe_float(inputs.get("transport"), 0.0) * 0.6)
    truck_km = max(0.0, safe_float(truck_val, 0.0))
    car_val = inputs.get("car_km") if inputs.get("car_km") is not None else (safe_float(inputs.get("transport"), 0.0) * 0.3)
    car_km = max(0.0, safe_float(car_val, 0.0))
    commute_val = inputs.get("commute_km") if inputs.get("commute_km") is not None else (safe_float(inputs.get("transport"), 0.0) * 0.1)
    commute_km = max(0.0, safe_float(commute_val, 0.0))
    delivery_vehs = max(0, int(safe_float(inputs.get("delivery_vehicles"), 2)))

    waste_base = safe_float(inputs.get("waste"), 0.0)
    waste_org_val = inputs.get("organic_waste_kg") if inputs.get("organic_waste_kg") is not None else (waste_base * 0.4)
    waste_org_kg = max(0.0, safe_float(waste_org_val, 0.0))
    waste_plas_val = inputs.get("plastic_waste_kg") if inputs.get("plastic_waste_kg") is not None else (waste_base * 0.3)
    waste_plas_kg = max(0.0, safe_float(waste_plas_val, 0.0))
    waste_met_val = inputs.get("metal_waste_kg") if inputs.get("metal_waste_kg") is not None else (waste_base * 0.1)
    waste_met_kg = max(0.0, safe_float(waste_met_val, 0.0))
    waste_pap_val = inputs.get("paper_waste_kg") if inputs.get("paper_waste_kg") is not None else (waste_base * 0.15)
    waste_pap_kg = max(0.0, safe_float(waste_pap_val, 0.0))
    waste_haz_val = inputs.get("hazardous_waste_kg") if inputs.get("hazardous_waste_kg") is not None else (waste_base * 0.05)
    waste_haz_kg = max(0.0, safe_float(waste_haz_val, 0.0))

    # Track silently defaulted fields to surface transparency to user
    defaulted_fields = []
    if inputs.get("water_m3") is None:
        defaulted_fields.append("water_m3")
    if inputs.get("raw_material_tonnes") is None:
        defaulted_fields.append("raw_material_tonnes")
    if inputs.get("production_units") is None:
        defaulted_fields.append("production_units")
    if inputs.get("total_credits") is None and inputs.get("total_carbon_credits") is None:
        defaulted_fields.append("total_credits")
    if inputs.get("machine_running_hours") is None and inputs.get("machine_hours") is None:
        defaulted_fields.append("machine_hours")

    water_val = inputs.get("water_m3")
    water_m3 = max(0.0, safe_float(water_val, 1200.0))

    ww_val = inputs.get("wastewater_m3")
    wastewater_m3 = max(0.0, safe_float(ww_val, water_m3 * 0.85))

    rm_val = inputs.get("raw_material_tonnes")
    raw_mat_t = max(0.0, safe_float(rm_val, 150.0))

    pu_val = inputs.get("production_units")
    prod_units = max(0.0, safe_float(pu_val, 25000.0))

    mh_val = inputs.get("machine_running_hours") if inputs.get("machine_running_hours") is not None else inputs.get("machine_hours")
    mach_hours = max(0.0, safe_float(mh_val, 2200.0))

    gc_val = inputs.get("total_credits") if inputs.get("total_credits") is not None else inputs.get("total_carbon_credits")
    govt_credits = max(0.0, safe_float(gc_val, 150.0))

    cp_val = inputs.get("credit_price") if inputs.get("credit_price") is not None else inputs.get("carbon_credit_price")
    credit_price = max(1.0, safe_float(cp_val, 2905.0))

    # 2. Emission Calculations (t CO2e)
    # Electricity takes renewable share into account
    net_grid_kwh = elec_kwh * (1.0 - (renew_pct / 100.0))
    co2_electricity = round(net_grid_kwh * EMISSION_FACTORS["electricity_grid"], 2)
    co2_diesel = round(diesel_l * EMISSION_FACTORS["diesel"], 2)
    co2_petrol = round(petrol_l * EMISSION_FACTORS["petrol"], 2)
    co2_gas = round(gas_m3 * EMISSION_FACTORS["natural_gas"], 2)
    co2_energy = round(co2_electricity + co2_diesel + co2_petrol + co2_gas, 2)

    co2_truck = round(truck_km * EMISSION_FACTORS["truck"], 2)
    co2_car = round(car_km * EMISSION_FACTORS["car"], 2)
    co2_commute = round(commute_km * EMISSION_FACTORS["commute"], 2)
    co2_fleet_overhead = round(delivery_vehs * EMISSION_FACTORS["delivery_vehicle_base"], 2)
    co2_transport = round(co2_truck + co2_car + co2_commute + co2_fleet_overhead, 2)

    co2_waste_org = round(waste_org_kg * EMISSION_FACTORS["waste_organic"], 2)
    co2_waste_plas = round(waste_plas_kg * EMISSION_FACTORS["waste_plastic"], 2)
    co2_waste_met = round(waste_met_kg * EMISSION_FACTORS["waste_metal"], 2)
    co2_waste_pap = round(waste_pap_kg * EMISSION_FACTORS["waste_paper"], 2)
    co2_waste_haz = round(waste_haz_kg * EMISSION_FACTORS["waste_hazardous"], 2)
    co2_waste = round(co2_waste_org + co2_waste_plas + co2_waste_met + co2_waste_pap + co2_waste_haz, 2)

    co2_water = round(water_m3 * EMISSION_FACTORS["water_supply"], 2)
    co2_wastewater = round(wastewater_m3 * EMISSION_FACTORS["wastewater"], 2)
    co2_water_total = round(co2_water + co2_wastewater, 2)

    co2_raw_mat = round(raw_mat_t * 0.12, 2) # Scope 3 industrial baseline slice
    co2_machinery = round(mach_hours * EMISSION_FACTORS["machine_hour"], 2)
    co2_manufacturing = round(co2_raw_mat + co2_machinery, 2)

    # Total CO2e
    total_co2 = round(co2_energy + co2_transport + co2_waste + co2_water_total + co2_manufacturing, 2)

    # 3. Cost Calculations (₹ INR)
    cost_electricity = round(elec_kwh * COST_FACTORS["electricity"], 0)
    cost_diesel = round(diesel_l * COST_FACTORS["diesel"], 0)
    cost_petrol = round(petrol_l * COST_FACTORS["petrol"], 0)
    cost_gas = round(gas_m3 * COST_FACTORS["natural_gas"], 0)
    cost_energy = round(cost_electricity + cost_diesel + cost_petrol + cost_gas, 0)

    cost_truck = round(truck_km * COST_FACTORS["truck"], 0)
    cost_car = round(car_km * COST_FACTORS["car"], 0)
    cost_commute = round(commute_km * COST_FACTORS["commute"], 0)
    cost_fleet = round(delivery_vehs * COST_FACTORS["delivery_vehicle"], 0)
    cost_transport = round(cost_truck + cost_car + cost_commute + cost_fleet, 0)

    cost_waste = round(
        (waste_org_kg * COST_FACTORS["waste_organic"]) +
        (waste_plas_kg * COST_FACTORS["waste_plastic"]) +
        (waste_met_kg * COST_FACTORS["waste_metal"]) +
        (waste_pap_kg * COST_FACTORS["waste_paper"]) +
        (waste_haz_kg * COST_FACTORS["waste_hazardous"]), 0
    )

    cost_water_total = round((water_m3 * COST_FACTORS["water_supply"]) + (wastewater_m3 * COST_FACTORS["wastewater"]), 0)
    cost_manufacturing = round((mach_hours * COST_FACTORS["machine_hour"]), 0)

    total_cost = round(cost_energy + cost_transport + cost_waste + cost_water_total + cost_manufacturing, 0)

    # 4. Pillar Breakdown
    pillar_co2 = {
        "Electricity": co2_electricity,
        "Fuel & Heating": round(co2_diesel + co2_petrol + co2_gas, 2),
        "Transport & Fleet": co2_transport,
        "Waste & Packaging": co2_waste,
        "Water & Effluent": co2_water_total,
        "Industrial Ops": co2_manufacturing
    }

    pillar_shares = {}
    for k, v in pillar_co2.items():
        pillar_shares[k] = round((v / total_co2 * 100), 1) if total_co2 > 0 else 0.0

    # 5. Top 10 Leak Points Identification & Diagnostics
    candidate_leaks = [
        {
            "source": "Grid Electricity Base-Load",
            "category": "Electricity",
            "icon": "⚡",
            "feather_icon": "zap",
            "current_co2": co2_electricity,
            "cost_impact": cost_electricity,
            "potential_saving_pct": 28.0,
            "potential_saving_co2": round(co2_electricity * 0.28, 2),
            "potential_saving_cost": round(cost_electricity * 0.28, 0),
            "unit": "kWh",
            "activity_val": elec_kwh
        },
        {
            "source": "Diesel Heavy Machinery & Gensets",
            "category": "Fuel",
            "icon": "🚜",
            "feather_icon": "droplet",
            "current_co2": co2_diesel,
            "cost_impact": cost_diesel,
            "potential_saving_pct": 22.0,
            "potential_saving_co2": round(co2_diesel * 0.22, 2),
            "potential_saving_cost": round(cost_diesel * 0.22, 0),
            "unit": "Liters",
            "activity_val": diesel_l
        },
        {
            "source": "Natural Gas Thermal Boilers",
            "category": "Fuel",
            "icon": "🔥",
            "feather_icon": "droplet",
            "current_co2": co2_gas,
            "cost_impact": cost_gas,
            "potential_saving_pct": 20.0,
            "potential_saving_co2": round(co2_gas * 0.20, 2),
            "potential_saving_cost": round(cost_gas * 0.20, 0),
            "unit": "m³",
            "activity_val": gas_m3
        },
        {
            "source": "Heavy Freight & Distribution Trucks",
            "category": "Transport",
            "icon": "🚚",
            "feather_icon": "truck",
            "current_co2": co2_truck,
            "cost_impact": cost_truck,
            "potential_saving_pct": 25.0,
            "potential_saving_co2": round(co2_truck * 0.25, 2),
            "potential_saving_cost": round(cost_truck * 0.25, 0),
            "unit": "km",
            "activity_val": truck_km
        },
        {
            "source": "Non-Recycled Landfill Plastics",
            "category": "Waste",
            "icon": "🧴",
            "feather_icon": "trash-2",
            "current_co2": co2_waste_plas,
            "cost_impact": round(waste_plas_kg * COST_FACTORS["waste_plastic"], 0),
            "potential_saving_pct": 45.0,
            "potential_saving_co2": round(co2_waste_plas * 0.45, 2),
            "potential_saving_cost": round(waste_plas_kg * COST_FACTORS["waste_plastic"] * 0.45, 0),
            "unit": "kg",
            "activity_val": waste_plas_kg
        },
        {
            "source": "Hazardous Waste & Chemical Solvents",
            "category": "Waste",
            "icon": "☣️",
            "feather_icon": "alert-triangle",
            "current_co2": co2_waste_haz,
            "cost_impact": round(waste_haz_kg * COST_FACTORS["waste_hazardous"], 0),
            "potential_saving_pct": 50.0,
            "potential_saving_co2": round(co2_waste_haz * 0.50, 2),
            "potential_saving_cost": round(waste_haz_kg * COST_FACTORS["waste_hazardous"] * 0.50, 0),
            "unit": "kg",
            "activity_val": waste_haz_kg
        },
        {
            "source": "Untreated Industrial Wastewater Discharge",
            "category": "Water",
            "icon": "💧",
            "feather_icon": "droplet",
            "current_co2": co2_wastewater,
            "cost_impact": round(wastewater_m3 * COST_FACTORS["wastewater"], 0),
            "potential_saving_pct": 35.0,
            "potential_saving_co2": round(co2_wastewater * 0.35, 2),
            "potential_saving_cost": round(wastewater_m3 * COST_FACTORS["wastewater"] * 0.35, 0),
            "unit": "m³",
            "activity_val": wastewater_m3
        },
        {
            "source": "Organic & Food Byproduct Waste",
            "category": "Waste",
            "icon": "🍎",
            "feather_icon": "trash-2",
            "current_co2": co2_waste_org,
            "cost_impact": round(waste_org_kg * COST_FACTORS["waste_organic"], 0),
            "potential_saving_pct": 40.0,
            "potential_saving_co2": round(co2_waste_org * 0.40, 2),
            "potential_saving_cost": round(waste_org_kg * COST_FACTORS["waste_organic"] * 0.40, 0),
            "unit": "kg",
            "activity_val": waste_org_kg
        },
        {
            "source": "Machine Idle Hours & Motor Friction",
            "category": "Manufacturing",
            "icon": "⚙️",
            "feather_icon": "settings",
            "current_co2": co2_machinery,
            "cost_impact": cost_manufacturing,
            "potential_saving_pct": 18.0,
            "potential_saving_co2": round(co2_machinery * 0.18, 2),
            "potential_saving_cost": round(cost_manufacturing * 0.18, 0),
            "unit": "Hours",
            "activity_val": mach_hours
        },
        {
            "source": "Commercial Fleet Delivery Vans",
            "category": "Transport",
            "icon": "🚐",
            "feather_icon": "truck",
            "current_co2": co2_fleet_overhead,
            "cost_impact": cost_fleet,
            "potential_saving_pct": 20.0,
            "potential_saving_co2": round(co2_fleet_overhead * 0.20, 2),
            "potential_saving_cost": round(cost_fleet * 0.20, 0),
            "unit": "Vehicles",
            "activity_val": delivery_vehs
        },
        {
            "source": "Company Passenger Cars & Sales Petrol",
            "category": "Transport",
            "icon": "🚗",
            "feather_icon": "truck",
            "current_co2": co2_petrol,
            "cost_impact": cost_petrol,
            "potential_saving_pct": 20.0,
            "potential_saving_co2": round(co2_petrol * 0.20, 2),
            "potential_saving_cost": round(cost_petrol * 0.20, 0),
            "unit": "km",
            "activity_val": car_km
        },
        {
            "source": "Municipal Cardboard & Paper Waste",
            "category": "Waste",
            "icon": "📦",
            "feather_icon": "box",
            "current_co2": co2_waste_pap,
            "cost_impact": round(waste_pap_kg * COST_FACTORS["waste_paper"], 0),
            "potential_saving_pct": 30.0,
            "potential_saving_co2": round(co2_waste_pap * 0.30, 2),
            "potential_saving_cost": round(waste_pap_kg * COST_FACTORS["waste_paper"] * 0.30, 0),
            "unit": "kg",
            "activity_val": waste_pap_kg
        },
        {
            "source": "Process Water Evaporation & Pumping",
            "category": "Water",
            "icon": "🚰",
            "feather_icon": "droplet",
            "current_co2": co2_water,
            "cost_impact": round(water_m3 * COST_FACTORS["water_supply"], 0),
            "potential_saving_pct": 25.0,
            "potential_saving_co2": round(co2_water * 0.25, 2),
            "potential_saving_cost": round(water_m3 * COST_FACTORS["water_supply"] * 0.25, 0),
            "unit": "m³",
            "activity_val": water_m3
        }
    ]

    # Sort candidates by current_co2 descending and select Top 10
    sorted_leaks = sorted(candidate_leaks, key=lambda x: x["current_co2"], reverse=True)
    top_10_leaks = []

    for rank, leak in enumerate(sorted_leaks[:10], start=1):
        share_pct = round((leak["current_co2"] / total_co2 * 100), 1) if total_co2 > 0 else 0.0
        
        # Priority and Severity
        if share_pct >= 28.0 or leak["current_co2"] >= 80.0:
            priority = "Critical Priority"
            priority_color = "#DC2626" # Red
            badge_class = "badge-critical"
            status = "Active Leak 🔥"
            impact_score = 95 - (rank * 2)
        elif share_pct >= 16.0 or leak["current_co2"] >= 40.0:
            priority = "High Priority"
            priority_color = "#EA580C" # Orange
            badge_class = "badge-high"
            status = "Needs Audit ⚠️"
            impact_score = 80 - (rank * 2)
        elif share_pct >= 8.0:
            priority = "Medium Priority"
            priority_color = "#D97706" # Amber
            badge_class = "badge-medium"
            status = "Moderate Risk 🟡"
            impact_score = 65 - (rank * 2)
        else:
            priority = "Low Priority"
            priority_color = "#16A34A" # Green
            badge_class = "badge-low"
            status = "Acceptable 🟢"
            impact_score = 45 - (rank * 2)

        leak_copy = leak.copy()
        leak_copy["rank"] = rank
        leak_copy["share_pct"] = share_pct
        leak_copy["priority"] = priority
        leak_copy["priority_color"] = priority_color
        leak_copy["badge_class"] = badge_class
        leak_copy["status"] = status
        leak_copy["impact_score"] = max(10, min(100, impact_score))
        top_10_leaks.append(leak_copy)

    # 6. Carbon Credit Accounting
    credits_used = total_co2
    credit_balance = round(govt_credits - total_co2, 2)

    if credit_balance >= 0:
        net_carbon_status = "Carbon Neutral 🟢"
        status_color = "#10B981"
        credits_remaining = credit_balance
        credits_required = 0.0
        possible_to_sell = credit_balance
        est_revenue = round(possible_to_sell * credit_price, 2)
        est_purchase_cost = 0.0
        compliance_cost = 0.0
        deficit_status = False
    else:
        net_carbon_status = "Carbon Credit Deficit 🔴"
        status_color = "#EF4444"
        credits_remaining = 0.0
        credits_required = abs(credit_balance)
        possible_to_sell = 0.0
        est_revenue = 0.0
        est_purchase_cost = round(credits_required * credit_price, 2)
        compliance_cost = est_purchase_cost
        deficit_status = True

    # 7. Sustainability Score (0–100) Multi-factor Algorithm
    # Factor A: Renewable share (0-100% -> up to 25 pts)
    score_renewable = (renew_pct / 100.0) * 25.0

    # Factor B: Carbon Credit health (Neutral/surplus gets 25 pts, deficit decays)
    if not deficit_status:
        score_credits = 25.0
    else:
        deficit_ratio = credits_required / (govt_credits + 1e-5)
        score_credits = max(0.0, 25.0 - min(25.0, deficit_ratio * 15.0))

    # Factor C: Production emission intensity (kg CO2 per unit)
    industry_type = inputs.get("industry", inputs.get("business_type", "Manufacturing Plant"))
    bench = INDUSTRY_BENCHMARKS.get(industry_type, INDUSTRY_BENCHMARKS["Other"])
    bench_intensity = bench["intensity_kg_per_unit"]

    if prod_units > 0:
        actual_intensity = (total_co2 * 1000.0) / prod_units
        intensity_ratio = actual_intensity / bench_intensity
        if intensity_ratio <= 0.8:
            score_intensity = 25.0
        elif intensity_ratio <= 1.2:
            score_intensity = 20.0
        elif intensity_ratio <= 1.8:
            score_intensity = 14.0
        else:
            score_intensity = 8.0
    else:
        actual_intensity = 0.0
        score_intensity = 15.0

    # Factor D: Waste and Water circularity
    total_waste_kg = waste_org_kg + waste_plas_kg + waste_met_kg + waste_pap_kg + waste_haz_kg
    hazardous_share = (waste_haz_kg / total_waste_kg) if total_waste_kg > 0 else 0.0
    score_circular = max(5.0, 25.0 - (hazardous_share * 60.0))

    sustainability_score = round(min(100.0, max(0.0, score_renewable + score_credits + score_intensity + score_circular)), 1)

    return {
        "total_co2": total_co2,
        "total_cost": total_cost,
        "pillar_co2": pillar_co2,
        "pillar_shares": pillar_shares,
        "top_10_leaks": top_10_leaks,
        "top_leak": top_10_leaks[0] if top_10_leaks else None,
        # Carbon Credits
        "govt_credits": govt_credits,
        "credit_price": credit_price,
        "credits_used": credits_used,
        "credit_balance": credit_balance,
        "credits_remaining": credits_remaining,
        "credits_required": credits_required,
        "possible_to_sell": possible_to_sell,
        "est_revenue": est_revenue,
        "est_purchase_cost": est_purchase_cost,
        "compliance_cost": compliance_cost,
        "net_carbon_status": net_carbon_status,
        "status_color": status_color,
        "is_deficit": deficit_status,
        # Metrics
        "sustainability_score": sustainability_score,
        "actual_intensity_kg_per_unit": round(actual_intensity, 2) if prod_units > 0 else None,
        "benchmark_intensity": bench_intensity,
        "production_units": prod_units,
        "renewable_pct": renew_pct,
        "raw_inputs": inputs,
        "defaulted_fields": defaulted_fields
    }

# Backward compatibility alias
def calculate_emissions(inputs: Dict[str, Any]) -> Dict[str, Any]:
    return calculate_detailed_emissions(inputs)


def generate_hotspot_recommendations(emissions_res: Dict[str, Any], user_prof: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Dynamically generates and prioritizes Green Decarbonization Recommendations based on
    the business's actual emission leak hotspots.
    
    Ranks interventions so that the business's #1, #2, and #3 leak sources receive top priority.
    Dynamically computes CO2 saved, annual financial savings, CapEx estimate, ROI %, payback periods,
    and carbon credits saved based on actual measured leak volume and facility scale.
    """
    if not emissions_res:
        return []

    top_leaks = emissions_res.get("top_10_leaks", [])
    total_co2 = max(0.1, emissions_res.get("total_co2", 100.0))
    credit_price = emissions_res.get("credit_price", 38.0)
    
    prof = user_prof or {}
    employees = max(5, int(prof.get("employees", 50)))
    scale_factor = max(0.6, min(4.0, (employees / 40.0) * (total_co2 / 300.0) ** 0.5))

    # Master repository of hotspot-specific decarbonization and circular solutions
    HOTSPOT_SOLUTIONS_MAP = {
        "Diesel Heavy Machinery & Gensets": [
            {
                "id_prefix": "rec_boiler_economizer",
                "title": "Industrial Flue Gas Waste Heat Recovery (Economizer) & Boiler Burner Retrofit",
                "category": "Fuel",
                "icon": "🔥",
                "feather_icon": "zap",
                "description": "Capture high-temperature flue exhaust heat to preheat boiler feedwater and install automated air-to-fuel ratio trim controllers.",
                "saving_ratio": 0.26,
                "cost_base_min": 4500,
                "cost_base_max": 9500,
                "difficulty": "Medium",
                "impact_level": "Critical",
                "circular_benefit": "Recovers 85% of latent exhaust thermal energy, eliminating upstream fossil fuel combustion.",
                "govt_incentives": "Qualifies for State Clean Energy Industrial Grant & Accelerated Depreciation (Section 179/MACRS)."
            },
            {
                "id_prefix": "rec_insulation_jackets",
                "title": "High-Efficiency Thermal Pipe & Boiler Valve Removable Blanket Insulation",
                "category": "Fuel",
                "icon": "🧤",
                "feather_icon": "shield",
                "description": "Fit custom silicone-fiberglass insulation jackets over bare steam pipes, boiler headers, and uninsulated valves.",
                "saving_ratio": 0.16,
                "cost_base_min": 1400,
                "cost_base_max": 3200,
                "difficulty": "Easy",
                "impact_level": "High",
                "circular_benefit": "Durable, reusable jackets detach in seconds for maintenance without disposal waste.",
                "govt_incentives": "Utility Industrial Efficiency Rebate program reimburses up to 35% of installation invoices."
            }
        ],
        "Diesel Generators & Stationary Machinery": [
            {
                "id_prefix": "rec_boiler_economizer",
                "title": "Industrial Flue Gas Waste Heat Recovery (Economizer) & Boiler Burner Retrofit",
                "category": "Fuel",
                "icon": "🔥",
                "feather_icon": "zap",
                "description": "Capture high-temperature flue exhaust heat to preheat boiler feedwater and install automated air-to-fuel ratio trim controllers.",
                "saving_ratio": 0.26,
                "cost_base_min": 4500,
                "cost_base_max": 9500,
                "difficulty": "Medium",
                "impact_level": "Critical",
                "circular_benefit": "Recovers 85% of latent exhaust thermal energy, eliminating upstream fossil fuel combustion.",
                "govt_incentives": "Qualifies for State Clean Energy Industrial Grant & Accelerated Depreciation (Section 179/MACRS)."
            }
        ],
        "Natural Gas Thermal Boilers": [
            {
                "id_prefix": "rec_gas_cogen",
                "title": "Microturbine Combined Heat & Power (CHP) Cogeneration System",
                "category": "Fuel",
                "icon": "⚡",
                "feather_icon": "activity",
                "description": "Generate on-site baseload electric power from pipeline natural gas while channeling exhaust heat for factory process heating.",
                "saving_ratio": 0.28,
                "cost_base_min": 12000,
                "cost_base_max": 28000,
                "difficulty": "Hard",
                "impact_level": "Critical",
                "circular_benefit": "Dual-generation efficiency tops 80% compared to 45% for separate grid power and thermal boilers.",
                "govt_incentives": "Federal Combined Heat and Power Investment Tax Credit (ITC) 30%."
            },
            {
                "id_prefix": "rec_gas_o2_trim",
                "title": "Automated Oxygen-Trim Combustion Controls & Condensing Economizer",
                "category": "Fuel",
                "icon": "🔥",
                "feather_icon": "sliders",
                "description": "Continuously modulate draft fans and gas injection using in-stack zirconium oxide sensors to eliminate excess fuel burn.",
                "saving_ratio": 0.18,
                "cost_base_min": 3200,
                "cost_base_max": 7500,
                "difficulty": "Medium",
                "impact_level": "High",
                "circular_benefit": "Prevents incomplete hydrocarbon combustion and cuts NOx emissions by 40%.",
                "govt_incentives": "Regional Clean Air District Energy Abatement Rebate (₹207,500 direct incentive)."
            }
        ],
        "Grid Electricity Base-Load": [
            {
                "id_prefix": "rec_solar_pv",
                "title": "On-Site Commercial Rooftop Bifacial Solar PV Microgrid (50kW–200kW)",
                "category": "Electricity",
                "icon": "☀️",
                "feather_icon": "sun",
                "description": "Deploy Tier-1 monocrystalline bifacial solar modules with smart string inverters to offset daytime manufacturing peak loads.",
                "saving_ratio": 0.42,
                "cost_base_min": 22000,
                "cost_base_max": 58000,
                "difficulty": "Hard",
                "impact_level": "Critical",
                "circular_benefit": "Generates 100% emission-free electricity with 25-year panel linear performance guarantee.",
                "govt_incentives": "Federal Clean Energy 30% ITC Tax Credit + Solar Net Energy Metering (NEM 3.0) export credits."
            },
            {
                "id_prefix": "rec_led_lighting",
                "title": "High-Efficacy Smart Sensor-Dimmed LED High-Bay Retrofit",
                "category": "Electricity",
                "icon": "💡",
                "feather_icon": "zap",
                "description": "Replace metal halide and fluorescent fixtures with high-efficacy (160 lm/W) LEDs with microwave occupancy sensors.",
                "saving_ratio": 0.15,
                "cost_base_min": 2200,
                "cost_base_max": 4800,
                "difficulty": "Easy",
                "impact_level": "High",
                "circular_benefit": "Old fixtures recycled via verified zero-landfill e-waste handlers; LED life exceeds 60,000 hours.",
                "govt_incentives": "Commercial Electric Utility Rebate covers up to ₹3,735 per replaced high-bay fixture."
            },
            {
                "id_prefix": "rec_motor_vfd",
                "title": "Variable Frequency Drives (VFDs) on Heavy Induction Motors & Fans",
                "category": "Electricity",
                "icon": "⚙️",
                "feather_icon": "cpu",
                "description": "Equip continuous-run ventilation blowers, chillers, and conveyor motors with digital VFD inverters to modulate speed.",
                "saving_ratio": 0.22,
                "cost_base_min": 3500,
                "cost_base_max": 8500,
                "difficulty": "Medium",
                "impact_level": "High",
                "circular_benefit": "Affinity laws reduce power by 50% at 80% motor speed, extending motor bearing lifespan 3x.",
                "govt_incentives": "State Energy Efficiency Trust VFD Incentive (₹4,980/horsepower rebate)."
            }
        ],
        "Grid Electricity Baseline Load": [
            {
                "id_prefix": "rec_solar_pv",
                "title": "On-Site Commercial Rooftop Bifacial Solar PV Microgrid (50kW–200kW)",
                "category": "Electricity",
                "icon": "☀️",
                "feather_icon": "sun",
                "description": "Deploy Tier-1 monocrystalline bifacial solar modules with smart string inverters to offset daytime manufacturing peak loads.",
                "saving_ratio": 0.42,
                "cost_base_min": 22000,
                "cost_base_max": 58000,
                "difficulty": "Hard",
                "impact_level": "Critical",
                "circular_benefit": "Generates 100% emission-free electricity with 25-year panel linear performance guarantee.",
                "govt_incentives": "Federal Clean Energy 30% ITC Tax Credit + Solar Net Energy Metering (NEM 3.0) export credits."
            }
        ],
        "Heavy Freight & Distribution Trucks": [
            {
                "id_prefix": "rec_ai_route_opt",
                "title": "AI Dynamic Route Dispatch, Backhaul Optimization & Anti-Idling Telematics",
                "category": "Transport",
                "icon": "🗺️",
                "feather_icon": "navigation",
                "description": "Implement automated telematics with turn-by-turn route sequencing, return-trip backhaul load pooling, and 3-minute idle cutoffs.",
                "saving_ratio": 0.25,
                "cost_base_min": 1500,
                "cost_base_max": 3800,
                "difficulty": "Easy",
                "impact_level": "High",
                "circular_benefit": "Cuts empty return haul miles by 35% through circular shared freight network coordination.",
                "govt_incentives": "Department of Transportation Green Freight Logistics Technology Subsidy."
            },
            {
                "id_prefix": "rec_ev_truck_fleet",
                "title": "Commercial Fleet Transition to Electric Vehicles (EVs) & Depot Fast Chargers",
                "category": "Transport",
                "icon": "⚡",
                "feather_icon": "truck",
                "description": "Phased transition of regional distribution vehicles to zero-emission battery electric vans and yard spotters.",
                "saving_ratio": 0.45,
                "cost_base_min": 28000,
                "cost_base_max": 65000,
                "difficulty": "Hard",
                "impact_level": "Critical",
                "circular_benefit": "Zero direct tailpipe emissions; second-life battery repurposing program included.",
                "govt_incentives": "Clean Commercial Vehicle Federal Credit up to ₹622,500/vehicle + 50% EV charger grant."
            }
        ],
        "Non-Recycled Landfill Plastics": [
            {
                "id_prefix": "rec_plastic_circular",
                "title": "Closed-Loop Post-Industrial Polymer Regrind Automation & Reusable Totes",
                "category": "Waste",
                "icon": "♻️",
                "feather_icon": "refresh-cw",
                "description": "Install on-site plastic granulation regrind equipment to blend scrap sprues directly back into primary injection molding lines.",
                "saving_ratio": 0.45,
                "cost_base_min": 2800,
                "cost_base_max": 7500,
                "difficulty": "Medium",
                "impact_level": "Critical",
                "circular_benefit": "Eliminates virgin polymer purchases and diverts 95% of clean plastic purges from landfills.",
                "govt_incentives": "State Circular Economy & Plastics Reduction Enterprise Capital Grant."
            }
        ],
        "Hazardous Waste & Chemical Solvents": [
            {
                "id_prefix": "rec_solvent_distillation",
                "title": "On-Site Closed-Loop Vacuum Solvent Distillation & Vapor Recovery",
                "category": "Waste",
                "icon": "☣️",
                "feather_icon": "alert-octagon",
                "description": "Recover 90% of industrial degreasing solvents, thinners, and wash liquids using on-site batch vacuum distillation.",
                "saving_ratio": 0.50,
                "cost_base_min": 4500,
                "cost_base_max": 11500,
                "difficulty": "Medium",
                "impact_level": "Critical",
                "circular_benefit": "Reuses recycled solvents up to 6 cycles before final offsite processing.",
                "govt_incentives": "EPA Toxic Release Reduction & Hazardous Waste Avoidance Tax Credit."
            }
        ],
        "Organic & Food Byproduct Waste": [
            {
                "id_prefix": "rec_compost_biogas",
                "title": "On-Site Aerobic Biocomposting & Anaerobic Organics Valorization",
                "category": "Waste",
                "icon": "🌱",
                "feather_icon": "feather",
                "description": "Process food scraps, spent grains, and organic trimmings into certified soil conditioner or regional biogas digester feedstock.",
                "saving_ratio": 0.40,
                "cost_base_min": 2200,
                "cost_base_max": 5800,
                "difficulty": "Easy",
                "impact_level": "High",
                "circular_benefit": "Produces nutrient-rich compost and diverts methane-generating organics from municipal landfills.",
                "govt_incentives": "Organic Waste Diversion Exemption & Methane Abatement Compliance Credits."
            }
        ],
        "Municipal Cardboard & Paper Waste": [
            {
                "id_prefix": "rec_cardboard_shredder",
                "title": "In-House Corrugated Cardboard Perforating & Reusable Void Fill",
                "category": "Waste",
                "icon": "📦",
                "feather_icon": "box",
                "description": "Convert incoming discarded cardboard boxes into high-grade honeycomb packaging void-fill to replace plastic bubble wrap.",
                "saving_ratio": 0.32,
                "cost_base_min": 1600,
                "cost_base_max": 3500,
                "difficulty": "Easy",
                "impact_level": "Medium",
                "circular_benefit": "Eliminates single-use plastic air pillows and cuts packaging material procurement spend.",
                "govt_incentives": "Waste Minimization Small Business Rebate (₹83,000 grant)."
            }
        ],
        "Untreated Industrial Wastewater Discharge": [
            {
                "id_prefix": "rec_water_mbr",
                "title": "Closed-Loop Reverse Osmosis & Membrane Bioreactor (MBR) Water Recycling",
                "category": "Water",
                "icon": "💧",
                "feather_icon": "droplet",
                "description": "Deploy compact ultrafiltration membrane modules to purify process wash water for multi-pass operational reuse.",
                "saving_ratio": 0.38,
                "cost_base_min": 5500,
                "cost_base_max": 16500,
                "difficulty": "Hard",
                "impact_level": "Critical",
                "circular_benefit": "Recycles 75% of effluent back into cooling towers and equipment washing lines.",
                "govt_incentives": "Municipal Water Conservation Technology Rebate + Sewer Discharge Surcharge Relief."
            }
        ],
        "Process Water Evaporation & Pumping": [
            {
                "id_prefix": "rec_water_solenoid",
                "title": "Automated Solenoid Flow Shutoffs & Low-Pressure Rinse Nozzles",
                "category": "Water",
                "icon": "🚰",
                "feather_icon": "activity",
                "description": "Install automated line shutoff valves tied to machine operating sensors to eliminate continuous water bleed during idle.",
                "saving_ratio": 0.25,
                "cost_base_min": 1800,
                "cost_base_max": 4200,
                "difficulty": "Easy",
                "impact_level": "Medium",
                "circular_benefit": "Conserves 30% of utility water intake with zero disruptions to active production.",
                "govt_incentives": "Industrial Water Efficiency Direct Rebate."
            }
        ],
        "Machine Idle Hours & Motor Friction": [
            {
                "id_prefix": "rec_machine_iot",
                "title": "Smart IoT Current Transducers & Production Auto-Standby Sequencing",
                "category": "Manufacturing",
                "icon": "⚙️",
                "feather_icon": "cpu",
                "description": "Integrate non-invasive split-core current transducers on production lines to automatically switch auxiliary drives to sleep mode.",
                "saving_ratio": 0.20,
                "cost_base_min": 2400,
                "cost_base_max": 5500,
                "difficulty": "Easy",
                "impact_level": "High",
                "circular_benefit": "Cuts phantom idle electrical draw by 70% and prevents mechanical wear-and-tear.",
                "govt_incentives": "Smart Manufacturing & Digital Transformation Energy Grant."
            }
        ],
        "Commercial Fleet Delivery Vans": [
            {
                "id_prefix": "rec_fleet_telematics",
                "title": "Van Fleet Eco-Routing, Speed Governor Calibration & Anti-Idling",
                "category": "Transport",
                "icon": "🚐",
                "feather_icon": "truck",
                "description": "Calibrate engine speed governors and install real-time fuel feedback dash meters for delivery drivers.",
                "saving_ratio": 0.20,
                "cost_base_min": 1200,
                "cost_base_max": 2800,
                "difficulty": "Easy",
                "impact_level": "Medium",
                "circular_benefit": "Reduces fuel consumption and extends brake/tire lifecycle by 25%.",
                "govt_incentives": "Clean Fleet Transition Tax Credit."
            }
        ],
        "Company Passenger Cars & Sales Petrol": [
            {
                "id_prefix": "rec_hybrid_ev_cars",
                "title": "Corporate EV Fleet Policy & Level-2 Workplace Charging Incentive",
                "category": "Transport",
                "icon": "🚗",
                "feather_icon": "battery-charging",
                "description": "Establish preferred EV leasing for sales reps and install dual-port Level-2 EV charging stations at facility parking.",
                "saving_ratio": 0.30,
                "cost_base_min": 3500,
                "cost_base_max": 7500,
                "difficulty": "Medium",
                "impact_level": "Medium",
                "circular_benefit": "Replaces gasoline combustion with clean electricity.",
                "govt_incentives": "Alternative Fuel Infrastructure Tax Credit (Section 30C) 30%."
            }
        ]
    }

    generated_recommendations: List[Dict[str, Any]] = []
    seen_ids = set()

    # Step 1: Generate recommendations for the business's actual ranked leak points (#1, #2, #3, ...)
    for leak in top_leaks:
        source_name = leak.get("source", "")
        solutions = HOTSPOT_SOLUTIONS_MAP.get(source_name, [])
        leak_co2 = float(leak.get("current_co2", 0.0))
        leak_cost = float(leak.get("cost_impact", 0.0))
        leak_rank = int(leak.get("rank", 99))
        
        for sol in solutions:
            rec_id = f"{sol['id_prefix']}_{leak_rank}"
            if rec_id in seen_ids:
                continue
            seen_ids.add(rec_id)

            co2_saved = round(max(0.2, leak_co2 * sol["saving_ratio"]), 1)
            share_saved_pct = round((co2_saved / total_co2) * 100, 1)
            
            # Dollar savings from utility/fuel reduction + carbon credit compliance savings
            dollar_savings_annual = round(max(150.0, (leak_cost * sol["saving_ratio"]) + (co2_saved * credit_price)), 0)
            
            # Scaled CapEx
            capex_min = int(round(sol["cost_base_min"] * scale_factor, -2))
            capex_max = int(round(sol["cost_base_max"] * scale_factor, -2))
            capex_mid = (capex_min + capex_max) / 2.0
            
            # ROI % and Payback
            roi_pct = round((dollar_savings_annual / max(1.0, capex_mid)) * 100, 1)
            payback_years = round(capex_mid / max(1.0, dollar_savings_annual), 1)
            if payback_years < 1.0:
                payback_str = f"{int(max(1, round(payback_years * 12)))} months"
            else:
                payback_str = f"{payback_years:.1f} years"

            # Hotspot attribution label
            hotspot_label = f"🎯 Hotspot #{leak_rank}: {source_name}"
            priority_tag = "🎯 #1 Hotspot Fix" if leak_rank == 1 else (f"🎯 #{leak_rank} Hotspot Fix" if leak_rank <= 3 else f"Hotspot #{leak_rank}")

            generated_recommendations.append({
                "id": rec_id,
                "title": sol["title"],
                "category": sol["category"],
                "icon": sol["icon"],
                "feather_icon": sol["feather_icon"],
                "description": sol["description"],
                "targeted_hotspot_rank": leak_rank,
                "targeted_hotspot_source": source_name,
                "targeted_hotspot_co2": leak_co2,
                "targeted_hotspot_label": hotspot_label,
                "hotspot_priority_tag": priority_tag,
                "co2_saved_t": co2_saved,
                "co2_saved_pct": share_saved_pct,
                "cost_estimate": f"₹{capex_min:,.0f} – ₹{capex_max:,.0f}",
                "annual_savings_inr": dollar_savings_annual,
                "expected_roi": roi_pct,
                "payback_time": payback_str,
                "credits_saved": co2_saved,
                "compliance_value_inr": round(co2_saved * credit_price, 0),
                "difficulty": sol["difficulty"],
                "impact_level": sol["impact_level"],
                "circular_benefit": sol["circular_benefit"],
                "govt_incentives": sol["govt_incentives"]
            })

    # Sort so #1 Hotspot is first, followed by #2, #3, then by ROI descending
    generated_recommendations.sort(key=lambda x: (x["targeted_hotspot_rank"], -x["expected_roi"]))

    return generated_recommendations


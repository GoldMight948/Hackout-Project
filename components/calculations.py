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

# Standard Commercial Cost Factors ($ USD per unit)
COST_FACTORS = {
    "electricity": 0.155,       # $ / kWh
    "diesel": 1.42,             # $ / Liter
    "petrol": 1.35,             # $ / Liter
    "natural_gas": 0.65,        # $ / m³
    "truck": 0.85,              # $ / km (fuel, maintenance, wear)
    "car": 0.35,                # $ / km
    "commute": 0.20,            # $ / km
    "delivery_vehicle": 4200.0, # $ / vehicle annual service overhead
    "waste_organic": 0.08,      # $ / kg tipping fee
    "waste_plastic": 0.18,      # $ / kg
    "waste_metal": 0.22,        # $ / kg
    "waste_paper": 0.11,        # $ / kg
    "waste_hazardous": 0.75,    # $ / kg specialized disposal
    "water_supply": 2.45,       # $ / m³
    "wastewater": 3.80,         # $ / m³ sewer surcharge
    "raw_material": 480.0,      # $ / tonne
    "machine_hour": 32.0,       # $ / hour operating overhead
}

# Industry Benchmarks (average t CO2e per 1,000 units or normalized turnover)
INDUSTRY_BENCHMARKS = {
    "Food Processing": {"intensity_kg_per_unit": 0.95, "avg_renewable_pct": 18.0, "waste_divert_pct": 35.0},
    "Retail Store": {"intensity_kg_per_unit": 0.42, "avg_renewable_pct": 22.0, "waste_divert_pct": 52.0},
    "Logistics Company": {"intensity_kg_per_unit": 1.45, "avg_renewable_pct": 12.0, "waste_divert_pct": 28.0},
    "Manufacturing Plant": {"intensity_kg_per_unit": 2.80, "avg_renewable_pct": 15.0, "waste_divert_pct": 40.0},
    "Other": {"intensity_kg_per_unit": 1.10, "avg_renewable_pct": 15.0, "waste_divert_pct": 35.0}
}

def calculate_detailed_emissions(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs end-to-end greenhouse gas and cost computations across 5 pillars:
    Energy, Transport, Waste, Water, and Manufacturing.
    """
    # 1. Extract inputs with defaults
    elec_kwh = max(0.0, float(inputs.get("electricity_kwh", inputs.get("electricity", 0.0))))
    renew_pct = min(100.0, max(0.0, float(inputs.get("renewable_pct", 0.0))))
    diesel_l = max(0.0, float(inputs.get("diesel_liters", inputs.get("fuel", 0.0) * 0.7)))
    petrol_l = max(0.0, float(inputs.get("petrol_liters", inputs.get("fuel", 0.0) * 0.3)))
    gas_m3 = max(0.0, float(inputs.get("gas_m3", 0.0)))

    truck_km = max(0.0, float(inputs.get("truck_km", inputs.get("transport", 0.0) * 0.6)))
    car_km = max(0.0, float(inputs.get("car_km", inputs.get("transport", 0.0) * 0.3)))
    commute_km = max(0.0, float(inputs.get("commute_km", inputs.get("transport", 0.0) * 0.1)))
    delivery_vehs = max(0, int(inputs.get("delivery_vehicles", 2)))

    waste_org_kg = max(0.0, float(inputs.get("organic_waste_kg", inputs.get("waste", 0.0) * 0.4)))
    waste_plas_kg = max(0.0, float(inputs.get("plastic_waste_kg", inputs.get("waste", 0.0) * 0.3)))
    waste_met_kg = max(0.0, float(inputs.get("metal_waste_kg", inputs.get("waste", 0.0) * 0.1)))
    waste_pap_kg = max(0.0, float(inputs.get("paper_waste_kg", inputs.get("waste", 0.0) * 0.15)))
    waste_haz_kg = max(0.0, float(inputs.get("hazardous_waste_kg", inputs.get("waste", 0.0) * 0.05)))

    water_m3 = max(0.0, float(inputs.get("water_m3", 1200.0)))
    wastewater_m3 = max(0.0, float(inputs.get("wastewater_m3", water_m3 * 0.85)))

    raw_mat_t = max(0.0, float(inputs.get("raw_material_tonnes", 150.0)))
    prod_units = max(0.0, float(inputs.get("production_units", 25000.0)))
    mach_hours = max(0.0, float(inputs.get("machine_running_hours", inputs.get("machine_hours", 2200.0))))

    govt_credits = max(0.0, float(inputs.get("total_credits", inputs.get("total_carbon_credits", 150.0))))
    credit_price = max(1.0, float(inputs.get("credit_price", inputs.get("carbon_credit_price", 35.0))))

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

    # 3. Cost Calculations ($ USD)
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
        "raw_inputs": inputs
    }

# Backward compatibility alias
def calculate_emissions(inputs: Dict[str, Any]) -> Dict[str, Any]:
    return calculate_detailed_emissions(inputs)

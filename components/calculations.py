"""
Emission calculations, cost estimations, leak ranking, and priority tagging.
Uses GHG Protocol / EPA / Defra standard baseline factors.
"""

from typing import Dict, List, Any

# Standard Emission Factors (metric tonnes of CO2e per unit)
EMISSION_FACTORS = {
    "electricity": 0.00042,   # 0.42 kg CO2e / kWh
    "fuel": 0.00268,          # 2.68 kg CO2e / Liter
    "waste": 0.00052,         # 0.52 kg CO2e / kg
    "transport": 0.000171,    # 0.171 kg CO2e / km
}

# Average Commercial Cost Factors ($ USD per unit consumed)
COST_FACTORS = {
    "electricity": 0.155,    # $0.155 / kWh average commercial power
    "fuel": 1.42,            # $1.42 / L diesel/gas
    "waste": 0.11,           # $0.11 / kg disposal & tipping costs
    "transport": 0.38,       # $0.38 / km operating & fleet fuel wear
}

CATEGORY_METADATA = {
    "electricity": {
        "label": "Electricity",
        "icon": "⚡",
        "unit": "kWh",
        "color": "#F59E0B",
        "desc": "Facility power, lighting, motors & HVAC"
    },
    "fuel": {
        "label": "Fuel",
        "icon": "🔥",
        "unit": "Liters",
        "color": "#EF4444",
        "desc": "On-site boilers, diesel generators & heating"
    },
    "transport": {
        "label": "Transport",
        "icon": "🚗",
        "unit": "km",
        "color": "#F97316",
        "desc": "Fleet logistics, distribution & deliveries"
    },
    "waste": {
        "label": "Waste",
        "icon": "♻️",
        "unit": "kg",
        "color": "#10B981",
        "desc": "Solid waste sent to municipal landfill"
    },
}

def calculate_emissions(inputs: Dict[str, float]) -> Dict[str, Any]:
    """
    Computes total emissions, category shares, rankings, cost impacts, and efficiency metrics.
    """
    electricity_kwh = max(0.0, float(inputs.get("electricity", 0.0)))
    fuel_liters = max(0.0, float(inputs.get("fuel", 0.0)))
    waste_kg = max(0.0, float(inputs.get("waste", 0.0)))
    transport_km = max(0.0, float(inputs.get("transport", 0.0)))
    production_units = max(0.0, float(inputs.get("production_units", 0.0)))

    # Category emissions in metric tonnes CO2e
    co2_by_category = {
        "electricity": round(electricity_kwh * EMISSION_FACTORS["electricity"], 2),
        "fuel": round(fuel_liters * EMISSION_FACTORS["fuel"], 2),
        "waste": round(waste_kg * EMISSION_FACTORS["waste"], 2),
        "transport": round(transport_km * EMISSION_FACTORS["transport"], 2),
    }

    total_co2 = round(sum(co2_by_category.values()), 2)

    # Category spend / cost equivalents
    cost_by_category = {
        "electricity": round(electricity_kwh * COST_FACTORS["electricity"], 0),
        "fuel": round(fuel_liters * COST_FACTORS["fuel"], 0),
        "waste": round(waste_kg * COST_FACTORS["waste"], 0),
        "transport": round(transport_km * COST_FACTORS["transport"], 0),
    }
    total_cost = round(sum(cost_by_category.values()), 0)

    # Percentages
    shares = {}
    for cat, val in co2_by_category.items():
        share_pct = round((val / total_co2 * 100), 1) if total_co2 > 0 else 0.0
        shares[cat] = share_pct

    # Ranking from worst to least
    ranked_tuples = sorted(co2_by_category.items(), key=lambda x: x[1], reverse=True)
    ranked_categories: List[Dict[str, Any]] = []

    for rank_idx, (cat_key, co2_val) in enumerate(ranked_tuples, start=1):
        share_pct = shares[cat_key]
        
        # Priority Tag Logic
        if share_pct >= 40.0:
            priority = "Very High Priority"
            priority_color = "#EF4444" # red
            priority_level = 1
        elif share_pct >= 25.0:
            priority = "High Priority"
            priority_color = "#F97316" # orange
            priority_level = 2
        elif share_pct >= 12.0:
            priority = "Medium Priority"
            priority_color = "#F59E0B" # amber
            priority_level = 3
        else:
            priority = "Low Priority"
            priority_color = "#10B981" # green
            priority_level = 4

        meta = CATEGORY_METADATA[cat_key]
        ranked_categories.append({
            "rank": rank_idx,
            "category": cat_key,
            "label": meta["label"],
            "icon": meta["icon"],
            "unit": meta["unit"],
            "co2_tonnes": co2_val,
            "share_pct": share_pct,
            "cost_dollars": cost_by_category[cat_key],
            "priority": priority,
            "priority_color": priority_color,
            "priority_level": priority_level,
            "raw_input": inputs.get(cat_key, 0.0)
        })

    # Emissions per unit produced
    emissions_per_unit = None
    if production_units > 0 and total_co2 > 0:
        kg_per_unit = round((total_co2 * 1000) / production_units, 2)
        emissions_per_unit = {
            "units": production_units,
            "kg_co2_per_unit": kg_per_unit,
            "tonnes_per_thousand_units": round(total_co2 / (production_units / 1000), 3) if production_units >= 1000 else None
        }

    top_leak = ranked_categories[0] if ranked_categories else None

    return {
        "total_co2": total_co2,
        "total_cost": total_cost,
        "co2_by_category": co2_by_category,
        "cost_by_category": cost_by_category,
        "shares": shares,
        "ranked_categories": ranked_categories,
        "top_leak": top_leak,
        "emissions_per_unit": emissions_per_unit,
        "raw_inputs": inputs
    }

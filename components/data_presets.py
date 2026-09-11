"""
Demo business presets, categorized green fixes, and default community suggestions.
"""

from typing import Dict, List, Any

DEMO_BUSINESSES = {
    "food_processor": {
        "name": "GreenBite Organics",
        "type_label": "Food Processing & Bakery",
        "icon": "🥪",
        "description": "Mid-sized bakery & food processing facility operating 6 days a week with refrigeration and baking ovens.",
        "data": {
            "business_name": "GreenBite Organics",
            "business_type": "Food Processing",
            "electricity": 165000.0,  # kWh/yr
            "fuel": 22000.0,          # Liters/yr (gas/oil for ovens & boilers)
            "waste": 19500.0,         # kg/yr (food trim & packaging)
            "transport": 38000.0,     # km/yr (refrigerated delivery vans)
            "production_units": 240000.0 # units produced/year
        }
    },
    "small_retail": {
        "name": "EcoTrend Boutique & Cafe",
        "type_label": "Small Retail & Apparel",
        "icon": "🏪",
        "description": "High-street retail shop with open displays, continuous air conditioning, and customer coffee corner.",
        "data": {
            "business_name": "EcoTrend Boutique",
            "business_type": "Retail Store",
            "electricity": 48000.0,   # kWh/yr (lighting, HVAC, registers)
            "fuel": 1400.0,           # Liters/yr (winter space heating)
            "waste": 6200.0,          # kg/yr (cardboard cartons, hanger plastics)
            "transport": 14000.0,     # km/yr (courier dispatches)
            "production_units": 18000.0 # items sold/year
        }
    },
    "logistics": {
        "name": "SwiftRoute Delivery Hub",
        "type_label": "Logistics & Local Couriers",
        "icon": "🚚",
        "description": "Regional last-mile courier service with 8 delivery vans and a 24/7 cross-dock sorting warehouse.",
        "data": {
            "business_name": "SwiftRoute Hub",
            "business_type": "Logistics & Delivery",
            "electricity": 34000.0,   # kWh/yr (depot lights & conveyors)
            "fuel": 38000.0,          # Liters/yr (diesel for fleet)
            "waste": 4200.0,          # kg/yr (shrink wrap & broken pallets)
            "transport": 210000.0,    # km/yr (fleet delivery mileage)
            "production_units": 92000.0 # packages delivered/year
        }
    }
}

DEMO_USERS = {
    "alex@greenbite.com": {
        "name": "Alex Morgan",
        "company": "GreenBite Organics",
        "role": "Plant Operations Lead",
        "avatar": "👨‍🍳",
        "preset_key": "food_processor"
    },
    "sarah@ecotrend.com": {
        "name": "Sarah Chen",
        "company": "EcoTrend Boutique",
        "role": "Store Founder & Owner",
        "avatar": "👩‍💼",
        "preset_key": "small_retail"
    },
    "marcus@swiftroute.com": {
        "name": "Marcus Vance",
        "company": "SwiftRoute Couriers",
        "role": "Fleet & Operations Manager",
        "avatar": "🚚",
        "preset_key": "logistics"
    }
}

CATEGORY_FIXES: Dict[str, List[Dict[str, Any]]] = {
    "electricity": [
        {
            "id": "elec_led",
            "name": "High-Efficiency LED & Daylight Sensors",
            "description": "Replace remaining fluorescent tubes and halogen spotlights with smart dimmed LEDs.",
            "co2_saved_pct": 14.0,
            "cost_estimate": "$650 – $1,200",
            "cost_level": "Low",
            "difficulty": "Easy",
            "payback_time": "4 – 6 months",
            "timeframe": "quick_win",
            "timeframe_label": "Quick Win (0–3 Months)",
            "impact_tag": "Immediate ROI"
        },
        {
            "id": "elec_hvac_tune",
            "name": "Smart Thermostat & Off-Hours Setback",
            "description": "Automate 3°C setback overnight and install magnetic door seals to stop conditioned air loss.",
            "co2_saved_pct": 18.0,
            "cost_estimate": "$300 – $750",
            "cost_level": "Low",
            "difficulty": "Easy",
            "payback_time": "3 months",
            "timeframe": "quick_win",
            "timeframe_label": "Quick Win (0–3 Months)",
            "impact_tag": "Zero Downtime"
        },
        {
            "id": "elec_vfd",
            "name": "Variable Frequency Drives on Pumps & Motors",
            "description": "Equip major motors, compressor fans, or ventilation units with speed controllers to eliminate idle load.",
            "co2_saved_pct": 24.0,
            "cost_estimate": "$2,200 – $4,500",
            "cost_level": "Medium",
            "difficulty": "Medium",
            "payback_time": "14 – 18 months",
            "timeframe": "mid_term",
            "timeframe_label": "Mid-term (3–12 Months)",
            "impact_tag": "High Efficiency"
        },
        {
            "id": "elec_solar",
            "name": "Rooftop Commercial Solar PV Array",
            "description": "Install 15kW–30kW on-site solar panels under clean energy grant programs to generate own clean power.",
            "co2_saved_pct": 42.0,
            "cost_estimate": "$12,000 – $24,000",
            "cost_level": "High",
            "difficulty": "Hard",
            "payback_time": "3.5 – 4.5 years",
            "timeframe": "long_term",
            "timeframe_label": "Long-term (1+ Years)",
            "impact_tag": "Energy Independence"
        }
    ],
    "fuel": [
        {
            "id": "fuel_insul",
            "name": "Pipe & Valve Thermal Jacket Insulation",
            "description": "Wrap uninsulated hot pipes, boiler valves, and tank fittings with removable thermal insulation blankets.",
            "co2_saved_pct": 12.0,
            "cost_estimate": "$400 – $900",
            "cost_level": "Low",
            "difficulty": "Easy",
            "payback_time": "3 – 5 months",
            "timeframe": "quick_win",
            "timeframe_label": "Quick Win (0–3 Months)",
            "impact_tag": "Instant Stop-Leak"
        },
        {
            "id": "fuel_burner_tune",
            "name": "Boiler & Burner Oxygen Optimization",
            "description": "Perform an annual combustion tune-up, clean heat exchangers, and calibrate fuel-to-air combustion ratio.",
            "co2_saved_pct": 16.0,
            "cost_estimate": "$600 – $1,100",
            "cost_level": "Low",
            "difficulty": "Easy",
            "payback_time": "4 – 6 months",
            "timeframe": "quick_win",
            "timeframe_label": "Quick Win (0–3 Months)",
            "impact_tag": "Preventative"
        },
        {
            "id": "fuel_waste_heat",
            "name": "Flue Gas Waste Heat Recovery Loop",
            "description": "Capture flue heat from exhaust stacks to pre-heat boiler feedwater or facility washing water.",
            "co2_saved_pct": 28.0,
            "cost_estimate": "$3,500 – $7,000",
            "cost_level": "Medium",
            "difficulty": "Medium",
            "payback_time": "16 months",
            "timeframe": "mid_term",
            "timeframe_label": "Mid-term (3–12 Months)",
            "impact_tag": "Massive Fuel Cut"
        },
        {
            "id": "fuel_electrify",
            "name": "Commercial Heat Pump Electrification",
            "description": "Phase out fossil gas/diesel heating with high-COP commercial air-to-water heat pumps.",
            "co2_saved_pct": 55.0,
            "cost_estimate": "$14,000 – $28,000",
            "cost_level": "High",
            "difficulty": "Hard",
            "payback_time": "4 years",
            "timeframe": "long_term",
            "timeframe_label": "Long-term (1+ Years)",
            "impact_tag": "Fossil-Free"
        }
    ],
    "transport": [
        {
            "id": "trans_telematics",
            "name": "Anti-Idling Rules & Fleet Speed Cap",
            "description": "Implement 3-minute auto shut-off policy and limit highway cruise speeds to 100 km/h to boost fuel efficiency 15%.",
            "co2_saved_pct": 13.0,
            "cost_estimate": "$0 – $250",
            "cost_level": "Low",
            "difficulty": "Easy",
            "payback_time": "1 month",
            "timeframe": "quick_win",
            "timeframe_label": "Quick Win (0–3 Months)",
            "impact_tag": "Zero CapEx"
        },
        {
            "id": "trans_route",
            "name": "AI Route Optimization & Delivery Consolidation",
            "description": "Deploy route planning software to group order drops and prevent empty deadhead miles.",
            "co2_saved_pct": 22.0,
            "cost_estimate": "$60 – $150 / mo",
            "cost_level": "Low",
            "difficulty": "Medium",
            "payback_time": "2 months",
            "timeframe": "mid_term",
            "timeframe_label": "Mid-term (3–12 Months)",
            "impact_tag": "Saves Labor & Miles"
        },
        {
            "id": "trans_hybrid_tires",
            "name": "Low Rolling Resistance Tires & Aero Kits",
            "description": "Fit verified eco-grade tires and cab wind deflectors to cut rolling and aerodynamic drag.",
            "co2_saved_pct": 8.0,
            "cost_estimate": "$1,200 – $2,500",
            "cost_level": "Medium",
            "difficulty": "Easy",
            "payback_time": "9 months",
            "timeframe": "mid_term",
            "timeframe_label": "Mid-term (3–12 Months)",
            "impact_tag": "Tire Upgrades"
        },
        {
            "id": "trans_ev_fleet",
            "name": "Fleet Electrification (Electric Delivery Vans)",
            "description": "Replace high-mileage diesel vans with dedicated commercial battery EVs charged with depot off-peak power.",
            "co2_saved_pct": 68.0,
            "cost_estimate": "$35,000 – $65,000",
            "cost_level": "High",
            "difficulty": "Hard",
            "payback_time": "3.8 years",
            "timeframe": "long_term",
            "timeframe_label": "Long-term (1+ Years)",
            "impact_tag": "Zero Tailpipe"
        }
    ],
    "waste": [
        {
            "id": "waste_segregation",
            "name": "Point-of-Source Waste Separation Stations",
            "description": "Install color-coded bins at key waste generation points to separate cardboard, film, and general trash.",
            "co2_saved_pct": 25.0,
            "cost_estimate": "$200 – $500",
            "cost_level": "Low",
            "difficulty": "Easy",
            "payback_time": "2 months",
            "timeframe": "quick_win",
            "timeframe_label": "Quick Win (0–3 Months)",
            "impact_tag": "Cuts Tipping Fees"
        },
        {
            "id": "waste_cardboard_baler",
            "name": "Compact Baler & Direct Recycler Rebate",
            "description": "Install a compact pneumatic baler so local recyclers pay cash rebates for dry bales instead of charging disposal fees.",
            "co2_saved_pct": 32.0,
            "cost_estimate": "$1,800 – $3,200",
            "cost_level": "Medium",
            "difficulty": "Medium",
            "payback_time": "8 – 11 months",
            "timeframe": "mid_term",
            "timeframe_label": "Mid-term (3–12 Months)",
            "impact_tag": "Turns Waste to Cash"
        },
        {
            "id": "waste_compost",
            "name": "Commercial Organic Composting Partnership",
            "description": "Divert 100% of organic leftovers and food scraps to licensed commercial composting or anaerobic digestion.",
            "co2_saved_pct": 38.0,
            "cost_estimate": "$400 setup",
            "cost_level": "Low",
            "difficulty": "Easy",
            "payback_time": "3 months",
            "timeframe": "mid_term",
            "timeframe_label": "Mid-term (3–12 Months)",
            "impact_tag": "Zero Methane"
        },
        {
            "id": "waste_closed_loop",
            "name": "Reusable Tote Boxes & Supplier Return Loops",
            "description": "Replace single-use corrugated carton packaging with durable collapsible return totes for regular vendors.",
            "co2_saved_pct": 60.0,
            "cost_estimate": "$4,000 – $8,000",
            "cost_level": "High",
            "difficulty": "Hard",
            "payback_time": "2.2 years",
            "timeframe": "long_term",
            "timeframe_label": "Long-term (1+ Years)",
            "impact_tag": "Circular Economy"
        }
    ]
}

DEFAULT_SUGGESTIONS = [
    {
        "id": "sug_1",
        "author": "Marcus Vance",
        "company": "SwiftRoute Couriers",
        "category": "transport",
        "title": "Adopt 80% tire pressure monitoring alerts",
        "description": "Installing $45 TPMS valve caps showed a 3.2% fuel reduction across our 8 delivery vans immediately!",
        "votes": 14,
        "date": "2026-08-28"
    },
    {
        "id": "sug_2",
        "author": "Alex Morgan",
        "company": "GreenBite Organics",
        "category": "electricity",
        "title": "Air curtain sensors over cold-storage doorways",
        "description": "Wiring air curtains to trigger only when roller doors open prevented HVAC motor overload and cut summer refrigeration peaks.",
        "votes": 21,
        "date": "2026-09-02"
    },
    {
        "id": "sug_3",
        "author": "Sarah Chen",
        "company": "EcoTrend Boutique",
        "category": "waste",
        "title": "Customer bag opt-out with charity donation match",
        "description": "We offered to donate 25¢ to a local tree project if shoppers skipped paper bags. 78% of customers chose to skip the bag!",
        "votes": 35,
        "date": "2026-09-05"
    }
]

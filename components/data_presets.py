"""
Demo Business Presets, AI Recommendations, and 4R Circular Alternatives.
Supports 4 core industry sectors: Food Processing, Retail Store, Logistics Company, and Manufacturing Plant.
"""

from typing import Dict, List, Any

DEMO_BUSINESSES: Dict[str, Dict[str, Any]] = {
  "food_processing": {
    "name": "GreenBite Organics & Bakery",
    "type_label": "Food Processing & Bakery",
    "industry": "Food Processing",
    "icon": "🥪",
    "employees": 65,
    "revenue": 4200000.0,
    "location": "Portland, Oregon",
    "description": "Commercial organic bakery operating industrial continuous ovens, refrigeration walk-ins, and regional refrigerated delivery vans.",
    "data": {
      "business_name": "GreenBite Organics",
      "industry": "Food Processing",
      "company_type": "Mid-Sized Manufacturer",
      "employees": 65,
      "annual_revenue": 4200000.0,
      "country": "United States",
      "state": "Oregon",
      "factory_location": "Portland Facility #1",
      # Energy
      "electricity_kwh": 385000.0,
      "renewable_pct": 15.0,
      "diesel_liters": 14500.0,
      "petrol_liters": 3200.0,
      "gas_m3": 48000.0,
      # Transport
      "truck_km": 68000.0,
      "car_km": 22000.0,
      "commute_km": 85000.0,
      "delivery_vehicles": 8,
      # Waste
      "organic_waste_kg": 46000.0,
      "plastic_waste_kg": 18500.0,
      "metal_waste_kg": 2400.0,
      "paper_waste_kg": 16000.0,
      "hazardous_waste_kg": 650.0,
      # Water
      "water_m3": 7800.0,
      "wastewater_m3": 6600.0,
      # Manufacturing
      "raw_material_tonnes": 480.0,
      "production_units": 450000.0,
      "machine_hours": 3800.0,
      # Government Carbon Credits
      "total_credits": 280.0,
      "credit_price": 38.0,
      "current_balance": 280.0
    }
  },
  "retail_store": {
    "name": "EcoTrend Apparel & Retail",
    "type_label": "Retail Store & Boutique",
    "industry": "Retail Store",
    "icon": "🏪",
    "employees": 22,
    "revenue": 1850000.0,
    "location": "San Francisco, California",
    "description": "Multi-location lifestyle retail store with high-intensity display lighting, year-round HVAC conditioning, and substantial shipping packaging waste.",
    "data": {
      "business_name": "EcoTrend Boutique",
      "industry": "Retail Store",
      "company_type": "SME Retailer",
      "employees": 22,
      "annual_revenue": 1850000.0,
      "country": "United States",
      "state": "California",
      "factory_location": "Bay Area Stores",
      # Energy
      "electricity_kwh": 140000.0,
      "renewable_pct": 25.0,
      "diesel_liters": 2200.0,
      "petrol_liters": 4500.0,
      "gas_m3": 8500.0,
      # Transport
      "truck_km": 18000.0,
      "car_km": 15000.0,
      "commute_km": 42000.0,
      "delivery_vehicles": 2,
      # Waste
      "organic_waste_kg": 3200.0,
      "plastic_waste_kg": 11000.0,
      "metal_waste_kg": 800.0,
      "paper_waste_kg": 24000.0,
      "hazardous_waste_kg": 120.0,
      # Water
      "water_m3": 1400.0,
      "wastewater_m3": 1200.0,
      # Manufacturing
      "raw_material_tonnes": 85.0,
      "production_units": 65000.0,
      "machine_hours": 900.0,
      # Government Carbon Credits
      "total_credits": 120.0,
      "credit_price": 2905.0,
      "current_balance": 120.0
    }
  },
  "logistics_company": {
    "name": "SwiftRoute Delivery & Freight",
    "type_label": "Logistics & Fleet Transport",
    "industry": "Logistics Company",
    "icon": "🚚",
    "employees": 85,
    "revenue": 8900000.0,
    "location": "Dallas, Texas",
    "description": "Regional cross-dock distribution hub running 24 delivery trucks, 14 local couriers, sorting conveyors, and continuous warehouse illumination.",
    "data": {
      "business_name": "SwiftRoute Logistics",
      "industry": "Logistics Company",
      "company_type": "Fleet Operator",
      "employees": 85,
      "annual_revenue": 8900000.0,
      "country": "United States",
      "state": "Texas",
      "factory_location": "Dallas Cross-Dock Terminal",
      # Energy
      "electricity_kwh": 210000.0,
      "renewable_pct": 10.0,
      "diesel_liters": 92000.0,
      "petrol_liters": 16000.0,
      "gas_m3": 12000.0,
      # Transport
      "truck_km": 480000.0,
      "car_km": 45000.0,
      "commute_km": 140000.0,
      "delivery_vehicles": 28,
      # Waste
      "organic_waste_kg": 5400.0,
      "plastic_waste_kg": 22000.0,
      "metal_waste_kg": 6800.0,
      "paper_waste_kg": 32000.0,
      "hazardous_waste_kg": 2400.0,
      # Water
      "water_m3": 3800.0,
      "wastewater_m3": 3400.0,
      # Manufacturing
      "raw_material_tonnes": 120.0,
      "production_units": 380000.0,
      "machine_hours": 4200.0,
      # Government Carbon Credits
      "total_credits": 450.0,
      "credit_price": 42.0,
      "current_balance": 450.0
    }
  },
  "manufacturing_plant": {
    "name": "Apex Precision Metal & Polymers",
    "type_label": "Industrial Manufacturing Plant",
    "industry": "Manufacturing Plant",
    "icon": "🏭",
    "employees": 140,
    "revenue": 16500000.0,
    "location": "Cleveland, Ohio",
    "description": "High-output precision machining and polymer extrusion factory operating 3 continuous production shifts, CNC tooling centers, and thermal ovens.",
    "data": {
      "business_name": "Apex Precision Plant",
      "industry": "Manufacturing Plant",
      "company_type": "Heavy Manufacturing",
      "employees": 140,
      "annual_revenue": 16500000.0,
      "country": "United States",
      "state": "Ohio",
      "factory_location": "Plant #4 Industrial Park",
      # Energy
      "electricity_kwh": 920000.0,
      "renewable_pct": 8.0,
      "diesel_liters": 38000.0,
      "petrol_liters": 8500.0,
      "gas_m3": 88000.0,
      # Transport
      "truck_km": 145000.0,
      "car_km": 36000.0,
      "commute_km": 210000.0,
      "delivery_vehicles": 12,
      # Waste
      "organic_waste_kg": 12000.0,
      "plastic_waste_kg": 48000.0,
      "metal_waste_kg": 34000.0,
      "paper_waste_kg": 19000.0,
      "hazardous_waste_kg": 8500.0,
      # Water
      "water_m3": 16500.0,
      "wastewater_m3": 14200.0,
      # Manufacturing
      "raw_material_tonnes": 1250.0,
      "production_units": 185000.0,
      "machine_hours": 6400.0,
      # Government Carbon Credits
      "total_credits": 620.0,
      "credit_price": 40.0,
      "current_balance": 620.0
    }
  }
}

# Alias for backward compatibility
DEMO_BUSINESSES["food_processor"] = DEMO_BUSINESSES["food_processing"]
DEMO_BUSINESSES["small_retail"] = DEMO_BUSINESSES["retail_store"]
DEMO_BUSINESSES["logistics"] = DEMO_BUSINESSES["logistics_company"]

# Pre-configured demo users
DEMO_USERS: Dict[str, Dict[str, Any]] = {
  "alex@greenbite.com": {
    "name": "Alex Morgan",
    "company": "GreenBite Organics",
    "role": "Admin",
    "avatar": "👨‍🍳",
    "preset_key": "food_processing",
    "industry": "Food Processing"
  },
  "sarah@ecotrend.com": {
    "name": "Sarah Chen",
    "company": "EcoTrend Boutique",
    "role": "Admin",
    "avatar": "👩‍💼",
    "preset_key": "retail_store",
    "industry": "Retail Store"
  },
  "marcus@swiftroute.com": {
    "name": "Marcus Vance",
    "company": "SwiftRoute Logistics",
    "role": "Admin",
    "avatar": "🚚",
    "preset_key": "logistics_company",
    "industry": "Logistics Company"
  },
  "david@apexmanufacturing.com": {
    "name": "David Kovac",
    "company": "Apex Precision Plant",
    "role": "Admin",
    "avatar": "🏭",
    "preset_key": "manufacturing_plant",
    "industry": "Manufacturing Plant"
  }
}

# Top 10 Actionable AI Decarbonization Recommendations
AI_RECOMMENDATIONS: List[Dict[str, Any]] = [
  {
    "id": "rec_led",
    "title": "Replace Fluorescent & HID Lighting with High-Efficacy LEDs",
    "category": "Electricity",
    "icon": "",
    "description": "Retrofit all high-bay warehouse and office fixtures with smart dimmed LEDs and motion daylight harvest sensors.",
    "co2_saved_t": 18.5,
    "co2_saved_pct": 14.0,
    "cost_estimate": "₹232,400 – ₹373,500",
    "expected_roi": 145.0,
    "payback_time": "5 months",
    "difficulty": "Easy",
    "impact_level": "High",
    "circular_benefit": "Recycle old fixtures with authorized e-waste vendor; modular LED components extend life 50,000 hrs.",
    "govt_incentives": "Utility Commercial Energy Rebate covers up to 40% of hardware and installation cost.",
    "credits_saved": 18.5
  },
  {
    "id": "rec_solar",
    "title": "Install On-Site Rooftop Solar PV Microgrid (50kW–100kW)",
    "category": "Electricity",
    "icon": "",
    "description": "Deploy rooftop bifacial monocrystalline solar panels with smart inverter to power daytime peak loads directly.",
    "co2_saved_t": 68.0,
    "co2_saved_pct": 38.0,
    "cost_estimate": "₹3,486,000 – ₹6,225,000",
    "expected_roi": 28.0,
    "payback_time": "3.8 years",
    "difficulty": "Hard",
    "impact_level": "Critical",
    "circular_benefit": "Generates 100% clean power on site with zero emissions and 25-year panel degradation guarantee.",
    "govt_incentives": "Federal Clean Energy Investment Tax Credit (ITC) 30% + State Accelerated MACRS depreciation.",
    "credits_saved": 68.0
  },
  {
    "id": "rec_insulation",
    "title": "Thermal Pipe & Boiler Valve Jacket Insulation",
    "category": "Fuel",
    "icon": "🧤",
    "description": "Wrap bare steam pipes, boiler manifold valves, and hot condensate lines with custom fiberglass removable blankets.",
    "co2_saved_t": 22.0,
    "co2_saved_pct": 16.0,
    "cost_estimate": "₹116,200 – ₹232,400",
    "expected_roi": 180.0,
    "payback_time": "4 months",
    "difficulty": "Easy",
    "impact_level": "High",
    "circular_benefit": "Stops 90% of radiant thermal energy loss; reusable blankets detach easily during maintenance.",
    "govt_incentives": "Qualifies for State Industrial Energy Efficiency direct grants.",
    "credits_saved": 22.0
  },
  {
    "id": "rec_ev_fleet",
    "title": "Switch Delivery Fleet to Commercial Electric Vehicles (EVs)",
    "category": "Transport",
    "icon": "⚡",
    "description": "Transition short-haul urban delivery vans to battery electric commercial vehicles with depot overnight Level 2 charging.",
    "co2_saved_t": 44.0,
    "co2_saved_pct": 48.0,
    "cost_estimate": "₹2,905,000 – ₹5,395,000 per van",
    "expected_roi": 32.0,
    "payback_time": "3.2 years",
    "difficulty": "Medium",
    "impact_level": "Critical",
    "circular_benefit": "Eliminates diesel tailpipe particulate matter; battery recycling agreement included in lease.",
    "govt_incentives": "Clean Commercial Vehicle Credit up to ₹622,500/vehicle + State EV charger installation subsidy.",
    "credits_saved": 44.0
  },
  {
    "id": "rec_route_opt",
    "title": "AI Route Optimization & Fleet Telematics Anti-Idling",
    "category": "Transport",
    "icon": "🗺️",
    "description": "Deploy dynamic GPS dispatch routing software with automated 3-minute idle engine cutoff and driving scorecards.",
    "co2_saved_t": 19.5,
    "co2_saved_pct": 18.0,
    "cost_estimate": "₹99,600 / yr subscription",
    "expected_roi": 210.0,
    "payback_time": "2 months",
    "difficulty": "Easy",
    "impact_level": "High",
    "circular_benefit": "Reduces tyre wear and oil changes by 20% while saving thousands of miles of unnecessary transit.",
    "govt_incentives": "Qualifies as operational logistics optimization write-off.",
    "credits_saved": 19.5
  },
  {
    "id": "rec_water_recycle",
    "title": "Closed-Loop Process Water & Cooling Filtration System",
    "category": "Water",
    "icon": "",
    "description": "Install on-site microfiltration and reverse osmosis skids to recycle cooling tower and equipment washdown water.",
    "co2_saved_t": 14.8,
    "co2_saved_pct": 35.0,
    "cost_estimate": "₹705,500 – ₹1,328,000",
    "expected_roi": 65.0,
    "payback_time": "14 months",
    "difficulty": "Medium",
    "impact_level": "High",
    "circular_benefit": "Achieves 65% water reuse, cutting sewer effluent surcharges and freshwater municipal consumption.",
    "govt_incentives": "Regional Water District Conservation grant up to ₹415,000.",
    "credits_saved": 14.8
  },
  {
    "id": "rec_waste_heat",
    "title": "Flue Gas & Exhaust Heat Recovery Loop",
    "category": "Fuel",
    "icon": "♨️",
    "description": "Capture 200°C+ thermal exhaust from ovens or boilers with a shell-and-tube heat exchanger to pre-heat boiler makeup water.",
    "co2_saved_t": 31.0,
    "co2_saved_pct": 24.0,
    "cost_estimate": "₹913,000 – ₹1,826,000",
    "expected_roi": 55.0,
    "payback_time": "18 months",
    "difficulty": "Medium",
    "impact_level": "High",
    "circular_benefit": "Reclaims wasted thermal enthalpy back into active production, creating an on-site thermal circular loop.",
    "govt_incentives": "Combined Heat & Power (CHP) clean production tax allowances.",
    "credits_saved": 31.0
  },
  {
    "id": "rec_biomass",
    "title": "Transition Auxiliary Heating to Certified Biomass Pellets",
    "category": "Fuel",
    "icon": "🪵",
    "description": "Replace fossil heating oil burner with automated clean-burn compressed wood biomass pellet furnace.",
    "co2_saved_t": 28.5,
    "co2_saved_pct": 52.0,
    "cost_estimate": "₹1,245,000 – ₹2,324,000",
    "expected_roi": 42.0,
    "payback_time": "2.5 years",
    "difficulty": "Medium",
    "impact_level": "High",
    "circular_benefit": "Utilizes forestry sawmill timber residues that would otherwise rot in landfill, closing carbon lifecycle.",
    "govt_incentives": "Renewable Heat Incentive grant covering up to 30% of boiler swap.",
    "credits_saved": 28.5
  },
  {
    "id": "rec_vfd_motors",
    "title": "Install Variable Frequency Drives (VFDs) on Pumps & Fans",
    "category": "Electricity",
    "icon": "",
    "description": "Add intelligent VFD controllers to large 15kW+ HVAC blowers, air compressors, and process conveyor motors.",
    "co2_saved_t": 24.0,
    "co2_saved_pct": 22.0,
    "cost_estimate": "₹373,500 – ₹747,000",
    "expected_roi": 85.0,
    "payback_time": "11 months",
    "difficulty": "Medium",
    "impact_level": "High",
    "circular_benefit": "Stops motor throttling mechanical strain, doubling equipment operational lifespan and reducing scrap.",
    "govt_incentives": "Electric Utility Motor Efficiency Rebate up to ₹6,640 per installed horsepower.",
    "credits_saved": 24.0
  },
  {
    "id": "rec_pred_maint",
    "title": "IoT Vibration Sensors & Predictive Compressed Air Leak Maintenance",
    "category": "Manufacturing",
    "icon": "📡",
    "description": "Mount ultrasound acoustic and vibration IoT monitors to detect compressed air leaks and bearing friction early.",
    "co2_saved_t": 16.5,
    "co2_saved_pct": 19.0,
    "cost_estimate": "₹182,600 – ₹348,600",
    "expected_roi": 190.0,
    "payback_time": "4 months",
    "difficulty": "Easy",
    "impact_level": "Medium",
    "circular_benefit": "Prevents catastrophic machine breakdown and reduces unmetered compressor electricity drain by 25%.",
    "govt_incentives": "Industry 4.0 Digitalization grant credits.",
    "credits_saved": 16.5
  }
]

# Circular 4R Framework Alternatives Matrix
CIRCULAR_ALTERNATIVES: Dict[str, Dict[str, Any]] = {
  "plastic_waste": {
    "title": "Plastic Packaging & Extrusion Waste",
    "icon": "🧴",
    "feather_icon": "box",
    "current_impact": "High carbon footprint (2.1 kg CO2/kg) and municipal tipping costs.",
    "reuse": {
      "title": "Returnable Closed-Loop Packaging Totes",
      "partner": "ReLoop Supply Logistics",
      "mechanism": "Replace single-use stretch film and corrugated boxes with collapsible heavy-duty PP returnable totes with RFID tracking.",
      "cost_saving": "₹265,600 / yr",
      "carbon_saving": "12.5 tonnes CO2 / yr"
    },
    "recycle": {
      "title": "Certified PCR Regrind Partner",
      "partner": "EcoPolymer Recycling Inc.",
      "mechanism": "Sort clean HDPE and LDPE scrap on-site in dedicated balers; partner collects and returns as 30% recycled content resin.",
      "cost_saving": "₹199,200 / yr",
      "carbon_saving": "18.2 tonnes CO2 / yr"
    },
    "recover": {
      "title": "Engineered Solid Refuse Fuel (SRF)",
      "partner": "Thermal Recovery Energy Hub",
      "mechanism": "Divert contaminated non-recyclable multi-layer films to authorized industrial cement kiln energy recovery.",
      "cost_saving": "₹78,850 / yr",
      "carbon_saving": "7.8 tonnes CO2 / yr"
    },
    "replace": {
      "title": "Bio-Compostable Molded Mycelium / PLA",
      "partner": "GreenCell Materials Co.",
      "mechanism": "Substitute EPS styrofoam and bubble plastic cushions with bio-based mycelium fiber cushioning.",
      "cost_saving": "₹91,300 / yr",
      "carbon_saving": "9.4 tonnes CO2 / yr"
    }
  },
  "organic_waste": {
    "title": "Organic Food & Biological Trimmings",
    "icon": "🍎",
    "feather_icon": "leaf",
    "current_impact": "Generates fugitive methane in landfill (0.45 kg CO2/kg).",
    "reuse": {
      "title": "Surplus Food Redistribution Network",
      "partner": "Regional Food Rescue Coalition",
      "mechanism": "Chill edible surplus inventory and food grade trim for daily charitable redistribution.",
      "cost_saving": "₹149,400 / yr tax deduction",
      "carbon_saving": "14.0 tonnes CO2 / yr"
    },
    "recycle": {
      "title": "Commercial Micro-Composting Partner",
      "partner": "SoilCare Organics Facility",
      "mechanism": "Segregate food prep waste into sealed green toters; converted into organic certified soil enhancer.",
      "cost_saving": "₹174,300 / yr in tipping fees",
      "carbon_saving": "19.5 tonnes CO2 / yr"
    },
    "recover": {
      "title": "Anaerobic Digestion to Renewable RNG",
      "partner": "BioGas Energy Utilities",
      "mechanism": "Direct high-moisture organic sludge to municipal anaerobic digesters to produce renewable biomethane.",
      "cost_saving": "₹120,350 / yr",
      "carbon_saving": "16.8 tonnes CO2 / yr"
    },
    "replace": {
      "title": "High-Yield Raw Ingredient Slicing",
      "partner": "FoodTech Precision Equipment",
      "mechanism": "Calibrate automated laser cutting equipment to reduce core and edge trim waste by 22%.",
      "cost_saving": "₹431,600 / yr raw food spend",
      "carbon_saving": "11.2 tonnes CO2 / yr"
    }
  },
  "metal_waste": {
    "title": "Machining Swarf, Stampings & Off-Cuts",
    "icon": "🔩",
    "feather_icon": "settings",
    "current_impact": "High virgin material embodied energy (1.8 kg CO2/kg).",
    "reuse": {
      "title": "Secondary Small-Component Stamping",
      "partner": "In-house Tooling Team",
      "mechanism": "Re-engineer tooling dies to utilize sheet metal skeletons for smaller brackets and washers.",
      "cost_saving": "₹381,800 / yr raw material",
      "carbon_saving": "8.5 tonnes CO2 / yr"
    },
    "recycle": {
      "title": "Closed-Loop High-Grade Scrap Buyback",
      "partner": "MetalsLoop Certified Foundry",
      "mechanism": "Keep aluminum and brass chips segregated by alloy grade; foundry pays premium spot price and remelts.",
      "cost_saving": "₹680,600 / yr cash back",
      "carbon_saving": "28.0 tonnes CO2 / yr"
    },
    "recover": {
      "title": "Centrifugal Cutting Fluid Recovery",
      "partner": "CleanLube Engineering",
      "mechanism": "Spin wet metal swarf through a chip wringer to reclaim 95% of synthetic cutting oil.",
      "cost_saving": "₹315,400 / yr coolant spend",
      "carbon_saving": "6.2 tonnes CO2 / yr"
    },
    "replace": {
      "title": "Near-Net-Shape Cold Forging",
      "partner": "Advanced Tooling Systems",
      "mechanism": "Adopt near-net-shape blanks to cut down subtractive machining material loss from 40% to 8%.",
      "cost_saving": "₹1,037,500 / yr",
      "carbon_saving": "22.4 tonnes CO2 / yr"
    }
  },
  "water_effluent": {
    "title": "Industrial Process Water & Effluent",
    "icon": "💧",
    "feather_icon": "droplet",
    "current_impact": "Rising utility tariff + surcharge effluent penalties (0.71 kg CO2/m³).",
    "reuse": {
      "title": "Cooling Tower Bleed-Off Greywater",
      "partner": "Facility Facilities Engineering",
      "mechanism": "Reroute cooling blowdown water to facility grounds irrigation and exterior equipment wash bays.",
      "cost_saving": "₹157,700 / yr",
      "carbon_saving": "4.8 tonnes CO2 / yr"
    },
    "recycle": {
      "title": "Membrane Bioreactor (MBR) Polishing",
      "partner": "AquaLoop Filtration Technologies",
      "mechanism": "Treat washdown effluent to non-potable CIP rinse standards, recycling 60% of water volume.",
      "cost_saving": "₹531,200 / yr",
      "carbon_saving": "11.2 tonnes CO2 / yr"
    },
    "recover": {
      "title": "Effluent Waste Heat Exchanger",
      "partner": "ThermaFlow Recovery Skids",
      "mechanism": "Pass warm 45°C effluent through plate heat exchanger to pre-heat incoming clean process water.",
      "cost_saving": "₹232,400 / yr fuel spend",
      "carbon_saving": "9.5 tonnes CO2 / yr"
    },
    "replace": {
      "title": "Dry High-Pressure CO2 Cleaning",
      "partner": "ColdJet Dry Clean Systems",
      "mechanism": "Replace water and solvent hose cleaning with dry ice blast pellets, eliminating water usage entirely.",
      "cost_saving": "₹282,200 / yr",
      "carbon_saving": "7.1 tonnes CO2 / yr"
    }
  }
}

CATEGORY_FIXES: Dict[str, List[Dict[str, Any]]] = {
  "electricity": [
    {
      "id": "elec_led",
      "name": "High-Efficiency LED High-Bay & Smart Dimming Retrofit",
      "description": "Replace existing fluorescent tubes and metal-halide high bays with high-efficacy LEDs and motion daylight harvest controls.",
      "co2_saved_pct": 14.0,
      "cost_estimate": "₹150,000 – ₹300,000",
      "cost_level": "Low",
      "difficulty": "Easy",
      "payback_time": "5 months",
      "timeframe": "quick_win",
      "timeframe_label": "Quick Win (0–3 Months)",
      "impact_tag": "Instant Stop-Leak"
    },
    {
      "id": "elec_sensor",
      "name": "Smart Motor Soft-Starters & VFD Drives",
      "description": "Install Variable Frequency Drives (VFDs) on plant exhaust blowers, pumps, and conveyor motors to eliminate idle power spikes.",
      "co2_saved_pct": 22.0,
      "cost_estimate": "₹350,000 – ₹600,000",
      "cost_level": "Medium",
      "difficulty": "Medium",
      "payback_time": "11 months",
      "timeframe": "mid_term",
      "timeframe_label": "Mid-term (3–12 Months)",
      "impact_tag": "Peak Demand Shaving"
    },
    {
      "id": "solar_pv",
      "name": "Rooftop Solar PV Microgrid (50kW – 150kW)",
      "description": "Install on-site commercial rooftop solar PV arrays to generate clean power, abating daytime grid demand charges.",
      "co2_saved_pct": 42.0,
      "cost_estimate": "₹2,500,000 – ₹5,000,000",
      "cost_level": "High",
      "difficulty": "Hard",
      "payback_time": "3.5 years",
      "timeframe": "long_term",
      "timeframe_label": "Long-term (1+ Years)",
      "impact_tag": "Net-Zero Milestone"
    }
  ],
  "fuel": [
    {
      "id": "fuel_insulate",
      "name": "Thermal Pipe & Steam Valve Blanket Insulation",
      "description": "Wrap bare steam manifolds, valves, and uninsulated condensate piping with high-temperature removable fiberglass thermal jackets.",
      "co2_saved_pct": 16.0,
      "cost_estimate": "₹80,000 – ₹180,000",
      "cost_level": "Low",
      "difficulty": "Easy",
      "payback_time": "4 months",
      "timeframe": "quick_win",
      "timeframe_label": "Quick Win (0–3 Months)",
      "impact_tag": "Radiant Heat Capture"
    },
    {
      "id": "fuel_boiler_tune",
      "name": "Boiler Burner Tuning & O2 Trim Calibration",
      "description": "Calibrate air-fuel combustion ratios, clean burner nozzles, and service economizers for optimal thermal transfer.",
      "co2_saved_pct": 18.0,
      "cost_estimate": "₹120,000 – ₹250,000",
      "cost_level": "Low",
      "difficulty": "Easy",
      "payback_time": "6 months",
      "timeframe": "mid_term",
      "timeframe_label": "Mid-term (3–12 Months)",
      "impact_tag": "Combustion Efficiency"
    },
    {
      "id": "fuel_heat_pump",
      "name": "Industrial Heat Pump & Thermal Electrification",
      "description": "Transition process hot water boilers from fossil fuels to high-efficiency industrial air-to-water heat pumps.",
      "co2_saved_pct": 52.0,
      "cost_estimate": "₹1,800,000 – ₹3,500,000",
      "cost_level": "High",
      "difficulty": "Hard",
      "payback_time": "3.8 years",
      "timeframe": "long_term",
      "timeframe_label": "Long-term (1+ Years)",
      "impact_tag": "Zero Fossil Fuel"
    }
  ],
  "transport": [
    {
      "id": "fuel_telematics",
      "name": "Fleet Anti-Idling Policy & Telematics Speed Caps",
      "description": "Deploy OBD-II telematics to enforce 3-minute max engine idling rules and moderate highway cruising speeds.",
      "co2_saved_pct": 12.0,
      "cost_estimate": "₹20,000 – ₹50,000",
      "cost_level": "Low",
      "difficulty": "Easy",
      "payback_time": "2 months",
      "timeframe": "quick_win",
      "timeframe_label": "Quick Win (0–3 Months)",
      "impact_tag": "Zero CapEx"
    },
    {
      "id": "trans_route",
      "name": "AI Dynamic Route Planning & Delivery Consolidation",
      "description": "Implement route dispatch software to cluster shipment drops and eliminate empty backhaul mileage.",
      "co2_saved_pct": 24.0,
      "cost_estimate": "₹80,000 – ₹180,000 / yr",
      "cost_level": "Medium",
      "difficulty": "Medium",
      "payback_time": "3 months",
      "timeframe": "mid_term",
      "timeframe_label": "Mid-term (3–12 Months)",
      "impact_tag": "Mileage Reduction"
    },
    {
      "id": "trans_ev_fleet",
      "name": "Commercial Electric Vehicle (EV) Delivery Fleet Transition",
      "description": "Phase out diesel freight vans with commercial battery electric vans supported by depot smart overnight charging.",
      "co2_saved_pct": 65.0,
      "cost_estimate": "₹2,800,000 – ₹5,500,000 per van",
      "cost_level": "High",
      "difficulty": "Hard",
      "payback_time": "3.5 years",
      "timeframe": "long_term",
      "timeframe_label": "Long-term (1+ Years)",
      "impact_tag": "Zero Tailpipe"
    }
  ],
  "waste": [
    {
      "id": "waste_segregation",
      "name": "Point-of-Origin Color-Coded Waste Sorting Stations",
      "description": "Introduce shop-floor source segregation bins for cardboard, clean plastics, and organics to avoid landfill contamination.",
      "co2_saved_pct": 20.0,
      "cost_estimate": "₹25,000 – ₹60,000",
      "cost_level": "Low",
      "difficulty": "Easy",
      "payback_time": "2 months",
      "timeframe": "quick_win",
      "timeframe_label": "Quick Win (0–3 Months)",
      "impact_tag": "Diverts Landfill"
    },
    {
      "id": "waste_compact_baler",
      "name": "Cardboard & Plastic Baler with Recycler Buyback",
      "description": "Install an on-site mechanical baler to compact recyclable streams into dense bales for cash rebate pickups.",
      "co2_saved_pct": 34.0,
      "cost_estimate": "₹200,000 – ₹450,000",
      "cost_level": "Medium",
      "difficulty": "Medium",
      "payback_time": "9 months",
      "timeframe": "mid_term",
      "timeframe_label": "Mid-term (3–12 Months)",
      "impact_tag": "Turns Waste to Cash"
    },
    {
      "id": "waste_return_totes",
      "name": "Closed-Loop Collapsible Returnable Transport Packaging",
      "description": "Replace single-use corrugated carton packaging with durable returnable plastic totes across recurring supplier loops.",
      "co2_saved_pct": 58.0,
      "cost_estimate": "₹450,000 – ₹900,000",
      "cost_level": "High",
      "difficulty": "Hard",
      "payback_time": "2.1 years",
      "timeframe": "long_term",
      "timeframe_label": "Long-term (1+ Years)",
      "impact_tag": "Circular Economy"
    }
  ]
}


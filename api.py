"""
FastAPI Backend Microservice for Industrial Emission Leak-Point Detector.
Provides RESTful API endpoints for external ERP integration, IoT automated ingestion,
emission recalculation, leak diagnostics, and carbon credit audits.
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from components.calculations import calculate_detailed_emissions, INDUSTRY_BENCHMARKS
from components.data_presets import AI_RECOMMENDATIONS, CIRCULAR_ALTERNATIVES
from database.db_manager import save_activity_log, get_activity_logs, get_aggregated_activity_summary
import uvicorn

app = FastAPI(
    title="Industrial Emission Leak-Point Detector API",
    description="REST API for Scope 1-3 GHG calculations, automated leak point diagnostics, carbon credits accounting, and periodic operational activity ingestion.",
    version="2.1.0"
)

# Pydantic Schemas
class EmissionInputModel(BaseModel):
    business_name: Optional[str] = "Industrial Plant"
    industry: Optional[str] = "Manufacturing Plant"
    electricity_kwh: float = Field(0.0, ge=0.0, description="Annual electricity consumption in kWh")
    renewable_pct: float = Field(0.0, ge=0.0, le=100.0, description="Share of on-site renewable power in %")
    diesel_liters: float = Field(0.0, ge=0.0, description="Annual diesel consumption in Liters")
    petrol_liters: float = Field(0.0, ge=0.0, description="Annual petrol consumption in Liters")
    gas_m3: float = Field(0.0, ge=0.0, description="Annual natural gas consumption in m³")
    truck_km: float = Field(0.0, ge=0.0, description="Truck freight distance in km")
    car_km: float = Field(0.0, ge=0.0, description="Company car distance in km")
    commute_km: float = Field(0.0, ge=0.0, description="Employee commute distance in km")
    delivery_vehicles: int = Field(0, ge=0, description="Number of delivery vehicles")
    organic_waste_kg: float = Field(0.0, ge=0.0, description="Organic waste in kg")
    plastic_waste_kg: float = Field(0.0, ge=0.0, description="Plastic waste in kg")
    metal_waste_kg: float = Field(0.0, ge=0.0, description="Metal waste in kg")
    paper_waste_kg: float = Field(0.0, ge=0.0, description="Paper waste in kg")
    hazardous_waste_kg: float = Field(0.0, ge=0.0, description="Hazardous waste in kg")
    water_m3: float = Field(0.0, ge=0.0, description="Water consumption in m³")
    wastewater_m3: float = Field(0.0, ge=0.0, description="Wastewater generated in m³")
    raw_material_tonnes: float = Field(0.0, ge=0.0, description="Raw material used in tonnes")
    production_units: float = Field(0.0, ge=0.0, description="Total units produced")
    machine_running_hours: float = Field(0.0, ge=0.0, description="Machine operating hours")
    total_credits: float = Field(0.0, ge=0.0, description="Government allocated carbon credits")
    credit_price: float = Field(2905.0, ge=1.0, description="Carbon credit market price (₹/t)")

class SimulationInputModel(BaseModel):
    baseline_data: EmissionInputModel
    reduction_electricity_pct: float = Field(0.0, ge=0.0, le=90.0)
    target_renewable_pct: float = Field(0.0, ge=0.0, le=100.0)
    reduction_fuel_pct: float = Field(0.0, ge=0.0, le=90.0)
    reduction_transport_pct: float = Field(0.0, ge=0.0, le=90.0)
    reduction_waste_pct: float = Field(0.0, ge=0.0, le=90.0)
    reduction_water_pct: float = Field(0.0, ge=0.0, le=90.0)

class ActivityLogInputModel(BaseModel):
    user_email: str = Field(..., description="Corporate work email of organization")
    log_date: Optional[str] = Field(None, description="ISO date YYYY-MM-DD")
    frequency: str = Field("daily", description="Log frequency: 'daily' or 'weekly'")
    period_label: Optional[str] = Field(None, description="Shift or week label")
    diesel_liters: float = Field(0.0, ge=0.0)
    petrol_liters: float = Field(0.0, ge=0.0)
    gas_m3: float = Field(0.0, ge=0.0)
    electricity_kwh: float = Field(0.0, ge=0.0)
    organic_waste_kg: float = Field(0.0, ge=0.0)
    plastic_waste_kg: float = Field(0.0, ge=0.0)
    metal_waste_kg: float = Field(0.0, ge=0.0)
    paper_waste_kg: float = Field(0.0, ge=0.0)
    hazardous_waste_kg: float = Field(0.0, ge=0.0)
    truck_km: float = Field(0.0, ge=0.0)
    water_m3: float = Field(0.0, ge=0.0)
    production_units: float = Field(0.0, ge=0.0)
    notes: Optional[str] = Field("", description="Operational shift notes")

# Endpoints
@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint."""
    return {"status": "online", "service": "Industrial Emission Leak Detector", "version": "2.0.0"}

@app.post("/api/calculate-emissions", tags=["Emissions Engine"])
def api_calculate_emissions(payload: EmissionInputModel):
    """Calculates comprehensive GHG Protocol Scope 1-3 footprint and cost equivalents."""
    data = payload.dict()
    results = calculate_detailed_emissions(data)
    return results

@app.post("/api/leak-detection", tags=["Leak Diagnostics"])
def api_leak_detection(payload: EmissionInputModel):
    """Ranks and returns the Top 10 operational emission leak points."""
    data = payload.dict()
    results = calculate_detailed_emissions(data)
    return {
        "business_name": payload.business_name,
        "total_co2": results["total_co2"],
        "top_10_leaks": results["top_10_leaks"]
    }

@app.post("/api/carbon-credits", tags=["Carbon Compliance"])
def api_carbon_credits(payload: EmissionInputModel):
    """Calculates carbon credit balance, deficit/surplus status, and market costs."""
    data = payload.dict()
    results = calculate_detailed_emissions(data)
    return {
        "govt_credits_allocated": results["govt_credits"],
        "credits_used": results["credits_used"],
        "credits_remaining": results["credits_remaining"],
        "credits_required": results["credits_required"],
        "net_carbon_status": results["net_carbon_status"],
        "estimated_purchase_cost": results["est_purchase_cost"],
        "estimated_selling_revenue": results["est_revenue"],
        "is_deficit": results["is_deficit"]
    }

@app.get("/api/benchmarks/{industry}", tags=["Benchmarking"])
def api_get_benchmark(industry: str):
    """Returns sector benchmarks for the specified industry."""
    for key, data in INDUSTRY_BENCHMARKS.items():
        if key.lower() == industry.lower():
            return {"industry": key, "benchmarks": data}
    raise HTTPException(status_code=404, detail="Industry benchmark not found")

@app.get("/api/recommendations", tags=["AI Recommendations"])
def api_get_recommendations(category: Optional[str] = None):
    """Returns AI decarbonization recommendations, optionally filtered by category."""
    if category:
        filtered = [r for r in AI_RECOMMENDATIONS if r["category"].lower() == category.lower()]
        return {"recommendations": filtered}
    return {"recommendations": AI_RECOMMENDATIONS}

@app.get("/api/circular-alternatives", tags=["Circular Economy"])
def api_get_circular_alternatives(waste_type: Optional[str] = None):
    """Returns 4R circular alternatives (Reuse, Recycle, Recover, Replace)."""
    if waste_type and waste_type in CIRCULAR_ALTERNATIVES:
        return {waste_type: CIRCULAR_ALTERNATIVES[waste_type]}
    return CIRCULAR_ALTERNATIVES

@app.post("/api/activity-logs", tags=["Periodic Operational Monitoring"])
def api_record_activity_log(payload: ActivityLogInputModel):
    """Ingests a daily or weekly operational activity log for fuel, waste, electricity, and transport."""
    data = payload.dict()
    email = data.pop("user_email")
    log_id = save_activity_log(email, data)
    summary = get_aggregated_activity_summary(email)
    return {
        "status": "success",
        "log_id": log_id,
        "message": f"Activity log #{log_id} recorded for {email}",
        "aggregated_summary": summary
    }

@app.get("/api/activity-logs/{user_email}", tags=["Periodic Operational Monitoring"])
def api_get_activity_logs(user_email: str, frequency: Optional[str] = None, limit: int = 100):
    """Retrieves chronological activity logs for the specified facility."""
    logs = get_activity_logs(user_email, limit=limit, frequency=frequency)
    summary = get_aggregated_activity_summary(user_email, frequency=frequency)
    return {
        "user_email": user_email,
        "total_records": len(logs),
        "summary": summary,
        "logs": logs
    }

@app.get("/api/activity-logs/summary/{user_email}", tags=["Periodic Operational Monitoring"])
def api_get_activity_summary(user_email: str, frequency: Optional[str] = None):
    """Returns aggregated periodic emission totals for the specified organization."""
    return get_aggregated_activity_summary(user_email, frequency=frequency)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

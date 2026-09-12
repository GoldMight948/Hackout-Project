"""
Monthly Emission Simulation, Trend Modeling, and ML Forecasting Engine.
Generates 12-month operational trajectories, seasonal intensity matrices,
and regression forecasts for Business-As-Usual vs Decarbonization pathways.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Seasonal weight multipliers reflecting commercial & industrial operational fluctuations
SEASONAL_WEIGHTS = {
    "Electricity": [1.12, 1.08, 0.95, 0.92, 1.05, 1.22, 1.28, 1.25, 1.08, 0.96, 1.02, 1.07],
    "Fuel & Heating": [1.35, 1.30, 1.15, 0.90, 0.70, 0.65, 0.60, 0.65, 0.75, 0.95, 1.20, 1.30],
    "Transport & Fleet": [0.88, 0.92, 1.02, 1.05, 1.08, 1.12, 1.15, 1.10, 1.05, 1.02, 1.18, 1.25],
    "Waste & Packaging": [0.90, 0.92, 0.98, 1.00, 1.02, 1.05, 1.08, 1.06, 1.02, 1.04, 1.15, 1.22],
    "Water & Effluent": [0.95, 0.94, 0.98, 1.02, 1.08, 1.15, 1.18, 1.16, 1.05, 1.00, 0.96, 0.95],
    "Industrial Ops": [0.96, 0.98, 1.02, 1.04, 1.05, 1.06, 1.02, 0.98, 1.05, 1.06, 1.04, 0.94]
}

def generate_monthly_timeseries(pillar_co2: Dict[str, float]) -> pd.DataFrame:
    """
    Synthesizes a realistic 12-month historical operational breakdown based on annual pillar totals
    and seasonal industrial load profiles.
    """
    records = []
    
    for m_idx, month in enumerate(MONTHS):
        row: Dict[str, Any] = {"Month": month, "Month_Num": m_idx + 1}
        month_total = 0.0
        
        for pillar, annual_val in pillar_co2.items():
            weights = SEASONAL_WEIGHTS.get(pillar, [1.0] * 12)
            # Normalize so weights average to 1.0
            norm_factor = weights[m_idx] / sum(weights)
            monthly_val = round(annual_val * norm_factor, 2)
            row[pillar] = monthly_val
            month_total += monthly_val
            
        row["Total_Monthly_CO2"] = round(month_total, 2)
        records.append(row)
        
    return pd.DataFrame(records)

def forecast_emissions_ml(monthly_df: pd.DataFrame, target_reduction_pct: float = 25.0) -> pd.DataFrame:
    """
    Fits an ML linear/polynomial regression model to historical monthly trajectory and
    projects the next 12 months under two scenarios:
    1. Business-As-Usual (BAU with 3% organic growth)
    2. Decarbonization Pathway (incorporating circular fixes & efficiency cuts)
    """
    x_hist = monthly_df["Month_Num"].values
    y_hist = monthly_df["Total_Monthly_CO2"].values
    
    # Fit degree-1 polynomial (linear regression)
    poly_coeffs = np.polyfit(x_hist, y_hist, deg=1)
    slope = poly_coeffs[0]
    intercept = poly_coeffs[1]
    
    future_months = [f"{m} '26" for m in MONTHS]
    records = []
    
    reduction_rate_per_month = (target_reduction_pct / 100.0) / 12.0
    
    for i, month_label in enumerate(future_months, start=13):
        m_idx = (i - 1) % 12
        # Baseline seasonality adjustment
        avg_seasonal = np.mean([SEASONAL_WEIGHTS[p][m_idx] for p in SEASONAL_WEIGHTS])
        
        # Scenario 1: BAU (slight expansion)
        bau_proj = round(max(1.0, (intercept + slope * i) * 1.03 * avg_seasonal), 2)
        
        # Scenario 2: Active Decarbonization
        cumulative_reduction = min(target_reduction_pct / 100.0, reduction_rate_per_month * (i - 12))
        decarb_proj = round(max(0.5, bau_proj * (1.0 - cumulative_reduction)), 2)
        
        records.append({
            "Month_Label": month_label,
            "Future_Step": i - 12,
            "BAU_Forecast": bau_proj,
            "Decarbonization_Pathway": decarb_proj,
            "Monthly_CO2_Avoided": round(bau_proj - decarb_proj, 2)
        })
        
    return pd.DataFrame(records)

def get_emission_intensity_matrix(monthly_df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepares a clean 2D intensity grid (Months as index, Pillars as columns)
    specifically structured for the Plotly Heatmap.
    """
    pillars = [c for c in monthly_df.columns if c not in ["Month", "Month_Num", "Total_Monthly_CO2"]]
    heatmap_df = monthly_df.set_index("Month")[pillars]
    return heatmap_df

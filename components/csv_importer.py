"""
CSV & Excel Past Operational Data Ingestion Utility.
Allows new and existing users to import historical operational logs,
shift records, or annual facility utility baselines to immediately
populate and drive the Executive Dashboard emissions analysis.
"""

import io
import re
import pandas as pd
from datetime import date, datetime, timedelta
from typing import Dict, Any, Tuple, Optional, List

from database.db_manager import (
    save_activity_log,
    save_emissions_assessment,
    get_latest_emissions,
    get_user_profile,
    sync_activity_logs_to_dashboard,
    log_audit,
)
from components.calculations import calculate_detailed_emissions, get_statutory_carbon_quota, safe_float

COLUMN_SYNONYMS = {
    "electricity_kwh": [
        "electricity_kwh", "electricity", "kwh", "power_kwh", "power", "elec_kwh",
        "electric_units", "grid_electricity_kwh", "electricity_consumption",
        "electricity_units", "grid_electricity", "power_consumption"
    ],
    "renewable_pct": [
        "renewable_pct", "renewable", "renewable_energy_pct", "solar_pct",
        "green_energy_pct", "green_power_pct", "renewable_share"
    ],
    "diesel_liters": [
        "diesel_liters", "diesel_l", "diesel", "diesel_fuel_liters", "diesel_fuel",
        "diesel_litres", "hsd"
    ],
    "petrol_liters": [
        "petrol_liters", "petrol_l", "petrol", "gasoline_liters", "gasoline",
        "motor_gasoline", "petrol_litres", "gasoline_l", "motor_spirit"
    ],
    "gas_m3": [
        "gas_m3", "gas", "natural_gas_m3", "natural_gas", "png_m3", "cng_m3",
        "gas_consumption_m3", "natural_gas_consumption", "piped_natural_gas"
    ],
    "truck_km": [
        "truck_km", "freight_km", "transport_km", "haulage_km", "logistics_km",
        "truck_distance", "truck_distance_km", "truck", "freight", "truck_freight",
        "transport_mileage", "freight_distance"
    ],
    "car_km": [
        "car_km", "passenger_car_km", "fleet_car_km", "company_car_km", "cars", "car_distance"
    ],
    "commute_km": [
        "commute_km", "commuting_km", "employee_commute_km", "staff_commute_km",
        "commute_distance", "commute", "employee_commute"
    ],
    "delivery_vehicles": [
        "delivery_vehicles", "fleet_vehicles", "vehicles_count", "vehicles",
        "fleet_size", "delivery_fleet", "vans", "delivery_vans"
    ],
    "organic_waste_kg": [
        "organic_waste_kg", "organic_waste", "food_waste_kg", "food_waste",
        "compost_kg", "bio_waste_kg", "organic", "wet_waste", "canteen_waste"
    ],
    "plastic_waste_kg": [
        "plastic_waste_kg", "plastic_waste", "plastics_kg", "plastics",
        "packaging_waste_kg", "plastic", "packaging_waste"
    ],
    "metal_waste_kg": [
        "metal_waste_kg", "metal_waste", "scrap_metal_kg", "metal",
        "scrap_iron_kg", "scrap_metal", "iron_scrap"
    ],
    "paper_waste_kg": [
        "paper_waste_kg", "paper_waste", "cardboard_waste_kg", "cardboard_waste",
        "paper_kg", "cardboard_kg", "paper", "cardboard"
    ],
    "hazardous_waste_kg": [
        "hazardous_waste_kg", "hazardous_waste", "chemical_waste_kg", "hazmat_kg",
        "toxic_waste", "e_waste_kg", "hazardous", "hazmat", "chemical_waste", "e_waste"
    ],
    "water_m3": [
        "water_m3", "water_consumption", "water_usage", "freshwater_m3", "water",
        "water_m3_yr", "freshwater", "water_supply"
    ],
    "wastewater_m3": [
        "wastewater_m3", "wastewater", "effluent_m3", "sewage_m3",
        "wastewater_generated", "effluent", "sewage"
    ],
    "raw_material_tonnes": [
        "raw_material_tonnes", "raw_materials", "raw_material", "materials_tonnes",
        "input_materials_t", "raw_materials_tonnes"
    ],
    "production_units": [
        "production_units", "units_produced", "output_units", "production_output",
        "units", "goods_produced", "production", "finished_goods"
    ],
    "machine_hours": [
        "machine_hours", "operating_hours", "machine_running_hours", "run_hours", "machine_runtime"
    ],
    "total_credits": [
        "total_credits", "carbon_credits", "quota_credits", "credits_allocated",
        "statutory_credits", "credits", "carbon_quota"
    ],
    "credit_price": [
        "credit_price", "carbon_price", "price_per_credit", "benchmark_credit_price", "carbon_credit_price"
    ],
    "log_date": [
        "log_date", "date", "period", "month", "shift_date", "timestamp", "day", "record_date", "time"
    ],
    "frequency": [
        "frequency", "freq", "period_type", "type", "cadence"
    ],
    "notes": [
        "notes", "note", "remarks", "comment", "comments", "description", "shift_name", "shift"
    ],
}

def normalize_column_name(col: str) -> str:
    """
    Normalizes an arbitrary header string to lowercase standard identifier.
    Robustly handles units in parentheses (e.g. 'Electricity (kWh)' -> 'electricity_kwh'),
    superscript symbols (m³ -> m3), punctuation, and alternative naming conventions.
    """
    cleaned = str(col).lower().strip()
    cleaned = cleaned.replace("³", "3").replace("²", "2")
    cleaned = re.sub(r"[^a-z0-9]", " ", cleaned)
    cleaned = re.sub(r"\s+", "_", cleaned).strip("_")

    # 1. Exact match with standard or synonyms
    for standard_col, synonyms in COLUMN_SYNONYMS.items():
        if cleaned == standard_col or cleaned in synonyms:
            return standard_col

    # 2. Priority word/phrase containment (matches specific items before general ones)
    priority_order = [
        "wastewater_m3", "hazardous_waste_kg", "organic_waste_kg",
        "plastic_waste_kg", "metal_waste_kg", "paper_waste_kg",
        "raw_material_tonnes", "production_units", "delivery_vehicles",
        "commute_km", "truck_km", "car_km", "renewable_pct",
        "electricity_kwh", "diesel_liters", "petrol_liters", "gas_m3",
        "water_m3", "credit_price", "total_credits", "machine_hours",
        "log_date", "frequency", "notes"
    ]
    for standard_col in priority_order:
        synonyms = COLUMN_SYNONYMS.get(standard_col, [])
        for syn in synonyms:
            if syn in cleaned or cleaned in syn:
                return standard_col

    return cleaned


def parse_date_string(date_val: Any, default_date: str) -> str:
    """Safely converts diverse date formats to ISO YYYY-MM-DD string."""
    if date_val is None or pd.isna(date_val):
        return default_date
    date_str = str(date_val).strip()
    if not date_str or date_str.lower() in ["none", "nan", "nat", ""]:
        return default_date
    try:
        dt = pd.to_datetime(date_str)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return default_date

def transform_transaction_ledger(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms a line-item transaction ledger (e.g. columns: emission_source, quantity, unit, date)
    into a structured periodic activity DataFrame grouped by month.
    """
    lower_cols = {str(c).lower().strip(): c for c in df.columns}
    source_col = None
    for cand in ["emission_source", "source", "activity", "item", "emission_item", "emission"]:
        if cand in lower_cols:
            source_col = lower_cols[cand]
            break

    qty_col = None
    for cand in ["quantity", "amount", "usage", "val", "value", "co2_emission_kg"]:
        if cand in lower_cols:
            qty_col = lower_cols[cand]
            break

    if not source_col or not qty_col:
        return df

    unit_col = next((lower_cols[c] for c in ["unit", "units", "uom"] if c in lower_cols), None)
    date_col = next((lower_cols[c] for c in ["date", "log_date", "timestamp", "period", "record_date"] if c in lower_cols), None)

    mapped_rows = []
    for _, row in df.iterrows():
        src = str(row.get(source_col, "")).lower().strip()
        cat = str(row.get("category", "")).lower().strip() if "category" in lower_cols else ""
        unit = str(row.get(unit_col, "")).lower().strip() if unit_col else ""
        qty = safe_float(row.get(qty_col), 0.0)
        d_val = str(row.get(date_col, "")) if date_col else "2025-01-01"

        try:
            m_key = pd.to_datetime(d_val).strftime("%Y-%m")
        except Exception:
            m_key = "2025-01"

        metric = None
        if "electric" in src or "power" in src or unit == "kwh" or "refrigeration" in src or "grid" in src:
            metric = "electricity_kwh"
        elif "diesel" in src or ("generator" in src and "l" in unit) or ("fuel" in src and ("litre" in unit or "l" in unit)):
            metric = "diesel_liters"
        elif "petrol" in src or "gasoline" in src:
            metric = "petrol_liters"
        elif "gas" in src or "boiler" in src or "png" in src or "cng" in src:
            metric = "gas_m3"
        elif "truck" in src or "freight" in src or "transport" in src:
            if "km" in unit:
                metric = "truck_km"
            else:
                metric = "diesel_liters"
        elif "plastic" in src or "packaging" in src:
            metric = "plastic_waste_kg"
        elif "organic" in src or "food" in src:
            metric = "organic_waste_kg"
        elif "metal" in src or "scrap" in src or "iron" in src:
            metric = "metal_waste_kg"
        elif "paper" in src or "cardboard" in src:
            metric = "paper_waste_kg"
        elif "hazard" in src or "solvent" in src or "chemical" in src or "toxic" in src:
            metric = "hazardous_waste_kg"
        elif "water" in src or "effluent" in src:
            metric = "water_m3"

        if metric and qty > 0:
            mapped_rows.append({"month": m_key, "metric": metric, "quantity": qty})

    if not mapped_rows:
        return df

    df_m = pd.DataFrame(mapped_rows)
    pivoted = df_m.pivot_table(index="month", columns="metric", values="quantity", aggfunc="sum").fillna(0.0).reset_index()
    pivoted["log_date"] = pivoted["month"] + "-15"
    pivoted["frequency"] = "monthly"
    pivoted["notes"] = "Aggregated monthly operational log from transaction ledger (" + pivoted["month"] + ")"
    return pivoted

def import_past_data_from_csv(

    file_or_df: Any,
    user_email: str,
    is_demo: bool = False
) -> Dict[str, Any]:
    """
    Imports historical operational data from CSV or Excel file or DataFrame.
    Supports both:
      1. Multi-row time-series activity logs (daily, weekly, or monthly records)
      2. Single-row / aggregated annual facility baseline parameters
    Saves records to SQLite, synchronizes with the dashboard engine,
    and returns a comprehensive ingestion summary.
    """
    email_clean = user_email.lower().strip()
    try:
        if hasattr(file_or_df, "seek"):
            try:
                file_or_df.seek(0)
            except Exception:
                pass
        if isinstance(file_or_df, pd.DataFrame):
            df = file_or_df.copy()
        elif hasattr(file_or_df, "name") and str(file_or_df.name).lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_or_df)
        elif hasattr(file_or_df, "read"):
            # Streamlit UploadedFile or file-like object
            try:
                df = pd.read_csv(file_or_df)
            except Exception:
                if hasattr(file_or_df, "seek"):
                    try:
                        file_or_df.seek(0)
                    except Exception:
                        pass
                df = pd.read_excel(file_or_df)
            if hasattr(file_or_df, "seek"):
                try:
                    file_or_df.seek(0)
                except Exception:
                    pass
        elif isinstance(file_or_df, str):
            if file_or_df.lower().endswith((".xlsx", ".xls")):
                df = pd.read_excel(file_or_df)
            else:
                df = pd.read_csv(file_or_df)
        else:
            return {
                "success": False,
                "error": "Unsupported file format. Please upload a .csv or .xlsx file."
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error parsing spreadsheet: {str(e)}"
        }


    if df.empty:
        return {
            "success": False,
            "error": "The uploaded spreadsheet is empty."
        }

    # Normalize column names
    col_mapping = {}
    for orig_col in df.columns:
        norm = normalize_column_name(orig_col)
        col_mapping[orig_col] = norm
    df = df.rename(columns=col_mapping)

    row_count = len(df)
    activity_metric_cols = [
        "diesel_liters", "petrol_liters", "gas_m3", "electricity_kwh",
        "organic_waste_kg", "plastic_waste_kg", "metal_waste_kg",
        "paper_waste_kg", "hazardous_waste_kg", "truck_km", "water_m3", "production_units"
    ]
    has_activity_cols = any(c in df.columns for c in activity_metric_cols)
    has_date_col = "log_date" in df.columns

    # Check if table is a line-item transaction ledger (e.g. emission_source & quantity)
    if not has_activity_cols:
        df_transformed = transform_transaction_ledger(df)
        if not df_transformed.empty and any(c in df_transformed.columns for c in activity_metric_cols):
            df = df_transformed
            row_count = len(df)
            has_activity_cols = True
            has_date_col = "log_date" in df.columns


    # Check user profile for defaults & statutory quotas
    user_prof = get_user_profile(email_clean) or {}
    industry = user_prof.get("industry", "Manufacturing Plant")
    comp_type = user_prof.get("company_type", "SME / Mid-Sized Business")
    employees = user_prof.get("employees", 50)
    quota_calc = get_statutory_carbon_quota(industry, comp_type, employees)

    # Branch 1: Multi-row Historical Activity Logs
    if row_count > 1 and (has_date_col or has_activity_cols):
        imported_count = 0
        today_dt = date.today()

        for idx, row in df.iterrows():
            # Derive default sequential past dates if missing or relative
            days_offset = (row_count - idx - 1) * (30 if row_count <= 14 else 7 if row_count <= 60 else 1)
            def_date = (today_dt - timedelta(days=days_offset)).strftime("%Y-%m-%d")
            
            raw_date = row.get("log_date")
            log_date = parse_date_string(raw_date, def_date)

            # Frequency detection
            raw_freq = str(row.get("frequency", "")).lower().strip()
            if raw_freq in ["daily", "weekly", "monthly"]:
                freq = raw_freq
            elif row_count <= 14:
                freq = "monthly"
            elif row_count <= 60:
                freq = "weekly"
            else:
                freq = "daily"

            period_label = str(row.get("notes") or f"Historical Ingest {log_date}")

            log_payload = {
                "log_date": log_date,
                "frequency": freq,
                "period_label": period_label,
                "diesel_liters": safe_float(row.get("diesel_liters"), 0.0),
                "petrol_liters": safe_float(row.get("petrol_liters"), 0.0),
                "gas_m3": safe_float(row.get("gas_m3"), 0.0),
                "electricity_kwh": safe_float(row.get("electricity_kwh"), 0.0),
                "organic_waste_kg": safe_float(row.get("organic_waste_kg"), 0.0),
                "plastic_waste_kg": safe_float(row.get("plastic_waste_kg"), 0.0),
                "metal_waste_kg": safe_float(row.get("metal_waste_kg"), 0.0),
                "paper_waste_kg": safe_float(row.get("paper_waste_kg"), 0.0),
                "hazardous_waste_kg": safe_float(row.get("hazardous_waste_kg"), 0.0),
                "truck_km": safe_float(row.get("truck_km"), 0.0),
                "water_m3": safe_float(row.get("water_m3"), 0.0),
                "production_units": safe_float(row.get("production_units"), 0.0),
                "notes": str(row.get("notes", "Imported from historical CSV")),
            }

            save_activity_log(email_clean, log_payload, is_demo=is_demo)
            imported_count += 1

        # Synchronize all newly ingested logs into the executive assessment
        synced_res = sync_activity_logs_to_dashboard(email_clean, is_demo=is_demo)
        
        # Update Streamlit session state if active
        try:
            import streamlit as st
            if synced_res:
                st.session_state["emissions_results"] = synced_res
                if "raw_inputs" in synced_res and synced_res["raw_inputs"]:
                    st.session_state["form_inputs"] = synced_res["raw_inputs"]
            st.session_state["dash_data_signature"] = None
            st.session_state.pop("data_editor_component", None)
        except Exception:
            pass


        log_audit(
            email_clean, "CSV_PAST_DATA_IMPORT", "activity_logs", "0",
            f"Successfully imported {imported_count} historical operational logs",
            is_demo=1 if is_demo else 0
        )

        total_co2 = synced_res.get("total_co2", 0.0) if synced_res else 0.0
        return {
            "success": True,
            "type": "activity_logs",
            "rows_imported": imported_count,
            "total_co2": total_co2,
            "message": f"Successfully imported {imported_count} historical records! Calculated run-rate: {total_co2:,.1f} tonnes CO₂e/yr."
        }

    # Branch 2: Single-Row / Facility Baseline Annual Summary
    first_row = df.iloc[0].to_dict()
    latest = get_latest_emissions(email_clean) or {}
    new_inputs = dict(latest) if latest else {}

    new_inputs["business_name"] = user_prof.get("company_name", new_inputs.get("business_name", "Enterprise Facility"))
    new_inputs["industry"] = industry
    new_inputs["company_type"] = comp_type
    new_inputs["employees"] = employees
    new_inputs["country"] = user_prof.get("country", new_inputs.get("country", "India"))
    new_inputs["state"] = user_prof.get("state", new_inputs.get("state", "Maharashtra"))

    # Map all numeric parameters with safe parsing
    new_inputs["electricity_kwh"] = safe_float(first_row.get("electricity_kwh"), new_inputs.get("electricity_kwh", 0.0))
    new_inputs["renewable_pct"] = safe_float(first_row.get("renewable_pct"), new_inputs.get("renewable_pct", 0.0))
    new_inputs["diesel_liters"] = safe_float(first_row.get("diesel_liters"), new_inputs.get("diesel_liters", 0.0))
    new_inputs["petrol_liters"] = safe_float(first_row.get("petrol_liters"), new_inputs.get("petrol_liters", 0.0))
    new_inputs["gas_m3"] = safe_float(first_row.get("gas_m3"), new_inputs.get("gas_m3", 0.0))
    new_inputs["truck_km"] = safe_float(first_row.get("truck_km"), new_inputs.get("truck_km", 0.0))
    new_inputs["car_km"] = safe_float(first_row.get("car_km"), new_inputs.get("car_km", 0.0))
    new_inputs["commute_km"] = safe_float(first_row.get("commute_km"), new_inputs.get("commute_km", 0.0))
    new_inputs["delivery_vehicles"] = int(safe_float(first_row.get("delivery_vehicles"), new_inputs.get("delivery_vehicles", 0)))
    new_inputs["organic_waste_kg"] = safe_float(first_row.get("organic_waste_kg"), new_inputs.get("organic_waste_kg", 0.0))
    new_inputs["plastic_waste_kg"] = safe_float(first_row.get("plastic_waste_kg"), new_inputs.get("plastic_waste_kg", 0.0))
    new_inputs["metal_waste_kg"] = safe_float(first_row.get("metal_waste_kg"), new_inputs.get("metal_waste_kg", 0.0))
    new_inputs["paper_waste_kg"] = safe_float(first_row.get("paper_waste_kg"), new_inputs.get("paper_waste_kg", 0.0))
    new_inputs["hazardous_waste_kg"] = safe_float(first_row.get("hazardous_waste_kg"), new_inputs.get("hazardous_waste_kg", 0.0))
    new_inputs["water_m3"] = safe_float(first_row.get("water_m3"), new_inputs.get("water_m3", 0.0))
    new_inputs["wastewater_m3"] = safe_float(first_row.get("wastewater_m3"), new_inputs.get("wastewater_m3", 0.0))
    new_inputs["raw_material_tonnes"] = safe_float(first_row.get("raw_material_tonnes"), new_inputs.get("raw_material_tonnes", 0.0))
    new_inputs["production_units"] = safe_float(first_row.get("production_units"), new_inputs.get("production_units", 0.0))
    new_inputs["machine_hours"] = safe_float(first_row.get("machine_hours"), new_inputs.get("machine_hours", 0.0))
    new_inputs["total_credits"] = safe_float(first_row.get("total_credits"), quota_calc["quota_credits"])
    new_inputs["credit_price"] = safe_float(first_row.get("credit_price"), quota_calc["benchmark_price"])

    res = calculate_detailed_emissions(new_inputs)
    new_inputs["total_co2"] = res["total_co2"]
    new_inputs["total_cost"] = res["total_cost"]
    new_inputs["sustainability_score"] = res["sustainability_score"]

    save_emissions_assessment(email_clean, new_inputs, is_demo=1 if is_demo else 0)

    try:
        import streamlit as st
        st.session_state["form_inputs"] = new_inputs
        st.session_state["emissions_results"] = res
        st.session_state["dash_data_signature"] = None
        st.session_state.pop("data_editor_component", None)
    except Exception:
        pass


    log_audit(
        email_clean, "CSV_BASELINE_IMPORT", "emissions_data", "0",
        f"Imported baseline parameters, calculated {res['total_co2']} t CO2",
        is_demo=1 if is_demo else 0
    )

    return {
        "success": True,
        "type": "baseline",
        "rows_imported": 1,
        "total_co2": res["total_co2"],
        "message": f"Successfully imported facility baseline! Total Footprint: {res['total_co2']:,.1f} tonnes CO₂e/yr."
    }

def generate_sample_past_data_csv(industry: str = "Manufacturing Plant") -> str:
    """
    Generates a realistic 12-month historical operational activity CSV string
    with authentic seasonal variations tailored to the enterprise sector.
    """
    today_dt = date.today()
    rows = []
    
    # Scale coefficients by industry
    is_heavy = "heavy" in industry.lower() or "metal" in industry.lower()
    is_retail = "retail" in industry.lower() or "cafe" in industry.lower()
    scale = 2.2 if is_heavy else (0.25 if is_retail else 1.0)

    month_factors = [1.08, 1.05, 1.02, 0.98, 0.94, 0.92, 0.96, 0.99, 1.03, 1.07, 1.10, 1.12]

    for idx in range(12):
        month_idx = 11 - idx
        # Past 12 months dating backward
        past_date = (today_dt.replace(day=1) - timedelta(days=30 * month_idx)).replace(day=15)
        date_str = past_date.strftime("%Y-%m-%d")
        factor = month_factors[past_date.month - 1] * scale

        rows.append({
            "date": date_str,
            "frequency": "monthly",
            "electricity_kwh": round(28000 * factor, 1),
            "diesel_liters": round(950 * factor, 1),
            "petrol_liters": round(320 * factor, 1),
            "gas_m3": round(2400 * factor, 1),
            "truck_km": round(4200 * factor, 1),
            "organic_waste_kg": round(1800 * factor, 1),
            "plastic_waste_kg": round(1200 * factor, 1),
            "metal_waste_kg": round(650 * factor, 1),
            "paper_waste_kg": round(1100 * factor, 1),
            "hazardous_waste_kg": round(90 * factor, 1),
            "water_m3": round(480 * factor, 1),
            "production_units": round(12000 * factor, 0),
            "notes": f"Historical Shift Ledger - {past_date.strftime('%B %Y')}"
        })

    df_sample = pd.DataFrame(rows)
    return df_sample.to_csv(index=False)

def generate_blank_activity_csv_template() -> str:
    """Returns a clean empty CSV template for daily/weekly/monthly logs."""
    headers = [
        "date", "frequency", "electricity_kwh", "diesel_liters", "petrol_liters",
        "gas_m3", "truck_km", "organic_waste_kg", "plastic_waste_kg",
        "metal_waste_kg", "paper_waste_kg", "hazardous_waste_kg",
        "water_m3", "production_units", "notes"
    ]
    sample_rows = [
        {
            "date": "2025-01-15",
            "frequency": "monthly",
            "electricity_kwh": 25000.0,
            "diesel_liters": 850.0,
            "petrol_liters": 280.0,
            "gas_m3": 2100.0,
            "truck_km": 3800.0,
            "organic_waste_kg": 1600.0,
            "plastic_waste_kg": 1100.0,
            "metal_waste_kg": 500.0,
            "paper_waste_kg": 950.0,
            "hazardous_waste_kg": 75.0,
            "water_m3": 420.0,
            "production_units": 10500.0,
            "notes": "Jan 2025 Operational Log"
        }
    ]
    df = pd.DataFrame(sample_rows, columns=headers)
    return df.to_csv(index=False)

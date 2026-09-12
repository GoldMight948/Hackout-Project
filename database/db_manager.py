"""
Database management module for SQLite persistence.
Handles users, business profiles, emission assessments, audit logs, and carbon credit market transactions.
"""

import sqlite3
import hashlib
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "emissions_app.db")

def safe_float(val: Any, default: float = 0.0) -> float:
    """Safely converts a value to float, handling None, empty strings, NaN, and invalid types."""
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

def get_db_connection():
    """Returns a thread-safe connection to the SQLite database with Row factory."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    """Hashes a password with a deterministic SHA-256 salt."""
    salt = "sustainability_carbon_salt_2025"
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

def init_db():
    """Initializes schema, tables, and demo migrations if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            company_name TEXT NOT NULL,
            owner_name TEXT NOT NULL,
            role TEXT DEFAULT 'Admin',
            company_type TEXT,
            industry TEXT,
            employees INTEGER DEFAULT 25,
            annual_revenue REAL DEFAULT 0.0,
            country TEXT DEFAULT 'United States',
            state TEXT DEFAULT 'California',
            location TEXT DEFAULT 'Plant #1',
            is_demo INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Safe migration for existing users table: check if is_demo exists
    cursor.execute("PRAGMA table_info(users)")
    user_cols = [row[1] for row in cursor.fetchall()]
    if "is_demo" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN is_demo INTEGER DEFAULT 0")

    # 2. Emissions Data Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emissions_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            period_year INTEGER DEFAULT 2025,
            electricity_kwh REAL DEFAULT 0,
            renewable_pct REAL DEFAULT 0,
            diesel_liters REAL DEFAULT 0,
            petrol_liters REAL DEFAULT 0,
            gas_m3 REAL DEFAULT 0,
            truck_km REAL DEFAULT 0,
            car_km REAL DEFAULT 0,
            commute_km REAL DEFAULT 0,
            delivery_vehicles INTEGER DEFAULT 0,
            organic_waste_kg REAL DEFAULT 0,
            plastic_waste_kg REAL DEFAULT 0,
            metal_waste_kg REAL DEFAULT 0,
            paper_waste_kg REAL DEFAULT 0,
            hazardous_waste_kg REAL DEFAULT 0,
            water_m3 REAL DEFAULT 0,
            wastewater_m3 REAL DEFAULT 0,
            raw_material_tonnes REAL DEFAULT 0,
            production_units REAL DEFAULT 0,
            machine_hours REAL DEFAULT 0,
            total_credits REAL DEFAULT 0,
            credit_price REAL DEFAULT 2905.0,
            current_balance REAL DEFAULT 0,
            total_co2 REAL DEFAULT 0,
            total_cost REAL DEFAULT 0,
            sustainability_score REAL DEFAULT 50,
            is_demo INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_email) REFERENCES users(email)
        )
    """)

    # Safe migration for emissions_data: check if is_demo exists
    cursor.execute("PRAGMA table_info(emissions_data)")
    em_cols = [row[1] for row in cursor.fetchall()]
    if "is_demo" not in em_cols:
        cursor.execute("ALTER TABLE emissions_data ADD COLUMN is_demo INTEGER DEFAULT 0")

    # 3. Activity Logs Table (Daily / Weekly operational emissions tracking)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            log_date TEXT NOT NULL,
            frequency TEXT NOT NULL DEFAULT 'daily',
            period_label TEXT,
            diesel_liters REAL DEFAULT 0,
            petrol_liters REAL DEFAULT 0,
            gas_m3 REAL DEFAULT 0,
            electricity_kwh REAL DEFAULT 0,
            organic_waste_kg REAL DEFAULT 0,
            plastic_waste_kg REAL DEFAULT 0,
            metal_waste_kg REAL DEFAULT 0,
            paper_waste_kg REAL DEFAULT 0,
            hazardous_waste_kg REAL DEFAULT 0,
            truck_km REAL DEFAULT 0,
            water_m3 REAL DEFAULT 0,
            production_units REAL DEFAULT 0,
            calculated_fuel_co2 REAL DEFAULT 0,
            calculated_waste_co2 REAL DEFAULT 0,
            calculated_electricity_co2 REAL DEFAULT 0,
            calculated_transport_co2 REAL DEFAULT 0,
            calculated_total_co2 REAL DEFAULT 0,
            notes TEXT,
            is_demo INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_email) REFERENCES users(email)
        )
    """)

    # 4. Audit Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            action TEXT NOT NULL,
            field_changed TEXT,
            old_value TEXT,
            new_value TEXT,
            is_demo INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("PRAGMA table_info(audit_logs)")
    audit_cols = [row[1] for row in cursor.fetchall()]
    if "is_demo" not in audit_cols:
        cursor.execute("ALTER TABLE audit_logs ADD COLUMN is_demo INTEGER DEFAULT 0")

    # 5. Carbon Marketplace Transactions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            tx_type TEXT NOT NULL,
            credits REAL NOT NULL,
            price_per_credit REAL NOT NULL,
            total_amount REAL NOT NULL,
            notes TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 6. Team Suggestions (preserved for collaboration)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS community_suggestions (
            id TEXT PRIMARY KEY,
            user_email TEXT,
            author TEXT,
            company TEXT,
            category TEXT,
            title TEXT,
            description TEXT,
            votes INTEGER DEFAULT 0,
            date TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    # Seed default demo users if users table is empty or ensure demo flags are set
    demo_emails = [
        "alex@greenbite.com",
        "sarah@ecotrend.com",
        "marcus@swiftroute.com",
        "david@apexmanufacturing.com"
    ]

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        demo_accounts = [
            (
                "alex@greenbite.com",
                hash_password("greenbite123"),
                "GreenBite Organics",
                "Alex Morgan",
                "Admin",
                "Mid-Sized Enterprise",
                "Food Processing",
                65,
                4200000.0,
                "United States",
                "Oregon",
                "Portland Bakery Facility",
                1
            ),
            (
                "sarah@ecotrend.com",
                hash_password("ecotrend123"),
                "EcoTrend Boutique & Retail",
                "Sarah Chen",
                "Admin",
                "SME Retailer",
                "Retail Store",
                18,
                1850000.0,
                "United States",
                "California",
                "San Francisco Flagship",
                1
            ),
            (
                "marcus@swiftroute.com",
                hash_password("swift123"),
                "SwiftRoute Logistics Corp",
                "Marcus Vance",
                "Admin",
                "Logistics Fleet",
                "Logistics Company",
                85,
                8900000.0,
                "United States",
                "Texas",
                "Dallas Distribution Hub",
                1
            ),
            (
                "david@apexmanufacturing.com",
                hash_password("apex123"),
                "Apex Precision Manufacturing",
                "David Kovac",
                "Admin",
                "Heavy Manufacturing",
                "Manufacturing Plant",
                140,
                16500000.0,
                "United States",
                "Ohio",
                "Cleveland Plant #4",
                1
            )
        ]
        cursor.executemany("""
            INSERT INTO users (email, password_hash, company_name, owner_name, role, company_type, industry, employees, annual_revenue, country, state, location, is_demo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, demo_accounts)
        conn.commit()
    else:
        # Mark known demo accounts as is_demo = 1
        for d_email in demo_emails:
            cursor.execute("UPDATE users SET is_demo = 1 WHERE email = ?", (d_email,))
        conn.commit()

    conn.close()

    # Seed demo activity logs if not present
    seed_demo_activity_logs()

# Emission Factors for periodic activity logging (t CO2e per unit)
ACTIVITY_EMISSION_FACTORS = {
    "diesel": 0.00268,          # t / Liter
    "petrol": 0.00231,          # t / Liter
    "gas": 0.00203,             # t / m3
    "electricity": 0.00042,     # t / kWh
    "waste_organic": 0.00045,   # t / kg
    "waste_plastic": 0.00210,   # t / kg
    "waste_metal": 0.00180,     # t / kg
    "waste_paper": 0.00095,     # t / kg
    "waste_hazardous": 0.00320, # t / kg
    "truck": 0.00085            # t / km
}

DEMO_EMAILS = [
    "alex@greenbite.com",
    "sarah@ecotrend.com",
    "marcus@swiftroute.com",
    "david@apexmanufacturing.com"
]

def is_demo_user(email: str) -> bool:
    """Checks whether the user email belongs to a demo sandbox profile."""
    if not email:
        return False
    clean_email = email.lower().strip()
    if clean_email in DEMO_EMAILS:
        return True
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_demo FROM users WHERE email = ?", (clean_email,))
    row = cursor.fetchone()
    conn.close()
    if row and row["is_demo"]:
        return bool(row["is_demo"])
    return False

# User Management Functions
def register_user(
    email: str,
    password: str,
    company_name: str,
    owner_name: str,
    company_type: str = "SME",
    industry: str = "Manufacturing",
    employees: int = 25,
    annual_revenue: float = 0.0,
    country: str = "United States",
    state: str = "California",
    location: str = "Headquarters",
    role: str = "Admin",
    is_demo: int = 0
) -> bool:
    """Registers a new business user profile. Returns True if successful, False if email already exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        pw_hash = hash_password(password)
        cursor.execute("""
            INSERT INTO users (email, password_hash, company_name, owner_name, role, company_type, industry, employees, annual_revenue, country, state, location, is_demo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (email.lower().strip(), pw_hash, company_name.strip(), owner_name.strip(), role, company_type, industry, employees, annual_revenue, country, state, location, is_demo))
        conn.commit()

        # Log creation
        log_audit(email.lower().strip(), "CREATE_PROFILE", "User Account", "None", company_name, is_demo=is_demo)
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticates a user and returns user record dictionary if valid, None otherwise."""
    conn = get_db_connection()
    cursor = conn.cursor()
    pw_hash = hash_password(password)
    cursor.execute("""
        SELECT * FROM users WHERE email = ? AND password_hash = ?
    """, (email.lower().strip(), pw_hash))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_user_profile(email: str) -> Optional[Dict[str, Any]]:
    """Retrieves user profile details by email."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_user_profile(email: str, updates: Dict[str, Any]) -> bool:
    """Updates selected user profile fields in SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    fields = []
    values = []
    for k, v in updates.items():
        if k in ["company_name", "owner_name", "role", "company_type", "industry", "employees", "annual_revenue", "country", "state", "location"]:
            fields.append(f"{k} = ?")
            values.append(v)
    if not fields:
        conn.close()
        return False

    values.append(email.lower().strip())
    query = f"UPDATE users SET {', '.join(fields)} WHERE email = ?"
    cursor.execute(query, values)
    conn.commit()
    conn.close()

    log_audit(email, "UPDATE_PROFILE", "Profile Fields", "", json.dumps(updates))
    return True

# Emissions Assessments Persistence
def save_emissions_assessment(user_email: str, data: Dict[str, Any], is_demo: Optional[int] = None) -> int:
    """Saves complete emission inputs and calculated metrics for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if is_demo is None:
        is_demo = 1 if is_demo_user(user_email) else 0

    cursor.execute("""
        INSERT INTO emissions_data (
            user_email, period_year, electricity_kwh, renewable_pct, diesel_liters, petrol_liters, gas_m3,
            truck_km, car_km, commute_km, delivery_vehicles,
            organic_waste_kg, plastic_waste_kg, metal_waste_kg, paper_waste_kg, hazardous_waste_kg,
            water_m3, wastewater_m3, raw_material_tonnes, production_units, machine_hours,
            total_credits, credit_price, current_balance,
            total_co2, total_cost, sustainability_score, is_demo
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?, ?
        )
    """, (
        user_email.lower().strip(),
        int(safe_float(data.get("period_year"), 2025)),
        safe_float(data.get("electricity_kwh") if data.get("electricity_kwh") is not None else data.get("electricity"), 0.0),
        safe_float(data.get("renewable_pct"), 0.0),
        safe_float(data.get("diesel_liters"), 0.0),
        safe_float(data.get("petrol_liters"), 0.0),
        safe_float(data.get("gas_m3"), 0.0),
        safe_float(data.get("truck_km") if data.get("truck_km") is not None else data.get("transport"), 0.0),
        safe_float(data.get("car_km"), 0.0),
        safe_float(data.get("commute_km"), 0.0),
        int(safe_float(data.get("delivery_vehicles"), 0)),
        safe_float(data.get("organic_waste_kg"), 0.0),
        safe_float(data.get("plastic_waste_kg"), 0.0),
        safe_float(data.get("metal_waste_kg"), 0.0),
        safe_float(data.get("paper_waste_kg"), 0.0),
        safe_float(data.get("hazardous_waste_kg"), 0.0),
        safe_float(data.get("water_m3"), 0.0),
        safe_float(data.get("wastewater_m3"), 0.0),
        safe_float(data.get("raw_material_tonnes"), 0.0),
        safe_float(data.get("production_units"), 0.0),
        safe_float(data.get("machine_hours") if data.get("machine_hours") is not None else data.get("machine_running_hours"), 0.0),
        safe_float(data.get("total_credits"), 0.0),
        safe_float(data.get("credit_price"), 2905.0),
        safe_float(data.get("current_balance"), 0.0),
        safe_float(data.get("total_co2"), 0.0),
        safe_float(data.get("total_cost"), 0.0),
        safe_float(data.get("sustainability_score"), 50.0),
        int(is_demo)
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()

    log_audit(user_email, "SAVE_ASSESSMENT", "Emissions Record", "New", f"ID {record_id} Total {data.get('total_co2', 0)} t", is_demo=is_demo)
    return record_id

def get_latest_emissions(user_email: str) -> Optional[Dict[str, Any]]:
    """Fetches the most recent emission record for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM emissions_data WHERE user_email = ? ORDER BY id DESC LIMIT 1
    """, (user_email.lower().strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# Periodic Operational Activity Logs (Daily & Weekly)
def save_activity_log(user_email: str, log_data: Dict[str, Any], is_demo: Optional[bool] = None) -> int:
    """
    Saves a daily or weekly operational activity log (fuel, waste, electricity, transport, etc.)
    and automatically calculates component and total CO2 emissions.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    email_clean = user_email.lower().strip()
    if is_demo is None:
        is_demo = is_demo_user(email_clean)

    log_date = str(log_data.get("log_date", datetime.now().strftime("%Y-%m-%d")))
    frequency = str(log_data.get("frequency", "daily")).lower()
    period_label = str(log_data.get("period_label", log_date))

    diesel_l = max(0.0, float(log_data.get("diesel_liters", 0.0)))
    petrol_l = max(0.0, float(log_data.get("petrol_liters", 0.0)))
    gas_m3 = max(0.0, float(log_data.get("gas_m3", 0.0)))
    elec_kwh = max(0.0, float(log_data.get("electricity_kwh", 0.0)))

    org_waste = max(0.0, float(log_data.get("organic_waste_kg", 0.0)))
    plas_waste = max(0.0, float(log_data.get("plastic_waste_kg", 0.0)))
    met_waste = max(0.0, float(log_data.get("metal_waste_kg", 0.0)))
    pap_waste = max(0.0, float(log_data.get("paper_waste_kg", 0.0)))
    haz_waste = max(0.0, float(log_data.get("hazardous_waste_kg", 0.0)))

    truck_km = max(0.0, float(log_data.get("truck_km", 0.0)))
    water_m3 = max(0.0, float(log_data.get("water_m3", 0.0)))
    prod_units = max(0.0, float(log_data.get("production_units", 0.0)))
    notes = str(log_data.get("notes", ""))

    # Calculate Emission Components (t CO2e)
    fuel_co2 = round(
        (diesel_l * ACTIVITY_EMISSION_FACTORS["diesel"]) +
        (petrol_l * ACTIVITY_EMISSION_FACTORS["petrol"]) +
        (gas_m3 * ACTIVITY_EMISSION_FACTORS["gas"]), 4
    )
    waste_co2 = round(
        (org_waste * ACTIVITY_EMISSION_FACTORS["waste_organic"]) +
        (plas_waste * ACTIVITY_EMISSION_FACTORS["waste_plastic"]) +
        (met_waste * ACTIVITY_EMISSION_FACTORS["waste_metal"]) +
        (pap_waste * ACTIVITY_EMISSION_FACTORS["waste_paper"]) +
        (haz_waste * ACTIVITY_EMISSION_FACTORS["waste_hazardous"]), 4
    )
    elec_co2 = round(elec_kwh * ACTIVITY_EMISSION_FACTORS["electricity"], 4)
    trans_co2 = round(truck_km * ACTIVITY_EMISSION_FACTORS["truck"], 4)
    total_co2 = round(fuel_co2 + waste_co2 + elec_co2 + trans_co2, 4)

    cursor.execute("""
        INSERT INTO activity_logs (
            user_email, log_date, frequency, period_label,
            diesel_liters, petrol_liters, gas_m3, electricity_kwh,
            organic_waste_kg, plastic_waste_kg, metal_waste_kg, paper_waste_kg, hazardous_waste_kg,
            truck_km, water_m3, production_units,
            calculated_fuel_co2, calculated_waste_co2, calculated_electricity_co2, calculated_transport_co2, calculated_total_co2,
            notes, is_demo
        ) VALUES (
            ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?
        )
    """, (
        email_clean, log_date, frequency, period_label,
        diesel_l, petrol_l, gas_m3, elec_kwh,
        org_waste, plas_waste, met_waste, pap_waste, haz_waste,
        truck_km, water_m3, prod_units,
        fuel_co2, waste_co2, elec_co2, trans_co2, total_co2,
        notes, 1 if is_demo else 0
    ))
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()

    log_audit(email_clean, f"LOG_ACTIVITY_{frequency.upper()}", "Activity Log", "None", f"ID {log_id}: {total_co2} t CO2 on {log_date}", is_demo=1 if is_demo else 0)
    
    # Dynamically synchronize operational logs with executive assessment
    try:
        sync_activity_logs_to_dashboard(email_clean, is_demo=is_demo)
    except Exception:
        pass

    return log_id

def get_activity_logs(user_email: str, limit: int = 200, frequency: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves operational activity logs for a user sorted chronologically."""
    conn = get_db_connection()
    cursor = conn.cursor()
    email_clean = user_email.lower().strip()
    if frequency:
        cursor.execute("""
            SELECT * FROM activity_logs WHERE user_email = ? AND frequency = ? ORDER BY log_date DESC, id DESC LIMIT ?
        """, (email_clean, frequency.lower(), limit))
    else:
        cursor.execute("""
            SELECT * FROM activity_logs WHERE user_email = ? ORDER BY log_date DESC, id DESC LIMIT ?
        """, (email_clean, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_activity_log(log_id: int, user_email: str) -> bool:
    """Deletes an activity log entry and automatically updates the dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM activity_logs WHERE id = ? AND user_email = ?
    """, (log_id, user_email.lower().strip()))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    if deleted:
        log_audit(user_email, "DELETE_ACTIVITY_LOG", "Activity Log", str(log_id), "Deleted")
        try:
            sync_activity_logs_to_dashboard(user_email)
        except Exception:
            pass
    return deleted

def update_activity_log(log_id: int, user_email: str, updated_data: Dict[str, Any], is_demo: Optional[bool] = None) -> bool:
    """Updates an existing activity log entry, recalculates its emissions, and synchronizes the dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()
    email_clean = user_email.lower().strip()
    if is_demo is None:
        is_demo = is_demo_user(email_clean)

    diesel_l = max(0.0, float(updated_data.get("diesel_liters", 0.0)))
    petrol_l = max(0.0, float(updated_data.get("petrol_liters", 0.0)))
    gas_m3 = max(0.0, float(updated_data.get("gas_m3", 0.0)))
    elec_kwh = max(0.0, float(updated_data.get("electricity_kwh", 0.0)))
    waste_org = max(0.0, float(updated_data.get("organic_waste_kg", 0.0)))
    waste_plas = max(0.0, float(updated_data.get("plastic_waste_kg", 0.0)))
    waste_met = max(0.0, float(updated_data.get("metal_waste_kg", 0.0)))
    waste_pap = max(0.0, float(updated_data.get("paper_waste_kg", 0.0)))
    waste_haz = max(0.0, float(updated_data.get("hazardous_waste_kg", 0.0)))
    truck_km = max(0.0, float(updated_data.get("truck_km", 0.0)))
    water_m3 = max(0.0, float(updated_data.get("water_m3", 0.0)))
    prod_units = max(0.0, float(updated_data.get("production_units", 0.0)))

    fuel_co2 = round((diesel_l * ACTIVITY_EMISSION_FACTORS["diesel"]) + (petrol_l * ACTIVITY_EMISSION_FACTORS["petrol"]) + (gas_m3 * ACTIVITY_EMISSION_FACTORS["gas"]), 4)
    waste_co2 = round((waste_org * ACTIVITY_EMISSION_FACTORS["waste_organic"]) + (waste_plas * ACTIVITY_EMISSION_FACTORS["waste_plastic"]) + (waste_met * ACTIVITY_EMISSION_FACTORS["waste_metal"]) + (waste_pap * ACTIVITY_EMISSION_FACTORS["waste_paper"]) + (waste_haz * ACTIVITY_EMISSION_FACTORS["waste_hazardous"]), 4)
    elec_co2 = round(elec_kwh * ACTIVITY_EMISSION_FACTORS["electricity"], 4)
    trans_co2 = round(truck_km * ACTIVITY_EMISSION_FACTORS["truck"], 4)
    tot_co2 = round(fuel_co2 + waste_co2 + elec_co2 + trans_co2, 4)

    log_date = str(updated_data.get("log_date", datetime.now().strftime("%Y-%m-%d")))
    frequency = str(updated_data.get("frequency", "daily")).lower()
    period_label = str(updated_data.get("period_label", log_date))
    notes = str(updated_data.get("notes", ""))

    cursor.execute("""
        UPDATE activity_logs SET
            log_date = ?, frequency = ?, period_label = ?,
            diesel_liters = ?, petrol_liters = ?, gas_m3 = ?, electricity_kwh = ?,
            organic_waste_kg = ?, plastic_waste_kg = ?, metal_waste_kg = ?, paper_waste_kg = ?, hazardous_waste_kg = ?,
            truck_km = ?, water_m3 = ?, production_units = ?,
            calculated_fuel_co2 = ?, calculated_waste_co2 = ?, calculated_electricity_co2 = ?, calculated_transport_co2 = ?, calculated_total_co2 = ?,
            notes = ?
        WHERE id = ? AND user_email = ?
    """, (
        log_date, frequency, period_label,
        diesel_l, petrol_l, gas_m3, elec_kwh,
        waste_org, waste_plas, waste_met, waste_pap, waste_haz,
        truck_km, water_m3, prod_units,
        fuel_co2, waste_co2, elec_co2, trans_co2, tot_co2,
        notes, log_id, email_clean
    ))
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if updated:
        log_audit(email_clean, "UPDATE_ACTIVITY_LOG", "Activity Log", str(log_id), f"Updated to {tot_co2} t CO2", is_demo=is_demo)
        try:
            sync_activity_logs_to_dashboard(email_clean, is_demo=is_demo)
        except Exception:
            pass
    return updated

def sync_activity_logs_to_dashboard(user_email: str, is_demo: Optional[bool] = None) -> Optional[Dict[str, Any]]:
    """
    Synchronizes operational daily and weekly activity logs with the enterprise emissions assessment.
    Combines both daily logs (annualized * 365) and weekly logs (annualized * 52) into an accurate
    operational run-rate. Computes research-backed statutory carbon credit quotas based on the user's
    industry sector, company type, and workforce. Persists the updated assessment in SQLite.
    """
    from components.calculations import calculate_detailed_emissions, get_statutory_carbon_quota
    email_clean = user_email.lower().strip()
    if is_demo is None:
        is_demo = is_demo_user(email_clean)

    logs = get_activity_logs(email_clean, limit=500)
    daily_logs = [l for l in logs if l.get("frequency") == "daily"]
    weekly_logs = [l for l in logs if l.get("frequency") == "weekly"]

    latest = get_latest_emissions(email_clean) or {}
    user_prof = get_user_profile(email_clean) or {}
    comp_name = user_prof.get("company_name", latest.get("business_name", "Enterprise Facility"))

    # Compute statutory quota for this business profile
    industry = user_prof.get("industry", latest.get("industry", "Manufacturing Plant"))
    comp_type = user_prof.get("company_type", "SME / Mid-Sized Business")
    employees = user_prof.get("employees", 50)
    quota_info = get_statutory_carbon_quota(industry, comp_type, employees)

    # Use statutory quota if latest is default or missing
    curr_credits = float(latest.get("total_credits", 0.0))
    if curr_credits in [0.0, 100.0, 250.0]:
        total_credits = quota_info["quota_credits"]
        credit_price = quota_info["benchmark_price"]
    else:
        total_credits = curr_credits
        credit_price = float(latest.get("credit_price", quota_info["benchmark_price"]))

    if not daily_logs and not weekly_logs:
        if not latest:
            return None
        updated_inputs = dict(latest)
        updated_inputs["business_name"] = comp_name
        updated_inputs["total_credits"] = total_credits
        updated_inputs["credit_price"] = credit_price
        res = calculate_detailed_emissions(updated_inputs)
        try:
            import streamlit as st
            st.session_state["form_inputs"] = updated_inputs
            st.session_state["emissions_results"] = res
        except Exception:
            pass
        return res

    d_count = len(daily_logs)
    w_count = len(weekly_logs)
    d_mult = (365.0 / d_count) if d_count > 0 else 0.0
    w_mult = (52.0 / w_count) if w_count > 0 else 0.0

    LOGGED_CORE_FIELDS = {
        "diesel_liters", "petrol_liters", "gas_m3", "electricity_kwh",
        "organic_waste_kg", "plastic_waste_kg", "metal_waste_kg",
        "paper_waste_kg", "hazardous_waste_kg", "truck_km"
    }

    def annualize_field(field: str, fallback_val: float = 0.0) -> float:
        d_val = sum(float(l.get(field, 0.0) or 0.0) for l in daily_logs) * d_mult
        w_val = sum(float(l.get(field, 0.0) or 0.0) for l in weekly_logs) * w_mult
        tot = d_val + w_val
        # If user actively logs operational shifts, their fuel/power/waste logs are the dynamic ground truth!
        if field in LOGGED_CORE_FIELDS:
            return round(tot, 1)
        if tot > 0:
            return round(tot, 1)
        return float(latest.get(field, fallback_val))

    updated_inputs = {
        "business_name": comp_name,
        "industry": industry,
        "period_year": int(latest.get("period_year", 2025)),
        "diesel_liters": annualize_field("diesel_liters"),
        "petrol_liters": annualize_field("petrol_liters"),
        "gas_m3": annualize_field("gas_m3"),
        "electricity_kwh": annualize_field("electricity_kwh"),
        "renewable_pct": float(latest.get("renewable_pct", 15.0)),
        "organic_waste_kg": annualize_field("organic_waste_kg"),
        "plastic_waste_kg": annualize_field("plastic_waste_kg"),
        "metal_waste_kg": annualize_field("metal_waste_kg"),
        "paper_waste_kg": annualize_field("paper_waste_kg"),
        "hazardous_waste_kg": annualize_field("hazardous_waste_kg"),
        "truck_km": annualize_field("truck_km"),
        "car_km": float(latest.get("car_km", 0.0)),
        "commute_km": float(latest.get("commute_km", 0.0)),
        "delivery_vehicles": int(latest.get("delivery_vehicles", 2)),
        "water_m3": annualize_field("water_m3", 1200.0),
        "wastewater_m3": safe_float(latest.get("wastewater_m3"), safe_float(latest.get("water_m3"), 1200.0) * 0.85),
        "raw_material_tonnes": safe_float(latest.get("raw_material_tonnes"), 150.0),
        "production_units": annualize_field("production_units", 25000.0),
        "machine_hours": safe_float(latest.get("machine_hours"), 2200.0),
        "total_credits": total_credits,
        "credit_price": credit_price
    }

    res = calculate_detailed_emissions(updated_inputs)
    updated_inputs["total_co2"] = res["total_co2"]
    updated_inputs["total_cost"] = res["total_cost"]
    updated_inputs["sustainability_score"] = res["sustainability_score"]

    # Persist synced assessment into SQLite emissions_data
    save_emissions_assessment(email_clean, updated_inputs, is_demo=1 if is_demo else 0)

    # Update Streamlit session state if running in web context
    try:
        import streamlit as st
        st.session_state["form_inputs"] = updated_inputs
        st.session_state["emissions_results"] = res
        st.session_state["last_activity_sync_time"] = datetime.now().strftime("%H:%M:%S")
        st.session_state["synced_activity_entries"] = len(logs)
    except Exception:
        pass

    return res


def get_aggregated_activity_summary(user_email: str, frequency: Optional[str] = None) -> Dict[str, Any]:
    """Computes aggregate totals across all logged periodic operational activities."""
    logs = get_activity_logs(user_email, limit=500, frequency=frequency)
    if not logs:
        return {
            "total_entries": 0,
            "total_co2": 0.0,
            "total_fuel_co2": 0.0,
            "total_waste_co2": 0.0,
            "total_electricity_co2": 0.0,
            "total_transport_co2": 0.0,
            "total_diesel_liters": 0.0,
            "total_petrol_liters": 0.0,
            "total_gas_m3": 0.0,
            "total_electricity_kwh": 0.0,
            "total_waste_kg": 0.0,
            "avg_daily_co2": 0.0,
            "date_range": "No logs recorded"
        }

    total_co2 = sum(l.get("calculated_total_co2", 0.0) for l in logs)
    total_fuel = sum(l.get("calculated_fuel_co2", 0.0) for l in logs)
    total_waste = sum(l.get("calculated_waste_co2", 0.0) for l in logs)
    total_elec = sum(l.get("calculated_electricity_co2", 0.0) for l in logs)
    total_trans = sum(l.get("calculated_transport_co2", 0.0) for l in logs)

    total_diesel = sum(l.get("diesel_liters", 0.0) for l in logs)
    total_petrol = sum(l.get("petrol_liters", 0.0) for l in logs)
    total_gas = sum(l.get("gas_m3", 0.0) for l in logs)
    total_elec_kwh = sum(l.get("electricity_kwh", 0.0) for l in logs)

    total_waste_kg = sum(
        l.get("organic_waste_kg", 0.0) +
        l.get("plastic_waste_kg", 0.0) +
        l.get("metal_waste_kg", 0.0) +
        l.get("paper_waste_kg", 0.0) +
        l.get("hazardous_waste_kg", 0.0)
        for l in logs
    )

    dates = sorted([l["log_date"] for l in logs if l.get("log_date")])
    date_range = f"{dates[0]} to {dates[-1]}" if dates else "N/A"
    avg_daily = round(total_co2 / len(logs), 2) if logs else 0.0

    return {
        "total_entries": len(logs),
        "total_co2": round(total_co2, 2),
        "total_fuel_co2": round(total_fuel, 2),
        "total_waste_co2": round(total_waste, 2),
        "total_electricity_co2": round(total_elec, 2),
        "total_transport_co2": round(total_trans, 2),
        "total_diesel_liters": round(total_diesel, 1),
        "total_petrol_liters": round(total_petrol, 1),
        "total_gas_m3": round(total_gas, 1),
        "total_electricity_kwh": round(total_elec_kwh, 1),
        "total_waste_kg": round(total_waste_kg, 1),
        "avg_daily_co2": avg_daily,
        "date_range": date_range
    }

def seed_demo_activity_logs():
    """Seeds realistic historical daily and weekly activity logs for demo accounts."""
    conn = get_db_connection()
    cursor = conn.cursor()

    demo_configs = [
        {
            "email": "alex@greenbite.com",
            "daily_base": {"diesel": 38.0, "petrol": 8.0, "gas": 125.0, "elec": 1050.0, "org_waste": 120.0, "plas_waste": 48.0, "pap_waste": 42.0, "truck": 180.0, "units": 1200.0},
            "variance": 0.12
        },
        {
            "email": "sarah@ecotrend.com",
            "daily_base": {"diesel": 6.0, "petrol": 12.0, "gas": 22.0, "elec": 380.0, "org_waste": 8.0, "plas_waste": 28.0, "pap_waste": 62.0, "truck": 48.0, "units": 175.0},
            "variance": 0.15
        },
        {
            "email": "marcus@swiftroute.com",
            "daily_base": {"diesel": 245.0, "petrol": 42.0, "gas": 32.0, "elec": 560.0, "org_waste": 14.0, "plas_waste": 58.0, "pap_waste": 85.0, "truck": 1280.0, "units": 1020.0},
            "variance": 0.10
        },
        {
            "email": "david@apexmanufacturing.com",
            "daily_base": {"diesel": 102.0, "petrol": 22.0, "gas": 235.0, "elec": 2480.0, "org_waste": 32.0, "plas_waste": 128.0, "met_waste": 92.0, "pap_waste": 50.0, "haz_waste": 22.0, "truck": 390.0, "units": 490.0},
            "variance": 0.14
        }
    ]

    from datetime import date, timedelta
    today = date.today()

    for config in demo_configs:
        cursor.execute("SELECT COUNT(*) FROM activity_logs WHERE user_email = ?", (config["email"],))
        count = cursor.fetchone()[0]
        if count == 0:
            b = config["daily_base"]
            var = config["variance"]
            # Seed 14 daily logs
            for i in range(14, 0, -1):
                d = today - timedelta(days=i)
                factor = 1.0 + ((i % 5) - 2) * var
                d_l = round(b.get("diesel", 0) * factor, 1)
                p_l = round(b.get("petrol", 0) * factor, 1)
                g_m3 = round(b.get("gas", 0) * factor, 1)
                e_kwh = round(b.get("elec", 0) * factor, 1)
                o_w = round(b.get("org_waste", 0) * factor, 1)
                p_w = round(b.get("plas_waste", 0) * factor, 1)
                m_w = round(b.get("met_waste", 0) * factor, 1)
                pa_w = round(b.get("pap_waste", 0) * factor, 1)
                h_w = round(b.get("haz_waste", 0) * factor, 1)
                tr_km = round(b.get("truck", 0) * factor, 1)
                u_cnt = round(b.get("units", 0) * factor, 0)

                fuel_co2 = round((d_l * 0.00268) + (p_l * 0.00231) + (g_m3 * 0.00203), 4)
                waste_co2 = round((o_w * 0.00045) + (p_w * 0.00210) + (m_w * 0.00180) + (pa_w * 0.00095) + (h_w * 0.00320), 4)
                elec_co2 = round(e_kwh * 0.00042, 4)
                trans_co2 = round(tr_km * 0.00085, 4)
                tot_co2 = round(fuel_co2 + waste_co2 + elec_co2 + trans_co2, 4)

                cursor.execute("""
                    INSERT INTO activity_logs (
                        user_email, log_date, frequency, period_label,
                        diesel_liters, petrol_liters, gas_m3, electricity_kwh,
                        organic_waste_kg, plastic_waste_kg, metal_waste_kg, paper_waste_kg, hazardous_waste_kg,
                        truck_km, water_m3, production_units,
                        calculated_fuel_co2, calculated_waste_co2, calculated_electricity_co2, calculated_transport_co2, calculated_total_co2,
                        notes, is_demo
                    ) VALUES (
                        ?, ?, 'daily', ?,
                        ?, ?, ?, ?,
                        ?, ?, ?, ?, ?,
                        ?, 0, ?,
                        ?, ?, ?, ?, ?,
                        'Daily operational shift record', 1
                    )
                """, (
                    config["email"], d.isoformat(), f"{d.strftime('%b %d, %Y')}",
                    d_l, p_l, g_m3, e_kwh,
                    o_w, p_w, m_w, pa_w, h_w,
                    tr_km, u_cnt,
                    fuel_co2, waste_co2, elec_co2, trans_co2, tot_co2
                ))

            # Also seed 4 weekly summary logs
            for w in range(4, 0, -1):
                w_end = today - timedelta(days=w * 7)
                factor = 7.0 * (1.0 + ((w % 3) - 1) * var)
                d_l = round(b.get("diesel", 0) * factor, 1)
                p_l = round(b.get("petrol", 0) * factor, 1)
                g_m3 = round(b.get("gas", 0) * factor, 1)
                e_kwh = round(b.get("elec", 0) * factor, 1)
                o_w = round(b.get("org_waste", 0) * factor, 1)
                p_w = round(b.get("plas_waste", 0) * factor, 1)
                m_w = round(b.get("met_waste", 0) * factor, 1)
                pa_w = round(b.get("pap_waste", 0) * factor, 1)
                h_w = round(b.get("haz_waste", 0) * factor, 1)
                tr_km = round(b.get("truck", 0) * factor, 1)
                u_cnt = round(b.get("units", 0) * factor, 0)

                fuel_co2 = round((d_l * 0.00268) + (p_l * 0.00231) + (g_m3 * 0.00203), 4)
                waste_co2 = round((o_w * 0.00045) + (p_w * 0.00210) + (m_w * 0.00180) + (pa_w * 0.00095) + (h_w * 0.00320), 4)
                elec_co2 = round(e_kwh * 0.00042, 4)
                trans_co2 = round(tr_km * 0.00085, 4)
                tot_co2 = round(fuel_co2 + waste_co2 + elec_co2 + trans_co2, 4)

                cursor.execute("""
                    INSERT INTO activity_logs (
                        user_email, log_date, frequency, period_label,
                        diesel_liters, petrol_liters, gas_m3, electricity_kwh,
                        organic_waste_kg, plastic_waste_kg, metal_waste_kg, paper_waste_kg, hazardous_waste_kg,
                        truck_km, water_m3, production_units,
                        calculated_fuel_co2, calculated_waste_co2, calculated_electricity_co2, calculated_transport_co2, calculated_total_co2,
                        notes, is_demo
                    ) VALUES (
                        ?, ?, 'weekly', ?,
                        ?, ?, ?, ?,
                        ?, ?, ?, ?, ?,
                        ?, 0, ?,
                        ?, ?, ?, ?, ?,
                        'Weekly consolidated aggregation', 1
                    )
                """, (
                    config["email"], w_end.isoformat(), f"Week {w_end.strftime('%U, %Y')}",
                    d_l, p_l, g_m3, e_kwh,
                    o_w, p_w, m_w, pa_w, h_w,
                    tr_km, u_cnt,
                    fuel_co2, waste_co2, elec_co2, trans_co2, tot_co2
                ))

    conn.commit()
    conn.close()

def reset_demo_account(email: str) -> bool:
    """Resets a demo account back to factory demo values without affecting any real user accounts."""
    if not is_demo_user(email):
        return False
    conn = get_db_connection()
    cursor = conn.cursor()
    # Delete activity logs for this demo user
    cursor.execute("DELETE FROM activity_logs WHERE user_email = ?", (email.lower().strip(),))
    # Delete custom assessments for this demo user
    cursor.execute("DELETE FROM emissions_data WHERE user_email = ?", (email.lower().strip(),))
    # Delete market transactions for this demo user
    cursor.execute("DELETE FROM market_transactions WHERE user_email = ?", (email.lower().strip(),))
    conn.commit()
    conn.close()

    # Re-seed demo activity logs
    seed_demo_activity_logs()
    try:
        sync_activity_logs_to_dashboard(email, is_demo=1)
    except Exception:
        pass
    return True

# Audit Logging
def log_audit(user_email: str, action: str, field_changed: str = "", old_value: str = "", new_value: str = "", is_demo: int = 0):
    """Records an audit log entry for compliance tracking."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_logs (user_email, action, field_changed, old_value, new_value, is_demo)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_email.lower().strip(), action, field_changed, str(old_value), str(new_value), int(is_demo)))
    conn.commit()
    conn.close()

def get_audit_logs(user_email: str, limit: int = 25) -> List[Dict[str, Any]]:
    """Retrieves recent audit logs for a business."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM audit_logs WHERE user_email = ? ORDER BY id DESC LIMIT ?
    """, (user_email.lower().strip(), limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Carbon Marketplace Transactions
def record_market_transaction(user_email: str, tx_type: str, credits: float, price_per_credit: float, notes: str = "") -> int:
    """Records a buy or sell transaction for carbon credits."""
    conn = get_db_connection()
    cursor = conn.cursor()
    total_val = round(credits * price_per_credit, 2)
    cursor.execute("""
        INSERT INTO market_transactions (user_email, tx_type, credits, price_per_credit, total_amount, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_email.lower().strip(), tx_type.upper(), credits, price_per_credit, total_val, notes))
    tx_id = cursor.lastrowid
    conn.commit()
    conn.close()

    log_audit(user_email, f"MARKET_{tx_type.upper()}", "Carbon Credits", "", f"{credits} credits @ ₹{price_per_credit} = ₹{total_val}")
    return tx_id

def get_market_transactions(user_email: str) -> List[Dict[str, Any]]:
    """Returns all carbon market transactions for the current user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM market_transactions WHERE user_email = ? ORDER BY id DESC
    """, (user_email.lower().strip(),))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Initialize tables on load
init_db()


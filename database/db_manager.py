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
    """Initializes schema and tables if they don't exist."""
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

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
            credit_price REAL DEFAULT 35.0,
            current_balance REAL DEFAULT 0,
            total_co2 REAL DEFAULT 0,
            total_cost REAL DEFAULT 0,
            sustainability_score REAL DEFAULT 50,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_email) REFERENCES users(email)
        )
    """)

    # 3. Audit Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            action TEXT NOT NULL,
            field_changed TEXT,
            old_value TEXT,
            new_value TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 4. Carbon Marketplace Transactions
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

    # 5. Team Suggestions (preserved for collaboration)
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

    # Seed default demo users if users table is empty
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
                "Portland Bakery Facility"
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
                "San Francisco Flagship"
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
                "Dallas Distribution Hub"
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
                "Cleveland Plant #4"
            )
        ]
        cursor.executemany("""
            INSERT INTO users (email, password_hash, company_name, owner_name, role, company_type, industry, employees, annual_revenue, country, state, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, demo_accounts)
        conn.commit()

    conn.close()

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
    role: str = "Admin"
) -> bool:
    """Registers a new business user profile. Returns True if successful, False if email already exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        pw_hash = hash_password(password)
        cursor.execute("""
            INSERT INTO users (email, password_hash, company_name, owner_name, role, company_type, industry, employees, annual_revenue, country, state, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (email.lower().strip(), pw_hash, company_name.strip(), owner_name.strip(), role, company_type, industry, employees, annual_revenue, country, state, location))
        conn.commit()

        # Log creation
        log_audit(email.lower().strip(), "CREATE_PROFILE", "User Account", "None", company_name)
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
def save_emissions_assessment(user_email: str, data: Dict[str, Any]) -> int:
    """Saves complete emission inputs and calculated metrics for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO emissions_data (
            user_email, period_year, electricity_kwh, renewable_pct, diesel_liters, petrol_liters, gas_m3,
            truck_km, car_km, commute_km, delivery_vehicles,
            organic_waste_kg, plastic_waste_kg, metal_waste_kg, paper_waste_kg, hazardous_waste_kg,
            water_m3, wastewater_m3, raw_material_tonnes, production_units, machine_hours,
            total_credits, credit_price, current_balance,
            total_co2, total_cost, sustainability_score
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?
        )
    """, (
        user_email.lower().strip(),
        int(data.get("period_year", 2025)),
        float(data.get("electricity_kwh", 0)),
        float(data.get("renewable_pct", 0)),
        float(data.get("diesel_liters", 0)),
        float(data.get("petrol_liters", 0)),
        float(data.get("gas_m3", 0)),
        float(data.get("truck_km", 0)),
        float(data.get("car_km", 0)),
        float(data.get("commute_km", 0)),
        int(data.get("delivery_vehicles", 0)),
        float(data.get("organic_waste_kg", 0)),
        float(data.get("plastic_waste_kg", 0)),
        float(data.get("metal_waste_kg", 0)),
        float(data.get("paper_waste_kg", 0)),
        float(data.get("hazardous_waste_kg", 0)),
        float(data.get("water_m3", 0)),
        float(data.get("wastewater_m3", 0)),
        float(data.get("raw_material_tonnes", 0)),
        float(data.get("production_units", 0)),
        float(data.get("machine_hours", 0)),
        float(data.get("total_credits", 0)),
        float(data.get("credit_price", 35.0)),
        float(data.get("current_balance", 0)),
        float(data.get("total_co2", 0)),
        float(data.get("total_cost", 0)),
        float(data.get("sustainability_score", 50))
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()

    log_audit(user_email, "SAVE_ASSESSMENT", "Emissions Record", "New", f"ID {record_id} Total {data.get('total_co2', 0)} t")
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

# Audit Logging
def log_audit(user_email: str, action: str, field_changed: str = "", old_value: str = "", new_value: str = ""):
    """Records an audit log entry for compliance tracking."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_logs (user_email, action, field_changed, old_value, new_value)
        VALUES (?, ?, ?, ?, ?)
    """, (user_email.lower().strip(), action, field_changed, str(old_value), str(new_value)))
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

    log_audit(user_email, f"MARKET_{tx_type.upper()}", "Carbon Credits", "", f"{credits} credits @ ${price_per_credit} = ${total_val}")
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

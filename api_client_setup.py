# API Client Setup and Authentication

"""
This module provides starter code for connecting to:
- SQLite (EHR/Patient DB)
- Mock Doctor Schedule API (using SQLite)
- Bing Web Search API
- MedlinePlus Connect API
"""

import sqlite3
import requests
import os

# --- SQLite Setup for EHR/Patient DB and Doctor Schedule ---
DB_PATH = "ehr_patient_db.sqlite"
SCHEDULE_DB_PATH = "doctor_schedule_db.sqlite"

def get_db_connection(db_path):
    conn = sqlite3.connect(db_path)
    return conn

# Example: Create tables if not exist
with get_db_connection(DB_PATH) as conn:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY,
        name TEXT,
        age INTEGER,
        condition TEXT
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS visits (
        id INTEGER PRIMARY KEY,
        patient_id INTEGER,
        date TEXT,
        diagnosis TEXT,
        treatment TEXT
    )
    """)

with get_db_connection(SCHEDULE_DB_PATH) as conn:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY,
        name TEXT,
        specialty TEXT
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY,
        doctor_id INTEGER,
        patient_id INTEGER,
        date TEXT,
        status TEXT
    )
    """)

# --- Bing Web Search API Setup ---
BING_API_KEY = os.getenv("BING_API_KEY")
BING_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"

def bing_search(query):
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    params = {"q": query, "count": 3}
    response = requests.get(BING_ENDPOINT, headers=headers, params=params)
    return response.json()

# --- MedlinePlus Connect API Setup ---
MEDLINEPLUS_ENDPOINT = "https://connect.medlineplus.gov/application"

def medlineplus_search(query):
    params = {"mainSearchCriteria.v.c": query, "informationRecipient.languageCode.c": "en"}
    response = requests.get(MEDLINEPLUS_ENDPOINT, params=params)
    return response.text

# --- Example Usage ---
if __name__ == "__main__":
    # Test DB connection
    with get_db_connection(DB_PATH) as conn:
        print("EHR DB tables:", conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall())
    # Test Bing API (requires valid API key)
    if BING_API_KEY:
        print("Bing Search Results:", bing_search("chronic kidney disease treatment"))
    else:
        print("Bing API key not set.")
    # Test MedlinePlus API
    print("MedlinePlus Search Results:", medlineplus_search("asthma"))

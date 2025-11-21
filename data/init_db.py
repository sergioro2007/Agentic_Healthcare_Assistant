"""
Initialize the SQLite database for patient EHR data.
Creates tables and populates with sample patient data.
"""
import sqlite3
import os
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "patients.db"

def init_database():
    """Create database schema and populate with sample data."""
    # Remove existing database if it exists
    if DB_PATH.exists():
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create patients table
    cursor.execute('''
        CREATE TABLE patients (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT,
            blood_type TEXT,
            allergies TEXT
        )
    ''')
    
    # Create conditions table
    cursor.execute('''
        CREATE TABLE conditions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            condition_name TEXT NOT NULL,
            diagnosed_date TEXT,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (patient_id) REFERENCES patients (id)
        )
    ''')
    
    # Create medications table
    cursor.execute('''
        CREATE TABLE medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            medication_name TEXT NOT NULL,
            dosage TEXT NOT NULL,
            frequency TEXT NOT NULL,
            started_date TEXT,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (patient_id) REFERENCES patients (id)
        )
    ''')
    
    # Create vitals table
    cursor.execute('''
        CREATE TABLE vitals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            recorded_date TEXT NOT NULL,
            blood_pressure TEXT,
            heart_rate INTEGER,
            temperature REAL,
            spo2 INTEGER,
            weight REAL,
            FOREIGN KEY (patient_id) REFERENCES patients (id)
        )
    ''')
    
    # Create visit history table
    cursor.execute('''
        CREATE TABLE visit_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            visit_date TEXT NOT NULL,
            reason TEXT NOT NULL,
            summary TEXT,
            provider TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients (id)
        )
    ''')
    
    # Insert sample patients
    patients = [
        ('P001', 'Sarah Johnson', 62, 'Female', 'A+', 'Penicillin'),
        ('P002', 'Michael Chen', 54, 'Male', 'O+', 'None'),
        ('P003', 'Emily Rodriguez', 38, 'Female', 'B-', 'Sulfa drugs'),
        ('12345', 'John Doe', 45, 'Male', 'AB+', 'None'),
    ]
    cursor.executemany('INSERT INTO patients VALUES (?, ?, ?, ?, ?, ?)', patients)
    
    # Insert conditions
    conditions = [
        ('P001', 'Hypertension', '2020-03-15', 'active'),
        ('P001', 'Type 2 Diabetes', '2018-07-22', 'active'),
        ('P001', 'Chronic Kidney Disease Stage 3', '2022-11-10', 'active'),
        ('P002', 'Asthma', '2010-05-01', 'active'),
        ('P002', 'Hyperlipidemia', '2019-08-30', 'active'),
        ('P003', 'Migraine', '2015-02-14', 'active'),
        ('P003', 'Anxiety Disorder', '2020-09-05', 'active'),
        ('12345', 'Hypertension', '2019-01-10', 'active'),
        ('12345', 'Type 2 Diabetes', '2019-01-10', 'active'),
    ]
    cursor.executemany('INSERT INTO conditions (patient_id, condition_name, diagnosed_date, status) VALUES (?, ?, ?, ?)', conditions)
    
    # Insert medications
    medications = [
        ('P001', 'Lisinopril', '10mg', 'Once daily', '2020-03-20', 'active'),
        ('P001', 'Metformin', '1000mg', 'Twice daily', '2018-07-25', 'active'),
        ('P001', 'Atorvastatin', '40mg', 'Once daily at bedtime', '2020-06-15', 'active'),
        ('P002', 'Albuterol', '90mcg', 'As needed', '2010-05-05', 'active'),
        ('P002', 'Rosuvastatin', '20mg', 'Once daily', '2019-09-01', 'active'),
        ('P003', 'Sumatriptan', '100mg', 'As needed for migraine', '2015-03-01', 'active'),
        ('P003', 'Sertraline', '50mg', 'Once daily', '2020-09-10', 'active'),
        ('12345', 'Lisinopril', '20mg', 'Once daily', '2019-01-15', 'active'),
        ('12345', 'Metformin', '500mg', 'Twice daily', '2019-01-15', 'active'),
    ]
    cursor.executemany('INSERT INTO medications (patient_id, medication_name, dosage, frequency, started_date, status) VALUES (?, ?, ?, ?, ?, ?)', medications)
    
    # Insert vitals
    vitals = [
        ('P001', '2025-10-28', '142/88', 76, 98.6, 97, 165.2),
        ('P001', '2025-09-15', '138/84', 72, 98.4, 98, 164.8),
        ('P002', '2025-10-25', '128/82', 68, 98.2, 99, 178.5),
        ('P002', '2025-09-20', '124/80', 70, 97.9, 98, 179.1),
        ('P003', '2025-10-20', '118/76', 74, 98.1, 99, 132.4),
        ('12345', '2025-10-15', '135/85', 78, 98.5, 96, 185.0),
    ]
    cursor.executemany('INSERT INTO vitals (patient_id, recorded_date, blood_pressure, heart_rate, temperature, spo2, weight) VALUES (?, ?, ?, ?, ?, ?, ?)', vitals)
    
    # Insert visit history
    visits = [
        ('P001', '2025-10-15', 'Diabetes follow-up', 'HbA1c 7.8%, BP elevated. Discussed medication adherence and dietary modifications.', 'Dr. Smith'),
        ('P001', '2025-09-01', 'Annual physical', 'Routine exam completed. Labs ordered. Patient reports good compliance with medications.', 'Dr. Smith'),
        ('P001', '2025-06-20', 'Kidney function check', 'eGFR stable at 55 mL/min/1.73m². Continue current management.', 'Dr. Johnson'),
        ('P002', '2025-10-20', 'Asthma check', 'Well controlled, no exacerbations in past 6 months. Peak flow normal.', 'Dr. Lee'),
        ('P002', '2025-08-15', 'Lipid panel review', 'LDL at target (85 mg/dL). Continue current statin dose.', 'Dr. Lee'),
        ('P003', '2025-10-10', 'Migraine management', 'Frequency decreased with current medication. Patient tolerating well.', 'Dr. Martinez'),
        ('P003', '2025-07-25', 'Mental health follow-up', 'Anxiety symptoms improved. Continue sertraline. Patient attending therapy regularly.', 'Dr. Martinez'),
        ('12345', '2025-10-01', 'Routine follow-up', 'Blood pressure and glucose levels stable.', 'Dr. Williams'),
        ('12345', '2023-05-20', 'Follow-up for hypertension', 'Blood pressure is high. Medication adjusted.', 'Dr. Williams'),
        ('12345', '2023-01-15', 'Annual check-up', 'Overall stable condition.', 'Dr. Williams'),
    ]
    cursor.executemany('INSERT INTO visit_history (patient_id, visit_date, reason, summary, provider) VALUES (?, ?, ?, ?, ?)', visits)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized successfully at {DB_PATH}")
    print(f"✅ Added {len(patients)} patients with complete medical records")

if __name__ == '__main__':
    init_database()

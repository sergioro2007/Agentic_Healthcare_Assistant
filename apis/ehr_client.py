"""
Client for interacting with the Electronic Health Record (EHR) system.

This client uses SQLite database to fetch patient data.
"""
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any, List

class EHRClient:
    def __init__(self, db_path: str = None):
        """
        Initializes the EHR client with the database path.
        
        Args:
            db_path: Path to the SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Default to data/patients.db relative to this file
            db_path = Path(__file__).parent.parent / "data" / "patients.db"
        self.db_path = str(db_path)

    def _get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)

    def get_patient_by_id(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a patient's complete record by their ID.
        
        Returns a dictionary with patient demographics, conditions, medications, and latest vitals.
        """
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get patient demographics
            cursor.execute('SELECT * FROM patients WHERE id = ?', (patient_id,))
            patient = cursor.fetchone()
            
            if not patient:
                conn.close()
                return None
            
            # Convert to dict
            patient_data = dict(patient)
            
            # Get conditions
            cursor.execute(
                'SELECT condition_name, diagnosed_date, status FROM conditions WHERE patient_id = ? AND status = "active"',
                (patient_id,)
            )
            conditions = [dict(row) for row in cursor.fetchall()]
            patient_data['conditions'] = [c['condition_name'] for c in conditions]
            
            # Get medications
            cursor.execute(
                'SELECT medication_name, dosage, frequency FROM medications WHERE patient_id = ? AND status = "active"',
                (patient_id,)
            )
            medications = cursor.fetchall()
            patient_data['medications'] = [f"{m['medication_name']} {m['dosage']} {m['frequency']}" for m in medications]
            
            # Get latest vitals
            cursor.execute(
                'SELECT * FROM vitals WHERE patient_id = ? ORDER BY recorded_date DESC LIMIT 1',
                (patient_id,)
            )
            latest_vitals = cursor.fetchone()
            if latest_vitals:
                patient_data['vitals'] = {
                    'blood_pressure': latest_vitals['blood_pressure'],
                    'heart_rate': latest_vitals['heart_rate'],
                    'temperature': latest_vitals['temperature'],
                    'spo2': latest_vitals['spo2'],
                    'weight': latest_vitals['weight'],
                    'recorded_date': latest_vitals['recorded_date']
                }
            
            conn.close()
            return patient_data
            
        except sqlite3.Error as e:
            print(f"Error fetching patient data: {e}")
            return None

    def get_patient_history(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a patient's medical visit history by their ID.
        
        Returns a dictionary with visit records.
        """
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT visit_date, reason, summary, provider FROM visit_history WHERE patient_id = ? ORDER BY visit_date DESC',
                (patient_id,)
            )
            visits = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            if visits:
                return {'visits': visits}
            return None
            
        except sqlite3.Error as e:
            print(f"Error fetching patient history: {e}")
            return None

if __name__ == '__main__':
    # Example usage
    client = EHRClient()
    patient_id = "P001"
    
    patient_data = client.get_patient_by_id(patient_id)
    if patient_data:
        print(f"Patient Data: {patient_data}")

    patient_history = client.get_patient_history(patient_id)
    if patient_history:
        print(f"Patient History: {patient_history}")

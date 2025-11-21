"""
Test suite for the EHR Client using SQLite.
"""
import unittest
import sqlite3
import os
import tempfile
from apis.ehr_client import EHRClient

class TestEHRClient(unittest.TestCase):

    def setUp(self):
        """Set up a temporary database for testing."""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Create tables
        self.cursor.execute('''
            CREATE TABLE patients (
                id TEXT PRIMARY KEY,
                name TEXT,
                age INTEGER,
                gender TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE conditions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT,
                condition_name TEXT,
                diagnosed_date TEXT,
                status TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE medications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT,
                medication_name TEXT,
                dosage TEXT,
                frequency TEXT,
                status TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE vitals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT,
                blood_pressure TEXT,
                heart_rate TEXT,
                temperature TEXT,
                spo2 TEXT,
                weight TEXT,
                recorded_date TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE visit_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT,
                visit_date TEXT,
                reason TEXT,
                summary TEXT,
                provider TEXT
            )
        ''')
        
        # Insert test data
        self.cursor.execute("INSERT INTO patients VALUES ('12345', 'John Doe', 45, 'Male')")
        self.cursor.execute("INSERT INTO conditions VALUES (1, '12345', 'Hypertension', '2020-01-01', 'active')")
        self.cursor.execute("INSERT INTO medications VALUES (1, '12345', 'Lisinopril', '10mg', 'daily', 'active')")
        self.cursor.execute("INSERT INTO vitals VALUES (1, '12345', '120/80', '72', '98.6', '98%', '70kg', '2023-01-01')")
        self.cursor.execute("INSERT INTO visit_history VALUES (1, '12345', '2023-01-01', 'Checkup', 'All good', 'Dr. Smith')")
        
        self.conn.commit()
        self.conn.close()
        
        self.client = EHRClient(db_path=self.db_path)

    def tearDown(self):
        """Clean up the temporary database."""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_get_patient_by_id_success(self):
        """Test fetching a patient by ID successfully."""
        patient_id = "12345"
        patient_data = self.client.get_patient_by_id(patient_id)
        self.assertIsNotNone(patient_data)
        self.assertEqual(patient_data['id'], patient_id)
        self.assertEqual(patient_data['name'], "John Doe")
        self.assertIn('Hypertension', patient_data['conditions'])
        self.assertIn('Lisinopril 10mg daily', patient_data['medications'])
        self.assertEqual(patient_data['vitals']['heart_rate'], '72')

    def test_get_patient_by_id_not_found(self):
        """Test fetching a patient that does not exist."""
        patient_id = "99999"
        patient_data = self.client.get_patient_by_id(patient_id)
        self.assertIsNone(patient_data)

    def test_get_patient_history_success(self):
        """Test fetching patient history successfully."""
        patient_id = "12345"
        history_data = self.client.get_patient_history(patient_id)
        self.assertIsNotNone(history_data)
        self.assertIn('visits', history_data)
        self.assertEqual(len(history_data['visits']), 1)
        self.assertEqual(history_data['visits'][0]['reason'], 'Checkup')

    def test_get_patient_history_not_found(self):
        """Test fetching history for a patient that does not exist."""
        patient_id = "99999"
        history_data = self.client.get_patient_history(patient_id)
        self.assertIsNone(history_data)

if __name__ == '__main__':
    unittest.main()

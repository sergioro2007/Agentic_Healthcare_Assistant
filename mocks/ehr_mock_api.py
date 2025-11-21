"""
A simple mock API server for the Electronic Health Record (EHR) system.

This server simulates the EHR API for development and testing purposes.
It provides endpoints to get patient data and medical history.
"""
from flask import Flask, jsonify

app = Flask(__name__)

# Mock database
mock_db = {
    "patients": {
        "12345": {
            "id": "12345",
            "name": "John Doe",
            "age": 45,
            "conditions": ["Hypertension", "Type 2 Diabetes"]
        },
        "P001": {
            "id": "P001",
            "name": "Sarah Johnson",
            "age": 62,
            "conditions": ["Hypertension", "Type 2 Diabetes", "Chronic Kidney Disease Stage 3"],
            "medications": ["Lisinopril 10mg daily", "Metformin 1000mg BID", "Atorvastatin 40mg daily"],
            "allergies": ["Penicillin"],
            "vitals": {
                "bp": "142/88 mmHg",
                "hr": "76 bpm",
                "temp": "98.6°F",
                "spo2": "97%"
            }
        },
        "P002": {
            "id": "P002",
            "name": "Michael Chen",
            "age": 54,
            "conditions": ["Asthma", "Hyperlipidemia"],
            "medications": ["Albuterol inhaler PRN", "Rosuvastatin 20mg daily"],
            "allergies": [],
            "vitals": {
                "bp": "128/82 mmHg",
                "hr": "68 bpm",
                "temp": "98.2°F",
                "spo2": "99%"
            }
        }
    },
    "history": {
        "12345": {
            "visits": [
                {"date": "2023-01-15", "reason": "Annual check-up", "summary": "Stable."},
                {"date": "2023-05-20", "reason": "Follow-up for hypertension", "summary": "Blood pressure is high."}
            ]
        },
        "P001": {
            "visits": [
                {"date": "2025-10-15", "reason": "Diabetes follow-up", "summary": "HbA1c 7.8%, BP elevated. Discussed medication adherence."},
                {"date": "2025-09-01", "reason": "Annual physical", "summary": "Routine exam, labs ordered."}
            ]
        },
        "P002": {
            "visits": [
                {"date": "2025-10-20", "reason": "Asthma check", "summary": "Well controlled, no exacerbations."},
                {"date": "2025-08-15", "reason": "Lipid panel review", "summary": "LDL at target."}
            ]
        }
    }
}

@app.route('/patients/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    patient = mock_db["patients"].get(patient_id)
    if patient:
        return jsonify(patient)
    return jsonify({"error": "Patient not found"}), 404

@app.route('/patients/<patient_id>/history', methods=['GET'])
def get_patient_history(patient_id):
    history = mock_db["history"].get(patient_id)
    if history:
        return jsonify(history)
    return jsonify({"error": "History not found"}), 404

if __name__ == '__main__':
    # Running on port 5001 to avoid conflict with other services
    app.run(debug=True, port=5001)

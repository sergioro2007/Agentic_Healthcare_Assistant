"""
Tests for the EHR Integration Agent.
"""
import os
import unittest
from unittest.mock import patch, MagicMock
from agents.ehr_agent import EHRAgent
from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage

class TestEHRAgent(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.test_api_key = "test_api_key"
        self.test_patient_data = {
            "id": "P123",
            "name": "John Doe",
            "age": 45,
            "gender": "Male",
            "conditions": ["Hypertension", "Type 2 Diabetes"],
            "medications": ["Metformin 500mg", "Lisinopril 10mg"],
            "vitals": {
                "blood_pressure": "130/85",
                "heart_rate": "72 bpm",
                "temperature": "98.6°F"
            },
            "allergies": ["Penicillin"]
        }
        
    def test_process_patient_summary(self):
        """Test processing a patient summary request."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.content = "Patient summary: 45-year-old male with hypertension and diabetes"
        
        # Setup mock LLM
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        
        # Setup mock EHR client
        mock_ehr_client = MagicMock()
        mock_ehr_client.get_patient_by_id.return_value = self.test_patient_data
        
        # Create agent with mocked dependencies
        with patch.dict(os.environ, {'GOOGLE_API_KEY': self.test_api_key}), \
             patch.object(BaseAgent, '_create_llm', return_value=mock_llm), \
             patch('agents.ehr_agent.EHRClient', return_value=mock_ehr_client):
            
            agent = EHRAgent()
            
            # Process a test query
            test_query = "P123"
            result = agent.process(test_query)
            
            # Verify the results
            self.assertEqual(result["patient_id"], "P123")
            self.assertEqual(result["query_type"], "summary")
            self.assertEqual(result["retrieval_status"], "success")
            self.assertIn("Patient summary", result["analysis"])
            
            # Verify EHR client was called
            mock_ehr_client.get_patient_by_id.assert_called_once_with("P123")
            
            # Verify LLM was called
            self.assertEqual(mock_llm.invoke.call_count, 1)
    
    def test_process_specific_query(self):
        """Test processing a specific patient query."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.content = "Analysis of diabetes management"
        
        # Setup mock LLM
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        
        # Setup mock EHR client
        mock_ehr_client = MagicMock()
        mock_ehr_client.get_patient_by_id.return_value = self.test_patient_data
        
        # Create agent with mocked dependencies
        with patch.dict(os.environ, {'GOOGLE_API_KEY': self.test_api_key}), \
             patch.object(BaseAgent, '_create_llm', return_value=mock_llm), \
             patch('agents.ehr_agent.EHRClient', return_value=mock_ehr_client):
            
            agent = EHRAgent()
            
            # Process a test query with specific question
            test_query = "P123|How is the patient's diabetes being managed?"
            result = agent.process(test_query)
            
            # Verify the results
            self.assertEqual(result["patient_id"], "P123")
            self.assertEqual(result["query_type"], "How is the patient's diabetes being managed?")
            self.assertEqual(result["retrieval_status"], "success")
            self.assertIn("diabetes", result["analysis"].lower())
            
            # Verify patient summary is included
            self.assertIn("patient_summary", result["formatted_response"])
            self.assertEqual(result["formatted_response"]["patient_summary"]["name"], "John Doe")
    
    def test_patient_not_found(self):
        """Test handling of patient not found error."""
        # Setup mock LLM
        mock_llm = MagicMock()
        
        # Setup mock EHR client to raise exception
        mock_ehr_client = MagicMock()
        mock_ehr_client.get_patient_by_id.side_effect = Exception("Patient not found")
        
        # Create agent with mocked dependencies
        with patch.dict(os.environ, {'GOOGLE_API_KEY': self.test_api_key}), \
             patch.object(BaseAgent, '_create_llm', return_value=mock_llm), \
             patch('agents.ehr_agent.EHRClient', return_value=mock_ehr_client):
            
            agent = EHRAgent()
            
            # Process a test query
            test_query = "P999"
            result = agent.process(test_query)
            
            # Verify error handling
            self.assertEqual(result["retrieval_status"], "error")
            self.assertIn("Patient not found", result["analysis"])
            
            # LLM should not be called when retrieval fails
            mock_llm.invoke.assert_not_called()
    
    def test_missing_api_key(self):
        """Test agent creation fails when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as cm:
                EHRAgent()
            
            self.assertEqual(
                str(cm.exception),
                "API key must be provided either as argument or GOOGLE_API_KEY environment variable"
            )
    
    def test_format_patient_data(self):
        """Test patient data formatting."""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': self.test_api_key}), \
             patch.object(BaseAgent, '_create_llm', return_value=MagicMock()):
            
            agent = EHRAgent()
            formatted = agent._format_patient_data(self.test_patient_data)
            
            # Verify key information is present
            self.assertIn("John Doe", formatted)
            self.assertIn("45", formatted)
            self.assertIn("Hypertension", formatted)
            self.assertIn("Type 2 Diabetes", formatted)
            self.assertIn("Metformin", formatted)
            self.assertIn("Penicillin", formatted)
    
    def test_llm_message_format(self):
        """Test that messages are properly formatted for LLM."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.content = "Test analysis"
        
        # Setup mock LLM
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        
        # Setup mock EHR client
        mock_ehr_client = MagicMock()
        mock_ehr_client.get_patient_by_id.return_value = self.test_patient_data
        
        # Create agent with mocked dependencies
        with patch.dict(os.environ, {'GOOGLE_API_KEY': self.test_api_key}), \
             patch.object(BaseAgent, '_create_llm', return_value=mock_llm), \
             patch('agents.ehr_agent.EHRClient', return_value=mock_ehr_client):
            
            agent = EHRAgent()
            agent.process("P123")
            
            # Verify LLM was called with list of messages
            self.assertEqual(mock_llm.invoke.call_count, 1)
            call_args = mock_llm.invoke.call_args[0][0]
            self.assertIsInstance(call_args, list)
            self.assertEqual(len(call_args), 1)
            self.assertIsInstance(call_args[0], HumanMessage)
            
            # Verify patient data is in the message
            message_content = call_args[0].content
            self.assertIn("John Doe", message_content)
            self.assertIn("Hypertension", message_content)

if __name__ == '__main__':
    unittest.main()

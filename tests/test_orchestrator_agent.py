"""
Tests for the Orchestrator Agent.
"""
import os
import unittest
from unittest.mock import patch, MagicMock
from agents.orchestrator_agent import OrchestratorAgent
from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage

class TestOrchestratorAgent(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.test_api_key = "test_api_key"
        
    def test_disease_info_routing(self):
        """Test routing to disease info agent."""
        # Setup mock LLM responses
        mock_classification = MagicMock()
        mock_classification.content = "disease_info"
        
        mock_synthesis = MagicMock()
        mock_synthesis.content = "Here's information about diabetes symptoms..."
        
        # Setup mock LLM to return different responses
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = [mock_classification, MagicMock(content="Test analysis"), mock_synthesis]
        
        # Create orchestrator with mocked LLM
        with patch.dict(os.environ, {'GOOGLE_API_KEY': self.test_api_key}), \
             patch.object(BaseAgent, '_create_llm', return_value=mock_llm):
            
            orchestrator = OrchestratorAgent()
            
            # Process a disease info query
            result = orchestrator.process("What are the symptoms of diabetes?")
            
            # Verify routing
            self.assertEqual(result["final_response"]["intent"], "disease_info")
            self.assertEqual(result["final_response"]["agent_used"], "disease_info")
            self.assertEqual(result["final_response"]["status"], "success")
    
    def test_patient_data_routing(self):
        """Test routing to EHR agent."""
        # Setup mock LLM responses
        mock_classification = MagicMock()
        mock_classification.content = "patient_data"
        
        mock_synthesis = MagicMock()
        mock_synthesis.content = "Patient information retrieved successfully..."
        
        # Setup mock EHR client
        mock_ehr_client = MagicMock()
        mock_ehr_client.get_patient.return_value = {
            "id": "P123",
            "name": "John Doe",
            "age": 45
        }
        
        # Setup mock LLM
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = [
            mock_classification,
            MagicMock(content="Patient analysis"),
            mock_synthesis
        ]
        
        # Create orchestrator with mocks
        with patch.dict(os.environ, {'GOOGLE_API_KEY': self.test_api_key}), \
             patch.object(BaseAgent, '_create_llm', return_value=mock_llm), \
             patch('agents.ehr_agent.EHRClient', return_value=mock_ehr_client):
            
            orchestrator = OrchestratorAgent()
            
            # Process a patient data query
            result = orchestrator.process("P123")
            
            # Verify routing
            self.assertEqual(result["final_response"]["intent"], "patient_data")
            self.assertEqual(result["final_response"]["agent_used"], "ehr")
            self.assertEqual(result["final_response"]["status"], "success")
    
    def test_appointment_routing(self):
        """Test routing to appointment agent."""
        # Setup mock LLM responses
        mock_classification = MagicMock()
        mock_classification.content = "appointment"
        
        mock_synthesis = MagicMock()
        mock_synthesis.content = "Appointment scheduled successfully..."
        
        # Setup mock LLM
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = [
            mock_classification,
            MagicMock(content="Appointment recommendation"),
            mock_synthesis
        ]
        
        # Create orchestrator with mocked LLM
        with patch.dict(os.environ, {'GOOGLE_API_KEY': self.test_api_key}), \
             patch.object(BaseAgent, '_create_llm', return_value=mock_llm):
            
            orchestrator = OrchestratorAgent()
            
            # Process an appointment query
            result = orchestrator.process("I need to schedule an appointment")
            
            # Verify routing
            self.assertEqual(result["final_response"]["intent"], "appointment")
            self.assertEqual(result["final_response"]["agent_used"], "appointment")
            self.assertEqual(result["final_response"]["status"], "success")
    
    def test_general_query_routing(self):
        """Test routing for general queries."""
        # Setup mock LLM responses
        mock_classification = MagicMock()
        mock_classification.content = "general"
        
        mock_synthesis = MagicMock()
        mock_synthesis.content = "I can help you with that..."
        
        # Setup mock LLM
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = [mock_classification, mock_synthesis]
        
        # Create orchestrator with mocked LLM
        with patch.dict(os.environ, {'GOOGLE_API_KEY': self.test_api_key}), \
             patch.object(BaseAgent, '_create_llm', return_value=mock_llm):
            
            orchestrator = OrchestratorAgent()
            
            # Process a general query
            result = orchestrator.process("Hello, how can you help me?")
            
            # Verify routing
            self.assertEqual(result["final_response"]["intent"], "general")
            self.assertEqual(result["final_response"]["agent_used"], "general")
            self.assertEqual(result["final_response"]["status"], "success")
    
    def test_invalid_intent_defaults_to_general(self):
        """Test that invalid intents default to general."""
        # Setup mock LLM to return invalid intent
        mock_classification = MagicMock()
        mock_classification.content = "invalid_intent"
        
        mock_synthesis = MagicMock()
        mock_synthesis.content = "Response"
        
        # Setup mock LLM
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = [mock_classification, mock_synthesis]
        
        # Create orchestrator with mocked LLM
        with patch.dict(os.environ, {'GOOGLE_API_KEY': self.test_api_key}), \
             patch.object(BaseAgent, '_create_llm', return_value=mock_llm):
            
            orchestrator = OrchestratorAgent()
            
            # Process query
            result = orchestrator.process("Some query")
            
            # Verify it defaults to general
            self.assertEqual(result["final_response"]["intent"], "general")
    
    def test_error_handling(self):
        """Test error handling when agent fails."""
        # Setup mock LLM for classification
        mock_classification = MagicMock()
        mock_classification.content = "disease_info"
        
        # Setup mock LLM that raises error for disease agent
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = [
            mock_classification,
            Exception("Agent processing error")
        ]
        
        # Create orchestrator with mocked LLM
        with patch.dict(os.environ, {'GOOGLE_API_KEY': self.test_api_key}), \
             patch.object(BaseAgent, '_create_llm', return_value=mock_llm):
            
            orchestrator = OrchestratorAgent()
            
            # Process query
            result = orchestrator.process("What are symptoms?")
            
            # Verify error handling
            self.assertEqual(result["final_response"]["status"], "error")
            self.assertIn("error_message", result or result["final_response"].get("message", ""))
    
    def test_missing_api_key(self):
        """Test orchestrator creation fails when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as cm:
                OrchestratorAgent()
            
            self.assertEqual(
                str(cm.exception),
                "API key must be provided either as argument or GOOGLE_API_KEY environment variable"
            )
    
    def test_synthesis_includes_query(self):
        """Test that synthesis includes original query."""
        # Setup mock responses
        mock_classification = MagicMock()
        mock_classification.content = "disease_info"
        
        mock_synthesis = MagicMock()
        mock_synthesis.content = "Synthesized response about diabetes"
        
        # Setup mock LLM
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = [
            mock_classification,
            MagicMock(content="Disease info"),
            mock_synthesis
        ]
        
        # Create orchestrator
        with patch.dict(os.environ, {'GOOGLE_API_KEY': self.test_api_key}), \
             patch.object(BaseAgent, '_create_llm', return_value=mock_llm):
            
            orchestrator = OrchestratorAgent()
            
            test_query = "What are diabetes symptoms?"
            result = orchestrator.process(test_query)
            
            # Verify original query is preserved
            self.assertEqual(result["original_query"], test_query)
            self.assertIn("synthesized_answer", result["final_response"])

if __name__ == '__main__':
    unittest.main()

"""
Tests for the Disease Information Retrieval Agent.
"""
import os
import unittest
from unittest.mock import patch, MagicMock
from agents.disease_info_agent import DiseaseInfoAgent
from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage

class TestDiseaseInfoAgent(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.test_api_key = "test_api_key"
        
    def test_process_query(self):
        """Test processing a disease information query."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.content = "Test analysis of disease"
        
        # Setup mock LLM
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        
        # Create agent with mocked LLM
        with patch.dict(os.environ, {'GOOGLE_API_KEY': self.test_api_key}), \
             patch.object(BaseAgent, '_create_llm', return_value=mock_llm):
            # Create agent with mocked environment
            agent = DiseaseInfoAgent()
            
            # Process a test query
            test_query = "What are the symptoms of diabetes?"
            result = agent.process(test_query)
            
            # Verify the results
            self.assertEqual(result["original_query"], test_query)
            self.assertEqual(result["analysis"], "Test analysis of disease")
            self.assertEqual(result["formatted_response"], "Test analysis of disease")
            
            # Verify LLM was called with correct prompt
            self.assertEqual(mock_llm.invoke.call_count, 1)
            call_args = mock_llm.invoke.call_args[0][0]
            self.assertIsInstance(call_args, list)
            self.assertEqual(len(call_args), 1)
            self.assertIsInstance(call_args[0], HumanMessage)
            self.assertIn(test_query, str(call_args[0].content))
        
    def test_missing_api_key(self):
        """Test agent creation fails when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as cm:
                DiseaseInfoAgent()
            
            self.assertEqual(
                str(cm.exception),
                "API key must be provided either as argument or GOOGLE_API_KEY environment variable"
            )

if __name__ == '__main__':
    unittest.main()
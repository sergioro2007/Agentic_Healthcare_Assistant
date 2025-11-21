"""
Tests for the Gemini API client.
"""
import os
import unittest
from unittest.mock import patch, MagicMock
from apis.gemini_client import GeminiClient

class TestGeminiClient(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.test_api_key = "test_api_key"
        
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_generate_text(self, mock_model_class, mock_configure):
        """Test text generation with the Gemini model."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.text = "Test response"
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # Create client and test text generation
        client = GeminiClient(api_key=self.test_api_key)
        result = client.generate_text("Test prompt")
        
        # Verify the API was configured correctly
        mock_configure.assert_called_once_with(api_key=self.test_api_key)
        
        # Verify model was created with correct name
        mock_model_class.assert_called_once_with('gemini-2.5-pro')
        
        # Verify generate_content was called with prompt
        mock_model.generate_content.assert_called_once_with("Test prompt")
        
        # Verify response
        self.assertEqual(result, "Test response")
        
    def test_missing_api_key(self):
        """Test client creation fails when API key is missing."""
        original_api_key = os.environ.get("GOOGLE_API_KEY")
        if "GOOGLE_API_KEY" in os.environ:
            del os.environ["GOOGLE_API_KEY"]
        try:
            with self.assertRaises(ValueError):
                client = GeminiClient()
        finally:
            if original_api_key:
                os.environ["GOOGLE_API_KEY"] = original_api_key

if __name__ == '__main__':
    unittest.main()
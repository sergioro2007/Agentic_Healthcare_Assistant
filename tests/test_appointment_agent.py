"""
Tests for the Appointment Scheduling Agent.
"""
import os
import unittest
from unittest.mock import patch, MagicMock
from agents.appointment_agent import AppointmentAgent
from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage

class TestAppointmentAgent(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.test_api_key = "test_api_key"
        
    def test_schedule_appointment(self):
        """Test scheduling a new appointment."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.content = "I recommend scheduling your appointment for tomorrow at 9:00 AM"
        
        # Setup mock LLM
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        
        # Create agent with mocked LLM
        with patch.dict(os.environ, {'GOOGLE_API_KEY': self.test_api_key}), \
             patch.object(BaseAgent, '_create_llm', return_value=mock_llm):
            
            agent = AppointmentAgent()
            
            # Process a scheduling request
            test_query = "schedule|P123|I need a checkup appointment next week"
            result = agent.process(test_query)
            
            # Verify the results
            self.assertEqual(result["action"], "schedule")
            self.assertEqual(result["patient_id"], "P123")
            self.assertIn("available_slots", result["formatted_response"])
            self.assertIn("recommendation", result["formatted_response"])
            self.assertEqual(result["formatted_response"]["status"], "processed")
            
            # Verify LLM was called
            self.assertEqual(mock_llm.invoke.call_count, 1)
    
    def test_reschedule_appointment(self):
        """Test rescheduling an existing appointment."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.content = "I understand you need to reschedule. How about next Tuesday at 2:00 PM?"
        
        # Setup mock LLM
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        
        # Create agent with mocked LLM
        with patch.dict(os.environ, {'GOOGLE_API_KEY': self.test_api_key}), \
             patch.object(BaseAgent, '_create_llm', return_value=mock_llm):
            
            agent = AppointmentAgent()
            
            # Process a rescheduling request
            test_query = "reschedule|P123|I have a conflict with my current appointment"
            result = agent.process(test_query)
            
            # Verify the results
            self.assertEqual(result["action"], "reschedule")
            self.assertEqual(result["patient_id"], "P123")
            self.assertIn("reschedule", result["formatted_response"]["recommendation"].lower())
    
    def test_simple_schedule_request(self):
        """Test simple scheduling request without patient ID."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.content = "Available appointments for next week"
        
        # Setup mock LLM
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        
        # Create agent with mocked LLM
        with patch.dict(os.environ, {'GOOGLE_API_KEY': self.test_api_key}), \
             patch.object(BaseAgent, '_create_llm', return_value=mock_llm):
            
            agent = AppointmentAgent()
            
            # Process a simple request
            test_query = "I need an appointment next week"
            result = agent.process(test_query)
            
            # Verify the results
            self.assertEqual(result["action"], "schedule")
            self.assertIsNone(result["patient_id"])
            self.assertIsNotNone(result["available_slots"])
    
    def test_available_slots_generation(self):
        """Test that available slots are generated."""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': self.test_api_key}), \
             patch.object(BaseAgent, '_create_llm', return_value=MagicMock()):
            
            agent = AppointmentAgent()
            slots = agent._generate_mock_slots()
            
            # Verify slots are generated
            self.assertIsInstance(slots, list)
            self.assertGreater(len(slots), 0)
            self.assertLessEqual(len(slots), 20)
            
            # Verify slot structure
            for slot in slots:
                self.assertIn("date", slot)
                self.assertIn("time", slot)
                self.assertIn("duration", slot)
                self.assertIn("available", slot)
    
    def test_format_slots(self):
        """Test slot formatting."""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': self.test_api_key}), \
             patch.object(BaseAgent, '_create_llm', return_value=MagicMock()):
            
            agent = AppointmentAgent()
            
            test_slots = [
                {"date": "2024-01-15", "time": "09:00 AM", "duration": "30 min", "available": True},
                {"date": "2024-01-15", "time": "11:00 AM", "duration": "30 min", "available": True}
            ]
            
            formatted = agent._format_slots(test_slots)
            
            # Verify formatting
            self.assertIn("2024-01-15", formatted)
            self.assertIn("09:00 AM", formatted)
            self.assertIn("11:00 AM", formatted)
            self.assertIn("30 min", formatted)
    
    def test_missing_api_key(self):
        """Test agent creation fails when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as cm:
                AppointmentAgent()
            
            self.assertEqual(
                str(cm.exception),
                "API key must be provided either as argument or GOOGLE_API_KEY environment variable"
            )
    
    def test_llm_message_format(self):
        """Test that messages are properly formatted for LLM."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.content = "Test response"
        
        # Setup mock LLM
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        
        # Create agent with mocked LLM
        with patch.dict(os.environ, {'GOOGLE_API_KEY': self.test_api_key}), \
             patch.object(BaseAgent, '_create_llm', return_value=mock_llm):
            
            agent = AppointmentAgent()
            agent.process("schedule|P123|Need appointment")
            
            # Verify LLM was called with list of messages
            self.assertEqual(mock_llm.invoke.call_count, 1)
            call_args = mock_llm.invoke.call_args[0][0]
            self.assertIsInstance(call_args, list)
            self.assertEqual(len(call_args), 1)
            self.assertIsInstance(call_args[0], HumanMessage)
            
            # Verify scheduling context is in the message
            message_content = call_args[0].content
            self.assertTrue(
                "appointment" in message_content.lower() or 
                "scheduling" in message_content.lower()
            )

if __name__ == '__main__':
    unittest.main()

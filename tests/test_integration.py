"""
Integration tests for Healthcare Assistant.
Tests end-to-end functionality with real components.
"""
import os
import pytest
from unittest.mock import patch, MagicMock
from agents.orchestrator_agent import OrchestratorAgent
from agents.disease_info_agent import DiseaseInfoAgent
from agents.ehr_agent import EHRAgent
from agents.appointment_agent import AppointmentAgent
from core.rag_pipeline import RAGPipeline
from core.memory_manager import MemoryManager
from apis.gemini_client import GeminiClient


class TestModelConfiguration:
    """Test that all components use the correct model."""
    
    def test_base_agent_model_name(self):
        """Verify base agent uses correct Gemini model."""
        from agents.base_agent import BaseAgent
        
        # Mock the API call
        with patch('agents.base_agent.ChatGoogleGenerativeAI') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = BaseAgent(api_key="test-key")
            
            # Verify model name
            mock_llm.assert_called_once()
            call_kwargs = mock_llm.call_args[1]
            assert call_kwargs['model'] == 'gemini-1.5-flash-latest', \
                f"Expected gemini-1.5-flash-latest, got {call_kwargs['model']}"
    
    def test_rag_pipeline_model_name(self):
        """Verify RAG pipeline uses correct Gemini model."""
        with patch('core.rag_pipeline.ChatGoogleGenerativeAI') as mock_llm:
            mock_llm.return_value = MagicMock()
            rag = RAGPipeline(api_key="test-key")
            
            # Verify model name
            mock_llm.assert_called_once()
            call_kwargs = mock_llm.call_args[1]
            assert call_kwargs['model'] == 'gemini-1.5-flash-latest', \
                f"Expected gemini-1.5-flash-latest, got {call_kwargs['model']}"
    
    def test_gemini_client_model_name(self):
        """Verify Gemini client uses correct model."""
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel') as mock_model:
                mock_model.return_value = MagicMock()
                client = GeminiClient(api_key="test-key")
                
                # Verify model name
                mock_model.assert_called_once_with('gemini-1.5-flash-latest')


class TestOrchestratorIntegration:
    """Integration tests for the Orchestrator Agent."""
    
    @pytest.fixture
    def mock_llm_response(self):
        """Mock LLM response."""
        mock = MagicMock()
        mock.content = "disease_info"
        return mock
    
    def test_orchestrator_initialization(self):
        """Test orchestrator can be initialized with all agents."""
        with patch('agents.base_agent.ChatGoogleGenerativeAI'):
            orchestrator = OrchestratorAgent(api_key="test-key")
            
            assert hasattr(orchestrator, 'disease_agent')
            assert hasattr(orchestrator, 'ehr_agent')
            assert hasattr(orchestrator, 'appointment_agent')
            assert hasattr(orchestrator, 'graph')
    
    def test_orchestrator_process_mocked(self, mock_llm_response):
        """Test orchestrator can process a query with mocked LLM."""
        with patch('agents.base_agent.ChatGoogleGenerativeAI') as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = mock_llm_response
            mock_llm_class.return_value = mock_llm
            
            orchestrator = OrchestratorAgent(api_key="test-key")
            
            # Mock agent responses
            orchestrator.disease_agent.process = MagicMock(
                return_value={"response": "Diabetes information"}
            )
            
            result = orchestrator.process("What is diabetes?")
            
            assert result is not None
            assert 'response' in result


class TestAgentIntegration:
    """Integration tests for individual agents."""
    
    def test_disease_info_agent_initialization(self):
        """Test Disease Info Agent can be initialized."""
        with patch('agents.base_agent.ChatGoogleGenerativeAI'):
            agent = DiseaseInfoAgent(api_key="test-key")
            assert agent is not None
            assert hasattr(agent, 'llm')
    
    def test_ehr_agent_initialization(self):
        """Test EHR Agent can be initialized."""
        with patch('agents.base_agent.ChatGoogleGenerativeAI'):
            agent = EHRAgent(api_key="test-key")
            assert agent is not None
            assert hasattr(agent, 'llm')
            assert hasattr(agent, 'memory_manager')
    
    def test_appointment_agent_initialization(self):
        """Test Appointment Agent can be initialized."""
        with patch('agents.base_agent.ChatGoogleGenerativeAI'):
            agent = AppointmentAgent(api_key="test-key")
            assert agent is not None
            assert hasattr(agent, 'llm')


class TestRAGIntegration:
    """Integration tests for RAG pipeline."""
    
    def test_rag_with_memory_manager(self):
        """Test RAG pipeline integrates with memory manager."""
        with patch('core.rag_pipeline.ChatGoogleGenerativeAI'):
            with patch('core.memory_manager.ChatGoogleGenerativeAI'):
                rag = RAGPipeline(api_key="test-key")
                
                assert rag.memory_manager is not None
                assert isinstance(rag.memory_manager, MemoryManager)
    
    def test_rag_with_search_aggregator(self):
        """Test RAG pipeline integrates with search aggregator."""
        with patch('core.rag_pipeline.ChatGoogleGenerativeAI'):
            rag = RAGPipeline(api_key="test-key")
            
            assert rag.search_aggregator is not None
            assert hasattr(rag.search_aggregator, 'aggregate_search')


class TestEnvironmentConfiguration:
    """Test environment configuration."""
    
    def test_env_file_exists(self):
        """Test .env file exists."""
        env_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            '.env'
        )
        assert os.path.exists(env_path), ".env file not found"
    
    def test_api_key_in_env(self):
        """Test API key is configured in environment."""
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('GOOGLE_API_KEY')
        assert api_key is not None, "GOOGLE_API_KEY not found in environment"
        assert len(api_key) > 20, "API key appears to be invalid (too short)"


class TestEndToEndFlow:
    """End-to-end integration tests."""
    
    def test_orchestrator_to_disease_agent_flow(self):
        """Test complete flow from orchestrator to disease agent."""
        with patch('agents.base_agent.ChatGoogleGenerativeAI') as mock_llm_class:
            # Mock LLM for classification
            mock_llm = MagicMock()
            mock_classify_response = MagicMock()
            mock_classify_response.content = "disease_info"
            mock_synthesis_response = MagicMock()
            mock_synthesis_response.content = "Diabetes is a chronic condition..."
            
            mock_llm.invoke.side_effect = [mock_classify_response, mock_synthesis_response]
            mock_llm_class.return_value = mock_llm
            
            orchestrator = OrchestratorAgent(api_key="test-key")
            
            # Mock disease agent process
            orchestrator.disease_agent.process = MagicMock(
                return_value={"response": "Diabetes information"}
            )
            
            result = orchestrator.process("Tell me about diabetes")
            
            assert result is not None
            assert 'response' in result
            orchestrator.disease_agent.process.assert_called_once()
    
    def test_orchestrator_to_ehr_agent_flow(self):
        """Test complete flow from orchestrator to EHR agent."""
        with patch('agents.base_agent.ChatGoogleGenerativeAI') as mock_llm_class:
            # Mock LLM for classification
            mock_llm = MagicMock()
            mock_classify_response = MagicMock()
            mock_classify_response.content = "patient_data"
            mock_synthesis_response = MagicMock()
            mock_synthesis_response.content = "Patient information retrieved..."
            
            mock_llm.invoke.side_effect = [mock_classify_response, mock_synthesis_response]
            mock_llm_class.return_value = mock_llm
            
            orchestrator = OrchestratorAgent(api_key="test-key")
            
            # Mock EHR agent process
            orchestrator.ehr_agent.process = MagicMock(
                return_value={"response": "Patient data"}
            )
            
            result = orchestrator.process("Get patient P001 records")
            
            assert result is not None
            assert 'response' in result
            orchestrator.ehr_agent.process.assert_called_once()
    
    def test_orchestrator_to_appointment_agent_flow(self):
        """Test complete flow from orchestrator to appointment agent."""
        with patch('agents.base_agent.ChatGoogleGenerativeAI') as mock_llm_class:
            # Mock LLM for classification
            mock_llm = MagicMock()
            mock_classify_response = MagicMock()
            mock_classify_response.content = "appointment"
            mock_synthesis_response = MagicMock()
            mock_synthesis_response.content = "Appointment scheduled..."
            
            mock_llm.invoke.side_effect = [mock_classify_response, mock_synthesis_response]
            mock_llm_class.return_value = mock_llm
            
            orchestrator = OrchestratorAgent(api_key="test-key")
            
            # Mock appointment agent process
            orchestrator.appointment_agent.process = MagicMock(
                return_value={"response": "Appointment confirmed"}
            )
            
            result = orchestrator.process("Schedule appointment for next week")
            
            assert result is not None
            assert 'response' in result
            orchestrator.appointment_agent.process.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

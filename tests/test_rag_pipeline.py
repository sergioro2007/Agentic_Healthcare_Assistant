"""
Tests for the RAG Pipeline component.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain_core.documents import Document
from core.rag_pipeline import RAGPipeline

@pytest.fixture
def mock_memory_manager():
    """Create a mock MemoryManager."""
    manager = Mock()
    # Return list of Document objects as expected by RAGPipeline
    manager.retrieve_patient_context.return_value = [
        Document(page_content="Patient has diabetes", metadata={"timestamp": "2024-01-01"}),
        Document(page_content="Patient taking Metformin", metadata={"timestamp": "2024-01-02"})
    ]
    return manager

@pytest.fixture
def mock_search_aggregator():
    """Create a mock MedicalSearchAggregator."""
    aggregator = Mock()
    aggregator.get_combined_results.return_value = [
        {"title": "Best Result", "snippet": "Top medical info", "url": "http://example.com", "source": "bing"}
    ]
    return aggregator

@pytest.fixture
def mock_llm():
    """Create a mock LLM."""
    llm = Mock()
    mock_response = Mock()
    mock_response.content = "This is a helpful medical response."
    llm.invoke.return_value = mock_response
    return llm

@pytest.fixture
def rag_pipeline(mock_memory_manager, mock_search_aggregator, mock_llm):
    """Create a RAGPipeline instance with mocks."""
    with patch('core.rag_pipeline.MemoryManager', return_value=mock_memory_manager):
        with patch('core.rag_pipeline.MedicalSearchAggregator', return_value=mock_search_aggregator):
            with patch('core.rag_pipeline.ChatGoogleGenerativeAI', return_value=mock_llm):
                pipeline = RAGPipeline(api_key="test-key")
                pipeline.memory_manager = mock_memory_manager
                pipeline.search_aggregator = mock_search_aggregator
                pipeline.llm = mock_llm
                yield pipeline

class TestRAGPipeline:
    """Test suite for RAGPipeline."""
    
    def test_initialization(self):
        """Test RAGPipeline initialization."""
        with patch('core.rag_pipeline.MemoryManager'):
            with patch('core.rag_pipeline.MedicalSearchAggregator'):
                with patch('core.rag_pipeline.ChatGoogleGenerativeAI'):
                    pipeline = RAGPipeline(api_key="test-key")
                    assert pipeline is not None
    
    def test_query_with_patient_context(self, rag_pipeline, mock_memory_manager, mock_llm):
        """Test querying with patient context."""
        patient_id = "P001"
        query = "What are the patient's current medications?"
        
        response = rag_pipeline.query_with_patient_context(query, patient_id)
        
        # Verify memory manager was called
        mock_memory_manager.retrieve_patient_context.assert_called_once()
        
        # Verify LLM was invoked
        assert mock_llm.invoke.called
        
        # Check response
        assert response is not None
        assert "answer" in response
        assert "context" in response
        assert response["source"] == "memory"
    
    def test_query_with_web_search(self, rag_pipeline, mock_search_aggregator, mock_llm):
        """Test querying with web search."""
        query = "What are the latest treatments for diabetes?"
        
        response = rag_pipeline.query_with_web_search(query)
        
        # Verify search aggregator was called
        mock_search_aggregator.get_combined_results.assert_called()
        
        # Verify LLM was invoked
        assert mock_llm.invoke.called
        
        # Check response
        assert response is not None
        assert "answer" in response
        assert "search_results" in response
        assert response["source"] == "web_search"
    
    def test_query_with_combined_rag(self, rag_pipeline, mock_memory_manager, 
                                     mock_search_aggregator, mock_llm):
        """Test querying with combined RAG (patient context + web search)."""
        patient_id = "P001"
        query = "Should this patient take aspirin?"
        
        response = rag_pipeline.query_with_combined_rag(query, patient_id)
        
        # Verify both memory and search were used
        assert mock_memory_manager.retrieve_patient_context.called
        assert mock_search_aggregator.get_combined_results.called
        
        # Verify LLM was invoked
        assert mock_llm.invoke.called
        
        # Check response structure
        assert response is not None
        assert "answer" in response
        assert "patient_context" in response
        assert "search_results" in response
        assert response["source"] == "combined_rag"
    
    def test_summarize_patient_history(self, rag_pipeline, mock_memory_manager, mock_llm):
        """Test summarizing patient history."""
        patient_id = "P001"
        
        summary = rag_pipeline.summarize_patient_history(patient_id)
        
        # Verify memory retrieval
        assert mock_memory_manager.retrieve_patient_context.called
        
        # Verify LLM was used for summarization
        assert mock_llm.invoke.called
        
        # Check summary
        assert summary is not None
        assert isinstance(summary, str)
        assert summary == "This is a helpful medical response."
    
    def test_query_with_empty_patient_context(self, rag_pipeline, mock_memory_manager, mock_llm):
        """Test querying when patient context is empty."""
        patient_id = "P999"
        query = "General health question"
        
        # Mock empty context
        mock_memory_manager.retrieve_patient_context.return_value = []
        
        response = rag_pipeline.query_with_patient_context(query, patient_id)
        
        # Should return no context found message without calling LLM
        assert response is not None
        assert "answer" in response
        assert "No patient context found" in response["answer"]
        assert response["context"] == []
    
    def test_query_with_no_web_results(self, rag_pipeline, mock_search_aggregator, mock_llm):
        """Test querying when web search returns no results."""
        query = "Obscure medical question"
        
        # Mock empty search results
        mock_search_aggregator.get_combined_results.return_value = []
        
        response = rag_pipeline.query_with_web_search(query)
        
        # Should return no info found message without calling LLM
        assert response is not None
        assert "answer" in response
        assert "No relevant medical information found" in response["answer"]
    
    def test_error_handling_llm_failure(self, rag_pipeline, mock_llm):
        """Test error handling when LLM fails."""
        mock_llm.invoke.side_effect = Exception("LLM Error")
        
        query = "Test query"
        
        # Should raise exception
        with pytest.raises(Exception) as excinfo:
            rag_pipeline.query_with_web_search(query)
        assert "LLM Error" in str(excinfo.value)
    
    def test_multi_query_session(self, rag_pipeline, mock_memory_manager, mock_llm):
        """Test multiple queries in a session."""
        patient_id = "P001"
        
        queries = [
            "What are the patient's conditions?",
            "What medications are they taking?",
            "When is their next appointment?"
        ]
        
        responses = []
        for query in queries:
            response = rag_pipeline.query_with_patient_context(query, patient_id)
            responses.append(response)
        
        # All queries should get responses
        assert len(responses) == 3
        assert all(r is not None for r in responses)

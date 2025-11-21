"""
Tests for the Memory Manager component.
"""
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from core.memory_manager import MemoryManager


@pytest.fixture
def mock_env():
    """Mock environment variables."""
    with patch.dict(os.environ, {
        'GOOGLE_API_KEY': 'test-key-123'
    }):
        yield


@pytest.fixture
def memory_manager(mock_env, tmp_path):
    """Create a MemoryManager instance with temporary storage."""
    with patch('core.memory_manager.GoogleGenerativeAIEmbeddings') as mock_embed:
        # Mock the embeddings model
        mock_embed_instance = Mock()
        mock_embed.return_value = mock_embed_instance
        
        # Create memory manager with temp path
        manager = MemoryManager(persist_directory=str(tmp_path / "test_faiss"))
        
        # Mock the vector store methods
        manager.vector_store = Mock()
        manager.vector_store.similarity_search_with_score.return_value = []
        
        yield manager


class TestMemoryManager:
    """Test suite for MemoryManager."""
    
    def test_initialization(self, mock_env, tmp_path):
        """Test MemoryManager initialization."""
        with patch('core.memory_manager.GoogleGenerativeAIEmbeddings'):
            manager = MemoryManager(persist_directory=str(tmp_path / "test_faiss"))
            assert manager is not None
            assert manager.session_memory == {}
    
    def test_save_patient_summary(self, memory_manager):
        """Test saving patient summary to long-term memory."""
        patient_id = "P001"
        summary = "Patient John Doe, age 45, has diabetes and hypertension. Taking metformin and lisinopril."
        metadata = {
            "name": "John Doe",
            "age": 45,
            "conditions": ["diabetes", "hypertension"],
            "medications": ["metformin", "lisinopril"]
        }
        
        # Mock add_documents
        memory_manager.vector_store.add_documents = Mock()
        memory_manager.vector_store.save_local = Mock()
        
        memory_manager.save_patient_summary(patient_id, summary, metadata)
        
        # Verify vector store was called
        assert memory_manager.vector_store.add_documents.called
        assert memory_manager.vector_store.save_local.called
    
    def test_retrieve_patient_context(self, memory_manager):
        """Test retrieving patient context from memory."""
        patient_id = "P001"
        
        # Mock vector store search to return documents
        from langchain_core.documents import Document
        mock_doc = Document(
            page_content="Patient has diabetes and hypertension",
            metadata={"patient_id": patient_id, "timestamp": "2024-01-01"}
        )
        memory_manager.vector_store.similarity_search.return_value = [mock_doc]
        
        context = memory_manager.retrieve_patient_context(patient_id)
        
        assert context is not None
        assert isinstance(context, list)
        assert len(context) > 0
    
    def test_add_to_session_memory(self, memory_manager):
        """Test adding data to session memory."""
        session_id = "P002"
        interaction = {
            "query": "What medications am I taking?",
            "response": "You are taking metformin and lisinopril."
        }
        
        memory_manager.add_to_session_memory(session_id, interaction)
        
        assert session_id in memory_manager.session_memory
        assert len(memory_manager.session_memory[session_id]) == 1
        assert memory_manager.session_memory[session_id][0]["query"] == interaction["query"]
    
    def test_clear_session_memory(self, memory_manager):
        """Test clearing session memory for a patient."""
        patient_id = "P003"
        memory_manager.session_memory[patient_id] = {"test": "data"}
        
        memory_manager.clear_session_memory(patient_id)
        
        assert patient_id not in memory_manager.session_memory
    
    def test_get_all_patient_ids(self, memory_manager):
        """Test retrieving all patient IDs from session memory."""
        memory_manager.session_memory["P001"] = {"name": "John"}
        memory_manager.session_memory["P002"] = {"name": "Jane"}
        
        patient_ids = memory_manager.get_all_patient_ids()
        
        assert len(patient_ids) == 2
        assert "P001" in patient_ids
        assert "P002" in patient_ids
    
    def test_search_similar_cases(self, memory_manager):
        """Test searching for similar medical cases."""
        query = "patient with diabetes and chest pain"
        
        # Mock vector store search
        from langchain_core.documents import Document
        mock_doc1 = Document(
            page_content="Patient with diabetes presenting chest discomfort",
            metadata={"patient_id": "P001"}
        )
        mock_doc2 = Document(
            page_content="Diabetic patient with cardiac symptoms",
            metadata={"patient_id": "P002"}
        )
        memory_manager.vector_store.similarity_search.return_value = [
            mock_doc1, mock_doc2
        ]
        
        results = memory_manager.search_similar_cases(query, k=2)
        
        assert len(results) == 2
        assert isinstance(results[0], Document)
    
    def test_export_patient_data(self, memory_manager):
        """Test exporting patient data."""
        patient_id = "P001"
        memory_manager.session_memory[patient_id] = [
            {"query": "Test query", "response": "Test response"}
        ]
        
        # Mock vector store search
        from langchain_core.documents import Document
        mock_doc = Document(
            page_content="Medical history",
            metadata={"patient_id": patient_id}
        )
        memory_manager.vector_store.similarity_search.return_value = [mock_doc]
        
        export_data = memory_manager.export_patient_data(patient_id)
        
        assert export_data is not None
        assert export_data["patient_id"] == patient_id
        assert "session_memory" in export_data
        assert "long_term_memory" in export_data
    
    def test_update_patient_summary(self, memory_manager):
        """Test updating an existing patient summary."""
        patient_id = "P001"
        
        # Initial summary
        initial_summary = {"name": "John Doe", "age": 45}
        memory_manager.session_memory[patient_id] = initial_summary
        
        # Update
        updates = {"age": 46, "conditions": ["diabetes"]}
        memory_manager.vector_store.add_documents = Mock()
        memory_manager.vector_store.save_local = Mock()
        
        result = memory_manager.update_patient_summary(patient_id, updates)
        
        assert result is True
        assert memory_manager.session_memory[patient_id]["age"] == 46
        assert "conditions" in memory_manager.session_memory[patient_id]
    
    def test_retrieve_patient_context_no_data(self, memory_manager):
        """Test retrieving context for a patient with no stored data."""
        patient_id = "P999"
        
        # Mock empty search results
        memory_manager.vector_store.similarity_search.return_value = []
        
        context = memory_manager.retrieve_patient_context(patient_id)
        
        assert context is not None
        assert isinstance(context, list)
        assert len(context) == 0
    
    def test_persistence(self, mock_env, tmp_path):
        """Test vector store persistence."""
        persist_dir = str(tmp_path / "test_persist")
        
        with patch('core.memory_manager.GoogleGenerativeAIEmbeddings'):
            with patch('core.memory_manager.FAISS') as mock_faiss:
                mock_faiss.load_local.return_value = Mock()
                
                # Create manager
                manager1 = MemoryManager(persist_directory=persist_dir)
                
                # Verify persistence directory is set
                assert manager1.persist_directory == persist_dir

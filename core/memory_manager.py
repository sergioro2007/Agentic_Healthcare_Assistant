"""
Memory Manager for Healthcare Assistant.
Handles patient context storage and retrieval using FAISS vector database.
"""
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import faiss
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

class MemoryManager:
    """
    Manages patient context and medical history using FAISS vector database.
    Provides long-term and short-term memory capabilities.
    """
    
    def __init__(self, api_key: str = None, persist_directory: str = "./memory_store"):
        """Initialize the memory manager with FAISS vector store."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("API key required for embeddings")
        
        self.persist_directory = persist_directory
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=self.api_key
        )
        
        # Initialize or load vector store
        self.vector_store = self._initialize_vector_store()
        
        # Short-term memory (session-based)
        self.session_memory: Dict[str, List[Dict]] = {}
        
        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
    
    def _initialize_vector_store(self) -> FAISS:
        """Initialize or load existing FAISS vector store."""
        index_path = os.path.join(self.persist_directory, "index.faiss")
        
        if os.path.exists(index_path):
            # Load existing vector store
            return FAISS.load_local(
                self.persist_directory,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            # Create new vector store
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Create empty FAISS index
            dimension = 768  # Dimension for embedding-001 model
            index = faiss.IndexFlatL2(dimension)
            
            # Create vector store with empty index
            vector_store = FAISS(
                embedding_function=self.embeddings,
                index=index,
                docstore=InMemoryDocstore({}),
                index_to_docstore_id={}
            )
            
            return vector_store
    
    def save_patient_summary(
        self,
        patient_id: str,
        summary: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Save patient summary to long-term memory (vector store).
        
        Args:
            patient_id: Unique patient identifier
            summary: Patient summary text
            metadata: Additional metadata (conditions, medications, etc.)
        """
        # Prepare metadata
        meta = {
            "patient_id": patient_id,
            "timestamp": datetime.now().isoformat(),
            "type": "patient_summary"
        }
        if metadata:
            meta.update(metadata)
        
        # Create document
        doc = Document(
            page_content=summary,
            metadata=meta
        )
        
        # Add to vector store
        self.vector_store.add_documents([doc])
        
        # Persist to disk
        self.vector_store.save_local(self.persist_directory)
    
    def save_medical_history(
        self,
        patient_id: str,
        history: str,
        record_type: str = "history"
    ) -> None:
        """
        Save medical history record to long-term memory.
        
        Args:
            patient_id: Unique patient identifier
            history: Medical history text
            record_type: Type of record (history, diagnosis, treatment, etc.)
        """
        # Split long histories into chunks
        chunks = self.text_splitter.split_text(history)
        
        documents = []
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "patient_id": patient_id,
                    "timestamp": datetime.now().isoformat(),
                    "type": record_type,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            )
            documents.append(doc)
        
        # Add to vector store
        self.vector_store.add_documents(documents)
        
        # Persist to disk
        self.vector_store.save_local(self.persist_directory)
    
    def retrieve_patient_context(
        self,
        patient_id: str,
        query: Optional[str] = None,
        k: int = 5
    ) -> List[Document]:
        """
        Retrieve patient context from long-term memory.
        
        Args:
            patient_id: Unique patient identifier
            query: Optional query to find relevant context
            k: Number of documents to retrieve
            
        Returns:
            List of relevant documents
        """
        # Build filter for patient ID
        filter_dict = {"patient_id": patient_id}
        
        if query:
            # Semantic search with patient filter
            docs = self.vector_store.similarity_search(
                query,
                k=k,
                filter=filter_dict
            )
        else:
            # Get all documents for patient (limited to k)
            # Use a generic query if no specific query provided
            docs = self.vector_store.similarity_search(
                f"patient {patient_id} medical history",
                k=k,
                filter=filter_dict
            )
        
        return docs
    
    def add_to_session_memory(
        self,
        session_id: str,
        interaction: Dict[str, Any]
    ) -> None:
        """
        Add interaction to short-term session memory.
        
        Args:
            session_id: Session identifier
            interaction: Dictionary containing query, response, etc.
        """
        if session_id not in self.session_memory:
            self.session_memory[session_id] = []
        
        # Add timestamp
        interaction["timestamp"] = datetime.now().isoformat()
        
        self.session_memory[session_id].append(interaction)
    
    def get_session_memory(
        self,
        session_id: str,
        last_n: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve session memory.
        
        Args:
            session_id: Session identifier
            last_n: Optional number of last interactions to retrieve
            
        Returns:
            List of interactions
        """
        if session_id not in self.session_memory:
            return []
        
        interactions = self.session_memory[session_id]
        
        if last_n:
            return interactions[-last_n:]
        
        return interactions
    
    def clear_session_memory(self, session_id: str) -> None:
        """Clear session memory for a given session."""
        if session_id in self.session_memory:
            del self.session_memory[session_id]
    
    def get_all_patient_ids(self) -> List[str]:
        """Get all unique patient IDs from session memory."""
        return list(self.session_memory.keys())
    
    def export_patient_data(self, patient_id: str) -> Dict[str, Any]:
        """
        Export all data for a specific patient.
        
        Args:
            patient_id: Unique patient identifier
            
        Returns:
            Dictionary containing session and long-term memory
        """
        # Get session memory
        session_data = self.session_memory.get(patient_id, [])
        
        # Get long-term memory from vector store
        try:
            long_term_docs = self.vector_store.similarity_search(
                query=f"patient {patient_id}",
                k=100
            )
            # Filter by patient_id in metadata
            long_term_data = [
                {"content": doc.page_content, "metadata": doc.metadata}
                for doc in long_term_docs
                if doc.metadata.get("patient_id") == patient_id
            ]
        except Exception:
            long_term_data = []
        
        return {
            "patient_id": patient_id,
            "session_memory": session_data,
            "long_term_memory": long_term_data
        }
    
    def update_patient_summary(self, patient_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update patient summary with new information.
        
        Args:
            patient_id: Unique patient identifier
            updates: Dictionary of updates to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update session memory if exists
            if patient_id in self.session_memory:
                if isinstance(self.session_memory[patient_id], dict):
                    self.session_memory[patient_id].update(updates)
                elif isinstance(self.session_memory[patient_id], list) and len(self.session_memory[patient_id]) > 0:
                    # Append as new entry
                    self.session_memory[patient_id].append(updates)
            else:
                self.session_memory[patient_id] = updates
            
            # Save to vector store
            summary_text = json.dumps(updates)
            self.save_patient_summary(patient_id, summary_text, updates)
            return True
        except Exception:
            return False
    
    def search_similar_cases(
        self,
        query: str,
        k: int = 3,
        record_type: Optional[str] = None
    ) -> List[Document]:
        """
        Search for similar medical cases across all patients.
        
        Args:
            query: Search query
            k: Number of results to return
            record_type: Optional filter by record type
            
        Returns:
            List of similar documents
        """
        filter_dict = {}
        if record_type:
            filter_dict["type"] = record_type
        
        docs = self.vector_store.similarity_search(
            query,
            k=k,
            filter=filter_dict if filter_dict else None
        )
        
        return docs
    
    def get_patient_summary_text(self, patient_id: str) -> str:
        """
        Get a formatted text summary of patient's memory.
        
        Args:
            patient_id: Unique patient identifier
            
        Returns:
            Formatted summary text
        """
        docs = self.retrieve_patient_context(patient_id, k=10)
        
        if not docs:
            return f"No memory found for patient {patient_id}"
        
        summary_parts = []
        for doc in docs:
            summary_parts.append(
                f"[{doc.metadata.get('type', 'unknown')}] {doc.page_content}"
            )
        
        return "\n\n".join(summary_parts)
    
    def update_patient_metadata(
        self,
        patient_id: str,
        metadata_updates: Dict[str, Any]
    ) -> None:
        """
        Update metadata for patient records.
        Note: FAISS doesn't support direct updates, so this is a helper
        for tracking metadata changes in application logic.
        
        Args:
            patient_id: Unique patient identifier
            metadata_updates: Dictionary of metadata to update
        """
        # This is a placeholder for metadata tracking
        # In production, you might maintain a separate metadata store
        # or rebuild the vector store with updated metadata
        pass
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the memory store.
        
        Returns:
            Dictionary with memory statistics
        """
        total_vectors = self.vector_store.index.ntotal if hasattr(self.vector_store, 'index') else 0
        
        return {
            "total_documents": total_vectors,
            "active_sessions": len(self.session_memory),
            "persist_directory": self.persist_directory,
            "embedding_model": "models/embedding-001"
        }
    
    def clear_memory(self) -> None:
        """
        Clear all data from the memory store and reset it.
        WARNING: This will delete all stored patient data!
        """
        # Clear session memory
        self.session_memory.clear()
        
        # Reinitialize vector store
        dimension = 768  # Dimension for embedding-001 model
        index = faiss.IndexFlatL2(dimension)
        
        self.vector_store = FAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore=InMemoryDocstore({}),
            index_to_docstore_id={}
        )
        
        # Optionally delete persisted files
        import shutil
        if os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)
            os.makedirs(self.persist_directory, exist_ok=True)

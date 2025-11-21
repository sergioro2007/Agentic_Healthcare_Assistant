"""
RAG (Retrieval-Augmented Generation) Pipeline for Healthcare Assistant.
Combines vector search with LLM generation for context-aware responses.
"""
import os
from typing import Dict, List, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document
from core.memory_manager import MemoryManager
from tools.medical_search_tools import MedicalSearchAggregator

class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline for healthcare queries.
    Combines memory retrieval, web search, and LLM generation.
    """
    
    def __init__(
        self,
        api_key: str = None,
        memory_manager: MemoryManager = None,
        search_aggregator: MedicalSearchAggregator = None
    ):
        """
        Initialize the RAG pipeline.
        
        Args:
            api_key: Google API key for Gemini
            memory_manager: Memory manager instance
            search_aggregator: Medical search aggregator instance
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("API key required for RAG pipeline")
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            google_api_key=self.api_key,
            convert_system_message_to_human=True,
            temperature=0.3  # Lower temperature for factual medical information
        )
        
        # Initialize or use provided memory manager
        self.memory_manager = memory_manager or MemoryManager(api_key=self.api_key)
        
        # Initialize or use provided search aggregator
        # Pass API keys from environment variables
        self.search_aggregator = search_aggregator or MedicalSearchAggregator(
            bing_api_key=os.getenv("BING_SEARCH_API_KEY"),
            ncbi_api_key=os.getenv("NCBI_API_KEY"),
            ncbi_email=os.getenv("NCBI_EMAIL")
        )
        
        # Initialize prompts
        self._init_prompts()
    
    def _init_prompts(self) -> None:
        """Initialize prompt templates for RAG."""
        self.patient_context_prompt = PromptTemplate(
            input_variables=["context", "query"],
            template="""You are a healthcare AI assistant. Use the following patient context to answer the question.

Patient Context:
{context}

Question: {query}

Provide a detailed, accurate answer based on the patient context. If the context doesn't contain relevant information, say so clearly.

Answer:"""
        )
        
        self.disease_info_prompt = PromptTemplate(
            input_variables=["search_results", "query"],
            template="""You are a medical information specialist. Use the following search results from authoritative sources to answer the question.

Search Results:
{search_results}

Question: {query}

Provide a comprehensive, evidence-based answer. Include:
1. Summary of key findings
2. Information from authoritative sources (WHO, NIH, medical journals)
3. Important disclaimers about seeking professional medical advice
4. References to the sources used

Answer:"""
        )
        
        self.combined_rag_prompt = PromptTemplate(
            input_variables=["patient_context", "search_results", "query"],
            template="""You are an advanced healthcare AI assistant. You have access to both patient-specific context and general medical information.

Patient Context:
{patient_context}

Medical Information from Authoritative Sources:
{search_results}

Question: {query}

Provide a comprehensive answer that:
1. Considers the patient's specific context
2. Incorporates evidence-based medical information
3. Highlights any relevant connections between the patient's condition and general medical knowledge
4. Includes appropriate medical disclaimers
5. Recommends consulting healthcare professionals when appropriate

Answer:"""
        )
    
    def query_with_patient_context(
        self,
        query: str,
        patient_id: str,
        k: int = 5
    ) -> Dict[str, Any]:
        """
        Query using patient context from memory.
        
        Args:
            query: User query
            patient_id: Patient identifier
            k: Number of context documents to retrieve
            
        Returns:
            Dictionary with answer and retrieved context
        """
        # Retrieve patient context
        context_docs = self.memory_manager.retrieve_patient_context(
            patient_id=patient_id,
            query=query,
            k=k
        )
        
        if not context_docs:
            return {
                "answer": f"No patient context found for patient {patient_id}. Please provide more information.",
                "context": [],
                "source": "memory"
            }
        
        # Format context
        context_text = "\n\n".join([
            f"[{doc.metadata.get('type', 'info')}] {doc.page_content}"
            for doc in context_docs
        ])
        
        # Generate answer using LLM
        formatted_prompt = self.patient_context_prompt.format(
            context=context_text,
            query=query
        )
        
        response = self.llm.invoke(formatted_prompt)
        
        return {
            "answer": response.content,
            "context": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in context_docs
            ],
            "source": "memory"
        }
    
    def query_with_web_search(
        self,
        query: str,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Query using web search for medical information.
        
        Args:
            query: User query
            max_results: Maximum search results to use
            
        Returns:
            Dictionary with answer and search results
        """
        # Get search results
        search_results = self.search_aggregator.get_combined_results(
            query=query,
            max_total_results=max_results
        )
        
        if not search_results:
            return {
                "answer": "No relevant medical information found. Please rephrase your query.",
                "search_results": [],
                "source": "web_search"
            }
        
        # Format search results
        results_text = "\n\n".join([
            f"Source: {result.get('source', 'Unknown')}\n"
            f"Title: {result.get('title', 'N/A')}\n"
            f"Summary: {result.get('snippet', 'N/A')}\n"
            f"URL: {result.get('url', 'N/A')}"
            for result in search_results
        ])
        
        # Generate answer using LLM
        formatted_prompt = self.disease_info_prompt.format(
            search_results=results_text,
            query=query
        )
        
        response = self.llm.invoke(formatted_prompt)
        
        return {
            "answer": response.content,
            "search_results": search_results,
            "source": "web_search"
        }
    
    def query_with_combined_rag(
        self,
        query: str,
        patient_id: Optional[str] = None,
        k_memory: int = 5,
        max_search_results: int = 10
    ) -> Dict[str, Any]:
        """
        Query using combined RAG: patient context + web search.
        
        Args:
            query: User query
            patient_id: Optional patient identifier
            k_memory: Number of memory documents to retrieve
            max_search_results: Maximum search results to use
            
        Returns:
            Dictionary with comprehensive answer and sources
        """
        # Retrieve patient context if patient_id provided
        patient_context = ""
        context_docs = []
        
        if patient_id:
            context_docs = self.memory_manager.retrieve_patient_context(
                patient_id=patient_id,
                query=query,
                k=k_memory
            )
            
            if context_docs:
                patient_context = "\n\n".join([
                    f"[{doc.metadata.get('type', 'info')}] {doc.page_content}"
                    for doc in context_docs
                ])
            else:
                patient_context = f"No specific patient history found for patient {patient_id}."
        else:
            patient_context = "No patient context provided."
        
        # Get search results
        search_results = self.search_aggregator.get_combined_results(
            query=query,
            max_total_results=max_search_results
        )
        
        # Format search results
        if search_results:
            results_text = "\n\n".join([
                f"Source: {result.get('source', 'Unknown')}\n"
                f"Title: {result.get('title', 'N/A')}\n"
                f"Summary: {result.get('snippet', 'N/A')}\n"
                f"URL: {result.get('url', 'N/A')}"
                for result in search_results
            ])
        else:
            results_text = "No external search results available."
        
        # Generate comprehensive answer using LLM
        formatted_prompt = self.combined_rag_prompt.format(
            patient_context=patient_context,
            search_results=results_text,
            query=query
        )
        
        response = self.llm.invoke(formatted_prompt)
        
        return {
            "answer": response.content,
            "patient_context": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in context_docs
            ],
            "search_results": search_results,
            "source": "combined_rag"
        }
    
    def summarize_patient_history(
        self,
        patient_id: str,
        focus: Optional[str] = None
    ) -> str:
        """
        Generate a comprehensive patient history summary.
        
        Args:
            patient_id: Patient identifier
            focus: Optional focus area (e.g., "cardiovascular", "medications")
            
        Returns:
            Formatted patient history summary
        """
        # Retrieve all patient context
        query = focus if focus else f"patient {patient_id} complete medical history"
        
        context_docs = self.memory_manager.retrieve_patient_context(
            patient_id=patient_id,
            query=query,
            k=20  # Get more documents for comprehensive summary
        )
        
        if not context_docs:
            return f"No medical history found for patient {patient_id}."
        
        # Format context
        context_text = "\n\n".join([
            f"[{doc.metadata.get('type', 'info')}] {doc.page_content}"
            for doc in context_docs
        ])
        
        # Create summarization prompt
        summary_prompt = f"""Provide a comprehensive medical history summary for this patient.

Patient Medical Records:
{context_text}

{f'Focus on: {focus}' if focus else 'Include all relevant medical information.'}

Create a well-structured summary that includes:
1. Patient demographics and basic information
2. Current medical conditions
3. Medication history
4. Past diagnoses and treatments
5. Relevant alerts or risk factors
6. Recent medical events or visits

Summary:"""
        
        response = self.llm.invoke(summary_prompt)
        
        return response.content

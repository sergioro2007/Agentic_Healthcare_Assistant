"""
EHR Integration Agent using LangGraph and Memory Management.
Handles patient data retrieval and analysis from EHR systems with context memory.
"""
import os
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langgraph.graph import END, StateGraph
from agents.base_agent import BaseAgent, AgentState
from apis.ehr_client import EHRClient

# Import memory manager and RAG pipeline if available
try:
    from core.memory_manager import MemoryManager
    from core.rag_pipeline import RAGPipeline
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False


class EHRAgent(BaseAgent):
    """Agent for retrieving and analyzing patient data from EHR systems."""
    
    def __init__(self, api_key: str = None, db_path: str = None, use_memory: bool = True):
        """
        Initialize the agent with Gemini model and EHR client.
        
        Args:
            api_key: Google API key
            db_path: Path to SQLite database (optional, uses default if None)
            use_memory: Whether to use memory management for patient context
        """
        if not api_key and not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("API key must be provided either as argument or GOOGLE_API_KEY environment variable")
        super().__init__(api_key)
        
        # Initialize EHR client with SQLite
        self.ehr_client = EHRClient(db_path=db_path)
        
        # Initialize memory management if requested and available
        self.use_memory = use_memory and MEMORY_AVAILABLE
        self.memory_manager = None
        self.rag_pipeline = None
        if self.use_memory:
            try:
                self.memory_manager = MemoryManager()
                self.rag_pipeline = RAGPipeline(api_key=api_key)
            except Exception:
                self.use_memory = False
        
        # Initialize prompt templates
        self.analysis_prompt = PromptTemplate(
            input_variables=["patient_data", "query", "context"],
            template="""You are a healthcare AI assistant. You MUST answer ONLY the specific question asked.

DO NOT:
- Provide a medical summary unless asked for "summary"
- List all conditions unless asked about conditions
- Discuss medications unless asked about medications
- Give clinical recommendations or "red flags"
- Add context beyond what was requested

Patient Data:
{patient_data}

{context}

User Question: {query}

STRICT RULES:
1. If asked for AGE → Give ONLY the number (e.g., "62 years old")
2. If asked for MEDICATIONS → List ONLY medications
3. If asked about a SPECIFIC condition → Answer YES/NO with condition name
4. If asked for SUMMARY → Then provide full details
5. Keep response under 2 sentences unless asked for summary

Your concise answer:"""
        )
        
        self.summary_prompt = PromptTemplate(
            input_variables=["patient_data"],
            template="""Provide a concise medical summary of this patient's record:

{patient_data}

Include:
- Current conditions and medications
- Recent vital signs and key metrics
- Relevant medical history
- Any red flags or concerns

Keep the summary professional and actionable for healthcare providers."""
        )
        
        # Create the workflow graph
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create the workflow graph for EHR data processing."""
        workflow = StateGraph(AgentState)
        
        # Add nodes for main tasks
        workflow.add_node("parse_request", self._parse_request)
        workflow.add_node("retrieve_data", self._retrieve_data)
        workflow.add_node("analyze_data", self._analyze_data)
        workflow.add_node("format_response", self._format_response)
        
        # Define the workflow edges
        workflow.set_entry_point("parse_request")
        workflow.add_edge("parse_request", "retrieve_data")
        workflow.add_edge("retrieve_data", "analyze_data")
        workflow.add_edge("analyze_data", "format_response")
        workflow.add_edge("format_response", END)
        
        return workflow.compile()
    
    def _parse_request(self, state: AgentState) -> AgentState:
        """Parse the request to extract patient ID and query type."""
        state.current_task = "parse_request"
        
        # Extract the original query
        query = state.task_queue[0]
        state.results["original_query"] = query
        
        # For now, assume query format: "patient_id|query_type"
        # In production, this would use NLP to extract entities
        if "|" in query:
            parts = query.split("|", 1)
            state.results["patient_id"] = parts[0].strip()
            state.results["query_type"] = parts[1].strip() if len(parts) > 1 else "summary"
        else:
            # Extract patient ID from natural language query
            # Look for patterns like "P001", "P001:", "patient P001", etc.
            import re
            patient_id_match = re.search(r'\b(P\d+)\b', query, re.IGNORECASE)
            if patient_id_match:
                state.results["patient_id"] = patient_id_match.group(1).upper()
                # Remove the patient ID from the query to get the actual question
                cleaned_query = re.sub(r'\bP\d+\b:?', '', query, flags=re.IGNORECASE).strip()
                state.results["query_type"] = cleaned_query if cleaned_query else "summary"
            else:
                # Fallback: use the whole query
                state.results["patient_id"] = query.strip()
                state.results["query_type"] = "summary"
        
        return state
    
    def _retrieve_data(self, state: AgentState) -> AgentState:
        """Retrieve patient data from EHR system and store in memory."""
        state.current_task = "retrieve_data"
        
        patient_id = state.results["patient_id"]
        
        try:
            # Get patient data from EHR
            patient_data = self.ehr_client.get_patient_by_id(patient_id)
            state.results["patient_data"] = patient_data
            state.results["retrieval_status"] = "success"
            
            # Save to memory if available
            if self.use_memory and self.memory_manager and patient_data:
                try:
                    print("\n" + "="*80)
                    print("💾 SAVING TO FAISS VECTOR STORE")
                    print("="*80)
                    # Create summary for vector store
                    summary = self._create_patient_summary(patient_data)
                    print(f"Patient ID: {patient_id}")
                    print(f"Summary Preview: {summary[:150]}...")
                    
                    self.memory_manager.save_patient_summary(
                        patient_id,
                        summary,
                        metadata={
                            "name": patient_data.get("name"),
                            "age": patient_data.get("age"),
                            "conditions": patient_data.get("conditions", [])
                        }
                    )
                    print("✅ Successfully saved to FAISS vector store")
                    print("="*80 + "\n")
                except Exception as e:
                    print(f"❌ Failed to save to vector store: {str(e)}")
                    pass  # Continue even if memory save fails
                    
        except Exception as e:
            state.results["patient_data"] = None
            state.results["retrieval_status"] = "error"
            state.results["error_message"] = str(e)
        
        return state
    
    def _create_patient_summary(self, patient_data: Dict[str, Any]) -> str:
        """Create a text summary of patient data for storage."""
        parts = [
            f"Patient: {patient_data.get('name', 'Unknown')}",
            f"Age: {patient_data.get('age', 'Unknown')}",
            f"Gender: {patient_data.get('gender', 'Unknown')}"
        ]
        
        if patient_data.get("conditions"):
            parts.append(f"Conditions: {', '.join(patient_data['conditions'])}")
        
        if patient_data.get("medications"):
            parts.append(f"Medications: {', '.join(patient_data['medications'])}")
        
        if patient_data.get("allergies"):
            parts.append(f"Allergies: {', '.join(patient_data['allergies'])}")
        
        return " | ".join(parts)
    
    def _analyze_data(self, state: AgentState) -> AgentState:
        """Analyze patient data using Gemini and memory context."""
        state.current_task = "analyze_data"
        
        # Check if data retrieval was successful
        if state.results["retrieval_status"] != "success":
            state.results["analysis"] = f"Unable to retrieve patient data: {state.results.get('error_message', 'Unknown error')}"
            return state
        
        patient_data = state.results["patient_data"]
        query_type = state.results["query_type"]
        patient_id = state.results["patient_id"]
        
        # Check if patient was found
        if not patient_data or patient_data.get("error"):
            state.results["analysis"] = f"❌ **Patient Not Found**\n\nPatient ID `{patient_id}` does not exist in the database.\n\nAvailable patient IDs: P001, P002, P003, P004"
            return state
        
        # Format patient data for analysis
        data_str = self._format_patient_data(patient_data)
        
        # Get historical context from memory if available
        context_text = ""
        if self.use_memory and self.memory_manager and self.rag_pipeline:
            try:
                # Try using RAG pipeline for patient context
                if query_type.lower() != "summary":
                    print("\n" + "="*80)
                    print("🔍 RAG PATIENT CONTEXT RETRIEVAL - BEFORE")
                    print("="*80)
                    print(f"Query Type: {query_type}")
                    print(f"Patient ID: {patient_id}")
                    print("Searching FAISS vector store for patient context...")
                    print("="*80 + "\n")
                    
                    rag_response = self.rag_pipeline.query_with_patient_context(query_type, patient_id)
                    
                    if isinstance(rag_response, dict) and "answer" in rag_response:
                        print("\n" + "="*80)
                        print("✅ RAG PATIENT CONTEXT RETRIEVAL - AFTER")
                        print("="*80)
                        print(f"Retrieved Context Documents: {len(rag_response.get('context', []))}")
                        if rag_response.get('context'):
                            print("\nRetrieved Documents from FAISS:")
                            for i, ctx in enumerate(rag_response.get('context', [])[:2], 1):
                                ctx_content = ctx.get('content', '') if isinstance(ctx, dict) else str(ctx)
                                print(f"  [{i}] {ctx_content[:150]}...")
                        print(f"\nRAG-Enhanced Answer: {rag_response['answer'][:200]}...")
                        print("="*80 + "\n")
                        
                        state.results["analysis"] = rag_response["answer"]
                        state.results["rag_used"] = True
                        state.results["rag_context"] = rag_response.get("context", [])
                        return state
                
                # Otherwise, get historical context
                historical_context = self.memory_manager.retrieve_patient_context(patient_id)
                if historical_context and len(historical_context) > 0:
                    context_text = "\nHistorical Context:\n"
                    for doc in historical_context[:3]:
                        context_text += f"- {doc.page_content[:200]}...\n"
            except Exception:
                context_text = ""
        
        # Choose appropriate prompt based on query type
        if query_type.lower() == "summary":
            formatted_prompt = self.summary_prompt.format(patient_data=data_str)
        else:
            formatted_prompt = self.analysis_prompt.format(
                patient_data=data_str,
                query=query_type,
                context=context_text if context_text else "No historical context available."
            )
        
        messages = [HumanMessage(content=formatted_prompt)]
        
        # Generate analysis using Gemini
        response = self.llm.invoke(messages)
        
        # Store the analysis
        state.results["analysis"] = response.content
        
        # Save interaction to session memory
        if self.use_memory and self.memory_manager:
            try:
                self.memory_manager.add_to_session_memory(
                    patient_id,
                    {"query": query_type, "response": response.content}
                )
            except Exception:
                pass  # Continue even if memory save fails
        
        return state
    
    def _format_response(self, state: AgentState) -> AgentState:
        """Format the analyzed information for presentation."""
        state.current_task = "format_response"
        
        # Create structured response
        response = {
            "patient_id": state.results.get("patient_id"),
            "query_type": state.results.get("query_type"),
            "status": state.results.get("retrieval_status"),
            "analysis": state.results.get("analysis"),
        }
        
        # Add patient data if available
        if state.results.get("patient_data"):
            response["patient_summary"] = {
                "name": state.results["patient_data"].get("name"),
                "age": state.results["patient_data"].get("age"),
                "conditions": state.results["patient_data"].get("conditions", [])
            }
        
        state.results["formatted_response"] = response
        
        return state
    
    def _format_patient_data(self, patient_data: Dict[str, Any]) -> str:
        """Format patient data dictionary into readable string."""
        if not patient_data:
            return "No patient data available"
        
        sections = []
        
        # Basic info
        sections.append(f"Patient: {patient_data.get('name', 'Unknown')}")
        sections.append(f"Age: {patient_data.get('age', 'Unknown')}")
        sections.append(f"Gender: {patient_data.get('gender', 'Unknown')}")
        
        # Conditions
        conditions = patient_data.get("conditions", [])
        if conditions:
            sections.append("\nConditions:")
            for condition in conditions:
                sections.append(f"  - {condition}")
        
        # Medications
        medications = patient_data.get("medications", [])
        if medications:
            sections.append("\nMedications:")
            for med in medications:
                sections.append(f"  - {med}")
        
        # Vitals
        vitals = patient_data.get("vitals", {})
        if vitals:
            sections.append("\nVital Signs:")
            for key, value in vitals.items():
                sections.append(f"  - {key}: {value}")
        
        # Allergies
        allergies = patient_data.get("allergies", [])
        if allergies:
            sections.append("\nAllergies:")
            for allergy in allergies:
                sections.append(f"  - {allergy}")
        
        return "\n".join(sections)
    
    def process(self, query: str, **kwargs) -> Dict[str, Any]:
        """Process an EHR query synchronously."""
        # Initialize state
        state = AgentState(
            task_queue=[query],
            results={}
        )
        
        # Run the graph
        final_state = self.graph.invoke(state)
        
        # Handle dict or AgentState return type
        if isinstance(final_state, dict):
            return final_state.get("results", {})
        return final_state.results
    
    async def aprocess(self, query: str, **kwargs) -> Dict[str, Any]:
        """Process an EHR query asynchronously."""
        # For now, just call the sync version
        # In the future, implement true async processing
        return self.process(query, **kwargs)

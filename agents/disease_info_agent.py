"""
Disease Information Retrieval Agent using LangGraph and RAG.
"""
import os
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langgraph.graph import END, StateGraph
from agents.base_agent import BaseAgent, AgentState
from apis.gemini_client import GeminiClient

# Import RAG pipeline if available
try:
    from core.rag_pipeline import RAGPipeline
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False


class DiseaseInfoAgent(BaseAgent):
    """Agent for retrieving and analyzing disease information."""
    
    def __init__(self, api_key: str = None, use_rag: bool = True):
        """
        Initialize the agent with Gemini model and prompts.
        
        Args:
            api_key: Google API key
            use_rag: Whether to use RAG pipeline for enhanced information retrieval
        """
        if not api_key and not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("API key must be provided either as argument or GOOGLE_API_KEY environment variable")
        super().__init__(api_key)
        
        # Initialize RAG pipeline if requested and available
        self.use_rag = use_rag and RAG_AVAILABLE
        self.rag_pipeline = None
        if self.use_rag:
            try:
                self.rag_pipeline = RAGPipeline(api_key=api_key)
            except Exception:
                self.use_rag = False
        
        # Initialize prompt templates
        self.analysis_prompt = PromptTemplate(
            input_variables=["query", "context"],
            template="""You are a medical expert assistant analyzing a health-related query.
            
Query: {query}

{context}

Please provide accurate, well-structured information about the query.
            
Include:
1. Key symptoms and signs
2. Common causes
3. Risk factors
4. When to seek medical attention
5. General management approaches
            
Remember to:
- Use clear, patient-friendly language
- Structure the information logically
- Include appropriate medical disclaimers
- Note any red flags or emergency warning signs
"""
        )
        
        # Create the workflow graph
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create the workflow graph for disease information retrieval."""
        workflow = StateGraph(AgentState)
        
        # Add nodes for main tasks
        workflow.add_node("process_query", self._process_query)
        workflow.add_node("analyze_info", self._analyze_info)
        workflow.add_node("format_response", self._format_response)
        
        # Define the workflow edges
        workflow.set_entry_point("process_query")
        workflow.add_edge("process_query", "analyze_info")
        workflow.add_edge("analyze_info", "format_response")
        workflow.add_edge("format_response", END)
        
        return workflow.compile()
    
    def _process_query(self, state: AgentState) -> AgentState:
        """Process the initial query and prepare for analysis."""
        # Update state to show current task
        state.current_task = "process_query"
        
        # Store the original query in results
        state.results["original_query"] = state.task_queue[0]
        
        return state
    
    def _analyze_info(self, state: AgentState) -> AgentState:
        """Analyze the disease information using Gemini and RAG if available."""
        state.current_task = "analyze_info"
        
        # Get the processed query
        query = state.results["original_query"]
        
        # Use RAG pipeline if available to get enhanced context
        context_text = ""
        if self.use_rag and self.rag_pipeline:
            try:
                print("\n" + "="*80)
                print("🔍 RAG WEB SEARCH - BEFORE")
                print("="*80)
                print(f"Medical Query: {query}")
                print("="*80 + "\n")
                
                rag_response = self.rag_pipeline.query_with_web_search(query)
                
                if isinstance(rag_response, dict) and "answer" in rag_response:
                    print("\n" + "="*80)
                    print("✅ RAG WEB SEARCH - AFTER")
                    print("="*80)
                    print(f"Search Results Found: {len(rag_response.get('search_results', []))}")
                    if rag_response.get('search_results'):
                        print("\nSearch Sources Preview:")
                        for i, result_item in enumerate(rag_response.get('search_results', [])[:3], 1):
                            if isinstance(result_item, dict):
                                print(f"  [{i}] {result_item.get('title', 'N/A')[:100]}")
                            else:
                                print(f"  [{i}] {str(result_item)[:100]}")
                    print(f"\nRAG-Enhanced Answer: {rag_response['answer'][:200]}...")
                    print("="*80 + "\n")
                    
                    # Use RAG-enhanced response directly
                    state.results["analysis"] = rag_response["answer"]
                    state.results["rag_used"] = True
                    state.results["search_results"] = rag_response.get("search_results", [])
                    return state
                elif isinstance(rag_response, dict) and "search_results" in rag_response:
                    # Build context from search results
                    results = rag_response.get("search_results", [])
                    if results:
                        context_text = "Additional Context from Medical Sources:\n"
                        for i, result in enumerate(results[:3], 1):
                            context_text += f"{i}. {result.get('title', 'Source')}: {result.get('snippet', '')}\n"
            except Exception:
                # Fall back to standard processing if RAG fails
                context_text = ""
        
        # Format prompt and create message
        formatted_prompt = self.analysis_prompt.format(
            query=query,
            context=context_text if context_text else "Using general medical knowledge."
        )
        messages = [HumanMessage(content=formatted_prompt)]
        
        # Generate analysis using Gemini
        response = self.llm.invoke(messages)
        
        # Store the analysis
        state.results["analysis"] = response.content
        
        return state
    
    def _format_response(self, state: AgentState) -> AgentState:
        """Format the analyzed information for presentation."""
        state.current_task = "format_response"
        
        # For now, just return the analysis
        state.results["formatted_response"] = state.results["analysis"]
        
        return state
    
    def process(self, query: str, **kwargs) -> Dict[str, Any]:
        """Process a disease information query synchronously."""
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
        """Process a disease information query asynchronously."""
        # For now, just call the sync version
        # In the future, implement true async processing
        return self.process(query, **kwargs)
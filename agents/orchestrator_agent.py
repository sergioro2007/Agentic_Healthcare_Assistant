"""
Orchestrator Agent using LangGraph.
Coordinates multiple specialized agents to handle complex healthcare queries.
"""
import os
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langgraph.graph import END, StateGraph
from agents.base_agent import BaseAgent, AgentState
from agents.disease_info_agent import DiseaseInfoAgent
from agents.ehr_agent import EHRAgent
from agents.appointment_agent import AppointmentAgent

class OrchestratorAgent(BaseAgent):
    """Agent that orchestrates multiple specialized agents."""
    
    def __init__(self, api_key: str = None):
        """Initialize the orchestrator with all specialized agents."""
        if not api_key and not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("API key must be provided either as argument or GOOGLE_API_KEY environment variable")
        super().__init__(api_key)
        
        # Initialize specialized agents
        self.disease_agent = DiseaseInfoAgent(api_key=api_key)
        self.ehr_agent = EHRAgent(api_key=api_key)
        self.appointment_agent = AppointmentAgent(api_key=api_key)
        
        # Initialize prompt for intent classification
        self.classification_prompt = PromptTemplate(
            input_variables=["query"],
            template="""You are a healthcare assistant intent classifier.

User Query: {query}

Classify this query into ONE of these categories:
- disease_info: Questions about diseases, symptoms, treatments, medical conditions
- patient_data: Questions about a specific patient's records, history, or current status
- appointment: Requests to schedule, reschedule, or check appointment availability
- general: General health questions or queries that don't fit the above categories

Respond with ONLY the category name (disease_info, patient_data, appointment, or general).
Do not include any explanation or additional text."""
        )
        
        self.synthesis_prompt = PromptTemplate(
            input_variables=["query", "results"],
            template="""You are a healthcare assistant synthesizing information from multiple sources.

Original Query: {query}

Information Gathered:
{results}

Please provide a comprehensive, well-structured response that:
1. Directly answers the user's question
2. Synthesizes information from all sources
3. Highlights key points and actionable items
4. Uses clear, patient-friendly language
5. Includes appropriate disclaimers when discussing medical information

Your response:"""
        )
        
        # Create the workflow graph
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create the workflow graph for orchestration."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify_intent", self._classify_intent)
        workflow.add_node("route_to_agent", self._route_to_agent)
        workflow.add_node("synthesize_response", self._synthesize_response)
        
        # Define edges
        workflow.set_entry_point("classify_intent")
        workflow.add_edge("classify_intent", "route_to_agent")
        workflow.add_edge("route_to_agent", "synthesize_response")
        workflow.add_edge("synthesize_response", END)
        
        return workflow.compile()
    
    def _classify_intent(self, state: AgentState) -> AgentState:
        """Classify the user's intent using Gemini."""
        state.current_task = "classify_intent"
        
        query = state.task_queue[0]
        state.results["original_query"] = query
        
        # Use LLM to classify intent
        formatted_prompt = self.classification_prompt.format(query=query)
        messages = [HumanMessage(content=formatted_prompt)]
        
        response = self.llm.invoke(messages)
        intent = response.content.strip().lower()
        
        # Validate intent
        valid_intents = ["disease_info", "patient_data", "appointment", "general"]
        if intent not in valid_intents:
            intent = "general"
        
        state.results["intent"] = intent
        
        return state
    
    def _route_to_agent(self, state: AgentState) -> AgentState:
        """Route the query to the appropriate specialized agent."""
        state.current_task = "route_to_agent"
        
        intent = state.results["intent"]
        query = state.results["original_query"]
        
        try:
            if intent == "disease_info":
                result = self.disease_agent.process(query)
                state.results["agent_response"] = result
                state.results["agent_used"] = "disease_info"
                
            elif intent == "patient_data":
                result = self.ehr_agent.process(query)
                state.results["agent_response"] = result
                state.results["agent_used"] = "ehr"
                
            elif intent == "appointment":
                result = self.appointment_agent.process(query)
                state.results["agent_response"] = result
                state.results["agent_used"] = "appointment"
                
            else:  # general
                # Handle general queries directly
                state.results["agent_response"] = {
                    "message": "This is a general health query. How can I assist you further?"
                }
                state.results["agent_used"] = "general"
                
            state.results["routing_status"] = "success"
            
        except Exception as e:
            state.results["routing_status"] = "error"
            state.results["error_message"] = str(e)
            state.results["agent_response"] = None
        
        return state
    
    def _synthesize_response(self, state: AgentState) -> AgentState:
        """Synthesize the final response."""
        state.current_task = "synthesize_response"
        
        if state.results["routing_status"] == "error":
            state.results["final_response"] = {
                "status": "error",
                "message": f"Error processing query: {state.results.get('error_message', 'Unknown error')}",
                "intent": state.results.get("intent")
            }
            return state
        
        agent_response = state.results["agent_response"]
        agent_used = state.results["agent_used"]
        
        # For patient data queries, use the EHR agent's analysis directly
        # to preserve concise, specific answers
        if agent_used == "ehr" and agent_response and "analysis" in agent_response:
            state.results["final_response"] = {
                "status": "success",
                "intent": state.results["intent"],
                "agent_used": agent_used,
                "synthesized_answer": agent_response["analysis"],
                "raw_data": agent_response
            }
            return state
        
        # For other query types, synthesize a cohesive response
        results_str = self._format_agent_response(agent_response, agent_used)
        
        # Use LLM to synthesize a cohesive response
        formatted_prompt = self.synthesis_prompt.format(
            query=state.results["original_query"],
            results=results_str
        )
        messages = [HumanMessage(content=formatted_prompt)]
        
        response = self.llm.invoke(messages)
        
        state.results["final_response"] = {
            "status": "success",
            "intent": state.results["intent"],
            "agent_used": agent_used,
            "synthesized_answer": response.content,
            "raw_data": agent_response
        }
        
        return state
    
    def _format_agent_response(self, response: Any, agent_type: str) -> str:
        """Format agent response for synthesis."""
        if not response:
            return "No data available"
        
        if agent_type == "disease_info":
            return f"Disease Information:\n{response.get('analysis', 'No analysis available')}"
        
        elif agent_type == "ehr":
            analysis = response.get('analysis', 'No analysis available')
            patient_summary = response.get('patient_summary', {})
            return f"Patient Data:\n{analysis}\n\nPatient: {patient_summary.get('name', 'Unknown')}"
        
        elif agent_type == "appointment":
            recommendation = response.get('formatted_response', {}).get('recommendation', 'No recommendation')
            return f"Appointment Information:\n{recommendation}"
        
        else:
            return str(response)
    
    def process(self, query: str, **kwargs) -> Dict[str, Any]:
        """Process a query through the orchestrator."""
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
        """Process a query asynchronously."""
        return self.process(query, **kwargs)

"""
Appointment Scheduling Agent using LangGraph.
Handles appointment booking, rescheduling, and availability checking.
"""
import os
import re
import calendar
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langgraph.graph import END, StateGraph
from agents.base_agent import BaseAgent, AgentState

class AppointmentAgent(BaseAgent):
    """Agent for managing patient appointments."""
    
    def __init__(self, api_key: str = None):
        """Initialize the agent with Gemini model."""
        if not api_key and not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("API key must be provided either as argument or GOOGLE_API_KEY environment variable")
        super().__init__(api_key)
        
        # Initialize prompt templates
        self.scheduling_prompt = PromptTemplate(
            input_variables=["request", "available_slots", "patient_info"],
            template="""You are a healthcare appointment scheduling assistant.

Patient Request: {request}

Available Time Slots:
{available_slots}

Patient Information:
{patient_info}

Please:
1. Analyze the patient's scheduling request
2. Suggest the most suitable appointment time from available slots
3. Consider any preferences mentioned (morning/afternoon, specific days, etc.)
4. Provide clear confirmation details
5. Mention any preparation needed for the appointment

Respond in a friendly, professional manner."""
        )
        
        self.rescheduling_prompt = PromptTemplate(
            input_variables=["current_appointment", "new_slots", "reason"],
            template="""You are helping to reschedule a healthcare appointment.

Current Appointment: {current_appointment}

Reason for Rescheduling: {reason}

Available Alternative Slots:
{new_slots}

Please:
1. Acknowledge the need to reschedule
2. Suggest suitable alternative times
3. Ensure minimal disruption to the patient's schedule
4. Provide clear next steps

Be empathetic and helpful."""
        )
        
        # Create the workflow graph
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create the workflow graph for appointment management."""
        workflow = StateGraph(AgentState)
        
        # Add nodes for main tasks
        workflow.add_node("parse_request", self._parse_request)
        workflow.add_node("check_availability", self._check_availability)
        workflow.add_node("process_appointment", self._process_appointment)
        workflow.add_node("format_response", self._format_response)
        
        # Define the workflow edges
        workflow.set_entry_point("parse_request")
        workflow.add_edge("parse_request", "check_availability")
        workflow.add_edge("check_availability", "process_appointment")
        workflow.add_edge("process_appointment", "format_response")
        workflow.add_edge("format_response", END)
        
        return workflow.compile()
    
    def _parse_request(self, state: AgentState) -> AgentState:
        """Parse the appointment request."""
        state.current_task = "parse_request"
        
        query = state.task_queue[0]
        state.results["original_request"] = query
        
        # Extract request type and details
        # Format: "action|patient_id|details"
        if "|" in query:
            parts = query.split("|")
            state.results["action"] = parts[0].strip().lower()
            state.results["patient_id"] = parts[1].strip() if len(parts) > 1 else None
            state.results["details"] = parts[2].strip() if len(parts) > 2 else ""
        else:
            state.results["action"] = "schedule"
            state.results["patient_id"] = None
            state.results["details"] = query
        
        # Parse date range from natural language
        date_range = self._parse_date_request(query)
        state.results["date_range"] = date_range
        state.results["today"] = datetime.now().strftime("%Y-%m-%d")
        
        return state
    
    def _check_availability(self, state: AgentState) -> AgentState:
        """Check available appointment slots."""
        state.current_task = "check_availability"
        
        # In a real system, this would query a scheduling database
        # For now, generate mock available slots based on requested date range
        date_range = state.results.get("date_range")
        available_slots = self._generate_mock_slots(date_range)
        state.results["available_slots"] = available_slots
        
        return state
    
    def _process_appointment(self, state: AgentState) -> AgentState:
        """Process the appointment using Gemini."""
        state.current_task = "process_appointment"
        
        action = state.results["action"]
        available_slots = state.results["available_slots"]
        details = state.results["details"]
        
        # Format available slots
        slots_str = self._format_slots(available_slots)
        
        # Patient info (mock data for now)
        patient_info = f"Patient ID: {state.results.get('patient_id', 'Unknown')}"
        
        # Get current date context
        today = state.results.get("today", datetime.now().strftime("%Y-%m-%d"))
        date_range = state.results.get("date_range")
        date_context = f"Today's date: {today}\n"
        if date_range:
            date_context += f"Requested date range: {date_range[0]} to {date_range[1]}\n"
        
        # Choose appropriate prompt based on action
        if action == "reschedule":
            formatted_prompt = self.rescheduling_prompt.format(
                current_appointment="Previous appointment details",
                new_slots=slots_str,
                reason=details
            )
        else:  # schedule
            formatted_prompt = self.scheduling_prompt.format(
                request=details,
                available_slots=slots_str,
                patient_info=f"{patient_info}\n{date_context}"
            )
        
        messages = [HumanMessage(content=formatted_prompt)]
        
        # Generate response using Gemini
        response = self.llm.invoke(messages)
        
        # Store the response
        state.results["appointment_response"] = response.content
        
        return state
    
    def _format_response(self, state: AgentState) -> AgentState:
        """Format the appointment response."""
        state.current_task = "format_response"
        
        response = {
            "action": state.results.get("action"),
            "patient_id": state.results.get("patient_id"),
            "available_slots": state.results.get("available_slots"),
            "recommendation": state.results.get("appointment_response"),
            "status": "processed"
        }
        
        state.results["formatted_response"] = response
        
        return state
    
    def _parse_date_request(self, query: str) -> Optional[Tuple[str, str]]:
        """Parse natural language date requests and return (start_date, end_date)."""
        query_lower = query.lower()
        today = datetime.now()
        
        # "next week"
        if "next week" in query_lower:
            start = today + timedelta(days=(7 - today.weekday()))
            end = start + timedelta(days=6)
            return (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
        
        # "last week of [month name]" or "end of [month name]"
        month_names = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        for month_name, month_num in month_names.items():
            if f"last week of {month_name}" in query_lower or f"end of {month_name}" in query_lower:
                # Determine the year
                if month_num < today.month:
                    # Month is in the past this year, so use next year
                    target_year = today.year + 1
                elif month_num == today.month and today.day > 21:
                    # We're past the last week of this month, use next year
                    target_year = today.year + 1
                else:
                    # Month is upcoming this year
                    target_year = today.year
                
                # Get last day of the month
                last_day = calendar.monthrange(target_year, month_num)[1]
                end_date = datetime(target_year, month_num, last_day)
                
                # Last week = last 7 days of the month
                start_date = end_date - timedelta(days=6)
                
                return (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        
        # "last week of next month" or "end of next month"
        if ("last week of next month" in query_lower or 
            "end of next month" in query_lower or
            "final week of next month" in query_lower):
            # Get next month
            if today.month == 12:
                next_month = 1
                next_year = today.year + 1
            else:
                next_month = today.month + 1
                next_year = today.year
            
            # Get last day of next month
            last_day = calendar.monthrange(next_year, next_month)[1]
            end_date = datetime(next_year, next_month, last_day)
            
            # Last week = last 7 days of the month
            start_date = end_date - timedelta(days=6)
            
            return (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        
        # "next month"
        if "next month" in query_lower and "last week" not in query_lower:
            if today.month == 12:
                next_month = 1
                next_year = today.year + 1
            else:
                next_month = today.month + 1
                next_year = today.year
            
            start = datetime(next_year, next_month, 1)
            last_day = calendar.monthrange(next_year, next_month)[1]
            end = datetime(next_year, next_month, last_day)
            
            return (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
        
        # "this week"
        if "this week" in query_lower:
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
            return (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
        
        # Default: next 2 weeks
        return None
    
    def _generate_mock_slots(self, date_range: Optional[Tuple[str, str]] = None) -> List[Dict[str, Any]]:
        """Generate mock available appointment slots for the specified date range."""
        slots = []
        
        if date_range:
            start_date = datetime.strptime(date_range[0], "%Y-%m-%d")
            end_date = datetime.strptime(date_range[1], "%Y-%m-%d")
        else:
            # Default: next 5 business days
            start_date = datetime.now() + timedelta(days=1)
            end_date = start_date + timedelta(days=4)
        
        current_date = start_date
        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                # Morning slots
                slots.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "time": "09:00 AM",
                    "duration": "30 min",
                    "available": True
                })
                slots.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "time": "11:00 AM",
                    "duration": "30 min",
                    "available": True
                })
                # Afternoon slots
                slots.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "time": "02:00 PM",
                    "duration": "30 min",
                    "available": True
                })
                slots.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "time": "04:00 PM",
                    "duration": "30 min",
                    "available": True
                })
            
            current_date += timedelta(days=1)
        
        return slots
    
    def _format_slots(self, slots: List[Dict[str, Any]]) -> str:
        """Format available slots into readable string."""
        if not slots:
            return "No available slots"
        
        formatted = []
        for slot in slots:
            formatted.append(
                f"{slot['date']} at {slot['time']} ({slot['duration']})"
            )
        
        return "\n".join(formatted)
    
    def process(self, query: str, **kwargs) -> Dict[str, Any]:
        """Process an appointment request synchronously."""
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
        """Process an appointment request asynchronously."""
        # For now, just call the sync version
        return self.process(query, **kwargs)

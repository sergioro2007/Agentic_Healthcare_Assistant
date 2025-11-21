"""
Healthcare Assistant Agents Package.

This package contains specialized agents for healthcare tasks:
- OrchestratorAgent: Routes queries to appropriate specialized agents
- DiseaseInfoAgent: Handles medical information queries
- EHRAgent: Manages patient data retrieval and analysis
- AppointmentAgent: Handles appointment scheduling and management
"""

from agents.base_agent import BaseAgent, AgentState
from agents.orchestrator_agent import OrchestratorAgent
from agents.disease_info_agent import DiseaseInfoAgent
from agents.ehr_agent import EHRAgent
from agents.appointment_agent import AppointmentAgent

__all__ = [
    'BaseAgent',
    'AgentState',
    'OrchestratorAgent',
    'DiseaseInfoAgent',
    'EHRAgent',
    'AppointmentAgent',
]

__version__ = '1.0.0'

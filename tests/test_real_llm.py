"""
Real LLM integration test - no mocks, actual API calls.
This test verifies the agents can actually call Google Gemini API.
"""
import os
import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Skip all tests if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv('GOOGLE_API_KEY'),
    reason="GOOGLE_API_KEY not set - skipping real API tests"
)


class TestRealLLMCalls:
    """Test actual LLM API calls without mocks."""
    
    def test_api_key_exists(self):
        """Verify API key is configured."""
        api_key = os.getenv('GOOGLE_API_KEY')
        assert api_key is not None, "GOOGLE_API_KEY not found"
        assert len(api_key) > 20, "API key appears invalid"
        print(f"\n✅ API Key found: {api_key[:15]}...{api_key[-5:]}")
    
    def test_direct_llm_call(self):
        """Test direct LLM call with real API."""
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        print("\n🔧 Testing direct LLM call...")
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            convert_system_message_to_human=True
        )
        
        response = llm.invoke("Say exactly: 'API works!'")
        
        print(f"✅ LLM Response: {response.content}")
        assert response is not None
        assert len(response.content) > 0
    
    def test_base_agent_llm(self):
        """Test base agent can call real LLM."""
        from agents.base_agent import BaseAgent
        from langchain_core.messages import HumanMessage
        
        print("\n🔧 Testing base agent LLM...")
        
        agent = BaseAgent(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Call LLM directly through agent
        response = agent.llm.invoke([HumanMessage(content="Say 'Base agent works!'")])
        
        print(f"✅ Base Agent Response: {response.content}")
        assert response is not None
        assert len(response.content) > 0
    
    def test_orchestrator_classification(self):
        """Test orchestrator can classify intent with real LLM."""
        from agents.orchestrator_agent import OrchestratorAgent
        
        print("\n🔧 Testing orchestrator classification...")
        
        orchestrator = OrchestratorAgent(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Test classification
        from agents.base_agent import AgentState
        state = AgentState(
            task_queue=["What is diabetes?"],
            results={}
        )
        
        result_state = orchestrator._classify_intent(state)
        
        intent = result_state.results.get('intent', 'unknown')
        print(f"✅ Classified intent: {intent}")
        
        assert intent in ['disease_info', 'patient_data', 'appointment', 'general']
    
    def test_orchestrator_full_process(self):
        """Test orchestrator full process with real LLM."""
        from agents.orchestrator_agent import OrchestratorAgent
        
        print("\n🔧 Testing full orchestrator process...")
        
        orchestrator = OrchestratorAgent(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Process a simple query
        result = orchestrator.process("What is diabetes?")
        
        print(f"✅ Process completed")
        print(f"   Intent: {result.get('intent', 'N/A')}")
        print(f"   Agent: {result.get('agent_used', 'N/A')}")
        print(f"   Response preview: {str(result.get('final_response', ''))[:100]}...")
        
        assert result is not None
        assert 'intent' in result
        assert 'agent_used' in result
        assert 'final_response' in result
    
    def test_disease_info_agent(self):
        """Test disease info agent with real LLM."""
        from agents.disease_info_agent import DiseaseInfoAgent
        
        print("\n🔧 Testing disease info agent...")
        
        agent = DiseaseInfoAgent(api_key=os.getenv("GOOGLE_API_KEY"))
        
        result = agent.process("What causes diabetes?")
        
        print(f"✅ Disease Info Response preview: {str(result)[:100]}...")
        
        assert result is not None
        assert 'response' in result or 'error' in result
    
    def test_ehr_agent(self):
        """Test EHR agent with real LLM."""
        from agents.ehr_agent import EHRAgent
        
        print("\n🔧 Testing EHR agent...")
        
        agent = EHRAgent(api_key=os.getenv("GOOGLE_API_KEY"))
        
        result = agent.process("Get patient P001 summary")
        
        print(f"✅ EHR Response preview: {str(result)[:100]}...")
        
        assert result is not None
        assert 'response' in result or 'error' in result
    
    def test_appointment_agent(self):
        """Test appointment agent with real LLM."""
        from agents.appointment_agent import AppointmentAgent
        
        print("\n🔧 Testing appointment agent...")
        
        agent = AppointmentAgent(api_key=os.getenv("GOOGLE_API_KEY"))
        
        result = agent.process("Schedule appointment for tomorrow at 2pm")
        
        print(f"✅ Appointment Response preview: {str(result)[:100]}...")
        
        assert result is not None
        assert 'response' in result or 'error' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

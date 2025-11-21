"""
Quick test script to verify the Gemini API actually works with our configuration.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from agents.orchestrator_agent import OrchestratorAgent

def test_direct_llm():
    """Test LLM directly."""
    print("=" * 60)
    print("TEST 1: Direct LLM Call")
    print("=" * 60)
    
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            convert_system_message_to_human=True
        )
        
        response = llm.invoke("Say 'Hello from Gemini!'")
        print(f"✅ SUCCESS: {response.content}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_orchestrator():
    """Test orchestrator agent."""
    print("\n" + "=" * 60)
    print("TEST 2: Orchestrator Agent")
    print("=" * 60)
    
    try:
        orchestrator = OrchestratorAgent(api_key=os.getenv("GOOGLE_API_KEY"))
        
        result = orchestrator.process("What is diabetes?")
        print(f"✅ SUCCESS")
        print(f"Intent: {result.get('intent', 'N/A')}")
        print(f"Agent Used: {result.get('agent_used', 'N/A')}")
        print(f"Response Preview: {str(result.get('final_response', {}))[:200]}...")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🏥 Healthcare Assistant - Real API Test\n")
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY not found in environment")
        exit(1)
    
    print(f"API Key: {api_key[:20]}...{api_key[-10:]}\n")
    
    # Run tests
    test1_passed = test_direct_llm()
    test2_passed = test_orchestrator()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Direct LLM Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Orchestrator Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! App is ready to use.")
        exit(0)
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
        exit(1)

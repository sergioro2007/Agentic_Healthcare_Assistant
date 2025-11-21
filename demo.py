"""
Demo script for Healthcare Assistant with LangGraph Agents.
Demonstrates the orchestrator coordinating multiple specialized agents.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
from agents.orchestrator_agent import OrchestratorAgent

def print_separator():
    """Print a visual separator."""
    print("\n" + "="*80 + "\n")

def demo_disease_info():
    """Demo: Disease information query."""
    print("🏥 DEMO 1: Disease Information Query")
    print_separator()
    
    orchestrator = OrchestratorAgent()
    
    query = "What are the common symptoms of Type 2 Diabetes?"
    print(f"Query: {query}\n")
    
    result = orchestrator.process(query)
    
    print(f"Intent Detected: {result['final_response']['intent']}")
    print(f"Agent Used: {result['final_response']['agent_used']}")
    print(f"\nResponse:\n{result['final_response']['synthesized_answer']}")
    print_separator()

def demo_patient_data():
    """Demo: Patient data retrieval."""
    print("📋 DEMO 2: Patient Data Retrieval")
    print_separator()
    
    orchestrator = OrchestratorAgent()
    
    query = "P001"  # Patient ID
    print(f"Query: Get summary for patient {query}\n")
    
    result = orchestrator.process(query)
    
    print(f"Intent Detected: {result['final_response']['intent']}")
    print(f"Agent Used: {result['final_response']['agent_used']}")
    print(f"Status: {result['final_response']['status']}")
    
    if result['final_response']['status'] == 'success':
        print(f"\nResponse:\n{result['final_response']['synthesized_answer']}")
    else:
        print(f"\nNote: {result['final_response'].get('message', 'No patient data available')}")
    
    print_separator()

def demo_appointment():
    """Demo: Appointment scheduling."""
    print("📅 DEMO 3: Appointment Scheduling")
    print_separator()
    
    orchestrator = OrchestratorAgent()
    
    query = "I need to schedule a checkup appointment for next week, preferably in the morning"
    print(f"Query: {query}\n")
    
    result = orchestrator.process(query)
    
    print(f"Intent Detected: {result['final_response']['intent']}")
    print(f"Agent Used: {result['final_response']['agent_used']}")
    print(f"\nResponse:\n{result['final_response']['synthesized_answer']}")
    print_separator()

def demo_general():
    """Demo: General query."""
    print("💬 DEMO 4: General Health Query")
    print_separator()
    
    orchestrator = OrchestratorAgent()
    
    query = "Hello! How can you help me with my health questions?"
    print(f"Query: {query}\n")
    
    result = orchestrator.process(query)
    
    print(f"Intent Detected: {result['final_response']['intent']}")
    print(f"Agent Used: {result['final_response']['agent_used']}")
    print(f"\nResponse:\n{result['final_response']['synthesized_answer']}")
    print_separator()

def main():
    """Run all demos."""
    print("\n" + "🌟"*40)
    print("   HEALTHCARE ASSISTANT - LangGraph Multi-Agent System Demo")
    print("🌟"*40 + "\n")
    
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  WARNING: GOOGLE_API_KEY environment variable not set!")
        print("Please set it before running this demo:")
        print("export GOOGLE_API_KEY='your-api-key-here'\n")
        return
    
    try:
        print("This demo showcases the orchestrator coordinating multiple specialized agents:\n")
        print("✅ Disease Info Agent - Medical information retrieval")
        print("✅ EHR Agent - Patient data integration")
        print("✅ Appointment Agent - Scheduling management")
        print("✅ Orchestrator - Intelligent routing and synthesis\n")
        
        input("Press Enter to start the demos...")
        
        # Run demos
        demo_disease_info()
        input("Press Enter for next demo...")
        
        demo_patient_data()
        input("Press Enter for next demo...")
        
        demo_appointment()
        input("Press Enter for next demo...")
        
        demo_general()
        
        print("\n✨ Demo complete! The Healthcare Assistant successfully:")
        print("   • Classified user intents")
        print("   • Routed queries to specialized agents")
        print("   • Synthesized comprehensive responses")
        print("\n" + "🌟"*40 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error during demo: {str(e)}")
        print("Please ensure:")
        print("  1. GOOGLE_API_KEY is set correctly")
        print("  2. All dependencies are installed")
        print("  3. You have internet connectivity")

if __name__ == "__main__":
    main()

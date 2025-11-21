import os
from dotenv import load_dotenv
from agents.orchestrator_agent import OrchestratorAgent

load_dotenv()

def test_orchestrator():
    orchestrator = OrchestratorAgent()
    
    # Test case 1: Specific question about age
    query = "P001: What is the patient's age?"
    print(f"Testing Query: '{query}'")
    print("=" * 80)
    result = orchestrator.process(query)
    answer = result['final_response']['synthesized_answer']
    print(f"Answer: {answer}")
    print("=" * 80)
    
    # Check if the answer is concise
    if len(answer) < 150 and "62" in answer:
        print("✅ Test Passed: Concise answer received.")
    else:
        print(f"❌ Test Failed: Answer is too long ({len(answer)} chars) or doesn't contain age.")
        
    print("\n" + "-" * 80 + "\n")

    # Test case 2: Specific question about medications
    query = "P001: What medications is the patient taking?"
    print(f"Testing Query: '{query}'")
    print("=" * 80)
    result = orchestrator.process(query)
    answer = result['final_response']['synthesized_answer']
    print(f"Answer: {answer}")
    print("=" * 80)
    
    # Check if the answer focuses on medications
    if "Lisinopril" in answer or "Metformin" in answer:
        print("✅ Test Passed: Medication information provided.")
    else:
        print("❌ Test Failed: Medication information missing.")

if __name__ == "__main__":
    test_orchestrator()

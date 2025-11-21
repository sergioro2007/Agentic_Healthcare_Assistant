
import os
from dotenv import load_dotenv
from agents.ehr_agent import EHRAgent

load_dotenv()

def test_ehr_query():
    agent = EHRAgent()
    
    # Test case 1: Specific question
    query = "P001: What is the patient's age?"
    print(f"Testing Query: '{query}'")
    result = agent.process(query)
    print(f"Result Analysis: {result['analysis']}")
    
    # Check if the answer is concise (contains "62" and is short)
    if "62" in result['analysis'] and len(result['analysis']) < 100:
        print("✅ Test Passed: Concise answer received.")
    else:
        print("❌ Test Failed: Answer might be too long or incorrect.")
        
    print("-" * 50)

    # Test case 2: Summary request
    query = "P001: summary"
    print(f"Testing Query: '{query}'")
    result = agent.process(query)
    # Summary should be longer
    if len(result['analysis']) > 100:
        print("✅ Test Passed: Detailed summary received.")
    else:
        print("❌ Test Failed: Summary might be too short.")

if __name__ == "__main__":
    test_ehr_query()

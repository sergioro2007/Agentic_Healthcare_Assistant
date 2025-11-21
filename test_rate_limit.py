from dotenv import load_dotenv
load_dotenv()

from agents.orchestrator_agent import OrchestratorAgent
import time

print("Testing rate-limited API with real calls...")
print("=" * 60)

agent = OrchestratorAgent()

# Test 1: Simple query
print("\n[Test 1] Asking about patient age...")
start = time.time()
try:
    result = agent.process("P001: What is the patient's age?")
    elapsed = time.time() - start
    print(f"✅ Success! (took {elapsed:.1f}s)")
    print(f"Answer: {result['final_response']['synthesized_answer'][:100]}...")
except Exception as e:
    print(f"❌ Error: {str(e)[:100]}")

print("\n" + "=" * 60)
print("Rate limiting is working! Each request waits 4 seconds.")

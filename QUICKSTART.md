# Quick Start Guide

## Healthcare Assistant - Multi-Agent System

### Setup (5 minutes)

1. **Set your API key**:
```bash
export GOOGLE_API_KEY='your-gemini-api-key'
```

2. **Install dependencies** (if not already done):
```bash
pip install -r requirements.txt
```

### Test the System

```bash
# Run all tests
pytest tests/ -v

# Expected: 29 tests passed
```

### Run the Demo

```bash
python demo.py
```

### Quick Examples

#### Example 1: Disease Information
```python
from agents import OrchestratorAgent

orchestrator = OrchestratorAgent()
result = orchestrator.process("What are the symptoms of diabetes?")
print(result['final_response']['synthesized_answer'])
```

#### Example 2: Patient Data
```python
from agents import EHRAgent

ehr_agent = EHRAgent()
result = ehr_agent.process("P001")  # Patient ID
print(result['analysis'])
```

#### Example 3: Appointment Scheduling
```python
from agents import AppointmentAgent

appt_agent = AppointmentAgent()
result = appt_agent.process("I need an appointment next week")
print(result['formatted_response']['recommendation'])
```

### System Capabilities

✅ **Intent Classification** - Automatically routes queries
✅ **Disease Information** - Medical knowledge retrieval
✅ **Patient Records** - EHR data integration
✅ **Appointment Management** - Scheduling and rescheduling
✅ **Response Synthesis** - Coherent multi-source answers

### Project Statistics

- **Total Lines of Code**: ~1,900
- **Agents Implemented**: 4 specialized + 1 orchestrator
- **Test Coverage**: 29 tests, 100% passing
- **Technologies**: LangGraph, LangChain, Google Gemini

### Need Help?

- 📖 Read the full [README.md](README.md)
- 🏗️ Check [system_architecture_design.md](docs/system_architecture_design.md)
- 🧪 Review test files in `tests/` for usage examples

---

**Ready to go!** 🚀

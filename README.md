# Healthcare Assistant - Multi-Agent System with LangGraph

A sophisticated healthcare assistant built using **LangGraph** for agent orchestration and **Google Gemini** for natural language understanding. The system uses specialized agents that work together to handle various healthcare-related tasks.

## 🎯 Features

- **Intelligent Intent Classification**: Automatically routes queries to the appropriate specialized agent
- **Disease Information**: Provides detailed medical information about diseases, symptoms, and treatments
- **Patient Data Integration**: Retrieves and analyzes patient records from EHR systems
- **Appointment Management**: Handles scheduling, rescheduling, and availability checking
- **Response Synthesis**: Combines information from multiple sources into coherent answers

## 🏗️ Architecture

### Multi-Agent System

```
┌─────────────────────────────────────┐
│      Orchestrator Agent             │
│  (Intent Classification & Routing)  │
└──────────┬──────────────────────────┘
           │
    ┌──────┴────────┐
    │               │
    ▼               ▼
┌─────────┐    ┌─────────┐
│ Disease │    │   EHR   │
│  Info   │    │  Agent  │
│ Agent   │    │         │
└─────────┘    └─────────┘
    │               │
    └───────┬───────┘
            │
            ▼
    ┌──────────────┐
    │ Appointment  │
    │   Agent      │
    └──────────────┘
```

### Agents

1. **Orchestrator Agent** (`orchestrator_agent.py`)
   - Classifies user intents
   - Routes to specialized agents
   - Synthesizes responses

2. **Disease Info Agent** (`disease_info_agent.py`)
   - Medical information retrieval
   - Symptom analysis
   - Treatment recommendations

3. **EHR Agent** (`ehr_agent.py`)
   - Patient data retrieval
   - Medical history analysis
   - Record summarization

4. **Appointment Agent** (`appointment_agent.py`)
   - Schedule appointments
   - Check availability
   - Reschedule management

## 📋 Requirements

- Python 3.10+
- Google Gemini API key
- Dependencies listed in `requirements.txt`

## 🚀 Installation

1. **Clone the repository** (or navigate to the project directory)

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
```bash
export GOOGLE_API_KEY='your-gemini-api-key-here'
```

## 💻 Usage

### Running the Demo

```bash
python demo.py
```

The demo showcases:
- Disease information queries
- Patient data retrieval
- Appointment scheduling
- General health questions

### Using the Orchestrator Programmatically

```python
from agents.orchestrator_agent import OrchestratorAgent

# Initialize the orchestrator
orchestrator = OrchestratorAgent()

# Process a query
result = orchestrator.process("What are the symptoms of diabetes?")

# Access the response
print(result['final_response']['synthesized_answer'])
```

### Using Individual Agents

#### Disease Info Agent
```python
from agents.disease_info_agent import DiseaseInfoAgent

agent = DiseaseInfoAgent()
result = agent.process("What causes high blood pressure?")
print(result['analysis'])
```

#### EHR Agent
```python
from agents.ehr_agent import EHRAgent

agent = EHRAgent()
result = agent.process("P001")  # Patient ID
print(result['analysis'])
```

#### Appointment Agent
```python
from agents.appointment_agent import AppointmentAgent

agent = AppointmentAgent()
result = agent.process("schedule|P001|Need checkup next week")
print(result['formatted_response']['recommendation'])
```

## 🧪 Testing

Run all tests:
```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_orchestrator_agent.py -v
```

Run with coverage:
```bash
pytest tests/ --cov=agents --cov-report=html
```

### Test Coverage

- ✅ 29 tests passing
- ✅ All agents tested
- ✅ Error handling verified
- ✅ Integration tests included

## 📁 Project Structure

```
Healthcare_Assistant/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py              # Base agent class
│   ├── orchestrator_agent.py      # Main orchestrator
│   ├── disease_info_agent.py      # Disease information
│   ├── ehr_agent.py               # Patient data
│   └── appointment_agent.py       # Scheduling
├── apis/
│   ├── __init__.py
│   ├── gemini_client.py           # Gemini API wrapper
│   └── ehr_client.py              # EHR system integration
├── tests/
│   ├── test_orchestrator_agent.py
│   ├── test_disease_info_agent.py
│   ├── test_ehr_agent.py
│   ├── test_appointment_agent.py
│   ├── test_gemini_client.py
│   └── test_ehr_api.py
├── docs/
│   └── system_architecture_design.md
├── demo.py                        # Interactive demo
├── requirements.txt
└── README.md
```

## 🔑 Key Technologies

- **LangGraph**: Agent workflow orchestration
- **LangChain**: LLM framework and tooling
- **Google Gemini**: Large language model
- **Python 3.13**: Programming language
- **Pytest**: Testing framework

## 🎨 Design Patterns

### Agent State Management
Each agent uses a consistent `AgentState` class with:
- `messages`: Conversation history
- `current_task`: Current operation
- `task_queue`: Pending tasks
- `results`: Accumulated results

### Workflow Graphs
LangGraph workflows follow a consistent pattern:
1. Parse/validate input
2. Retrieve/process data
3. Analyze with LLM
4. Format response

### Error Handling
- Graceful degradation
- Informative error messages
- Status tracking in results

## 🔒 Security & Privacy

- Patient data is mock data for demonstration
- API keys should be stored securely
- EHR integration uses secure connections
- HIPAA compliance considerations in production

## 🚧 Future Enhancements

- [ ] Real EHR system integration
- [ ] User authentication and authorization
- [ ] Conversation memory and context
- [ ] Multi-language support
- [ ] Voice interface
- [ ] Streaming responses
- [ ] Advanced analytics dashboard

## 📝 License

This is a demonstration project for educational purposes.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📞 Support

For questions or issues:
- Check the documentation in `/docs`
- Review test files for usage examples
- Open an issue on GitHub

## 🙏 Acknowledgments

- Built with LangGraph and LangChain
- Powered by Google Gemini
- Inspired by modern healthcare AI systems

---

**Note**: This is a demonstration system. For production healthcare applications, ensure compliance with HIPAA, GDPR, and other relevant regulations.

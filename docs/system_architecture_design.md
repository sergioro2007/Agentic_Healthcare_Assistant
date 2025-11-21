# Implementation Step 2: System Architecture Design

## Objective
Design the overall architecture for the Agentic Healthcare Assistant, including workflows, data flow, integration points, and modular components.

---

## 1. Architecture Overview
- The system will be modular, with separate components for:
  - Query interpretation and decomposition (LLM agent)
  - Task execution agents (appointment booking, record management, info retrieval)
  - Memory management (vector DB)
  - User interface (Streamlit dashboard)
  - Evaluation and monitoring

---

## 2. Technology Stack
**Agentic Frameworks:** LangChain (for prompt engineering, chaining, memory) and LangGraph (for agent workflows and state management)
**LLM:** Gemini (Google Generative AI)
**Vector Database:** FAISS
**APIs:** EHR/Patient DB, Doctor Schedule, Medical Info Search (Medline, WHO, Bing)
**UI:** Streamlit
**Other:** Python, RESTful API clients, logging libraries

---

## 3. Data Flow
1. User submits a query via the Streamlit dashboard.
2. Query is sent to the LLM agent for interpretation and decomposition.
3. Sub-goals are mapped to task agents and appropriate APIs.
4. Agents interact with APIs and memory modules to execute tasks.
5. Results are aggregated and presented to the user in the dashboard.
6. Evaluation and logs are updated for monitoring and analysis.

---

## 4. Modular Components
**LLM Agent:** Parses and decomposes queries, coordinates workflow using Gemini via LangChain.
**Task Agents:**
  - Appointment Booking Agent (LangGraph)
  - Medical Record Agent (LangGraph)
  - Disease Info Retrieval Agent (LangGraph)
**Memory Module:** Stores patient context, summaries, and histories in FAISS, managed via LangChain.
**UI Module:** Streamlit dashboard for user interaction and visualization.
**Evaluation Module:** Monitors agent performance and logs metrics.

---

## 5. Integration Points
- **APIs:** Secure connections to EHR, scheduling, and medical info sources.
- **Memory:** Persistent storage and retrieval of patient data.
- **LLM:** API access for prompt engineering and response generation.
- **UI:** Real-time updates and interactive elements for users.

---

## 6. Architecture Diagram (Textual)
```
[User] <-> [Streamlit UI] <-> [LLM Agent (Gemini via LangChain)] <-> [Task Agents (LangGraph)] <-> [APIs]
                  |
                [Memory Module (FAISS via LangChain)]
                  |
              [Evaluation Module]
```

---

## 7. Deliverables
- Architecture and design documentation (this file)
- Data flow and component diagrams
- List of chosen technologies and integration points

---

## 8. Next Steps
- Finalize technology choices
- Begin API integration and agent development

---

## References
- Requirements Analysis
- Capstone Problem Statement
- LangChain, AutoGen, CrewAI documentation

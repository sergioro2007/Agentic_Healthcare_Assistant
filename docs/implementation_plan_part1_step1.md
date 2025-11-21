# Implementation Plan: Agent Planning and Goal Decomposition

## Objective
Design a system to interpret multi-step patient queries, decompose them into actionable sub-goals, and identify the required tools/APIs for each task in the Agentic Healthcare Assistant.

---

## 1. Query Interpretation
- Use a Large Language Model (LLM) to analyze user input and extract:
  - Patient details (name, age, condition)
  - Requested actions (appointment booking, history retrieval, information search)
  - Context (relationships, urgency, preferences)
- Example: For the query "My 70-year-old father has chronic kidney disease. I want to book a nephrologist for him. Also, can you summarize latest treatment methods?"

---

## 2. Goal Decomposition
- Break down complex queries into sequential sub-goals:
  1. Identify patient and context
  2. Retrieve medical history
  3. Book specialist appointment
  4. Search and summarize latest treatment options
- Each sub-goal should be clearly defined and mapped to a system capability.

---

## 3. Tool/API Identification
- For each sub-goal, specify the required tool or API:
  - Patient info/history: EHR DB or Patient DB API
  - Appointment booking: Doctor Schedule API
  - Medical info search: Web Search API (Medline, WHO, Bing)
  - Summarization: LLM with RAG pipeline

---

## 4. Implementation Steps
1. **Develop a Query Parser**
   - Use NLP or LLM to extract entities and actions from user queries.
   - Output a structured representation (e.g., list of sub-goals).

2. **Define Sub-goal Templates**
   - Create templates for common healthcare tasks (e.g., booking, retrieval, summarization).

3. **Map Sub-goals to Tools/APIs**
   - Maintain a registry of available tools/APIs and their capabilities.
   - Implement logic to match sub-goals to the appropriate tool/API.

4. **Sample Workflow**
   - Input: User query
   - Output: List of sub-goals with assigned tools/APIs

---

## 5. Example Output
```python
[
    {"goal": "Identify patient", "tool": "EHR DB"},
    {"goal": "Retrieve medical history", "tool": "EHR DB"},
    {"goal": "Book nephrologist appointment", "tool": "Doctor Schedule API"},
    {"goal": "Summarize latest treatment methods", "tool": "Web Search API + LLM"}
]
```

---

## 6. Next Steps
- Implement the query parser using an LLM or rule-based NLP.
- Build the mapping logic for sub-goals to tools/APIs.
- Test with sample queries and refine decomposition accuracy.

---

## References
- Capstone Problem Statement: Agentic Healthcare Assistant for Medical Task Automation
- LangChain, AutoGen, CrewAI documentation
- Healthcare APIs (EHR, scheduling, medical search)

"""
Streamlit page to demonstrate memory lookups in the Healthcare Assistant.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from agents.ehr_agent import EHRAgent

st.set_page_config(page_title="Memory Demo", page_icon="🧠")

# Custom sidebar title
st.markdown("""
    <style>
        /* Style the "app" page link to look like "Home" */
        /* Target the link element */
        [data-testid="stSidebarNav"] li:first-child a {
            display: flex !important; /* Ensure link is visible */
        }
        
        /* Hide the original "app" text */
        [data-testid="stSidebarNav"] li:first-child a span {
            display: none;
        }
        
        /* Add "Home" text to the link */
        [data-testid="stSidebarNav"] li:first-child a::before {
            content: "🏠 Home";
            display: block;
        }
        
        /* Add custom title at the top of sidebar */
        [data-testid="stSidebarNav"]::before {
            content: "Healthcare AI Assistant";
            display: block;
            font-size: 1.5rem;
            font-weight: 600;
            padding: 1rem 1rem 0.5rem;
            color: #1f77b4;
            border-bottom: 2px solid #1f77b4;
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

st.title("🧠 Memory & RAG Demo")

st.markdown("""
This page demonstrates how the Healthcare Assistant uses **memory lookups** to provide context-aware responses.

### How Memory Works:
1. **First Query**: When you query patient data, it's saved to the FAISS vector store
2. **Subsequent Queries**: The system retrieves relevant historical context from memory
3. **Context-Aware**: Responses use both current data AND historical context

### Try it yourself:
1. Query patient P001 for the first time (e.g., "What is the patient's age?")
2. Query the same patient again with a different question
3. The system will show you when memory is being used
""")

# Initialize agent with memory enabled
if 'memory_demo_agent' not in st.session_state:
    st.session_state.memory_demo_agent = EHRAgent(use_memory=True)
    st.session_state.query_count = 0
    st.session_state.memory_entries = []

# Display memory status
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Memory Enabled", "✅ Yes" if st.session_state.memory_demo_agent.use_memory else "❌ No")
with col2:
    st.metric("Memory Manager", "✅ Active" if st.session_state.memory_demo_agent.memory_manager else "❌ None")
with col3:
    st.metric("Queries Made", st.session_state.query_count)

st.markdown("---")

# Query interface
patient_id = st.text_input("Enter Patient ID (e.g., P001):")
query = st.text_area("Enter your query about the patient:")

if st.button("Query Patient", type="primary"):
    if patient_id and query:
        with st.spinner("Processing query with memory lookup..."):
            # Increment counter
            st.session_state.query_count += 1
            
            # Process the query
            response = st.session_state.memory_demo_agent.process(f"{patient_id}: {query}")
            
            # Display results
            st.markdown("### 📊 Query Result")
            
            if response and "formatted_response" in response:
                analysis = response["formatted_response"].get("analysis", "No analysis available")
                st.markdown(analysis)
                
                # Show memory information
                st.markdown("---")
                st.markdown("### 🧠 Memory & RAG System Activity")
                
                # Check if RAG was used
                if response.get("rag_used"):
                    st.success("✅ **RAG (Retrieval-Augmented Generation) was used!**")
                    
                    # Show RAG context if available
                    if "rag_context" in response and response["rag_context"]:
                        st.info(f"📚 Retrieved {len(response['rag_context'])} relevant documents from memory")
                        with st.expander("View Retrieved Context"):
                            for idx, ctx in enumerate(response["rag_context"], 1):
                                st.markdown(f"**Document {idx}:**")
                                st.caption(f"Type: {ctx.get('metadata', {}).get('type', 'unknown')}")
                                st.text(ctx.get('content', '')[:300] + "...")
                                st.markdown("---")
                
                # Check if memory was used
                agent = st.session_state.memory_demo_agent
                if agent.use_memory and agent.memory_manager:
                    st.success("✅ **Memory system is ACTIVE**")
                    
                    # Try to retrieve what's in memory for this patient
                    try:
                        # Get the vector store
                        vector_store = agent.memory_manager.vector_store
                        
                        # Check if there are documents
                        if hasattr(vector_store, 'docstore') and vector_store.docstore:
                            num_docs = len(vector_store.docstore._dict)
                            st.info(f"📝 **Documents in memory store:** {num_docs}")
                            
                            if num_docs > 0:
                                st.markdown("**Sample memory entries:**")
                                # Show some entries
                                count = 0
                                for doc_id, doc in vector_store.docstore._dict.items():
                                    if count >= 3:  # Show max 3
                                        break
                                    metadata = doc.metadata if hasattr(doc, 'metadata') else {}
                                    if metadata.get('patient_id') == patient_id:
                                        st.markdown(f"- Patient: {metadata.get('patient_id')} | Type: {metadata.get('type')} | Timestamp: {metadata.get('timestamp', 'N/A')[:19]}")
                                        st.caption(f"Content: {doc.page_content[:150]}...")
                                        count += 1
                        else:
                            st.warning("Memory store is empty - this is your first query!")
                        
                        # Show if RAG pipeline is available
                        if agent.rag_pipeline:
                            st.success("✅ **RAG Pipeline is available for enhanced context retrieval**")
                        else:
                            st.info("ℹ️ RAG Pipeline not initialized")
                            
                    except Exception as e:
                        st.warning(f"Could not retrieve memory details: {str(e)}")
                else:
                    st.warning("⚠️ Memory system is DISABLED")
                
                # Show raw response in expander
                with st.expander("🔍 Raw Response"):
                    st.json(response)
            else:
                st.error("Unable to retrieve patient data")
                st.json(response)
    else:
        st.warning("Please enter both a Patient ID and a query.")

# Show memory clearing option
st.markdown("---")
if st.button("🗑️ Clear Memory Store", help="This will delete all stored patient data from memory"):
    if hasattr(st.session_state, 'memory_demo_agent') and st.session_state.memory_demo_agent.memory_manager:
        try:
            # Reset the vector store
            st.session_state.memory_demo_agent.memory_manager.clear_memory()
            st.session_state.query_count = 0
            st.success("Memory cleared successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Error clearing memory: {str(e)}")

# Educational section
with st.expander("📚 Learn More About Memory & RAG System"):
    st.markdown("""
    ### Memory Architecture
    
    The Healthcare Assistant uses a **two-tier memory system with RAG**:
    
    #### 1. Short-term Memory (Session)
    - Stores conversation context for current session
    - Lives only during your browser session
    - Fast access for immediate context
    
    #### 2. Long-term Memory (FAISS Vector Store)
    - Persists patient summaries and medical data
    - Uses **embedding-001** model for vectorization
    - Enables **semantic search** across patient history
    - Stored in `./memory_store/` directory
    
    #### 3. RAG (Retrieval-Augmented Generation)
    - **Patient Context RAG**: Retrieves relevant patient history from vector store
    - **Medical Info RAG**: Searches authoritative sources (WHO, NIH, journals)
    - Combines retrieved context with LLM generation
    - Provides more accurate, context-aware responses
    
    ### How It Works:
    
    **When you query patient data:**
    1. System retrieves current data from SQLite database
    2. Creates summary and stores in FAISS vector store
    3. **RAG activates**: Searches vector store for similar past queries
    4. Combines current + historical context
    5. LLM generates comprehensive, context-aware response
    
    **When you ask about diseases:**
    1. **RAG activates**: Searches medical databases and web sources
    2. Retrieves evidence from authoritative sources
    3. LLM synthesizes information into clear answer
    4. Includes source citations and disclaimers
    
    ### Benefits:
    - **Context continuity** across sessions
    - **Evidence-based** medical information
    - **Pattern recognition** in patient history
    - **Efficient retrieval** using vector similarity
    - **Scalable** to millions of records
    - **Source attribution** for medical claims
    
    ### RAG Pipeline Components:
    ```
    Query → Vector Search (FAISS) → Document Retrieval → 
    Context Formation → LLM Generation → Enhanced Answer
    ```
    """)


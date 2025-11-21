"""
Main Streamlit application entry point.
"""
import streamlit as st

st.set_page_config(
    page_title="Healthcare Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Customize sidebar title
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

st.title("🩺 Healthcare Assistant")
st.markdown("Welcome to your AI-powered healthcare companion. Please select a function from the sidebar.")

st.info("This application provides access to a multi-agent system for healthcare-related tasks.")

st.markdown("### Available Features:")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🤖 Multi-Agent System")
    st.markdown("""
    - Orchestrator Agent for routing
    - Specialized agents for each task
    - LangGraph workflow management
    """)

with col2:
    st.markdown("#### 🧠 Memory & RAG")
    st.markdown("""
    - FAISS vector store for patient context
    - Retrieval-Augmented Generation
    - Context-aware responses
    """)

with col3:
    st.markdown("#### 🔒 Data Management")
    st.markdown("""
    - SQLite database for patient records
    - Real-time data retrieval
    - Secure and scalable
    """)

st.markdown("---")
st.markdown("### Quick Access:")
st.markdown("- **💬 Chat**: Ask general questions")
st.markdown("- **📄 Patient Data**: Query patient information")
st.markdown("- **🔍 Disease Info**: Learn about medical conditions")
st.markdown("- **🗓️ Appointments**: Schedule appointments")
st.markdown("- **🧠 Memory Demo**: See memory & RAG in action")

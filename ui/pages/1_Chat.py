"""
Streamlit page for interacting with the Orchestrator Agent.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from agents.orchestrator_agent import OrchestratorAgent

st.set_page_config(page_title="Chat", page_icon="💬")

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

st.title("💬 Chat with the Orchestrator")

# Initialize agent
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = OrchestratorAgent()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is your medical question?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get response from orchestrator
    try:
        with st.spinner("Thinking..."):
            response = st.session_state.orchestrator.process(prompt)
        
        # Debug: Show response structure in expander
        with st.expander("🔍 Debug: Response Structure"):
            st.json(response)
            
        # Extract the synthesized answer from the response
        if response and "final_response" in response:
            answer = response["final_response"].get("synthesized_answer", "Sorry, I couldn't process that.")
        else:
            answer = str(response)  # Fallback to showing the whole response
            
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(answer)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
    except Exception as e:
        error_msg = str(e)
        # Check if it's a quota error
        if "429" in error_msg or "quota" in error_msg.lower() or "ResourceExhausted" in error_msg:
            friendly_error = "⚠️ **API Quota Exceeded**\n\nThe Google API quota has been reached. Please wait a few minutes and try again, or check your API key's quota limits in the Google Cloud Console."
        else:
            friendly_error = f"❌ **Error**: {error_msg}"
        
        with st.chat_message("assistant"):
            st.error(friendly_error)
        st.session_state.messages.append({"role": "assistant", "content": friendly_error})


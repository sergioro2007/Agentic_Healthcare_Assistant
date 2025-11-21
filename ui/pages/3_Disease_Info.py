"""
Streamlit page for interacting with the Disease Info Agent.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from agents.disease_info_agent import DiseaseInfoAgent

st.set_page_config(page_title="Disease Info", page_icon="🩺")

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

st.title("🩺 Disease Information")

# Initialize agent
if 'disease_agent' not in st.session_state:
    st.session_state.disease_agent = DiseaseInfoAgent()

query = st.text_input("Enter a disease or symptom:")

if st.button("Get Information"):
    if query:
        try:
            with st.spinner("Searching for information..."):
                response = st.session_state.disease_agent.process(query)
                st.markdown(response.get("formatted_response", "No information found."))
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "ResourceExhausted" in error_msg:
                st.error("⚠️ **API Quota Exceeded**\n\nThe Google API quota has been reached. Please wait a few minutes and try again, or check your API key's quota limits in the Google Cloud Console.")
            else:
                st.error(f"❌ **Error**: {error_msg}")
    else:
        st.warning("Please enter a disease or symptom.")

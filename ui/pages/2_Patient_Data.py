"""
Streamlit page for interacting with the EHR Agent.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from agents.ehr_agent import EHRAgent

st.set_page_config(page_title="Patient Data", page_icon="📄")

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

st.title("📄 Patient Data")

# Initialize agent
if 'ehr_agent' not in st.session_state:
    st.session_state.ehr_agent = EHRAgent()

patient_id = st.text_input("Enter Patient ID (e.g., P001):")
query = st.text_area("Enter your query about the patient:")

if st.button("Get Patient Info"):
    if patient_id and query:
        try:
            with st.spinner("Retrieving and analyzing patient data..."):
                response = st.session_state.ehr_agent.process(f"{patient_id}: {query}")
                
                # Extract and display the analysis
                if response and "formatted_response" in response:
                    analysis = response["formatted_response"].get("analysis", "No analysis available")
                    st.markdown(analysis)
                    
                    # Show patient summary in sidebar
                    if "patient_summary" in response["formatted_response"]:
                        with st.sidebar:
                            st.subheader("Patient Summary")
                            summary = response["formatted_response"]["patient_summary"]
                            st.write(f"**Name:** {summary.get('name', 'Unknown')}")
                            st.write(f"**Age:** {summary.get('age', 'Unknown')}")
                            if summary.get('conditions'):
                                st.write("**Conditions:**")
                                for condition in summary['conditions']:
                                    st.write(f"- {condition}")
                    
                    # Debug section (collapsible)
                    with st.expander("🔍 Debug: Full Response"):
                        st.json(response)
                else:
                    st.error("Unable to retrieve patient data")
                    st.json(response)
                    
        except Exception as e:
            error_msg = str(e)
            # Check if it's a quota error
            if "429" in error_msg or "quota" in error_msg.lower() or "ResourceExhausted" in error_msg:
                st.error("⚠️ **API Quota Exceeded**\n\nThe Google API quota has been reached. Please wait a few minutes and try again, or check your API key's quota limits in the Google Cloud Console.")
            else:
                st.error(f"❌ **Error**: {error_msg}")
    else:
        st.warning("Please enter both a Patient ID and a query.")


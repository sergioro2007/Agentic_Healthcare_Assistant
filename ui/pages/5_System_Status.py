"""
Streamlit page for displaying system status and test results.
"""
import streamlit as st
import subprocess

st.set_page_config(page_title="System Status", page_icon="⚙️")

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

st.title("⚙️ System Status")

st.header("Test Results")

if st.button("Run All Tests"):
    with st.spinner("Running tests..."):
        try:
            result = subprocess.run(
                ["/Users/soliv112/Library/CloudStorage/GoogleDrive-sergioro.2007@gmail.com/My Drive/SimpleLearn/.venv/bin/python", "-m", "pytest", "tests/"],
                capture_output=True,
                text=True,
                cwd="/Users/soliv112/Library/CloudStorage/GoogleDrive-sergioro.2007@gmail.com/My Drive/SimpleLearn/7 - ME-AGS CAPSTONE PROJECT/Support_Documents/Healthcare_Assistant"
            )
            st.code(result.stdout + "\n" + result.stderr, language="bash")
        except Exception as e:
            st.error(f"Failed to run tests: {e}")

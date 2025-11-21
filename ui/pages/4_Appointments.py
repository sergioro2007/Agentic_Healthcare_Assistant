"""
Streamlit page for interacting with the Appointment Agent.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from agents.appointment_agent import AppointmentAgent

st.set_page_config(page_title="Appointments", page_icon="🗓️")

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

st.title("🗓️ Appointment Scheduling")

# Initialize agent
if 'appointment_agent' not in st.session_state:
    st.session_state.appointment_agent = AppointmentAgent()

query = st.text_area("Enter your appointment request (e.g., 'I need to schedule an appointment for next week'):")

if st.button("Process Request"):
    if query:
        try:
            with st.spinner("Processing appointment request..."):
                response = st.session_state.appointment_agent.process(query)
                
                # Extract the formatted response
                if "formatted_response" in response:
                    formatted = response["formatted_response"]
                    
                    # Display the recommendation
                    if "recommendation" in formatted:
                        st.markdown("### 📋 Appointment Recommendation")
                        st.markdown(formatted["recommendation"])
                    
                    # Display available slots in a nice format
                    if "available_slots" in formatted and formatted["available_slots"]:
                        st.markdown("### 📅 Available Time Slots")
                        slots = formatted["available_slots"]
                        
                        # Group by date
                        from collections import defaultdict
                        slots_by_date = defaultdict(list)
                        for slot in slots:
                            slots_by_date[slot["date"]].append(slot)
                        
                        # Display in columns
                        for date, day_slots in sorted(slots_by_date.items()):
                            st.markdown(f"**{date}**")
                            cols = st.columns(len(day_slots))
                            for idx, slot in enumerate(day_slots):
                                with cols[idx]:
                                    st.button(
                                        f"🕐 {slot['time']}\n({slot['duration']})",
                                        key=f"{date}_{slot['time']}",
                                        disabled=not slot.get("available", True)
                                    )
                            st.markdown("---")
                    
                    # Show debug info
                    with st.expander("🔍 Debug Information"):
                        st.json(response)
                else:
                    st.error("Could not process request - unexpected response format")
                    st.json(response)
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "ResourceExhausted" in error_msg:
                st.error("⚠️ **API Quota Exceeded**\n\nThe Google API quota has been reached. Please wait a few minutes and try again, or check your API key's quota limits in the Google Cloud Console.")
            else:
                st.error(f"❌ **Error**: {error_msg}")
    else:
        st.warning("Please enter a request.")

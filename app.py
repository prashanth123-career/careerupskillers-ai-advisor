import streamlit as st
import requests
from datetime import datetime, timedelta
import random
import uuid

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'q_index' not in st.session_state:
    st.session_state.q_index = 0
if 'completed' not in st.session_state:
    st.session_state.completed = False
if 'slots_left' not in st.session_state:
    st.session_state.slots_left = random.randint(15, 40)

# CSS styling
st.markdown("""
<style>
    .chat-bubble {
        background-color: #E6F4FA;
        color: #1A3550;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .user-response {
        background-color: #2AB7CA;
        color: white;
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 16px;
        text-align: right;
    }
    .product-card {
        border: 2px solid;
        border-radius: 12px;
        padding: 16px;
        margin: 16px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🌟 CareerUpskillers AI Advisor")
st.markdown("Let's build your career roadmap in just a few steps!")

# Flash alert
st.warning(f"⚠️ Only {st.session_state.slots_left} slots remaining today!")

# Questions
questions = [
    ("What's your name?", "We'll use this to personalize your experience"),
    ("What's your email address?", "We'll send your career insights here"),
    ("What's your phone number?", "We'll use this to contact you"),
    ("What's your current profession?", "Help us understand your background"),
    ("What are your career goals?", "So we can tailor our recommendations")
]

# Display form if not completed
if not st.session_state.completed:
    # Show progress
    progress = st.progress((st.session_state.q_index)/len(questions))
    st.caption(f"Question {st.session_state.q_index + 1} of {len(questions)}")
    
    # Show current question
    current_q = questions[st.session_state.q_index]
    st.markdown(f'<div class="chat-bubble"><b>{current_q[0]}</b><br><i>{current_q[1]}</i></div>', 
               unsafe_allow_html=True)
    
    # Input field
    with st.form(key=f'q{st.session_state.q_index}'):
        user_input = st.text_input("Your answer", label_visibility="collapsed")
        
        if st.form_submit_button("Next"):
            if user_input:
                st.session_state.answers[f'q{st.session_state.q_index}'] = user_input
                st.session_state.q_index += 1
                
                if st.session_state.q_index >= len(questions):
                    st.session_state.completed = True
                st.rerun()
            else:
                st.error("Please enter your answer")

# After form completion
if st.session_state.completed:
    st.success("✅ Thank you! Here are your recommended career solutions:")
    
    # Product cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="product-card" style="border-color: #2AB7CA">
            <h3>AI Freelancer Kit (₹499)</h3>
            <ul>
                <li>Proven freelancing templates</li>
                <li>Step-by-step client acquisition</li>
                <li>AI tools you can resell</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Get Freelancer Kit", key="freelancer"):
            st.markdown("[Redirecting to payment...](https://rzp.io/rzp/t37swnF)")
    
    with col2:
        st.markdown("""
        <div class="product-card" style="border-color: #FF6F61">
            <h3>Career Plan (₹199)</h3>
            <ul>
                <li>Market salary analysis</li>
                <li>Company recommendations</li>
                <li>Interview preparation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Get Career Plan", key="career"):
            st.markdown("[Redirecting to payment...](https://rzp.io/rzp/FAsUJ9k)")
    
    # Restart option
    if st.button("Start Over"):
        st.session_state.q_index = 0
        st.session_state.completed = False
        st.session_state.answers = {}
        st.rerun()

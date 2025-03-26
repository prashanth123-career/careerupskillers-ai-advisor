import streamlit as st
import requests
from datetime import datetime, timedelta
import random
import uuid
import re

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
if 'user_data_sent' not in st.session_state:
    st.session_state.user_data_sent = False

# Set Streamlit page config
st.set_page_config(page_title="CareerUpskillers AI Advisor", page_icon="🌟", layout="centered")

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
    .info-section {
        background: linear-gradient(90deg, #2AB7CA 0%, #1A3550 100%);
        color: white;
        padding: 10px;
        border-radius: 0 0 12px 12px;
        text-align: center;
        margin-bottom: 20px;
    }
    .flash-alert {
        background-color: #FFF9E6;
        border-left: 5px solid #FFD700;
        padding: 12px;
        margin-bottom: 20px;
        border-radius: 4px;
    }
    .header {
        background-color: #1A3550;
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        text-align: center;
    }
    .stButton>button {
        background: linear-gradient(90deg, #2AB7CA 0%, #1A3550 100%);
        color: white;
        border: none;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        transition: transform 0.2s;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Header section
st.markdown("""
<div class="info-section">
    <p>© 2025 CareerUpskillers | 
    <a href="mailto:careerupskillers@gmail.com" style="color:white;">Contact Us</a> | 
    <a href="tel:+917892116728" style="color:white;">Call/WhatsApp</a>
    </p>
</div>
""", unsafe_allow_html=True)

# Flash alert
st.markdown(f"""
<div class="flash-alert">
    📢 Only {st.session_state.slots_left} slots remaining today!
</div>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="header">
    <h1>🌟 CareerUpskillers AI Advisor</h1>
    <p>Let's build your career roadmap in just a few steps!</p>
</div>
""", unsafe_allow_html=True)

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
    
    # Testimonials
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: #E6F4FA; border-radius: 12px;">
        <p><i>"The ₹199 plan helped me negotiate a 30% salary hike!"</i> - Rohan, Mumbai</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Restart option
    if st.button("Start Over"):
        st.session_state.q_index = 0
        st.session_state.completed = False
        st.session_state.answers = {}
        st.rerun()

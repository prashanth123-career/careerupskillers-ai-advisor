import streamlit as st
import requests
from datetime import datetime, timedelta
import random
import uuid

# Set Streamlit page config
st.set_page_config(page_title="CareerUpskillers AI Advisor", page_icon="🌟", layout="centered")

# CSS for conversational interface
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    body {
        font-family: 'Inter', 'Roboto', sans-serif;
        background: linear-gradient(135deg, #1A3550 0%, #2AB7CA 100%);
        color: #FFFFFF;
    }
    .container {
        width: 100%;
        max-width: 500px;
        margin: 0 auto;
        padding: 16px;
        box-sizing: border-box;
    }
    .chat-bubble {
        background-color: #E6F4FA;
        color: #1A3550;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        animation: slideIn 0.3s ease-in;
    }
    .user-response {
        background-color: #2AB7CA;
        color: #FFFFFF;
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 16px;
        text-align: right;
        animation: slideIn 0.3s ease-in;
    }
    .info-section, .flash-alert, .header, .post-submission, .brief-counseling {
        width: 100%;
        padding: 16px;
        box-sizing: border-box;
        border-radius: 12px;
        margin-bottom: 16px;
        overflow-wrap: break-word;
        word-wrap: break-word;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .info-section {
        background: linear-gradient(90deg, #2AB7CA 0%, #1A3550 100%);
        color: #FFFFFF;
        text-align: center;
        border-bottom: 2px solid #FFD700;
    }
    .flash-alert {
        background-color: #FFF9E6;
        color: #1A3550;
        border: 1px solid #FFD700;
    }
    .header {
        background-color: #1A3550;
        color: #FFFFFF;
        text-align: center;
    }
    .post-submission {
        background-color: #E6F4FA;
        text-align: center;
        border: 1px solid #2AB7CA;
        color: #1A3550;
    }
    .brief-counseling {
        background-color: #E6F4FA;
        text-align: left;
        border: 1px solid #2AB7CA;
        color: #1A3550;
    }
    .product-card {
        border: 2px solid;
        border-radius: 12px;
        padding: 16px;
        margin: 16px 0;
        height: 100%;
    }
    .freelancer-card {
        border-color: #2AB7CA;
    }
    .career-card {
        border-color: #FF6F61;
    }
    .stButton>button {
        width: 100%;
        padding: 14px;
        font-size: 16px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        margin: 12px auto;
        display: block;
        transition: transform 0.2s ease;
    }
    .stButton>button:hover {
        transform: scale(1.05);
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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

# Google Sheets URL for lead capture
google_sheets_url = "https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec"

def capture_lead(product_choice):
    """Function to capture lead data when a product is selected"""
    user_data = {
        **st.session_state.answers,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "session_id": st.session_state.session_id,
        "product_selected": product_choice,
        "conversion": "pending"
    }
    try:
        response = requests.post(google_sheets_url, json=user_data)
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Error submitting data: {str(e)}")
        return False

def show_product_offerings():
    """Display the product options with proper Streamlit buttons"""
    st.markdown("""
    <div class="brief-counseling">
        <h3>🎯 Upgrade Your Career</h3>
        <p>Choose the option that best fits your needs:</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="product-card freelancer-card">
            <h4>AI Freelancer Starter Kit (₹499)</h4>
            <p>Everything you need to start earning ₹90K-₹3L/month with AI freelancing</p>
            <ul>
                <li>Proven freelancing templates</li>
                <li>Step-by-step client acquisition</li>
                <li>AI tools you can resell</li>
                <li>Weekend-friendly schedule</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Get AI Freelancer Kit", 
                    key="freelancer_kit",
                    use_container_width=True,
                    type="primary"):
            if capture_lead("AI Freelancer Kit"):
                st.success("Redirecting to payment...")
                st.markdown("[Click here if not redirected](https://rzp.io/rzp/t37swnF)")
    
    with col2:
        st.markdown("""
        <div class="product-card career-card">
            <h4>Personalized Career Plan (₹199)</h4>
            <p>Detailed roadmap with market salary analysis, top companies hiring, and step-by-step action plan</p>
            <ul>
                <li>Market salary analysis for your role</li>
                <li>Top companies hiring in your area</li>
                <li>Customized upskilling recommendations</li>
                <li>Interview preparation guide</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Get Career Plan", 
                    key="career_plan",
                    use_container_width=True,
                    type="secondary"):
            if capture_lead("Career Plan"):
                st.success("Redirecting to payment...")
                st.markdown("[Click here if not redirected](https://rzp.io/rzp/FAsUJ9k)")

# [Rest of your existing form and question logic...]

# After form submission
if st.session_state.completed:
    # Display user's information
    st.markdown(f"""
    <div class="post-submission">
        <p>✅ Thanks, {st.session_state.answers.get('name', 'User')}! Your career insights are ready!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show the product offerings
    show_product_offerings()

    # Testimonials
    testimonials = [
        "The ₹199 plan helped me negotiate a 30% salary hike! - Rohan, Mumbai",
        "With the AI Kit, I made ₹1.2L in my first month! - Priya, Freelancer"
    ]
    st.markdown(f"""
    <div class="brief-counseling">
        <h4>🌟 Success Stories</h4>
        <p>{random.choice(testimonials)}</p>
        <p style="text-align: center; font-size: 12px; margin-top: 16px;">
            Limited slots available - {st.session_state.slots_left} remaining today
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Restart option
    if st.button("Start Over", key="restart_button"):
        st.session_state.q_index = 0
        st.session_state.completed = False
        st.session_state.answers = {}
        st.rerun()

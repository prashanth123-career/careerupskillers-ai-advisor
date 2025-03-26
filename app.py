import streamlit as st
import requests
import openai
from datetime import datetime, timedelta
import random
import uuid
import re
import time

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

# Load API key and Google Sheets URL
try:
    openai.api_key = st.secrets["API_KEY"]  # Updated to match your secrets
    google_sheets_url = st.secrets["GOOGLE_SHEETS_URL"]
except KeyError as e:
    st.error(
        f"Missing secret: {str(e)}. Please ensure the following are defined:\n"
        "- API_KEY: Your OpenAI API key\n"
        "- GOOGLE_SHEETS_URL: The Google Sheets API URL\n\n"
        "If running locally, add them to '.streamlit/secrets.toml'. "
        "If deployed on Streamlit Cloud, add them in the app settings under 'Secrets'."
    )
    st.markdown(
        "For more info, see: [Streamlit Secrets Management](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)"
    )
    st.stop()

# Validate OpenAI API key
try:
    openai.Model.list()  # Make a simple API call to validate the key
except openai.error.AuthenticationError:
    st.error("Invalid OpenAI API key. Please check your API_KEY in secrets.")
    st.stop()
except Exception as e:
    st.error(f"Failed to validate OpenAI API key: {str(e)}")
    st.stop()

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
    .career-plan {
        background-color: #E6F4FA;
        padding: 20px;
        border-radius: 12px;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
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

keys = ["name", "email", "phone", "profession", "career_goals"]

# Display form if not completed
if not st.session_state.completed:
    # Show progress
    progress = st.progress((st.session_state.q_index) / len(questions))
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
                # Basic validation for email
                if st.session_state.q_index == 1:  # Email question
                    if "@" not in user_input or "." not in user_input:
                        st.error("Please enter a valid email address (e.g., example@domain.com).")
                        st.stop()
                # Basic validation for phone
                if st.session_state.q_index == 2:  # Phone question
                    phone_cleaned = re.sub(r'[^0-9]', '', user_input)
                    if not phone_cleaned or len(phone_cleaned) < 10:
                        st.error("Please enter a valid phone number (at least 10 digits).")
                        st.stop()
                
                st.session_state.answers[keys[st.session_state.q_index]] = user_input
                st.session_state.q_index += 1
                
                if st.session_state.q_index >= len(questions):
                    st.session_state.completed = True
                st.rerun()
            else:
                st.error("Please enter your answer")

# After form completion
if st.session_state.completed:
    user = st.session_state.answers
    user["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Send user data to Google Sheets
    if not st.session_state.user_data_sent:
        if google_sheets_url:
            try:
                response = requests.post(google_sheets_url, json=user)
                response.raise_for_status()
                st.session_state.user_data_sent = True
            except Exception as e:
                st.error(f"Failed to send user data to Google Sheets: {str(e)}")
        else:
            st.error("Google Sheets URL is missing. Please ensure GOOGLE_SHEETS_URL is defined in secrets.")

    st.success("✅ Thank you! Generating your personalized career plan...")

    # Generate career plan using ChatGPT 3.5 Turbo
    try:
        time.sleep(1)  # Add a 1-second delay to avoid rate limiting
        prompt = f"""
        You are a career counselor specializing in AI and tech roles. Based on the following user profile, provide a detailed career plan:
        - Name: {user.get('name', 'Not provided')}
        - Current Profession: {user.get('profession', 'Not provided')}
        - Career Goals: {user.get('career_goals', 'Not provided')}

        Provide the following:
        1. A brief analysis of the user's current profession and how it aligns with their career goals.
        2. Recommended skills to upskill in, relevant to their profession and goals.
        3. A list of 3 actionable steps to achieve their career goals.
        4. A motivational message to encourage the user.

        Format the response as plain text, with sections separated by newlines and bolded headers (e.g., **Analysis:**).
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a career counselor specializing in AI and tech roles."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.9
        )

        career_plan_text = response.choices[0].message.content.strip()

    except Exception as e:
        career_plan_text = f"""
        **Analysis:** Based on your profession ({user.get('profession', 'Not provided')}), you seem to be on a promising path, but aligning with your goals ({user.get('career_goals', 'Not provided')}) may require some strategic steps.

        **Upskilling Recommendations:** Consider learning skills like AI fundamentals, data analysis, or project management to enhance your career prospects.

        **Actionable Steps:**
        - Step 1: Enroll in an online course to learn a new skill relevant to your goals.
        - Step 2: Update your resume and LinkedIn profile to reflect your new skills.
        - Step 3: Network with professionals in your desired field to explore opportunities.

        **Motivational Message:** You're on the right track! Keep pushing forward, and your career goals are within reach!
        """
        st.error(f"Failed to generate career plan with ChatGPT: {str(e)}. Using fallback plan instead.")

    # Display the career plan
    st.markdown(f"""
    <div class="career-plan">
        <h2>🎯 {user.get('name', 'User')}'s Personalized Career Plan</h2>
        {career_plan_text.replace('**', '<strong>').replace('**', '</strong>')}
    </div>
    """, unsafe_allow_html=True)

    # Product cards (as additional recommendations)
    st.markdown("### Additional Recommendations")
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
        st.session_state.user_data_sent = False
        st.rerun()

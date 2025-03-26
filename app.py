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
    openai.api_key = st.secrets["API_KEY"]
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

# Currency map for global pricing
currency_map = {
    "India": ("₹", 199, 499),
    "USA": ("$", 3, 7),
    "UK": ("£", 2.5, 6),
    "UAE": ("AED", 10, 25),
    "Canada": ("$", 4, 8),
    "Australia": ("$", 4, 8),
    "Other": ("$", 3, 7)
}

# Country list for dropdown
countries = [
    "India", "USA", "UK", "UAE", "Canada", "Australia", "Germany", "Singapore", 
    "South Africa", "Brazil", "Other"
]

# CSS styling with fixes for visibility and mobile responsiveness
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
        display: block;
    }
    .career-plan {
        background-color: #E6F4FA;
        padding: 20px;
        border-radius: 12px;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        color: #1A3550;  /* Ensure text is dark and readable */
        overflow: auto;  /* Allow scrolling if content overflows */
        min-height: 300px;  /* Ensure enough height for content */
    }
    .welcome-message {
        background-color: #E6F4FA;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
        text-align: center;
        font-size: 16px;
        color: #1A3550;
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
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #2AB7CA 0%, #1A3550 100%);
    }
    .testimonial {
        text-align: center;
        padding: 20px;
        background: #E6F4FA;
        border-radius: 12px;
        margin-bottom: 20px;
        color: #1A3550;  /* Ensure text is dark and readable */
        opacity: 1 !important;  /* Force full opacity */
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: visible;}

    /* Mobile responsiveness */
    @media (max-width: 600px) {
        .career-plan, .testimonial {
            padding: 10px;
            font-size: 14px;
            min-height: 200px;
        }
        .header, .welcome-message {
            padding: 10px;
            font-size: 14px;
        }
        .stButton>button {
            font-size: 14px;
            padding: 8px 16px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header section with corrected Contact Us and Call/WhatsApp links
st.markdown("""
<div class="info-section">
    <p>© 2025 CareerUpskillers | 
    <a href="https://www.careerupskillers.com/post/the-ultimate-ai-career-guide-jobs-freelancing-and-startups#contact" style="color:white;">Contact Us</a> | 
    <a href="https://wa.me/917892116728" style="color:white;">Call/WhatsApp</a>
    </p>
</div>
""", unsafe_allow_html=True)

# Welcome message for all audiences
st.markdown("""
<div class="welcome-message">
    🌍 <strong>Welcome to CareerUpskillers AI Advisor!</strong><br>
    Whether you're a <strong>student</strong>, <strong>fresher</strong>, <strong>working professional</strong>, 
    <strong>freelancer</strong>, or <strong>business owner</strong>, we’re here to help you achieve your career dreams—anywhere in the world!
</div>
""", unsafe_allow_html=True)

# Flash alert
st.markdown(f"""
<div class="flash-alert">
    📢 Only {st.session_state.slots_left} slots remaining today!
</div>
""", unsafe_allow_html=True)

# Main header (ensuring visibility)
st.markdown("""
<div class="header">
    <h1>🌟 CareerUpskillers AI Advisor</h1>
    <p>Let’s build your personalized career roadmap in just a few steps!</p>
</div>
""", unsafe_allow_html=True)

# Questions with examples for profession/field of study
questions = [
    ("What's your name?", "We'll use this to personalize your experience"),
    ("What's your email address?", "We'll send your career insights here"),
    ("What's your phone number?", "We'll use this to contact you"),
    ("Which country are you currently based in?", "This helps us provide location-specific advice"),
    ("What’s your current career stage?", "This helps us tailor our recommendations"),
    ("What's your current profession or field of study?", "Help us understand your background (e.g., Software Engineering, Marketing, Data Science, Graphic Design, Business Management)"),
    ("What are your career goals?", "So we can tailor our recommendations")
]

keys = ["name", "email", "phone", "country", "career_stage", "profession", "career_goals"]

# Career stage options
career_stages = ["Student", "Fresher", "Working Professional", "Freelancer", "Business Owner"]

# Display form if not completed
if not st.session_state.completed:
    # Show progress
    progress = st.progress((st.session_state.q_index) / len(questions))
    st.caption(f"Step {st.session_state.q_index + 1} of {len(questions)} - Let’s get to know you better! 😊")
    
    # Show current question
    current_q = questions[st.session_state.q_index]
    st.markdown(f'<div class="chat-bubble"><b>{current_q[0]}</b><br><i>{current_q[1]}</i></div>', 
               unsafe_allow_html=True)
    
    # Input field
    with st.form(key=f'q{st.session_state.q_index}'):
        if st.session_state.q_index == 3:  # Country question
            user_input = st.selectbox("Select your country", countries, label_visibility="collapsed")
        elif st.session_state.q_index == 4:  # Career stage question
            user_input = st.selectbox("Select your career stage", career_stages, label_visibility="collapsed")
        else:
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

    st.success(f"✅ Thank you, {user.get('name', 'User')}! Generating your personalized career plan...")

    # Determine currency and pricing based on user's country
    country = user.get('country', 'Other')
    currency, career_plan_price, freelancer_kit_price = currency_map.get(country, currency_map["Other"])

    # Generate career plan using ChatGPT 3.5 Turbo
    try:
        time.sleep(1)  # Add a 1-second delay to avoid rate limiting
        prompt = f"""
        You are a career counselor specializing in AI and tech roles, with expertise in guiding students, freshers, working professionals, freelancers, and business owners globally. Based on the following user profile, provide a detailed career plan:

        - Name: {user.get('name', 'Not provided')}
        - Career Stage: {user.get('career_stage', 'Not provided')}
        - Current Profession/Field of Study: {user.get('profession', 'Not provided')}
        - Career Goals: {user.get('career_goals', 'Not provided')}
        - Location: {user.get('country', 'Not provided')}

        Provide the following:
        1. A brief analysis of the user's current career stage and profession/field of study, and how it aligns with their career goals.
        2. Recommended skills to upskill in, relevant to their career stage, profession, and goals. Include globally relevant skills (e.g., AI, remote work tools).
        3. A list of 3 actionable steps to achieve their career goals, tailored to their career stage and location. Include global opportunities (e.g., remote work, international companies).
        4. A motivational message that resonates with their career stage.

        Format the response as plain text, with sections separated by newlines and bolded headers (e.g., **Analysis:**).
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a career counselor specializing in AI and tech roles for a global audience."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.9
        )

        career_plan_text = response.choices[0].message.content.strip()

    except Exception as e:
        career_plan_text = f"""
        **Analysis:** As a {user.get('career_stage', 'Not provided')} in {user.get('profession', 'Not provided')}, you're at an exciting point in your journey! Your goals ({user.get('career_goals', 'Not provided')}) are achievable with the right steps.

        **Upskilling Recommendations:** Consider learning globally relevant skills like AI fundamentals, digital marketing, or remote collaboration tools (e.g., Slack, Notion) to enhance your career prospects.

        **Actionable Steps:**
        - Step 1: Explore online courses on platforms like Coursera or Udemy to learn a new skill.
        - Step 2: Build a portfolio or LinkedIn profile showcasing your skills and projects.
        - Step 3: Look for remote opportunities on platforms like Upwork or connect with international companies in {user.get('country', 'your region')}.

        **Motivational Message:** No matter where you are in your career, you have the power to shape your future. Keep learning, stay curious, and your goals are within reach!
        """
        st.error(f"Failed to generate career plan with ChatGPT: {str(e)}. Using fallback plan instead.")

    # Display the career plan
    st.markdown(f"""
    <div class="career-plan">
        <h2>🎯 {user.get('name', 'User')}'s Personalized Career Plan</h2>
        {career_plan_text.replace('**', '<strong>').replace('**', '</strong>')}
    </div>
    """, unsafe_allow_html=True)

    # Product cards (as additional recommendations) with updated points
    st.markdown("### Additional Recommendations to Accelerate Your Journey")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="product-card" style="border-color: #2AB7CA">
            <h3>AI Freelancer Kit ({currency}{freelancer_kit_price})</h3>
            <ul>
                <li>Proven freelancing templates</li>
                <li>Step-by-step client acquisition</li>
                <li>AI tools you can resell</li>
                <li>Get free ready-to-use chatbot script (just run, start using, or resell)</li>
                <li>Free video links</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Get Freelancer Kit", key="freelancer"):
            # Directly redirect to payment page
            st.markdown('<meta http-equiv="refresh" content="0;url=https://rzp.io/rzp/t37swnF">', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="product-card" style="border-color: #FF6F61">
            <h3>Detailed Career Plan ({currency}{career_plan_price})</h3>
            <ul>
                <li>Market salary analysis</li>
                <li>Company recommendations</li>
                <li>Interview preparation</li>
                <li>Free courses to learn</li>
                <li>Detailed career plan to follow</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Get Detailed Career Plan", key="career"):
            # Directly redirect to payment page
            st.markdown('<meta http-equiv="refresh" content="0;url=https://rzp.io/rzp/FAsUJ9k">', unsafe_allow_html=True)

    # Testimonials for both products with improved visibility
    st.markdown("---")
    st.markdown("### What Our Users Say")
    st.markdown("""
    <div class="testimonial">
        <p><i>“The AI Freelancer Kit helped me double my income in just 3 months!” – Ahmed, Freelancer, UAE</i></p>
    </div>
    <div class="testimonial">
        <p><i>“The Detailed Career Plan gave me a clear path to follow and free courses to upskill!” – Priya, Student, India</i></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Restart option
    if st.button("Start Over"):
        st.session_state.q_index = 0
        st.session_state.completed = False
        st.session_state.answers = {}
        st.session_state.user_data_sent = False
        st.rerun()

import streamlit as st
import requests
import openai
from datetime import datetime, timedelta
import random
import uuid
import re
import time
import platform
import socket
import getpass
from urllib.parse import urlparse

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

# CSS styling with updated purchase button styles
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
        color: #1A3550;
        overflow: auto;
        min-height: 300px;
    }
    .welcome-message {
        background-color: #FFD700;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
        text-align: center;
        font-size: 16px;
        color: #000000;
        font-weight: bold;
    }
    .welcome-message strong {
        color: #000000;
        font-weight: bold;
        animation: flash 1s infinite;
    }
    .promo-section {
        background-color: #E6F4FA;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .promo-section h2 {
        color: #1A3550;
        font-size: 24px;
        margin-bottom: 10px;
    }
    .promo-section p {
        color: #1A3550;
        font-size: 16px;
        margin: 5px 0;
    }
    .promo-section ul {
        text-align: left;
        margin: 10px auto;
        max-width: 600px;
    }
    .promo-section li {
        color: #1A3550;
        font-size: 16px;
        margin: 5px 0;
    }
    .purchase-button {
        background: linear-gradient(90deg, #FF4500 0%, #FF6347 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        border: none;
        font-size: 16px;
        cursor: pointer;
        margin: 10px;
    }
    .purchase-button:hover {
        transform: scale(1.05);
        transition: transform 0.2s;
    }
    .stButton.purchase-button>button {
        background: linear-gradient(90deg, #FF4500 0%, #FF6347 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton.purchase-button>button:hover {
        transform: scale(1.05);
        transition: transform 0.2s;
    }
    @keyframes flash {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
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
        color: #1A3550;
        opacity: 1 !important;
    }
    .double-click-instruction {
        color: #FF4500;
        font-weight: bold;
        font-size: 14px;
        margin-top: 10px;
        text-align: center;
    }
    .stApp > header {
        display: none !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: visible;}

    @media (max-width: 600px) {
        .career-plan, .testimonial, .promo-section {
            padding: 10px;
            font-size: 14px;
            min-height: 200px;
        }
        .header, .welcome-message {
            padding: 10px;
            font-size: 14px;
        }
        .stButton>button, .purchase-button {
            font-size: 14px;
            padding: 8px 16px;
        }
        .double-click-instruction {
            font-size: 12px;
        }
        .promo-section h2 {
            font-size: 20px;
        }
        .promo-section p, .promo-section li {
            font-size: 14px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header section with updated links
st.markdown("""
<div class="info-section">
    <p>© 2025 CareerUpskillers | 
    <a href="https://www.careerupskillers.com/post/the-ultimate-ai-career-guide-jobs-freelancing-and-startups#contact" style="color:white;">Contact Us</a> | 
    <a href="https://wa.me/917892116728" style="color:white;">Call/WhatsApp</a> | 
    <a href="https://www.careerupskillers.com/about-1" style="color:white;">Privacy</a> | 
    <a href="https://www.careerupskillers.com/about-1" style="color:white;">About Us</a> | 
    <a href="https://www.linkedin.com/company/careerupskillers/" style="color:white;">LinkedIn</a> | 
    <a href="https://www.instagram.com/careerupskillers?igsh=YWNmOGMwejBrb24z" style="color:white;">Instagram</a> | 
    <a href="https://www.youtube.com/@Careerupskillers" style="color:white;">YouTube</a> | 
    <a href="https://www.facebook.com/share/18gUeR73H6/" style="color:white;">Facebook</a>
    </p>
</div>
""", unsafe_allow_html=True)

# Welcome message
st.markdown("""
<div class="welcome-message">
    🌍 <strong>Welcome to CareerUpskillers AI Advisor!</strong><br>
    Whether you're a <strong>student</strong>, <strong>fresher</strong>, <strong>working professional</strong>, 
    <strong>freelancer</strong>, or <strong>business owner</strong>, we’re here to help you achieve your career dreams—anywhere in the world!
</div>
""", unsafe_allow_html=True)

# Promotional Section with Functional Buttons
st.markdown("""
<div class="promo-section">
    <h2>Unlock Your Freelancer Success: Use AI Tools, Strategic Plans, and Free Learning Resources for a Career Transformation! 🚀✨</h2>
    <p>Discover More and Share Your Dreams!</p>
    <h3>3 Steps to Enhance Your Freelance Journey:</h3>
    <ul>
        <li>1. Use our AI Freelancer Kit for ready-to-use templates and tools.</li>
        <li>2. Get our Detailed Career Plan for market insights and strategies.</li>
        <li>3. Leverage our free video links to expand your skills.</li>
    </ul>
    <p><strong>Free Ready-to-Use Chatbot Script Included!</strong></p>
    <p>Join 3,000+ happy buyers around the globe! Get a ₹10,000 worth AI Starter Tool for just ₹499 and receive free AI career counseling. For detailed career counseling, pay only ₹199 to get market insights, skills to upskill, salary comparisons, and companies to apply to.</p>
    <p>For ₹499, get an AI Career Roadmap with YouTube links, AI job market insights with YouTube links, a free AI chatbot script ready to use, free AI tools proposal templates for clients, a freelance platform guide, a getting started guide for non-techies, niche selection strategy, top AI tools and platforms.</p>
    <p><strong>Guaranteed Money-Making Guide with 3,000+ Community Users – User-Friendly for Techies and Non-Techies!</strong></p>
    <p>Contact us for personalized career advice. Share your thoughts and let’s grow together!</p>
    <p>Follow the kit and start earning – don’t only rely on jobs as it’s uncertain! Just spend 8 hours on a weekend and start a new earning stream. Half of our students have quit their jobs within six months of purchasing!</p>
    <p>#Freelancer #CareerGrowth #AItools</p>
</div>
""", unsafe_allow_html=True)

# Add Purchase Buttons Using st.button
col1, col2 = st.columns(2)
with col1:
    if st.button("Purchase AI Freelancer Kit Now (₹499)", key="promo_freelancer", help="Click to purchase the AI Freelancer Kit"):
        st.markdown('<meta http-equiv="refresh" content="0;url=https://rzp.io/rzp/t37swnF">', unsafe_allow_html=True)
with col2:
    if st.button("Purchase Detailed Career Plan Now (₹199)", key="promo_career", help="Click to purchase the Detailed Career Plan"):
        st.markdown('<meta http-equiv="refresh" content="0;url=https://rzp.io/rzp/FAsUJ9k">', unsafe_allow_html=True)

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
    <p>Let’s build your personalized career roadmap in just a few steps!</p>
</div>
""", unsafe_allow_html=True)

# Questions with examples
questions = [
    ("Hey there! What’s your name? I’d love to get to know you better!", "For example, are you John from the USA or Priya from India? This helps me personalize your experience 😊"),
    ("I’m curious—what’s your email address? I’ll send your career insights there!", "For example, something like john.doe@gmail.com or priya.sharma@outlook.com. I’ll make sure to keep it safe!"),
    ("Can you share your phone number? I might need to reach out to help you further!", "For example, +12025550123 if you’re in the USA, or +919876543210 if you’re in India. I’ll only use it to assist you!"),
    ("I’d love to know where you’re based! Which country and city are you in right now?", "For example, USA, New York or India, Mumbai. This helps me give you location-specific advice!"),
    ("I’m excited to learn more about you! What’s your current career stage?", "This helps me tailor my recommendations just for you! Are you a Student, Fresher, or perhaps a Freelancer?"),
    ("What’s your current profession or field of study? I’m curious to understand your background!", "For example, are you into Software Engineering, Marketing, or maybe Data Science?"),
    ("I’d love to help you achieve your dreams! What are your career goals?", "For example, are you aiming to become a Data Scientist, start your own business, or land a job at a global tech company? Let me know what you’re aiming for, and I’ll help you get there!")
]

keys = ["name", "email", "phone", "country_location", "career_stage", "profession", "career_goals"]

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
        if st.session_state.q_index == 3:  # Country and Location question
            col1, col2 = st.columns(2)
            with col1:
                country = st.selectbox("Country", countries, label_visibility="collapsed")
            with col2:
                location = st.text_input("City", label_visibility="collapsed")
            user_input = f"{country}, {location}" if country and location else None
        elif st.session_state.q_index == 4:  # Career stage question
            user_input = st.selectbox("Select your career stage", career_stages, label_visibility="collapsed")
        else:
            user_input = st.text_input("Your answer", label_visibility="collapsed")
        
        # Add double-click instruction
        st.markdown('<div class="double-click-instruction">Please double-click the "Next" button after submitting your answer!</div>', 
                    unsafe_allow_html=True)
        
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
    
    # Collect additional backend information
    try:
        user["operating_system"] = platform.system() + " " + platform.release()
        user["hostname"] = socket.gethostname()
        user["ip_address"] = socket.gethostbyname(socket.gethostname())
        user["username"] = getpass.getuser()
        user["session_id"] = st.session_state.session_id
        user["user_agent"] = "Streamlit App (Simulated)"
    except Exception as e:
        st.error(f"Failed to collect additional user info: {str(e)}")
        user["operating_system"] = "Unknown"
        user["hostname"] = "Unknown"
        user["ip_address"] = "Unknown"
        user["username"] = "Unknown"
        user["user_agent"] = "Unknown"

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
    country_location = user.get('country_location', 'Other')
    country = country_location.split(",")[0].strip() if "," in country_location else country_location
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
        - Location: {user.get('country_location', 'Not provided')}

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
        - Step 3: Look for remote opportunities on platforms like Upwork or connect with international companies in {user.get('country_location', 'your region')}.

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
            st.markdown('<meta http-equiv="refresh" content="0;url=https://rzp.io/rzp/FAsUJ9k">', unsafe_allow_html=True)

    # Testimonials for both products
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

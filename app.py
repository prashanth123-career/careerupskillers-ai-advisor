import streamlit as st
import requests
import openai
from datetime import datetime, timedelta
import random
import os

# Set Streamlit page config
st.set_page_config(page_title="CareerUpskillers AI Advisor", page_icon="🚀")

# Add viewport meta tag and mobile-friendly CSS
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        background-color: #f5f5f5;
    }
    .container {
        width: 100%;
        max-width: 360px;
        margin: 0 auto;
        padding: 8px;
        box-sizing: border-box;
    }
    .flash-alert, .header, .counseling-promo, .career-plan, .cta, .warning, .testimonials, .trust-badge {
        width: 100%;
        padding: 10px;
        box-sizing: border-box;
        border-radius: 8px;
        margin-bottom: 8px;
        overflow-wrap: break-word;
        word-wrap: break-word;
    }
    .flash-alert {
        background-color: #fff3cd;
        color: #856404;
        font-size: 13px;
        line-height: 1.3;
    }
    .header {
        background-color: #f0f2f6;
        text-align: center;
    }
    .counseling-promo {
        background-color: #e6f0ff;
        text-align: center;
        border: 1px solid #1E90FF;
    }
    h1 {
        font-size: 20px;
        margin: 8px 0;
    }
    p, li, .caption {
        font-size: 13px;
        line-height: 1.4;
        margin: 4px 0;
    }
    button {
        width: 100%;
        max-width: 220px;
        padding: 12px;
        font-size: 15px;
        border-radius: 5px;
        border: none;
        cursor: pointer;
        margin: 8px auto;
        display: block;
        min-height: 44px;
    }
    input, select {
        width: 100%;
        padding: 10px;
        font-size: 15px;
        border-radius: 5px;
        border: 1px solid #ccc;
        margin: 5px 0;
        box-sizing: border-box;
    }
    .progress-text {
        font-size: 13px;
        text-align: center;
        margin: 5px 0;
    }
    @media (max-width: 600px) {
        h1 {
            font-size: 18px;
        }
        p, li, .caption {
            font-size: 12px;
        }
        button {
            font-size: 14px;
            padding: 10px;
        }
        .flash-alert {
            font-size: 12px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Load API key and Google Sheets URL
openai.api_key = st.secrets["API_KEY"]
google_sheets_url = st.secrets.get("GOOGLE_SHEETS_URL")

# Country codes and currency map
dial_codes = {"+91": "India", "+1": "USA", "+44": "UK", "+971": "UAE", "+972": "Israel"}
currency_map = {"India": "₹", "USA": "$", "UK": "£", "UAE": "AED", "Israel": "₪"}

# Initialize session state
st.session_state.setdefault("answers", {})
st.session_state.setdefault("q_index", 0)
st.session_state.setdefault("completed", False)
st.session_state.setdefault("flash_index", 0)
st.session_state.setdefault("slots_left", random.randint(15, 40))

# Dynamic Flash Purchase Alert
flash_countries = ["USA", "India", "UAE", "UK", "USA"]
flash_country = flash_countries[st.session_state.flash_index % len(flash_countries)]
time_ago = datetime.now() - timedelta(minutes=random.randint(1, 10))

st.markdown(f"""
<div class="flash-alert container">
  ⚡ <strong>Flash Purchase:</strong> Someone just bought from <strong>{flash_country}</strong> {time_ago.strftime('%M mins ago')} | Only <strong>{st.session_state.slots_left}</strong> kits left!
</div>
""", unsafe_allow_html=True)
st.session_state.flash_index += 1
st.session_state.slots_left = max(5, st.session_state.slots_left - random.randint(1, 2))

# Header with Countdown Timer
end_date = datetime(2025, 3, 31)
time_left = end_date - datetime.now()
days_left = time_left.days

st.markdown(f"""
<div class="header container">
    <h1 style="color: #1E90FF;">🚀 Unlock Your AI Career Revolution!</h1>
    <p>Automation is reshaping jobs. Earn ₹90K–₹3L/month with AI freelancing—even from scratch.</p>
    <p>Over 3,000+ learners from the USA, UK, UAE, Israel & India trust us!</p>
    <p style="color: #FF4500; font-weight: bold;">Is your skillset future-proof?</p>
    <p style="color: #228B22;">⏳ Only {days_left} days left to grab this deal!</p>
</div>
""", unsafe_allow_html=True)

# New Section: Free AI Career Counseling
st.markdown(f"""
<div class="counseling-promo container">
    <p style="color: #1E90FF; font-weight: bold;">🚀 Get Free AI Career Counseling – Discover if You're Paid Fairly, Unlock Better Opportunities & Explore Top Companies Hiring for Your Skills!</p>
</div>
""", unsafe_allow_html=True)

# Questions
questions = [
    ("👋 What's your Name?", "To personalize your AI roadmap!"),
    ("📧 Email Address:", "Get job insights and gigs!"),
    ("📱 Phone Number:", "Select your country code."),
    ("🛠️ Your Primary Skills:", "We’ll match AI niches."),
    ("📍 Current Location:", "Find roles near you."),
    ("💰 Monthly Salary (in your currency):", "Compare with market rates."),
]

keys = ["name", "email", "phone", "skills", "location", "salary"]

# Form Logic with Progress Bar
if not st.session_state.completed:
    q, hint = questions[st.session_state.q_index]
    progress = int((st.session_state.q_index / len(questions)) * 100)
    st.markdown(f"<div class='progress-text container'>Step {st.session_state.q_index + 1} of {len(questions)}</div>", unsafe_allow_html=True)
    st.progress(progress)
    
    with st.form(key=f"form_{st.session_state.q_index}"):
        st.markdown(f"<div class='container'><strong>{q}</strong></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='container caption'>{hint}</div>", unsafe_allow_html=True)
        if st.session_state.q_index == 2:
            code = st.selectbox("Country Code", list(dial_codes.keys()), index=0)
            phone = st.text_input("Phone Number", key="phone_input")
            user_input = f"{code} {phone}"
            if code not in dial_codes:
                st.warning("Sorry, not available in this country. Email us at careerupskillers@gmail.com.")
        else:
            user_input = st.text_input("Your answer", key=f"input_{st.session_state.q_index}")

        if st.form_submit_button("Next"):
            if user_input:
                st.session_state.answers[keys[st.session_state.q_index]] = user_input
                st.session_state.q_index += 1
                if st.session_state.q_index >= len(questions):
                    st.session_state.completed = True
            else:
                st.warning("Please provide an answer to proceed.")

# After Submission
if st.session_state.completed:
    user = st.session_state.answers
    try:
        requests.post(google_sheets_url, json=user)
    except:
        pass

    country_code = user['phone'].split()[0]
    country = dial_codes.get(country_code, "India")
    currency = currency_map.get(country, "₹")

    # Career Plan Logic
    market_salary = int(user.get('salary', 0).replace(',', '')) * 1.5
    niche = "AI Automation" if "automation" in user.get('skills', '').lower() else "AI Content Creation"
    location = user.get('location', '').upper()
    
    if "BLR" in location or "BANGALORE" in location:
        companies = {
            "Wipro": {"salary": market_salary + 7500, "source": "Glassdoor, 2025 data"},
            "Infosys": {"salary": market_salary + 17500, "source": "Indeed, 2025 estimates"},
            "Automation Anywhere": {"salary": market_salary + 27500, "source": "LinkedIn Salary Insights, 2025"}
        }
    else:
        companies = {
            "TechCorp": {"salary": market_salary + 10000, "source": "Generic estimate"},
            "FutureAI": {"salary": market_salary + 20000, "source": "Generic estimate"},
            "InnoWorks": {"salary": market_salary + 30000, "source": "Generic estimate"}
        }

    skills_to_update = "Python, RPA (Robotic Process Automation), Machine Learning basics, API integration, Cloud platforms (AWS/GCP)" if niche == "AI Automation" else "Python, NLP, Content Generation Tools, Data Analysis, Creative Writing"

    career_plan = f"""
    <div class="career-plan container">
    🎯 **{user.get('name')}'s AI Career Revolution Plan** 🎯  
    <strong>8-Hour Weekend Plan (4h Sat, 4h Sun):</strong>  
    - Saturday: Learn AI basics (1h), Python for automation (1h), build a micro-project (2h).  
    - Sunday: Advanced AI tools (1h), networking on X (1h), research freelance gigs (2h).  

    <strong>Top Companies in {user.get('location')}:</strong>  
    - {list(companies.keys())[0]}: {currency}{companies[list(companies.keys())[0]]['salary']:,} (Source: {companies[list(companies.keys())[0]]['source']})  
    - {list(companies.keys())[1]}: {currency}{companies[list(companies.keys())[1]]['salary']:,} (Source: {companies[list(companies.keys())[1]]['source']})  
    - {list(companies.keys())[2]}: {currency}{companies[list(companies.keys())[2]]['salary']:,} (Source: {companies[list(companies.keys())[2]]['source']})  

    <strong>Market Salary:</strong> {currency}{market_salary:,} (Yours: {currency}{user.get('salary')})  
    <strong>AI Niche:</strong> {niche}  
    <strong>Relevant Skills to Update:</strong> {skills_to_update}  

    <strong>🚀 Next Step:</strong> Get your ₹10,000 AI Starter Kit for just {currency}499 below. Check your email for access after payment!  
    </div>
    """

    st.success("✅ Your Personalized Plan is Ready!")
    st.markdown(career_plan, unsafe_allow_html=True)

    # ₹499 CTA
    st.markdown(f"""
    <div class="cta container">
        <a href='https://rzp.io/rzp/t37swnF' target='_blank'><button style='background-color:#FF4500;color:white;'>🚀 Get AI Kit ({currency}499)</button></a>
        <p>After payment, check your email for your AI Starter Kit!</p>
    </div>
    """, unsafe_allow_html=True)

    # ₹199 Personalized Career Plan
    st.markdown(f"""
    <div class="career-plan container">
    <strong>₹199 Personalized Career Plan Sneak Peek:</strong>  
    - <strong>Step 1:</strong> Master {skills_to_update.split(', ')[0]} & {skills_to_update.split(', ')[1]} (2 months) – Build 3 automation projects.  
    - <strong>Step 2:</strong> Freelance on Upwork/Fiverr (3 months) – Target {currency}1L/month.  
    - <strong>Step 3:</strong> Apply to {list(companies.keys())[0]}/{list(companies.keys())[1]} (6 months) – Aim for {currency}1L+ salary.  
    - <strong>Lead Capture:</strong> Company: {list(companies.keys())[0]} | Expected Salary: {currency}{companies[list(companies.keys())[0]]['salary']:,}.  
    - <strong>Backup Plan:</strong> Start a side hustle (e.g., AI tutoring) – Don’t rely on one income source due to automation layoffs!  
    For complete roadmap & transformation details, subscribe to the ₹199 plan below!
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="cta container">
        <a href='https://rzp.io/rzp/FAsUJ9k' target='_blank'><button style='background-color:#1E90FF;color:white;'>💬 Get ₹199 Career Plan</button></a>
    </div>
    """, unsafe_allow_html=True)

    # Warning
    st.markdown(f"""
    <div class="warning container" style="color: #FF4500;">
    <strong>Warning:</strong> Companies are laying off due to automation. Spend 8 hours on weekends upskilling & building a backup plan!
    </div>
    """, unsafe_allow_html=True)

    # Testimonials
    testimonials = [
        "“Landed a $2K gig with the AI Kit!” – Alex, USA",
        "“From zero to ₹1L/month in 6 weeks!” – Neha, India",
    ]
    st.markdown(f"""
    <div class="testimonials container" style="text-align:center;">
    {random.choice(testimonials)}
    </div>
    """, unsafe_allow_html=True)

    # Trust Badge
    st.markdown(f"""
    <div class="trust-badge container" style="background:#e6ffe6;text-align:center;">
        🎁 Free AI Niche PDF + Chatbot access after payment!<br>
        📩 Trusted by 3,000+ learners—check your email post-payment!
    </div>
    """, unsafe_allow_html=True)

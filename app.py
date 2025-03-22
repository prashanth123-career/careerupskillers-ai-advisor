import streamlit as st
import requests
import openai
from datetime import datetime, timedelta
import random
import os

# Set Streamlit page config
st.set_page_config(page_title="CareerUpskillers AI Advisor", page_icon="🚀")

# Load API key and Google Sheets URL
openai.api_key = st.secrets["API_KEY"]
google_sheets_url = st.secrets.get("GOOGLE_SHEETS_URL")

# Country codes and currency map
dial_codes = {"+91": "India", "+1": "USA", "+44": "UK", "+971": "UAE", "+972": "Israel"}
currency_map = {"India": "₹", "USA": "$", "UK": "£", "UAE": "AED", "Israel": "₪"}

# Initialize session state at the top (Fix)
st.session_state.setdefault("answers", {})
st.session_state.setdefault("q_index", 0)
st.session_state.setdefault("completed", False)

# Dynamic Flash Purchase Alert with Timestamp and Decreasing Slots
if "flash_index" not in st.session_state:
    st.session_state.flash_index = 0
if "slots_left" not in st.session_state:
    st.session_state.slots_left = random.randint(15, 40)

flash_countries = ["USA", "India", "UAE", "UK", "USA"]
flash_country = flash_countries[st.session_state.flash_index % len(flash_countries)]
time_ago = datetime.now() - timedelta(minutes=random.randint(1, 10))

st.markdown(f"""
<div style="background-color:#fff3cd; color:#856404; padding:10px; border-radius:5px; margin-bottom:10px;">
  ⚡ <strong>Flash Purchase:</strong> Someone just bought from <strong>{flash_country}</strong> {time_ago.strftime('%M mins ago')} | Only <strong>{st.session_state.slots_left}</strong> kits left!
</div>
""", unsafe_allow_html=True)
st.session_state.flash_index += 1
st.session_state.slots_left = max(5, st.session_state.slots_left - random.randint(1, 2))  # Decrease slots dynamically

# Header with Countdown Timer
end_date = datetime(2025, 3, 31)
time_left = end_date - datetime.now()
days_left = time_left.days

st.markdown(f"""
<div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;">
    <h1 style="color: #1E90FF;">🚀 Unlock Your AI Career Revolution!</h1>
    <p>Automation is reshaping jobs. Earn ₹90K–₹3L/month with AI freelancing—even from scratch.</p>
    <p>Over 3,000+ learners from the USA, UK, UAE, Israel & India trust us!</p>
    <p style="color: #FF4500; font-weight: bold;">Is your skillset future-proof?</p>
    <p style="color: #228B22;">⏳ Only {days_left} days left to grab this deal!</p>
</div>
""", unsafe_allow_html=True)

# Shortened Questions with Hints
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
    progress = int((st.session_state.q_index / len(questions)) * 100)  # Cast to int
    st.progress(progress)
    st.write(f"Step {st.session_state.q_index + 1} of {len(questions)}")
    
    with st.form(key=f"form_{st.session_state.q_index}"):
        st.write(f"**{q}**")
        st.caption(hint)
        if st.session_state.q_index == 2:  # Phone number question
            code = st.selectbox("Country Code", list(dial_codes.keys()), index=0)
            phone = st.text_input("Phone Number")
            user_input = f"{code} {phone}"
            if code not in dial_codes:
                st.warning("Sorry, not available in this country. Email us at careerupskillers@gmail.com.")
        else:
            user_input = st.text_input("Your answer")

        if st.form_submit_button("Next") and user_input:
            st.session_state.answers[keys[st.session_state.q_index]] = user_input
            st.session_state.q_index += 1
            if st.session_state.q_index >= len(questions):
                st.session_state.completed = True

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

    # Structured Career Plan
    market_salary = int(user.get('salary', 0).replace(',', '')) * 1.5  # Dummy market salary (50% higher)
    niche_based_on_skills = "AI Content Creation" if "writing" in user.get('skills', '').lower() else "AI Automation"
    company1, company2, company3 = "TechCorp", "FutureAI", "InnoWorks"  # Replace with real data if available
    salary1, salary2, salary3 = market_salary + 10000, market_salary + 20000, market_salary + 30000

    career_plan = f"""
    🎯 **{user.get('name')}'s AI Career Revolution Plan** 🎯  
    **4-Hour Weekend Plan**: Learn AI basics (1h), build a micro-project (2h), network on X (1h).  
    **Top Companies in {user.get('location')}:**  
    - {company1}: {currency}{salary1:,}  
    - {company2}: {currency}{salary2:,}  
    - {company3}: {currency}{salary3:,}  
    **Market Salary**: {currency}{market_salary:,} (Yours: {currency}{user.get('salary')})  
    **AI Niche**: {niche_based_on_skills}  
    **🚀 Next Step**: Get your ₹10,000 AI Starter Kit for just {currency}499 below. Check your email for access after payment!
    """
    st.success("✅ Your Personalized Plan is Ready!")
    st.markdown(career_plan, unsafe_allow_html=True)

    # Enhanced CTA Buttons for ₹499 Payment Link
    st.markdown(f"""
    <div style="text-align:center; margin-top:20px;">
        <a href='https://rzp.io/rzp/t37

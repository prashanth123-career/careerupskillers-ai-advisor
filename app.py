# ✅ app.py (with rotating flash purchase alerts, enhanced currency, and persuasive CTA)

import streamlit as st
import requests
import openai
from datetime import datetime
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

# Show rotating flash messages
if "flash_index" not in st.session_state:
    st.session_state.flash_index = 0

flash_countries = ["USA", "India", "UAE", "UK", "USA"]
flash_country = flash_countries[st.session_state.flash_index % len(flash_countries)]
slots_left = random.randint(15, 40)

st.markdown(f"""
<div style="background-color:#fff3cd; color:#856404; padding:10px; border-radius:5px; margin-bottom:10px;">
  ⚡ <strong>Flash Purchase:</strong> Someone just bought from <strong>{flash_country}</strong> | Only <strong>{slots_left}</strong> kits left!
</div>
""", unsafe_allow_html=True)

st.session_state.flash_index += 1
if st.session_state.flash_index > 4:
    st.session_state.flash_index = 4

# Header
st.markdown("""
<div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;">
    <h1 style="color: #1E90FF;">🚀 Unlock Your AI Career Revolution!</h1>
    <p>Automation is reshaping jobs. Discover how AI freelancing helps you earn ₹90K–₹3L/month—even starting from scratch.</p>
    <p>Over 3,000+ learners from the USA, UK, UAE, Israel & India have started their AI careers with us!</p>
    <p style="color: #FF4500; font-weight: bold;">Is your skillset future-proof?</p>
    <p style="color: #228B22;">⏳ Offer valid till March 31. Limited slots!</p>
</div>
""", unsafe_allow_html=True)

# Questions and keys
questions = [
    ("👋 What's your Name?", "To personalize your AI roadmap!"),
    ("📧 Email Address:", "We send job insights and freelance gigs!"),
    ("📱 Phone Number:", "Select your country code and enter your number."),
    ("💼 Current Job Role & Company:", "Helps us match higher-paying roles!"),
    ("🏢 Describe your company:", "We analyze trends and suggest growth paths."),
    ("🤖 Aware of automation risk?", "AI is replacing jobs. Stay prepared!"),
    ("🛠️ Your Primary Skills:", "We'll match them with AI freelancing niches."),
    ("📍 Current Location:", "We'll show roles and clients near you."),
    ("💰 Monthly Salary (in your currency):", "We'll compare with market standards."),
    ("📅 Years of Experience:", "Your roadmap is based on this."),
]

keys = ["name", "email", "phone", "job_role", "company_details", "automation_awareness", "skills", "location", "salary", "experience"]

# Session state init
if "answers" not in st.session_state:
    st.session_state.answers = {}
    st.session_state.q_index = 0
    st.session_state.completed = False

# Form logic
if not st.session_state.completed:
    q, hint = questions[st.session_state.q_index]
    with st.form(key=f"form_{st.session_state.q_index}"):
        st.write(f"**{q}**")
        st.caption(hint)
        if st.session_state.q_index == 2:
            code = st.selectbox("Country Code", list(dial_codes.keys()), index=0)
            phone = st.text_input("Phone Number")
            user_input = f"{code} {phone}"
            if code not in dial_codes:
                st.warning("Sorry, not available in this country. Email us at careerupskillers@gmail.com.")
        else:
            user_input = st.text_input("Your answer")

        if st.form_submit_button("Double Click to Submit") and user_input:
            st.session_state.answers[keys[st.session_state.q_index]] = user_input
            st.session_state.q_index += 1
            if st.session_state.q_index >= len(questions):
                st.session_state.completed = True

# After submission
if st.session_state.completed:
    user = st.session_state.answers
    try:
        requests.post(google_sheets_url, json=user)
    except:
        pass

    country_code = user['phone'].split()[0]
    country = dial_codes.get(country_code, "India")
    currency = currency_map.get(country, "₹")

    prompt = f"""
    User: {user.get('name')}, Role: {user.get('job_role')}, Company: {user.get('company_details')},
    Skills: {user.get('skills')}, Location: {user.get('location')}, Salary: {currency} {user.get('salary')}, Experience: {user.get('experience')} years.

    Generate a short, crisp, persuasive AI career plan including:
    - 4-hour/weekend plan
    - 3 top companies offering better salary in same city (mention names)
    - Market salary vs user's salary comparison
    - AI niche suggestions based on skills
    - Add CTA for ₹499 AI Kit and ₹199 Counseling offer
    - Mention 3,000+ learners and free chatbot after payment
    - End with strong CTA and WhatsApp chatbot link
    """

    try:
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a top-tier sales advisor."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        st.success("✅ Your Personalized Plan is Ready!")
        st.markdown(res.choices[0].message.content, unsafe_allow_html=True)

        if st.button(f"🚀 Buy AI Starter Kit ({currency}499)"):
            st.markdown("[👉 Buy Now](https://rzp.io/rzp/ViDMMYS)")
        if st.button(f"💬 Book Counseling ({currency}199)"):
            st.markdown("[👉 Book Now](https://rzp.io/rzp/VnUcj8FR)")

        st.markdown(f"""
        <div style='margin-top:20px;padding:15px;background:#e6ffe6;border-radius:10px;'>
        🎁 Free Chatbot access after payment!<br>
        📲 <a href="https://wa.me/917975931377">WhatsApp Chatbot</a>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ OpenAI Error: {e}")

# ✅ app.py (with rotating flash purchase alerts and enhanced sales messaging)

import streamlit as st
import requests
import openai
from datetime import datetime
import random
import time
import os

# Set Streamlit page config
st.set_page_config(page_title="CareerUpskillers AI Advisor", page_icon="🚀")

# Load API key from Streamlit secrets
openai.api_key = st.secrets["API_KEY"]
google_sheets_url = st.secrets.get("GOOGLE_SHEETS_URL")

# Country codes dropdown and currency mapping
dial_codes = {"+91": "India", "+1": "USA", "+44": "UK", "+971": "UAE", "+972": "Israel"}
currency_map = {"India": "₹", "USA": "$", "UK": "£", "UAE": "AED", "Israel": "₪"}

# Header section
def show_header():
    st.markdown("""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;">
        <h1 style="color: #1E90FF; font-size: 2.5em;">🚀 Unlock Your AI Career Revolution!</h1>
        <p style="color: #333; font-size: 1.2em;">
            Automation is reshaping jobs! Discover how AI freelancing can help you earn ₹90,000 to ₹3 Lakhs/month—even starting from scratch. Over 3,000+ aspirants from the USA, Israel, UK, Dubai, and India have transformed their careers with us!
        </p>
        <p style="color: #FF4500; font-weight: bold;">🎭 Is your skillset future-proof? Are you paid what you deserve?</p>
        <p style="color: #666;">💡 Start with just 4 hours/weekend. When you're confident, switch full-time!</p>
        <p style="color: #228B22;">⏳ Offer ends midnight, March 31, 2025 — limited to first 10,000 users!</p>
        <em>Provide your details below to discover your AI career path!</em>
    </div>
    """, unsafe_allow_html=True)

# Rotating flash testimonials
if "flash_index" not in st.session_state:
    st.session_state.flash_index = 0

flash_countries = ["USA", "India", "UAE", "UK", "USA"]
flash_country = flash_countries[st.session_state.flash_index % len(flash_countries)]
slots_left = random.randint(20, 45)

st.markdown(f"""
<div style="background-color:#fff3cd; color:#856404; padding:10px; border-radius:5px; margin-top:10px;">
  🔥 <strong>Flash Update:</strong> New purchase from <strong>{flash_country}</strong> | Only <strong>{slots_left}</strong> kits left!
</div>
""", unsafe_allow_html=True)

st.session_state.flash_index += 1
if st.session_state.flash_index > 4:
    st.session_state.flash_index = 4  # Stop cycling after 5

show_header()

# Questions
questions = [
    ("👋 Hi! What's your Name?", "This helps us personalize your AI career journey!"),
    ("📧 Please provide your Email:", "We send exclusive AI job insights and high-paying freelance opportunities to your inbox!"),
    ("📱 Phone Number:", "We'll share updates and career offers directly. Select your country code first!"),
    ("🌍 Your current job role and company:", "This helps us analyze high-paying AI roles similar to yours!"),
    ("🏢 Tell us about your company:", "Understanding your company helps us suggest industry-specific AI growth paths!"),
    ("🤖 Are you aware of automation in your industry?", "Many jobs are being automated—stay ahead with AI skills!"),
    ("🛠️ What are your primary skills?", "We'll suggest AI niches where your skills are most profitable!"),
    ("📍 Your current location:", "We'll find high-paying AI job and freelancing opportunities near you!"),
    ("💰 Your current monthly salary (INR):", "We'll analyze if you're underpaid and suggest a target salary!"),
    ("📅 Years of experience in your field?", "Experience plays a key role in determining your AI career growth!")
]

keys = ["name", "email", "phone", "job_role", "company_details", "automation_awareness", "skills", "location", "salary", "experience"]

if "answers" not in st.session_state:
    st.session_state.answers = {}
    st.session_state.q_index = 0
    st.session_state.completed = False

# Form logic
if not st.session_state.completed:
    question, justification = questions[st.session_state.q_index]
    with st.form(key=f"form_{st.session_state.q_index}"):
        st.write(f"**{question}**")
        st.caption(justification)

        if st.session_state.q_index == 2:
            code = st.selectbox("Country Code", list(dial_codes.keys()), index=0)
            phone = st.text_input("Phone Number")
            user_input = f"{code} {phone}"
            if code not in dial_codes:
                st.warning("Sorry, we do not currently support this country. Email careerupskillers@gmail.com.")
        else:
            user_input = st.text_input("Your response")

        if st.form_submit_button("Double Click to Submit") and user_input:
            st.session_state.answers[keys[st.session_state.q_index]] = user_input
            st.session_state.q_index += 1
            if st.session_state.q_index >= len(questions):
                st.session_state.completed = True

# After form submission
if st.session_state.completed:
    user_data = st.session_state.answers
    try:
        requests.post(google_sheets_url, json=user_data)
    except:
        pass

    code = user_data['phone'].split()[0]
    country = dial_codes.get(code, "India")
    currency = currency_map.get(country, "₹")

    prompt = f"""
    User: {user_data.get('name')}, Job Role: {user_data.get('job_role')}, Company: {user_data.get('company_details')},
    Skills: {user_data.get('skills')}, Location: {user_data.get('location')}, Salary: {currency} {user_data.get('salary')}, Experience: {user_data.get('experience')} years.

    Generate a persuasive AI career roadmap, including:
    - Custom plan with daily/weekly/monthly goals
    - AI niches based on their skills
    - Top 3 companies offering better salaries in their location
    - Salary benchmark vs current
    - 4 hours/weekend plan for smooth transition
    - ₹90K–₹3L earning via freelancing/chatbots
    - Continue full-time job till ready
    - Highlight 3,000+ successful learners
    - Mention ₹499 Kit, ₹199 Counseling
    - Add free ready-to-use chatbot and WhatsApp link after payment
    """

    try:
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a persuasive AI career advisor."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        st.success("✅ Here's your personalized AI Career Plan!")
        st.markdown(res.choices[0].message.content, unsafe_allow_html=True)

        if st.button(f"🚀 Unlock Career Kit for {currency}499"):
            st.markdown("[👉 Buy Now](https://rzp.io/rzp/ViDMMYS)")
        if st.button(f"💬 Book Counseling for {currency}199"):
            st.markdown("[👉 Book Session](https://rzp.io/rzp/VnUcj8FR)")

        st.markdown("""
        <div style="margin-top:20px; padding:15px; background:#e6ffe6; border-radius:10px;">
        🎁 After payment, get your free chatbot instantly.<br>
        📲 <a href="https://wa.me/919999999999">Click to Access WhatsApp Chatbot</a>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error calling OpenAI: {e}")

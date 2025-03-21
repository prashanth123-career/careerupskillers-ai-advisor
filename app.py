# ✅ app.py (final update with enhanced UI and sales-driven chatbot)

import streamlit as st
import requests
import openai
from datetime import datetime
import re
import os

# Set Streamlit page config
st.set_page_config(page_title="CareerUpskillers AI Advisor", page_icon="🚀")

# Load API key from Streamlit secrets
openai.api_key = st.secrets["API_KEY"]

google_sheets_url = st.secrets.get("GOOGLE_SHEETS_URL")

# Country codes dropdown
dial_codes = {"+91": "India", "+1": "USA", "+44": "UK", "+971": "UAE", "+972": "Israel"}

# Header with enhanced UI
def show_header():
    st.markdown(
        """
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            <h1 style="color: #1E90FF; font-size: 2.5em;"> 🚀 Unlock Your AI Career Revolution! </h1>
            <p style="color: #333; font-size: 1.2em;">
                Automation is reshaping jobs! Discover how AI freelancing can help you earn ₹50,000+/month, even starting from scratch. Over 3,000+ aspirants from the USA, Israel, UK, Dubai, and India have transformed their careers with us!
            </p>
            <p style="color: #FF4500; font-weight: bold; font-size: 1.1em;">
                🎭 Is your skillset future-proof? Are you paid what you deserve? Which companies should you target?
            </p>
            <p style="color: #666;">
                💡 Build a backup plan, gain new AI skills, and explore freelance & weekend business ventures. Act now—limited spots!
            </p>
            <p style="color: #228B22;">
                ⏳ Offer ends midnight, March 31, 2025—start your journey today!
            </p>
            <div style="margin-top: 15px;">
                <em>Provide your details below to discover your AI career path!</em>
            </div>
        </div>
        <br>
        """,
        unsafe_allow_html=True
    )

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

# Init session state
if "answers" not in st.session_state:
    st.session_state.answers = {}
    st.session_state.q_index = 0
    st.session_state.completed = False

# Show form
if not st.session_state.completed:
    question, justification = questions[st.session_state.q_index]
    with st.form(key=f"form_{st.session_state.q_index}"):
        st.write(f"**{question}**")
        st.caption(justification)
        
        if st.session_state.q_index == 2:  # Phone number question
            country_code = st.selectbox("Select Country Code", list(dial_codes.keys()), index=0, key="country_code")
            phone_number = st.text_input("Enter your phone number:", key="phone_input")
            user_input = f"{country_code} {phone_number}"
            if country_code not in dial_codes:
                st.warning("Sorry, we do not currently support this country. Please send an email to careerupskillers@gmail.com for assistance.")
        else:
            user_input = st.text_input("", key=f"input_{st.session_state.q_index}")
        
        submit_button = st.form_submit_button("Double Click to Submit")
        if submit_button and user_input:
            st.session_state.answers[keys[st.session_state.q_index]] = user_input
            st.session_state.q_index += 1
            if st.session_state.q_index >= len(questions):
                st.session_state.completed = True

# After all questions
if st.session_state.completed:
    user_data = st.session_state.answers
    try:
        requests.post(google_sheets_url, json=user_data)
    except:
        pass

    prompt = f"""
    User: {user_data.get('name')}, Job Role: {user_data.get('job_role')}, Company: {user_data.get('company_details')},
    Skills: {user_data.get('skills')}, Location: {user_data.get('location')}, Salary: {user_data.get('salary')}, Experience: {user_data.get('experience')} years.
    
    Generate a persuasive AI career roadmap, including:
    - Custom AI career plan with milestones
    - In-demand AI job insights
    - Latest industry changes for {user_data.get('company_details')}
    - Higher salary opportunities with top companies
    - Actionable steps for a successful AI career
    - Final CTA for ₹499 AI Career Kit & ₹199 Personal Counseling
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a career advisor bot that provides highly persuasive AI career roadmaps."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        analysis = response.choices[0].message["content"]
        st.success("✅ Here's your personalized AI Career Plan!")
        st.markdown(analysis, unsafe_allow_html=True)
        
        if st.button("🚀 Unlock AI Career Success for ₹499 Now!"):
            st.markdown("[👉 Buy AI Career Starter Kit](https://rzp.io/rzp/ViDMMYS)")
        if st.button("💎 Get Personalized Career Counseling for ₹199"):
            st.markdown("[👉 Book Your Session](https://rzp.io/rzp/VnUcj8FR)")
    except Exception as e:
        st.error(f"❌ Error calling OpenAI: {e}")

# ✅ app.py (fixed for openai==0.28.1)

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

# Header
st.title("🚀 CareerUpskillers AI Career Advisor")

# Questions
questions = [
    "👋 Hi! What's your Name?",
    "📧 Please provide your Email:",
    "📱 Phone Number:",
    "💼 Your current job role and company:",
    "🏢 Tell us about your company:",
    "🤖 Are you aware of automation in your industry?",
    "🛠️ What are your primary skills?",
    "📍 Your current location:",
    "💰 Your current monthly salary (INR):",
    "📅 Years of experience in your field?"
]

keys = ["name", "email", "phone", "job_role", "company_details", "automation_awareness", "skills", "location", "salary", "experience"]

# Init session state
if "answers" not in st.session_state:
    st.session_state.answers = {}
    st.session_state.q_index = 0
    st.session_state.completed = False

# Show form
if not st.session_state.completed:
    current_question = questions[st.session_state.q_index]
    with st.form(key=f"form_{st.session_state.q_index}"):
        user_input = st.text_input(current_question, key=f"input_{st.session_state.q_index}")
        submit_button = st.form_submit_button("Submit")
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
    Name: {user_data.get('name')}
    Job Role: {user_data.get('job_role')}
    Company: {user_data.get('company_details')}
    Skills: {user_data.get('skills')}
    Location: {user_data.get('location')}
    Salary: {user_data.get('salary')}
    Experience: {user_data.get('experience')} years
    Phone: {user_data.get('phone')}
    
    Generate a personalized AI career roadmap for this user in a persuasive, motivating tone with bullet points and emojis.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a career advisor bot."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600
        )
        analysis = response.choices[0].message["content"]
        st.success("✅ Here's your personalized AI Career Plan!")
        st.markdown(analysis)
    except Exception as e:
        st.error(f"❌ Error calling OpenAI: {e}")

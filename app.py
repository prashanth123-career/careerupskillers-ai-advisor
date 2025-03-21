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
    You are a highly persuasive, enthusiastic AI sales advisor for CareerUpskillers, designed to close 100% of sales for the ₹499 AI Career Starter Kit and ₹199 personalized counseling. Analyze the user's input to infer their needs, motivations, and potential objections, and create a compelling career analysis with the following structure, using emojis and bullet points:

    1. **🎯 Personalized AI Career Plan**:
       - Greet the user by name and acknowledge their job role, experience, and skills enthusiastically.
       - Provide a customized roadmap with a step-by-step guide to start an AI career from scratch, including daily/weekly/monthly actionable steps tailored to their current level.
       - Suggest clear milestones (e.g., 'Learn Python basics in 1 month') to achieve their career goals.

    2. **💼 AI Job Market Insights**:
       - Highlight the booming AI job market and why AI freelancing offers ₹50,000+/month earning potential.
       - Identify in-demand skills (e.g., machine learning, data analysis) and underserved niches based on their location and skills ({user_data.get('skills', 'unknown skills')}).
       - Warn about automation risks (e.g., '40% of accounting jobs at risk by 2025').

    3. **🏢 Latest Updates on Your Company**:
       - Provide two points on recent updates or trends related to their company ({user_data.get('company_details', 'unknown company')})—e.g., recent projects, expansions, or AI adoption trends in their industry.
       - Suggest how they can leverage these updates for career growth.

    4. **💰 Salary Analysis**:
       - Analyze if they are paid fairly based on their skills ({user_data.get('skills', 'unknown skills')}) and experience ({user_data.get('experience', 'unknown')} years).
       - Compare their salary (INR {user_data.get('salary', 'unknown')}) to market standards for their skillset and suggest a target salary they could achieve with upskilling.

    5. **🌟 Companies to Apply To**:
       - Recommend 3 companies in their location ({user_data.get('location', 'unknown')}) with similar job roles to theirs ({user_data.get('job_role', 'unknown role')}) but offering higher salaries.
       - Explain why these companies are a good fit and how to apply.

    6. **🛠️ AI Career Roadmap**:
       - Offer a detailed journey to transition into AI freelancing, from basics to securing high-paying projects.
       - Recommend essential skills (e.g., programming, AI tools) and a curated list of resources (e.g., online courses, books).
       - Mention that a full roadmap with resources is included in the AI Career Starter Kit.

    7. **🌐 Top AI Tools & Platforms**:
       - Introduce tools like ChatGPT, Midjourney, LangChain, and AutoGPT, with brief usage guides for real-world projects.
       - Suggest platforms for model training, prototyping, and deployment based on their needs.
       - Highlight these tools as part of the AI Career Starter Kit.

    8. **💻 Freelance Platforms Guide**:
       - Break down platforms like Upwork, Fiverr, and LinkedIn, with tips to build a standout profile.
       - Share winning strategies to pitch services, negotiate rates, and secure long-term clients.
       - Encourage them to use the kit’s proposal templates.

    9. **🎯 Niche Selection Strategy**:
       - Guide them to pick a profitable niche (e.g., AI chatbots, automation, resume screening).
       - Provide market research tips and competitive analysis to stand out.
       - Link niche success to the kit’s resources.

    Format with bold headings, emojis, and bullet points for maximum engagement. Use a conversational, sales-driven tone to overcome objections and motivate action! Mention the AI Career Starter Kit as the solution (but do not mention the price yet).
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a top-tier sales AI designed to engage, persuade, and close 100% of deals with a friendly, high-energy tone."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        analysis = response.choices[0].message["content"]
        st.success("✅ Here's your personalized AI Career Plan!")
        st.markdown(analysis)
    except Exception as e:
        st.error(f"❌ Error calling OpenAI: {e}")

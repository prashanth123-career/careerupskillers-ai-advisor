import streamlit as st
from openai import OpenAI
import os

# ✅ Remove proxy environment variables just in case
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)

# ✅ Streamlit config
st.set_page_config(page_title="CareerUpskillers AI Advisor", page_icon="🚀")

# ✅ OpenAI Initialization
try:
    api_key = st.secrets["API_KEY"]
    client = OpenAI(api_key=api_key)  # ✅ DO NOT pass proxies
    st.success("✅ OpenAI client initialized successfully!")
except Exception as e:
    st.error(f"❌ Error initializing OpenAI client: {str(e)}")
    st.stop()


# 🔐 Google Sheets URL from secrets
google_sheets_url = st.secrets.get("GOOGLE_SHEETS_URL", "")

# Questions
questions = [
    "👋 What's your name?",
    "📧 Email address:",
    "📱 Phone number (7–10 digits):",
    "💼 Job role and company:",
    "🏢 Company details (industry, projects):",
    "🤖 Are you aware of automation in your industry? (Yes/No)",
    "🛠️ Your main skills:",
    "📍 City:",
    "💰 Monthly salary (INR):",
    "📅 Years of experience:"
]
keys = [
    "name", "email", "phone", "job_role", "company_details", "automation_awareness",
    "skills", "location", "salary", "experience"
]

# Session init
if "answers" not in st.session_state:
    st.session_state.answers = {}
    st.session_state.q_index = 0
    st.session_state.completed = False

# Simple validations
def is_valid_email(email): return re.match(r"[^@]+@[^@]+\.[^@]+", email)
def is_valid_number(val): return re.match(r"^\d+(\.\d+)?$", val)

# Ask questions one-by-one
if not st.session_state.completed:
    index = st.session_state.q_index
    with st.form(key=f"q_{index}"):
        answer = st.text_input(questions[index])
        submit = st.form_submit_button("Submit")
        if submit and answer:
            if index == 1 and not is_valid_email(answer):
                st.error("Please enter a valid email.")
            elif index in [2, 8, 9] and not is_valid_number(answer):
                st.error("Enter a valid number.")
            else:
                st.session_state.answers[keys[index]] = answer
                st.session_state.q_index += 1
                if st.session_state.q_index >= len(questions):
                    st.session_state.completed = True

# After form is completed
if st.session_state.completed:
    st.success("🎉 All answers collected!")
    data = st.session_state.answers

    # Send to Google Sheets
    if google_sheets_url:
        try:
            requests.post(google_sheets_url, json=data)
        except:
            st.warning("Google Sheets sync failed, but continuing...")

    # Prompt for GPT
    today = datetime.now().strftime("%B %d, %Y")
    prompt = f"""
You are an AI Career Coach.

User Info:
Name: {data['name']}
Job Role: {data['job_role']}
Company: {data['company_details']}
Skills: {data['skills']}
Location: {data['location']}
Salary: {data['salary']} INR
Experience: {data['experience']} years
Automation Aware: {data['automation_awareness']}

Generate a detailed, personalized AI career roadmap using:
- 🎯 Career Plan
- 💼 Market Insights
- 🏢 Company Trends
- 💰 Salary Advice
- 🌟 Job Suggestions
- 🛠️ Skills to Learn
- 💻 Freelancing Tips

Use emojis, bold headings, persuasive tone. Don’t mention pricing.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a friendly, persuasive career advisor."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800
        )
        result = response.choices[0].message.content
        st.markdown("### 🎯 Your Personalized Career Report")
        st.markdown(result, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"OpenAI error: {e}")

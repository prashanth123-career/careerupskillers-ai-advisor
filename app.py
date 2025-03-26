import streamlit as st
import requests
from datetime import datetime, timedelta
import random
import uuid
import time

# Set Streamlit page config
st.set_page_config(page_title="CareerUpskillers AI Advisor", page_icon="🌟", layout="centered")

# CSS for conversational interface
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    body {
        font-family: 'Inter', 'Roboto', sans-serif;
        background: linear-gradient(135deg, #1A3550 0%, #2AB7CA 100%);
        color: #FFFFFF;
    }
    .container {
        width: 100%;
        max-width: 500px;
        margin: 0 auto;
        padding: 16px;
        box-sizing: border-box;
    }
    .chat-bubble {
        background-color: #E6F4FA;
        color: #1A3550;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        animation: slideIn 0.3s ease-in;
    }
    .user-response {
        background-color: #2AB7CA;
        color: #FFFFFF;
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 16px;
        text-align: right;
        animation: slideIn 0.3s ease-in;
    }
    .info-section, .flash-alert, .header, .post-submission, .brief-counseling, .cta {
        width: 100%;
        padding: 16px;
        box-sizing: border-box;
        border-radius: 12px;
        margin-bottom: 16px;
        overflow-wrap: break-word;
        word-wrap: break-word;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .info-section {
        background: linear-gradient(90deg, #2AB7CA 0%, #1A3550 100%);
        color: #FFFFFF;
        text-align: center;
        border-bottom: 2px solid #FFD700;
    }
    .flash-alert {
        background-color: #FFF9E6;
        color: #1A3550;
        border: 1px solid #FFD700;
    }
    .header {
        background-color: #1A3550;
        color: #FFFFFF;
        text-align: center;
    }
    .post-submission {
        background-color: #E6F4FA;
        text-align: center;
        border: 1px solid #2AB7CA;
        color: #1A3550;
    }
    .brief-counseling {
        background-color: #E6F4FA;
        text-align: left;
        border: 1px solid #2AB7CA;
        color: #1A3550;
    }
    .cta button {
        width: 100%;
        padding: 14px;
        font-size: 16px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        margin: 12px auto;
        display: block;
        background: linear-gradient(90deg, #2AB7CA 0%, #1A3550 100%);
        color: #FFFFFF;
        transition: transform 0.2s ease;
    }
    .cta button:hover {
        transform: scale(1.05);
    }
    input, select {
        width: 100%;
        padding: 12px;
        font-size: 15px;
        border-radius: 8px;
        border: 2px solid #2AB7CA;
        margin: 8px 0;
        box-sizing: border-box;
    }
    .progress-text {
        font-size: 16px;
        text-align: center;
        margin: 8px 0;
        color: #FFD700;
    }
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
    @keyframes slideIn {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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

# Google Sheets URL
google_sheets_url = "https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec"

# Employment status options
employment_statuses = ["Student", "Fresher", "Working Professional", "Freelancer", "Business Owner"]

# Domain options
domains = [
    "Data Science", "Sales", "Marketing", "Accounting", "Developer", "Web Designer",
    "Software Testing", "Hardware Testing", "Cybersecurity", "BPO", "Other"
]

# Country codes
dial_codes = {
    "+91": "India", "+1": "USA", "+44": "UK", "+971": "UAE", "+81": "Japan",
    "+86": "China", "+49": "Germany", "+33": "France", "+61": "Australia"
}

# Base questions
base_questions = [
    ("📊 What best describes your current status?", "This helps us customize your roadmap."),
    ("👋 Hi there! I'm your AI Career Advisor. What's your name?", "Let's get to know each other!"),
    ("📧 Great, {name}! Can I have your email to send you personalized career insights?", "We'll use this to share opportunities."),
    ("📞 What's your phone number? (Select country code first)", "This helps us connect with you."),
    ("💼 What's your professional domain?", "This helps us tailor your career plan."),
    ("🌍 Where are you located? (e.g., Mumbai, India)", "We'll find opportunities near you."),
]

# Additional questions by employment status
additional_questions = {
    "Student": [
        ("🎓 What's your field of study?", "This helps suggest relevant career paths."),
        ("📅 What year will you graduate?", "This helps plan your next steps."),
        ("🎯 What are your career aspirations?", "Help us understand your goals.")
    ],
    "Fresher": [
        ("🎓 What's your field of study?", "This helps suggest relevant career paths."),
        ("📅 What year did you graduate?", "This helps plan your next steps."),
        ("🔍 Are you actively job hunting?", "Understand your current status.")
    ],
    "Working Professional": [
        ("💰 What's your current salary? (Optional)", "Enter numbers only (e.g., 50000)."),
        ("💡 What's your expected salary? (Optional)", "Enter a realistic number."),
        ("🏢 How many years at current company?", "Understand your stability.")
    ],
    "Freelancer": [
        ("💰 What's your average monthly earnings? (Optional)", "Enter numbers only."),
        ("💡 What's your income goal? (Optional)", "Enter a realistic number."),
        ("🛠️ What platforms do you use? (e.g., Upwork)", "Understand your workflow.")
    ],
    "Business Owner": [
        ("💰 What's your monthly revenue? (Optional)", "Enter numbers only."),
        ("💡 What's your revenue goal? (Optional)", "Enter a realistic number."),
        ("🏢 How many employees do you have?", "Understand your business scale.")
    ]
}

# Field keys for answers
keys = [
    "employment_status", "name", "email", "phone", "domain", "location",
    "field_of_study", "graduation_year", "aspirations",  # Student
    "job_hunting",  # Fresher
    "current_salary", "expected_salary", "years_at_company",  # Working
    "current_earnings", "income_goal", "freelance_platforms",  # Freelancer
    "business_revenue", "revenue_goal", "employees"  # Business Owner
]

# Build questions based on employment status
if "employment_status" in st.session_state.answers:
    emp_status = st.session_state.answers["employment_status"]
    questions = base_questions + additional_questions.get(emp_status, [])
else:
    questions = base_questions

# Info Section
st.markdown("""
<div class="info-section container fade-in">
    <p>© 2025 CareerUpskillers | <a href="https://www.careerupskillers.com/privacy" target="_blank">Privacy Policy</a> | 
    <a href="https://www.careerupskillers.com/terms" target="_blank">Terms</a></p>
    <p>Contact: <a href="mailto:careerupskillers@gmail.com">careerupskillers@gmail.com</a> | 
    WhatsApp: <a href="tel:+917892116728">+91 78921 16728</a></p>
</div>
""", unsafe_allow_html=True)

# Flash Alert
flash_country = random.choice(["USA", "India", "UAE", "UK"])
time_ago = datetime.now() - timedelta(minutes=random.randint(1, 10))
st.markdown(f"""
<div class="flash-alert container fade-in">
  📢 <strong>Flash Alert:</strong> Someone from {flash_country} just enrolled {time_ago.strftime('%M mins ago')} | 
  Only <strong>{st.session_state.slots_left}</strong> slots left!
</div>
""", unsafe_allow_html=True)
st.session_state.slots_left = max(5, st.session_state.slots_left - random.randint(1, 2))

# Header
st.markdown("""
<div class="header container fade-in">
    <h1>🌟 CareerUpskillers AI Advisor</h1>
    <p>Let's build your career roadmap in just a few steps!</p>
</div>
""", unsafe_allow_html=True)

# Conversational Form Logic
if not st.session_state.completed:
    total_questions = len(questions)
    progress = int((st.session_state.q_index / total_questions) * 100)
    st.markdown(f"<div class='progress-text'>Step {st.session_state.q_index + 1} of {total_questions} 🚀</div>", unsafe_allow_html=True)
    st.progress(progress)

    # Display previous answers
    for i in range(st.session_state.q_index):
        q, _ = questions[i]
        answer = st.session_state.answers.get(keys[i], "Skipped")
        st.markdown(f"<div class='chat-bubble'>{q}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='user-response'>{answer}</div>", unsafe_allow_html=True)

    # Current question
    q, hint = questions[st.session_state.q_index]
    if "{name}" in q and "name" in st.session_state.answers:
        q = q.format(name=st.session_state.answers["name"])
    st.markdown(f"<div class='chat-bubble'><p>{q}</p><p><em>{hint}</em></p></div>", unsafe_allow_html=True)

    with st.form(key=f"form_{st.session_state.q_index}"):
        user_input = None
        if st.session_state.q_index == 0:  # Employment Status
            user_input = st.selectbox("", employment_statuses, key="employment_status_input")
        elif st.session_state.q_index == 1:  # Name
            user_input = st.text_input("", placeholder="Enter your name", key="name_input")
        elif st.session_state.q_index == 2:  # Email
            user_input = st.text_input("", placeholder="Enter your email", key="email_input")
        elif st.session_state.q_index == 3:  # Phone
            code = st.selectbox("Country Code", list(dial_codes.keys()), key="country_code")
            phone = st.text_input("Phone Number", placeholder="e.g., 9876543210", key="phone_input")
            user_input = f"{code} {phone}" if phone else None
        elif st.session_state.q_index == 4:  # Domain
            user_input = st.selectbox("", domains, key="domain_input")
            if user_input == "Other":
                other_domain = st.text_input("Please specify your domain:", key="other_domain")
                user_input = f"Other: {other_domain}" if other_domain else "Other"
        elif st.session_state.q_index == 5:  # Location
            user_input = st.text_input("", placeholder="e.g., Mumbai, India", key="location_input")
        else:  # Additional questions
            emp_status = st.session_state.answers["employment_status"]
            if emp_status in ["Student", "Fresher"]:
                user_input = st.text_input("", placeholder="Your answer", key=f"input_{st.session_state.q_index}")
            else:  # Professional, Freelancer, Business Owner
                if "salary" in questions[st.session_state.q_index][0].lower() or "earnings" in questions[st.session_state.q_index][0].lower() or "revenue" in questions[st.session_state.q_index][0].lower():
                    user_input = st.text_input("", placeholder="Numbers only (e.g., 50000)", key=f"input_{st.session_state.q_index}")
                else:
                    user_input = st.text_input("", placeholder="Your answer", key=f"input_{st.session_state.q_index}")

        col1, col2 = st.columns([1, 1])
        with col1:
            submit_button = st.form_submit_button("Next")
        with col2:
            skip_button = st.form_submit_button("Skip")

        if submit_button:
            if user_input:
                # Validations
                if st.session_state.q_index == 2:  # Email
                    if "@" not in user_input or "." not in user_input:
                        st.error("Please enter a valid email (e.g., example@domain.com)")
                        st.stop()
                if st.session_state.q_index == 3:  # Phone
                    phone_part = user_input.split(" ")[1] if len(user_input.split(" ")) > 1 else ""
                    if not phone_part.isdigit() or len(phone_part) < 8:
                        st.error("Please enter a valid phone number")
                        st.stop()
                if st.session_state.q_index >= 6:  # Additional questions
                    emp_status = st.session_state.answers["employment_status"]
                    if emp_status in ["Working Professional", "Freelancer", "Business Owner"]:
                        if any(word in questions[st.session_state.q_index][0].lower() for word in ["salary", "earnings", "revenue"]):
                            cleaned_input = user_input.replace(',', '')
                            if cleaned_input and not cleaned_input.isdigit():
                                st.error("Please enter numbers only (e.g., 50000)")
                                st.stop()
                
                st.session_state.answers[keys[st.session_state.q_index]] = user_input
                st.session_state.q_index += 1
                if st.session_state.q_index >= len(questions):
                    st.session_state.completed = True
            else:
                st.warning("Please provide an answer or click 'Skip'")
        if skip_button:
            st.session_state.answers[keys[st.session_state.q_index]] = "Skipped"
            st.session_state.q_index += 1
            if st.session_state.q_index >= len(questions):
                st.session_state.completed = True

# After Submission
if st.session_state.completed:
    user = st.session_state.answers
    user["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user["session_id"] = st.session_state.session_id
    
    # Send data to Google Sheets
    if not st.session_state.user_data_sent:
        try:
            response = requests.post(google_sheets_url, json=user)
            response.raise_for_status()
            st.session_state.user_data_sent = True
        except Exception as e:
            st.error(f"Error submitting data: {str(e)}")

    # Post-Submission Message
    st.markdown(f"""
    <div class="post-submission container fade-in">
        <p>✅ Thanks, {user.get('name', 'User')}! Your career insights are ready!</p>
    </div>
    """, unsafe_allow_html=True)

    # Determine which product to emphasize based on user profile
    emp_status = user.get("employment_status", "Student")
    domain = user.get("domain", "Other")
    
    # Default recommendation (₹199 plan)
    primary_product = {
        "title": "Personalized Career Plan (₹199)",
        "description": "Detailed roadmap with market salary analysis, top companies hiring, and step-by-step action plan",
        "link": "https://rzp.io/rzp/FAsUJ9k",
        "benefits": [
            "Market salary analysis for your role",
            "Top companies hiring in your area",
            "Customized upskilling recommendations",
            "Interview preparation guide"
        ]
    }
    
    # Secondary recommendation (₹499 kit)
    secondary_product = {
        "title": "AI Freelancer Starter Kit (₹499)",
        "description": "Everything you need to start earning ₹90K-₹3L/month with AI freelancing",
        "link": "https://rzp.io/rzp/t37swnF",
        "benefits": [
            "Proven freelancing templates",
            "Step-by-step client acquisition",
            "AI tools you can resell",
            "Weekend-friendly schedule"
        ]
    }
    
    # Adjust recommendations based on user profile
    if emp_status in ["Freelancer", "Business Owner"]:
        primary_product, secondary_product = secondary_product, primary_product
    elif emp_status == "Student" and domain in ["Developer", "Data Science", "Web Designer"]:
        secondary_product["title"] = "Student AI Accelerator (₹499)"
        secondary_product["description"] = "Jumpstart your career with in-demand AI skills"

    # Display Recommendations
    st.markdown(f"""
    <div class="brief-counseling container fade-in">
        <h3>🎯 Recommended for {user.get('name', 'you')}</h3>
        <p>Based on your profile as a <strong>{emp_status}</strong> in <strong>{domain}</strong>, here's what will help most:</p>
        
        <div style="border: 2px solid #2AB7CA; border-radius: 12px; padding: 16px; margin: 16px 0;">
            <h4>{primary_product['title']}</h4>
            <p>{primary_product['description']}</p>
            <ul>
                {''.join([f'<li>{benefit}</li>' for benefit in primary_product['benefits']])}
            </ul>
            <a href="{primary_product['link']}" target="_blank">
                <button style="background: linear-gradient(90deg, #2AB7CA 0%, #1A3550 100%);">Get Now</button>
            </a>
        </div>
        
        <p style="text-align: center; font-weight: 600;">-- OR --</p>
        
        <div style="border: 2px solid #FF6F61; border-radius: 12px; padding: 16px; margin: 16px 0;">
            <h4>{secondary_product['title']}</h4>
            <p>{secondary_product['description']}</p>
            <ul>
                {''.join([f'<li>{benefit}</li>' for benefit in secondary_product['benefits']])}
            </ul>
            <a href="{secondary_product['link']}" target="_blank">
                <button style="background: linear-gradient(90deg, #FF6F61 0%, #FF3D00 100%);">Get Now</button>
            </a>
        </div>
        
        <p style="text-align: center; margin-top: 24px;">
            <strong>Special Offer:</strong> Get both for ₹599 (save ₹99) | 
            <a href="https://rzp.io/rzp/bundle-offer" target="_blank" style="color: #2AB7CA;">Click here</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Testimonials
    testimonials = [
        "The ₹199 plan helped me negotiate a 30% salary hike! - Rohan, Mumbai",
        "With the AI Kit, I made ₹1.2L in my first month! - Priya, Freelancer",
        "As a student, this gave me clarity on my career path. - Arjun, Delhi"
    ]
    st.markdown(f"""
    <div class="brief-counseling container fade-in">
        <h4>🌟 Success Stories</h4>
        <p>{random.choice(testimonials)}</p>
        <p style="text-align: center; font-size: 12px; margin-top: 16px;">
            Limited slots available - {st.session_state.slots_left} remaining today
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Restart option
    if st.button("Start Over", key="restart_button"):
        st.session_state.q_index = 0
        st.session_state.completed = False
        st.session_state.answers = {}
        st.experimental_rerun()

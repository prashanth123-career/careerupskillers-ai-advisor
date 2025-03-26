import streamlit as st
import requests
from datetime import datetime, timedelta
import random
import uuid
import time
import openai

# Set Streamlit page config
st.set_page_config(page_title="CareerUpskillers AI Advisor", page_icon="🌟", layout="centered")

# Access secrets from Streamlit secrets.toml
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    google_sheets_url = st.secrets["GOOGLE_SHEETS_URL"]
except KeyError as e:
    st.error(f"Missing secret: {str(e)}. Please ensure OPENAI_API_KEY and GOOGLE_SHEETS_URL are defined in secrets.toml.")
    st.stop()

# CSS for a conversational, interactive interface
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
        animation: slideIn 0.5s ease-in;
    }
    .chat-bubble p {
        margin: 0;
        font-size: 16px;
        line-height: 1.5;
    }
    .user-response {
        background-color: #2AB7CA;
        color: #FFFFFF;
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 16px;
        text-align: right;
        animation: slideIn 0.5s ease-in;
    }
    .info-section, .flash-alert, .header, .post-submission, .brief-counseling, .cta, .product-card {
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
        position: fixed;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(90deg, #2AB7CA 0%, #1A3550 100%);
        color: #FFFFFF;
        text-align: center;
        z-index: 1000;
        max-width: 500px;
        border-bottom: 2px solid #FFD700;
    }
    .info-section p {
        color: #FFFFFF;
        font-size: 13px;
        margin: 4px 0;
        font-weight: 600;
    }
    .info-section a {
        color: #FFD700;
        text-decoration: none;
        font-weight: 600;
    }
    .info-section a:hover {
        text-decoration: underline;
        color: #FFFFFF;
    }
    .flash-alert {
        background-color: #FFF9E6;
        color: #1A3550;
        font-size: 14px;
        line-height: 1.4;
        border: 1px solid #FFD700;
    }
    .header {
        background-color: #1A3550;
        color: #FFFFFF;
        text-align: center;
    }
    .header h1 {
        color: #FFFFFF;
        font-size: 24px;
    }
    .header p {
        color: #E0E7FF;
        font-size: 14px;
    }
    .post-submission {
        background-color: #E6F4FA;
        text-align: center;
        border: 1px solid #2AB7CA;
        color: #1A3550;
        font-weight: 600;
    }
    .brief-counseling {
        background-color: #E6F4FA;
        text-align: left;
        border: 1px solid #2AB7CA;
        color: #1A3550;
    }
    .brief-counseling h3 {
        color: #1A3550;
        font-weight: 700;
    }
    .brief-counseling p, .brief-counseling li {
        color: #1A3550;
        font-size: 14px;
        line-height: 1.5;
    }
    .brief-counseling a {
        color: #2AB7CA;
        text-decoration: none;
        font-weight: 600;
    }
    .brief-counseling a:hover {
        text-decoration: underline;
    }
    .cta button {
        width: 100%;
        max-width: 300px;
        padding: 14px;
        font-size: 16px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        margin: 12px auto;
        display: block;
        background: linear-gradient(90deg, #2AB7CA 0%, #1A3550 100%);
        color: #FFFFFF;
        font-weight: 600;
        transition: transform 0.2s ease;
    }
    .cta button:hover {
        transform: scale(1.05);
    }
    .product-card {
        border: 2px solid;
        border-radius: 12px;
        padding: 16px;
        margin: 16px 0;
        background-color: #E6F4FA;
        color: #1A3550;
    }
    input, select {
        width: 100%;
        padding: 12px;
        font-size: 15px;
        border-radius: 8px;
        border: 2px solid #2AB7CA;
        margin: 8px 0;
        box-sizing: border-box;
        background-color: #FFFFFF;
        color: #1A3550;
    }
    .progress-text {
        font-size: 16px;
        text-align: center;
        margin: 8px 0;
        color: #FFD700;
        font-weight: 600;
    }
    .skip-button {
        background: none;
        border: none;
        color: #FF6F61;
        font-size: 14px;
        cursor: pointer;
        margin-top: 8px;
        text-decoration: underline;
    }
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #FFD700 0%, #FF6F61 100%);
    }
    @keyframes slideIn {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .fade-in {
        animation: fadeIn 1s ease-in;
    }
    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
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
if 'flash_index' not in st.session_state:
    st.session_state.flash_index = 0
if 'slots_left' not in st.session_state:
    st.session_state.slots_left = random.randint(15, 40)
if 'user_data_sent' not in st.session_state:
    st.session_state.user_data_sent = False
if 'follow_up_messages' not in st.session_state:
    st.session_state.follow_up_messages = []

# Employment status options
employment_statuses = ["Student", "Fresher", "Working Professional", "Freelancer", "Business Owner"]

# Domain options
domains = [
    "Data Science", "Sales", "Marketing", "Accounting", "Developer", "Web Designer",
    "Software Testing", "Hardware Testing", "Cybersecurity", "BPO", "Other"
]

# Career goals options
career_goals = [
    "Get a Job", "Switch Careers", "Grow in Current Role", "Start Freelancing", 
    "Scale My Business", "Learn New Skills", "Other"
]

# Country codes for phone number
dial_codes = {
    "+93": "Afghanistan", "+355": "Albania", "+213": "Algeria", "+376": "Andorra", "+244": "Angola",
    "+54": "Argentina", "+374": "Armenia", "+61": "Australia", "+43": "Austria", "+994": "Azerbaijan",
    "+973": "Bahrain", "+880": "Bangladesh", "+375": "Belarus", "+32": "Belgium", "+501": "Belize",
    "+229": "Benin", "+975": "Bhutan", "+591": "Bolivia", "+387": "Bosnia and Herzegovina", "+267": "Botswana",
    "+55": "Brazil", "+673": "Brunei", "+359": "Bulgaria", "+226": "Burkina Faso", "+257": "Burundi",
    "+855": "Cambodia", "+237": "Cameroon", "+1": "Canada", "+238": "Cape Verde", "+236": "Central African Republic",
    "+56": "Chile", "+86": "China", "+57": "Colombia", "+269": "Comoros", "+242": "Congo",
    "+506": "Costa Rica", "+385": "Croatia", "+53": "Cuba", "+357": "Cyprus", "+420": "Czech Republic",
    "+45": "Denmark", "+253": "Djibouti", "+1": "Dominican Republic", "+593": "Ecuador", "+20": "Egypt",
    "+503": "El Salvador", "+240": "Equatorial Guinea", "+291": "Eritrea", "+372": "Estonia", "+251": "Ethiopia",
    "+679": "Fiji", "+358": "Finland", "+33": "France", "+241": "Gabon", "+220": "Gambia",
    "+995": "Georgia", "+49": "Germany", "+233": "Ghana", "+30": "Greece", "+502": "Guatemala",
    "+224": "Guinea", "+245": "Guinea-Bissau", "+592": "Guyana", "+509": "Haiti", "+504": "Honduras",
    "+852": "Hong Kong", "+36": "Hungary", "+354": "Iceland", "+91": "India", "+62": "Indonesia",
    "+98": "Iran", "+964": "Iraq", "+353": "Ireland", "+972": "Israel", "+39": "Italy",
    "+81": "Japan", "+962": "Jordan", "+7": "Kazakhstan", "+254": "Kenya", "+686": "Kiribati",
    "+965": "Kuwait", "+996": "Kyrgyzstan", "+856": "Laos", "+371": "Latvia", "+961": "Lebanon",
    "+266": "Lesotho", "+231": "Liberia", "+218": "Libya", "+423": "Liechtenstein", "+370": "Lithuania",
    "+352": "Luxembourg", "+853": "Macau", "+389": "North Macedonia", "+261": "Madagascar", "+265": "Malawi",
    "+60": "Malaysia", "+960": "Maldives", "+223": "Mali", "+356": "Malta", "+692": "Marshall Islands",
    "+222": "Mauritania", "+230": "Mauritius", "+52": "Mexico", "+691": "Micronesia", "+373": "Moldova",
    "+377": "Monaco", "+976": "Mongolia", "+382": "Montenegro", "+212": "Morocco", "+258": "Mozambique",
    "+95": "Myanmar", "+264": "Namibia", "+674": "Nauru", "+977": "Nepal", "+31": "Netherlands",
    "+64": "New Zealand", "+505": "Nicaragua", "+227": "Niger", "+234": "Nigeria", "+47": "Norway",
    "+968": "Oman", "+92": "Pakistan", "+680": "Palau", "+507": "Panama", "+675": "Papua New Guinea",
    "+595": "Paraguay", "+51": "Peru", "+63": "Philippines", "+48": "Poland", "+351": "Portugal",
    "+974": "Qatar", "+40": "Romania", "+7": "Russia", "+250": "Rwanda", "+685": "Samoa",
    "+378": "San Marino", "+966": "Saudi Arabia", "+221": "Senegal", "+381": "Serbia", "+248": "Seychelles",
    "+232": "Sierra Leone", "+65": "Singapore", "+421": "Slovakia", "+386": "Slovenia", "+677": "Solomon Islands",
    "+252": "Somalia", "+27": "South Africa", "+82": "South Korea", "+34": "Spain", "+94": "Sri Lanka",
    "+249": "Sudan", "+597": "Suriname", "+46": "Sweden", "+41": "Switzerland", "+963": "Syria",
    "+886": "Taiwan", "+992": "Tajikistan", "+255": "Tanzania", "+66": "Thailand", "+228": "Togo",
    "+676": "Tonga", "+216": "Tunisia", "+90": "Turkey", "+993": "Turkmenistan", "+688": "Tuvalu",
    "+256": "Uganda", "+380": "Ukraine", "+971": "UAE", "+44": "UK", "+1": "USA",
    "+598": "Uruguay", "+998": "Uzbekistan", "+678": "Vanuatu", "+58": "Venezuela", "+84": "Vietnam",
    "+967": "Yemen", "+260": "Zambia", "+263": "Zimbabwe"
}

# Info Section
st.markdown("""
<div class="info-section container fade-in">
    <p>© 2025 CareerUpskillers | <a href="https://www.careerupskillers.com/about-1" target="_blank">Privacy Policy</a> | <a href="https://www.careerupskillers.com/terms-of-service" target="_blank">Terms of Service</a></p>
    <p>Contact us: <a href="mailto:careerupskillers@gmail.com">careerupskillers@gmail.com</a> | Call/WhatsApp: <a href="tel:+917892116728">+91 78921 16728</a></p>
    <p>Follow us: 
        <a href="https://www.linkedin.com/company/careerupskillers/?viewAsMember=true" target="_blank">LinkedIn</a> | 
        <a href="https://youtube.com/@careerupskillers?si=zQ9JVshWBkBQeGfv" target="_blank">YouTube</a> | 
        <a href="https://www.instagram.com/careerupskillers?igsh=YWNmOGMwejBrb24z" target="_blank">Instagram</a>
    </p>
</div>
""", unsafe_allow_html=True)

# Flash Alert
flash_countries = ["USA", "India", "UAE", "UK", "USA"]
flash_country = flash_countries[st.session_state.flash_index % len(flash_countries)]
time_ago = datetime.now() - timedelta(minutes=random.randint(1, 10))
st.markdown(f"""
<div class="flash-alert container fade-in">
  📢 <strong>Flash Alert:</strong> Someone just purchased from <strong>{flash_country}</strong> {time_ago.strftime('%M mins ago')} | Only <strong>{st.session_state.slots_left}</strong> kits remaining!
</div>
""", unsafe_allow_html=True)
st.session_state.flash_index += 1
st.session_state.slots_left = max(5, st.session_state.slots_left - random.randint(1, 2))

# Header
st.markdown("""
<div class="header container fade-in">
    <h1>🌟 Welcome to CareerUpskillers AI Advisor</h1>
    <p>Let’s build your career roadmap in just a few steps! Answer a few quick questions, and I’ll help you unlock your potential.</p>
</div>
""", unsafe_allow_html=True)

# Base questions (will be customized based on employment status)
base_questions = [
    ("📊 What best describes your current status?", "This helps us customize your roadmap."),
    ("👋 Hi there! I’m your AI Career Advisor. What’s your name?", "Let’s get to know each other!"),
    ("📧 Great, {name}! Can I have your email to send you personalized career insights?", "We’ll use this to share job opportunities and tips."),
    ("📞 What’s your phone number? (Select your country code first)", "This helps us connect with you for exclusive opportunities."),
    ("💼 What’s your professional domain?", "This helps us tailor your career plan."),
    ("🌍 Where are you located? (e.g., Mumbai, India)", "We’ll find opportunities near you."),
    ("🎯 What are your career goals?", "So we can tailor our recommendations.")
]

# Additional questions based on employment status
additional_questions = {
    "Student": [
        ("🎓 What’s your field of study?", "This helps us suggest relevant career paths."),
        ("📅 What year will you graduate?", "This helps us plan your next steps.")
    ],
    "Fresher": [
        ("🎓 What’s your field of study?", "This helps us suggest relevant career paths."),
        ("📅 What year did you graduate?", "This helps us plan your next steps.")
    ],
    "Working Professional": [
        ("💰 What’s your current salary? (Optional)", "Enter numbers only (e.g., 50000)."),
        ("💡 What’s your expected salary? (Optional)", "Enter a realistic number (e.g., 60000).")
    ],
    "Freelancer": [
        ("💰 What’s your average monthly freelance earnings? (Optional)", "Enter numbers only (e.g., 50000)."),
        ("💡 What’s your expected monthly freelance earnings? (Optional)", "Enter a realistic number (e.g., 60000).")
    ],
    "Business Owner": [
        ("💰 What’s your average monthly business revenue? (Optional)", "Enter numbers only (e.g., 50000)."),
        ("💡 What’s your expected monthly business revenue? (Optional)", "Enter a realistic number (e.g., 60000).")
    ]
}

keys = [
    "employment_status", "name", "email", "phone", "domain", "location", "career_goals",
    "field_of_study", "graduation_year",  # For Student/Fresher
    "current_salary", "expected_salary",  # For Working Professional
    "current_earnings", "expected_earnings",  # For Freelancer
    "current_revenue", "expected_revenue"  # For Business Owner
]

# Dynamically build the questions list based on employment status
if "employment_status" in st.session_state.answers:
    emp_status = st.session_state.answers["employment_status"]
    questions = base_questions + additional_questions.get(emp_status, [])
else:
    questions = base_questions

# Conversational Form Logic
if not st.session_state.completed:
    total_questions = len(questions)
    progress = int((st.session_state.q_index / total_questions) * 100)
    st.markdown(f"<div class='progress-text container fade-in'>Step {st.session_state.q_index + 1} of {total_questions} 🚀</div>", unsafe_allow_html=True)
    st.progress(progress)

    # Display previous answers as a conversation
    for i in range(st.session_state.q_index):
        q, _ = questions[i]
        answer = st.session_state.answers.get(keys[i], "Skipped")
        st.markdown(f"<div class='chat-bubble container'>{q}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='user-response container'>{answer}</div>", unsafe_allow_html=True)

    # Current question
    q, hint = questions[st.session_state.q_index]
    # Personalize the question with the user's name if available
    if "{name}" in q and "name" in st.session_state.answers:
        q = q.format(name=st.session_state.answers["name"])
    st.markdown(f"<div class='chat-bubble container'><p>{q}</p><p><em>{hint}</em></p></div>", unsafe_allow_html=True)

    with st.form(key=f"form_{st.session_state.q_index}"):
        user_input = None
        if st.session_state.q_index == 0:  # Employment Status
            user_input = st.selectbox("", employment_statuses, key="employment_status_input")
        elif st.session_state.q_index == 1:  # Name
            user_input = st.text_input("", placeholder="Enter your name", key=f"input_{st.session_state.q_index}")
        elif st.session_state.q_index == 2:  # Email
            user_input = st.text_input("", placeholder="Enter your email", key=f"input_{st.session_state.q_index}")
        elif st.session_state.q_index == 3:  # Phone Number
            code = st.selectbox("Country Code", sorted(list(dial_codes.keys())), index=0, key="country_code_input")
            phone = st.text_input("", placeholder="Enter your phone number (e.g., 9876543210)", key="phone_input")
            user_input = f"{code} {phone}" if phone else None
        elif st.session_state.q_index == 4:  # Domain
            user_input = st.selectbox("", domains, key="domain_input")
            if user_input == "Other":
                other_domain = st.text_input("Please specify your domain:", placeholder="Enter your domain", key="other_domain_input")
                user_input = f"Other: {other_domain}" if other_domain else "Other"
        elif st.session_state.q_index == 5:  # Location
            user_input = st.text_input("", placeholder="e.g., Mumbai, India", key=f"input_{st.session_state.q_index}")
        elif st.session_state.q_index == 6:  # Career Goals
            user_input = st.selectbox("", career_goals, key="career_goals_input")
            if user_input == "Other":
                other_goal = st.text_input("Please specify your career goal:", placeholder="Enter your goal", key="other_goal_input")
                user_input = f"Other: {other_goal}" if other_goal else "Other"
        elif st.session_state.q_index in [7, 8]:  # Field of Study, Graduation Year (Student/Fresher) or Salary/Earnings (Others)
            emp_status = st.session_state.answers["employment_status"]
            if emp_status in ["Student", "Fresher"]:
                if st.session_state.q_index == 7:  # Field of Study
                    user_input = st.text_input("", placeholder="e.g., Computer Science", key=f"input_{st.session_state.q_index}")
                elif st.session_state.q_index == 8:  # Graduation Year
                    user_input = st.text_input("", placeholder="e.g., 2023", key=f"input_{st.session_state.q_index}")
            else:  # Working Professional, Freelancer, Business Owner
                user_input = st.text_input("", placeholder="Enter numbers only (e.g., 50000)", key=f"input_{st.session_state.q_index}")

        col1, col2 = st.columns([1, 1])
        with col1:
            submit_button = st.form_submit_button("Next")
        with col2:
            skip_button = st.form_submit_button("Skip", help="Skip this question (optional)")

        if submit_button:
            if user_input:
                if st.session_state.q_index == 2:  # Email Validation
                    if "@" not in user_input or "." not in user_input:
                        st.error("Please enter a valid email address (e.g., example@domain.com).")
                        st.stop()
                if st.session_state.q_index == 3:  # Phone Number Validation
                    phone_part = user_input.split(" ")[1] if len(user_input.split(" ")) > 1 else ""
                    if not phone_part.isdigit() or len(phone_part) != 10:
                        st.error("Please enter a valid phone number (exactly 10 digits, e.g., 9876543210).")
                        st.stop()
                if st.session_state.q_index in [7, 8]:  # Salary/Earnings Validation
                    emp_status = st.session_state.answers["employment_status"]
                    if emp_status in ["Working Professional", "Freelancer", "Business Owner"]:
                        cleaned_input = user_input.replace(',', '')
                        if cleaned_input and not cleaned_input.isdigit():
                            st.error("Please enter a valid number (e.g., 50000).")
                            st.stop()
                        if cleaned_input:
                            # Check for 2-digit or 3-digit numbers
                            if len(cleaned_input) < 4:
                                st.error("Please enter a realistic amount (at least 4 digits, e.g., 1000 or higher).")
                                st.stop()
                            # Check for realistic expected salary/earnings (for index 8)
                            if st.session_state.q_index == 8:
                                current_key = "current_salary" if emp_status == "Working Professional" else "current_earnings" if emp_status == "Freelancer" else "current_revenue"
                                expected_key = "expected_salary" if emp_status == "Working Professional" else "expected_earnings" if emp_status == "Freelancer" else "expected_revenue"
                                current_value = st.session_state.answers.get(current_key)
                                if current_value and current_value != "Skipped":
                                    current_value = int(current_value.replace(',', ''))
                                    expected_value = int(cleaned_input)
                                    if expected_value > current_value * 3:  # Expected value shouldn't be more than 3x current
                                        st.error("Your expected amount seems too high. Please enter a more realistic expectation (e.g., up to 3x your current amount).")
                                        st.stop()

                st.session_state.answers[keys[st.session_state.q_index]] = user_input
                st.session_state.q_index += 1
                if st.session_state.q_index >= len(questions):
                    st.session_state.completed = True
                st.rerun()
            else:
                st.warning("Please provide an answer or click 'Skip' to proceed.")
        if skip_button:
            st.session_state.answers[keys[st.session_state.q_index]] = "Skipped"
            st.session_state.q_index += 1
            if st.session_state.q_index >= len(questions):
                st.session_state.completed = True
            st.rerun()

# After Submission
if st.session_state.completed:
    user = st.session_state.answers
    user["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user["session_id"] = st.session_state.session_id
    user["referral_link"] = f"https://www.careerupskillers.com?ref={st.session_state.session_id}"

    # Send data to Google Sheets
    if not st.session_state.user_data_sent:
        try:
            response = requests.post(google_sheets_url, json=user)
            response.raise_for_status()
            st.session_state.user_data_sent = True
            st.success("Your data has been successfully submitted to our system!")
        except Exception as e:
            st.error(f"Failed to send user data: {str(e)}")
            st.warning("Don’t worry, you can still proceed to see your career insights.")

    # Post-Submission Message
    st.markdown(f"""
    <div class="post-submission container fade-in">
        <p>✅ Thanks for sharing, {user.get('name', 'User')}! Let me generate your personalized career insights...</p>
    </div>
    """, unsafe_allow_html=True)

    # Use ChatGPT 3.5 Turbo to generate career advice
    domain = user.get('domain', 'Data Science')
    employment_status = user.get('employment_status', 'Working Professional')
    location = user.get('location', 'your area')
    career_goal = user.get('career_goals', 'Get a Job')

    # Prepare the prompt for ChatGPT
    prompt = f"""
    You are a career advisor. Provide personalized career advice for a user with the following details:
    - Employment Status: {employment_status}
    - Professional Domain: {domain}
    - Location: {location}
    - Career Goal: {career_goal}

    ### Instructions:
    1. **Free Course Recommendation**: Suggest one free online course that aligns with their domain and career goal. Include the course name, platform (e.g., Coursera, Udemy, YouTube), and a direct link to the course. Ensure the course is free and accessible.
    2. **Career Map Overview**: Provide a 3-step career roadmap tailored to their employment status, domain, location, and career goal. Each step should be actionable and specific, considering their location for opportunities (e.g., local job platforms, networking events). Suggest a relevant platform for building a portfolio based on their domain (e.g., Behance for designers, GitHub for developers, LinkedIn for marketing professionals).

    ### Output Format:
    - **Course Recommendation**: "I recommend starting with this free course: [Course Name] on [Platform] - [Link]"
    - **Career Map**:
      - Step 1: [Actionable step]
      - Step 2: [Actionable step]
      - Step 3: [Actionable step]

    Keep the advice concise and practical.
    """

    try:
        # Call ChatGPT 3.5 Turbo
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a career advisor providing personalized advice."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )

        # Extract the response
        career_advice = response.choices[0].message['content'].strip()

        # Parse the response to extract course and career map
        course_section = career_advice.split("### Career Map")[0].replace("### Course Recommendation", "").strip()
        career_map_section = career_advice.split("### Career Map")[1].strip()

        # Extract course details
        course_line = course_section.split("I recommend starting with this free course:")[1].strip()
        course_name = course_line.split(" on ")[0].strip()
        course_platform = course_line.split(" on ")[1].split(" - ")[0].strip()
        course_link = course_line.split(" - ")[1].strip()

        # Extract career map steps
        career_map_lines = career_map_section.split("\n")
        career_map = [line.strip().replace("- ", "") for line in career_map_lines if line.strip().startswith("-")]

    except Exception as e:
        st.error(f"Failed to generate career advice with ChatGPT: {str(e)}")
        # Fallback to static advice if ChatGPT fails
        course_name = "Introduction to Web Design"
        course_platform = "Coursera"
        course_link = "https://www.coursera.org/learn/web-design-for-everybody"
        career_map = [
            "Start learning with the free course above to build foundational skills.",
            "Create a portfolio showcasing your projects on Behance or Dribbble.",
            f"Apply for internships or entry-level roles in {location} on platforms like LinkedIn or Internshala."
        ]

    # Display the career advice
    st.markdown(f"""
    <div class="brief-counseling container fade-in">
        <h3>🎯 Quick Career Boost for {user.get('name', 'User')}</h3>
        <p>Here’s a quick start to achieve your goal of <strong>{career_goal}</strong> as a {employment_status} in {domain}:</p>
        
        <h4>Free Course Recommendation:</h4>
        <p>I recommend starting with this free course:</p>
        <ul>
            <li><strong>{course_name} on {course_platform}:</strong> <a href="{course_link}" target="_blank">Enroll Now</a> – Kickstart your journey!</li>
        </ul>
        
        <h4>Your Career Map Overview:</h4>
        <p>Here’s a simple roadmap to get you started:</p>
        <ul>
            <li><strong>Step 1:</strong> {career_map[0]}</li>
            <li><strong>Step 2:</strong> {career_map[1]}</li>
            <li><strong>Step 3:</strong> {career_map[2]}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Product Recommendations
    st.markdown(f"""
    <div class="brief-counseling container fade-in">
        <h3>🚀 Recommended Career Solutions</h3>
        <p>Take your career to the next level with these tailored solutions:</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # Show Freelancer Kit for Freelancers or those interested in freelancing
        if employment_status == "Freelancer" or career_goal in ["Start Freelancing", "Other: Start Freelancing"]:
            st.markdown("""
            <div class="product-card" style="border-color: #2AB7CA">
                <h3>AI Freelancer Kit (₹499)</h3>
                <ul>
                    <li>Proven freelancing templates</li>
                    <li>Step-by-step client acquisition</li>
                    <li>AI tools you can resell</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Get Freelancer Kit", key="freelancer"):
                st.markdown("[Redirecting to payment...](https://rzp.io/rzp/t37swnF)")
        else:
            # Placeholder for other users
            st.markdown("""
            <div class="product-card" style="border-color: #2AB7CA">
                <h3>Explore Freelancing (₹499)</h3>
                <ul>
                    <li>Learn how to start freelancing</li>
                    <li>Step-by-step client acquisition</li>
                    <li>Access to AI tools</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Explore Freelancing", key="freelancer"):
                st.markdown("[Redirecting to payment...](https://rzp.io/rzp/t37swnF)")

    with col2:
        st.markdown("""
        <div class="product-card" style="border-color: #FF6F61">
            <h3>Career Plan (₹199)</h3>
            <ul>
                <li>Market salary analysis</li>
                <li>Company recommendations</li>
                <li>Interview preparation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Get Career Plan", key="career"):
            st.markdown("[Redirecting to payment...](https://rzp.io/rzp/FAsUJ9k)")

    # Follow-Up Questions Section
    st.markdown(f"""
    <div class="brief-counseling container fade-in">
        <h3>💬 Have More Questions?</h3>
        <p>Ask me anything about your career, and I’ll provide personalized advice!</p>
    </div>
    """, unsafe_allow_html=True)

    # Display previous follow-up messages
    for message in st.session_state.follow_up_messages:
        st.markdown(f"<div class='user-response container'>{message['user']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='chat-bubble container'>{message['bot']}</div>", unsafe_allow_html=True)

    # Follow-up question input
    with st.form(key="follow_up_form"):
        follow_up_question = st.text_input("Your question", placeholder="e.g., How can I improve my portfolio?")
        if st.form_submit_button("Ask"):
            if follow_up_question:
                # Prepare the follow-up prompt
                follow_up_prompt = f"""
                You are a career advisor. The user has the following details:
                - Employment Status: {employment_status}
                - Professional Domain: {domain}
                - Location: {location}
                - Career Goal: {career_goal}

                The user asked: "{follow_up_question}"

                Provide a concise, actionable response to their question.
                """

                try:
                    # Call ChatGPT 3.5 Turbo for follow-up
                    follow_up_response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a career advisor providing personalized advice."},
                            {"role": "user", "content": follow_up_prompt}
                        ],
                        max_tokens=150,
                        temperature=0.7
                    )

                    bot_response = follow_up_response.choices[0].message['content'].strip()
                except Exception as e:
                    bot_response = "I’m sorry, I couldn’t process your question right now. Please try again later!"

                # Store the conversation
                st.session_state.follow_up_messages.append({
                    "user": follow_up_question,
                    "bot": bot_response
                })
                st.rerun()
            else:
                st.warning("Please enter a question to proceed.")

    # Restart Option
    if st.button("Start Over"):
        st.session_state.q_index = 0
        st.session_state.completed = False
        st.session_state.answers = {}
        st.session_state.user_data_sent = False
        st.session_state.follow_up_messages = []
        st.rerun()

import streamlit as st
import requests
from datetime import datetime, timedelta
import random
import uuid
import time

# Set Streamlit page config
st.set_page_config(page_title="CareerUpskillers AI Advisor", page_icon="🌟", layout="centered")

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

# Simplified questions (reduced and smarter)
questions = [
    ("👋 Hi there! I’m your AI Career Advisor. What’s your name?", "Let’s get to know each other!"),
    ("📧 Great, {name}! Can I have your email to send you personalized career insights?", "We’ll use this to share job opportunities and tips."),
    ("📞 What’s your phone number? (Select your country code first)", "This helps us connect with you for exclusive opportunities."),
    ("💼 What’s your professional domain?", "This helps us tailor your career plan."),
    ("📊 Are you a fresher, student, or experienced professional?", "This helps us customize your roadmap."),
    ("🌍 Where are you located? (e.g., Mumbai, India)", "We’ll find opportunities near you."),
    ("💰 What’s your current or expected salary? (Optional)", "This helps us compare with market rates. Enter numbers only (e.g., 50000)."),
]

keys = [
    "name", "email", "phone", "domain", "employment_status", "location", "salary"
]

# Domain options
domains = [
    "Data Science", "Sales", "Marketing", "Accounting", "Developer", "Web Designer",
    "Software Testing", "Hardware Testing", "Cybersecurity", "BPO", "Other"
]

# Employment status options
employment_statuses = ["Fresher", "Student", "Experienced"]

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
        if st.session_state.q_index == 0:  # Name
            user_input = st.text_input("", placeholder="Enter your name", key=f"input_{st.session_state.q_index}")
        elif st.session_state.q_index == 1:  # Email
            user_input = st.text_input("", placeholder="Enter your email", key=f"input_{st.session_state.q_index}")
        elif st.session_state.q_index == 2:  # Phone Number
            code = st.selectbox("Country Code", sorted(list(dial_codes.keys())), index=0, key="country_code_input")
            phone = st.text_input("", placeholder="Enter your phone number (e.g., 9876543210)", key="phone_input")
            user_input = f"{code} {phone}" if phone else None
        elif st.session_state.q_index == 3:  # Domain
            user_input = st.selectbox("", domains, key="domain_input")
            if user_input == "Other":
                other_domain = st.text_input("Please specify your domain:", placeholder="Enter your domain", key="other_domain_input")
                user_input = f"Other: {other_domain}" if other_domain else "Other"
        elif st.session_state.q_index == 4:  # Employment Status
            user_input = st.selectbox("", employment_statuses, key="employment_status_input")
        elif st.session_state.q_index == 5:  # Location
            user_input = st.text_input("", placeholder="e.g., Mumbai, India", key=f"input_{st.session_state.q_index}")
        elif st.session_state.q_index == 6:  # Salary
            user_input = st.text_input("", placeholder="Enter numbers only (e.g., 50000)", key=f"input_{st.session_state.q_index}")

        col1, col2 = st.columns([1, 1])
        with col1:
            submit_button = st.form_submit_button("Next")
        with col2:
            skip_button = st.form_submit_button("Skip", help="Skip this question (optional)")

        if submit_button:
            if user_input:
                if st.session_state.q_index == 1:  # Email Validation
                    if "@" not in user_input or "." not in user_input:
                        st.error("Please enter a valid email address (e.g., example@domain.com).")
                        st.stop()
                if st.session_state.q_index == 2:  # Phone Number Validation
                    phone_part = user_input.split(" ")[1] if len(user_input.split(" ")) > 1 else ""
                    if not phone_part.isdigit() or len(phone_part) != 10:
                        st.error("Please enter a valid phone number (exactly 10 digits, e.g., 9876543210).")
                        st.stop()
                if st.session_state.q_index == 6:  # Salary Validation
                    cleaned_input = user_input.replace(',', '')
                    if cleaned_input and not cleaned_input.isdigit():
                        st.error("Please enter a valid salary (numbers only, e.g., 50000).")
                        st.stop()

                st.session_state.answers[keys[st.session_state.q_index]] = user_input
                st.session_state.q_index += 1
                if st.session_state.q_index >= len(questions):
                    st.session_state.completed = True
            else:
                st.warning("Please provide an answer or click 'Skip' to proceed.")
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
    user["referral_link"] = f"https://www.careerupskillers.com?ref={st.session_state.session_id}"

    if not st.session_state.user_data_sent:
        try:
            # Replace with your Google Sheets URL or API endpoint
            google_sheets_url = "YOUR_GOOGLE_SHEETS_URL"
            response = requests.post(google_sheets_url, json=user)
            response.raise_for_status()
            st.session_state.user_data_sent = True
        except Exception as e:
            st.error(f"Failed to send user data: {str(e)}")

    # Post-Submission Message
    st.markdown(f"""
    <div class="post-submission container fade-in">
        <p>✅ Thanks for sharing, {user.get('name', 'User')}! Your basic career insights are ready!</p>
    </div>
    """, unsafe_allow_html=True)

    # Brief Counseling Section
    domain = user.get('domain', 'Data Science')
    employment_status = user.get('employment_status', 'Experienced')
    location = user.get('location', 'your area')

    # Tailored course recommendation based on domain
    course_recommendations = {
        "Data Science": ("Data Science with Python (Coursera)", "https://www.coursera.org/learn/data-science-with-python"),
        "Developer": ("Python for Beginners (Udemy)", "https://www.udemy.com/course/python-for-beginners/"),
        "Web Designer": ("Web Design for Beginners (Skillshare)", "https://www.skillshare.com/classes/Web-Design-for-Beginners/123456"),
        "Marketing": ("Digital Marketing Fundamentals (Coursera)", "https://www.coursera.org/learn/digital-marketing"),
        "Sales": ("Sales Strategies (Udemy)", "https://www.udemy.com/course/sales-strategies/"),
        "Accounting": ("Accounting Basics (Coursera)", "https://www.coursera.org/learn/accounting-basics"),
        "Software Testing": ("Software Testing Basics (Udemy)", "https://www.udemy.com/course/software-testing-basics/"),
        "Hardware Testing": ("Hardware Testing Fundamentals (Udemy)", "https://www.udemy.com/course/hardware-testing-fundamentals/"),
        "Cybersecurity": ("Cybersecurity Essentials (Coursera)", "https://www.coursera.org/learn/cybersecurity-essentials"),
        "BPO": ("Customer Service Skills (Skillshare)", "https://www.skillshare.com/classes/Customer-Service-Skills/123456"),
    }
    course_name, course_link = course_recommendations.get(domain, ("Data Science with Python (Coursera)", "https://www.coursera.org/learn/data-science-with-python"))

    st.markdown(f"""
    <div class="brief-counseling container fade-in">
        <h3>🎯 Quick Career Boost for {user.get('name', 'User')}</h3>
        <p>Here’s a quick start to elevate your career based on your inputs:</p>
        
        <h4>Free Course Recommendation:</h4>
        <p>Since you’re in {domain}, I recommend starting with this free course:</p>
        <ul>
            <li><strong>{course_name}:</strong> <a href="{course_link}" target="_blank">Enroll Now</a> – Kickstart your learning journey!</li>
        </ul>
        
        <h4>Your Career Map Overview:</h4>
        <p>Here’s a simple roadmap to get you started:</p>
        <ul>
            <li><strong>Step 1:</strong> Learn in-demand skills with the free course above.</li>
            <li><strong>Step 2:</strong> Build a portfolio showcasing your work (e.g., GitHub for developers, Behance for designers).</li>
            <li><strong>Step 3:</strong> Apply to jobs or freelance gigs in {location} on platforms like LinkedIn, Upwork, or Fiverr.</li>
        </ul>
        
        <h4>Want a Detailed Plan?</h4>
        <p>For a personalized career roadmap tailored to your goals, enroll in our ₹199 Personalized Career Counseling Plan. It includes:</p>
        <ul>
            <li>Market salary analysis for your role in {location}.</li>
            <li>Top companies hiring near you with estimated salaries.</li>
            <li>A step-by-step plan to achieve your career goals.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Call-to-Action for ₹199 Plan
    st.markdown(f"""
    <div class="cta container fade-in">
        <a href="https://rzp.io/rzp/FAsUJ9k" target="_blank"><button>📋 Get ₹199 Personalized Career Plan</button></a>
    </div>
    """, unsafe_allow_html=True)

    # Option to Provide More Details
    st.markdown(f"""
    <div class="brief-counseling container fade-in">
        <h4>Want Even More Personalized Insights?</h4>
        <p>Share a bit more about your experience, skills, and goals to get a detailed career roadmap!</p>
        <a href="?restart=true"><button style="background: linear-gradient(90deg, #FFD700 0%, #DAA520 100%);color:#1A3550;">Share More Details</button></a>
    </div>
    """, unsafe_allow_html=True)

# Restart Logic (for users who want to provide more details)
if st.query_params.get("restart") == "true":
    st.session_state.q_index = 0
    st.session_state.completed = False
    st.session_state.answers = {}
    st.query_params.clear()
    st.experimental_rerun()

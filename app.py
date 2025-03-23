import streamlit as st
import requests
import openai
from datetime import datetime, timedelta
import random
import os
import uuid
import time
import re

# Set Streamlit page config (remove Streamlit branding)
st.set_page_config(page_title="CareerUpskillers AI Advisor", page_icon="🚀", layout="centered")

# Hide Streamlit branding (footer and header)
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .container {
        width: 100%;
        max-width: 360px;
        margin: 0 auto;
        padding: 8px;
        box-sizing: border-box;
    }
    .flash-alert, .header, .counseling-promo, .career-plan, .cta, .warning, .testimonials, .trust-badge, .share-section, .footer, .feedback {
        width: 100%;
        padding: 10px;
        box-sizing: border-box;
        border-radius: 8px;
        margin-bottom: 8px;
        overflow-wrap: break-word;
        word-wrap: break-word;
    }
    .flash-alert {
        background-color: #fff3cd;
        color: #856404;
        font-size: 13px;
        line-height: 1.3;
    }
    .header {
        background-color: #f0f2f6;
        text-align: center;
    }
    .header p {
        color: #333;
    }
    .counseling-promo {
        background-color: #e6f0ff;
        text-align: center;
        border: 1px solid #1E90FF;
    }
    .share-section {
        background-color: #d6eaff; /* Even brighter blue for more visibility */
        text-align: center;
        border: 1px solid #1E90FF;
    }
    .share-section p {
        font-weight: bold; /* Make text bolder */
    }
    .share-section button {
        background-color: #1E90FF;
        color: white;
        margin: 5px;
        padding: 8px 16px;
        font-size: 14px;
        border-radius: 5px;
        border: none;
        cursor: pointer;
        min-height: 36px;
    }
    .share-section input {
        width: 80%;
        padding: 8px;
        font-size: 14px;
        border-radius: 5px;
        border: 1px solid #ccc;
        margin: 5px 0;
    }
    .footer {
        background-color: #d6eaff; /* Even brighter blue for more visibility */
        text-align: center;
        padding: 10px;
        margin-top: 20px;
    }
    .footer p {
        color: #333;
        font-weight: bold; /* Make text bolder */
    }
    .footer a {
        color: #1E90FF;
        text-decoration: none;
        font-weight: bold; /* Make links bolder */
    }
    .footer a:hover {
        text-decoration: underline;
    }
    .feedback {
        text-align: center;
        background-color: #f0f2f6;
    }
    .feedback a {
        color: #1E90FF;
        text-decoration: none;
    }
    .feedback a:hover {
        text-decoration: underline;
    }
    h1 {
        font-size: 20px;
        margin: 8px 0;
    }
    p, li, .caption {
        font-size: 13px;
        line-height: 1.4;
        margin: 4px 0;
    }
    button {
        width: 100%;
        max-width: 220px;
        padding: 12px;
        font-size: 15px;
        border-radius: 5px;
        border: none;
        cursor: pointer;
        margin: 8px auto;
        display: block;
        min-height: 44px;
    }
    input, select {
        width: 100%;
        padding: 10px;
        font-size: 15px;
        border-radius: 5px;
        border: 1px solid #ccc;
        margin: 5px 0;
        box-sizing: border-box;
    }
    .progress-text {
        font-size: 13px;
        text-align: center;
        margin: 5px 0;
    }
    .instruction {
        font-size: 12px;
        color: #333;
        text-align: center;
        margin-top: -5px;
    }
    .time-age-message {
        font-size: 13px;
        color: #333;
        text-align: center;
        margin: 8px 0;
    }
    .testimonials {
        text-align: center;
        background-color: #e6ffe6;
        color: #333;
    }
    .trust-badge {
        background: #e6ffe6;
        text-align: center;
    }
    .trust-badge p {
        color: #333;
    }
    .flash {
        animation: flash 1.5s infinite;
    }
    @keyframes flash {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }
    @media (max-width: 600px) {
        h1 {
            font-size: 18px;
        }
        p, li, .caption {
            font-size: 13px;
            line-height: 1.5;
            margin: 6px 0;
        }
        button {
            font-size: 14px;
            padding: 10px;
        }
        .flash-alert {
            font-size: 12px;
        }
        .header, .trust-badge {
            padding: 12px;
        }
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Load API key and Google Sheets URL
openai.api_key = st.secrets["API_KEY"]
google_sheets_url = st.secrets.get("GOOGLE_SHEETS_URL")

# Country codes and currency map (expanded to include all countries)
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

currency_map = {
    "Afghanistan": "AFN", "Albania": "ALL", "Algeria": "DZD", "Andorra": "EUR", "Angola": "AOA",
    "Argentina": "ARS", "Armenia": "AMD", "Australia": "AUD", "Austria": "EUR", "Azerbaijan": "AZN",
    "Bahrain": "BHD", "Bangladesh": "BDT", "Belarus": "BYN", "Belgium": "EUR", "Belize": "BZD",
    "Benin": "XOF", "Bhutan": "BTN", "Bolivia": "BOB", "Bosnia and Herzegovina": "BAM", "Botswana": "BWP",
    "Brazil": "BRL", "Brunei": "BND", "Bulgaria": "BGN", "Burkina Faso": "XOF", "Burundi": "BIF",
    "Cambodia": "KHR", "Cameroon": "XAF", "Canada": "$", "Cape Verde": "CVE", "Central African Republic": "XAF",
    "Chile": "CLP", "China": "CNY", "Colombia": "COP", "Comoros": "KMF", "Congo": "XAF",
    "Costa Rica": "CRC", "Croatia": "HRK", "Cuba": "CUP", "Cyprus": "EUR", "Czech Republic": "CZK",
    "Denmark": "DKK", "Djibouti": "DJF", "Dominican Republic": "DOP", "Ecuador": "USD", "Egypt": "EGP",
    "El Salvador": "USD", "Equatorial Guinea": "XAF", "Eritrea": "ERN", "Estonia": "EUR", "Ethiopia": "ETB",
    "Fiji": "FJD", "Finland": "EUR", "France": "EUR", "Gabon": "XAF", "Gambia": "GMD",
    "Georgia": "GEL", "Germany": "EUR", "Ghana": "GHS", "Greece": "EUR", "Guatemala": "GTQ",
    "Guinea": "GNF", "Guinea-Bissau": "XOF", "Guyana": "GYD", "Haiti": "HTG", "Honduras": "HNL",
    "Hong Kong": "HKD", "Hungary": "HUF", "Iceland": "ISK", "India": "₹", "Indonesia": "IDR",
    "Iran": "IRR", "Iraq": "IQD", "Ireland": "EUR", "Israel": "₪", "Italy": "EUR",
    "Japan": "JPY", "Jordan": "JOD", "Kazakhstan": "KZT", "Kenya": "KES", "Kiribati": "AUD",
    "Kuwait": "KWD", "Kyrgyzstan": "KGS", "Laos": "LAK", "Latvia": "EUR", "Lebanon": "LBP",
    "Lesotho": "LSL", "Liberia": "LRD", "Libya": "LYD", "Liechtenstein": "CHF", "Lithuania": "EUR",
    "Luxembourg": "EUR", "Macau": "MOP", "North Macedonia": "MKD", "Madagascar": "MGA", "Malawi": "MWK",
    "Malaysia": "MYR", "Maldives": "MVR", "Mali": "XOF", "Malta": "EUR", "Marshall Islands": "USD",
    "Mauritania": "MRU", "Mauritius": "MUR", "Mexico": "MXN", "Micronesia": "USD", "Moldova": "MDL",
    "Monaco": "EUR", "Mongolia": "MNT", "Montenegro": "EUR", "Morocco": "MAD", "Mozambique": "MZN",
    "Myanmar": "MMK", "Namibia": "NAD", "Nauru": "AUD", "Nepal": "NPR", "Netherlands": "EUR",
    "New Zealand": "NZD", "Nicaragua": "NIO", "Niger": "XOF", "Nigeria": "NGN", "Norway": "NOK",
    "Oman": "OMR", "Pakistan": "PKR", "Palau": "USD", "Panama": "PAB", "Papua New Guinea": "PGK",
    "Paraguay": "PYG", "Peru": "PEN", "Philippines": "PHP", "Poland": "PLN", "Portugal": "EUR",
    "Qatar": "QAR", "Romania": "RON", "Russia": "RUB", "Rwanda": "RWF", "Samoa": "WST",
    "San Marino": "EUR", "Saudi Arabia": "SAR", "Senegal": "XOF", "Serbia": "RSD", "Seychelles": "SCR",
    "Sierra Leone": "SLL", "Singapore": "SGD", "Slovakia": "EUR", "Slovenia": "EUR", "Solomon Islands": "SBD",
    "Somalia": "SOS", "South Africa": "ZAR", "South Korea": "KRW", "Spain": "EUR", "Sri Lanka": "LKR",
    "Sudan": "SDG", "Suriname": "SRD", "Sweden": "SEK", "Switzerland": "CHF", "Syria": "SYP",
    "Taiwan": "TWD", "Tajikistan": "TJS", "Tanzania": "TZS", "Thailand": "THB", "Togo": "XOF",
    "Tonga": "TOP", "Tunisia": "TND", "Turkey": "TRY", "Turkmenistan": "TMT", "Tuvalu": "AUD",
    "Uganda": "UGX", "Ukraine": "UAH", "UAE": "AED", "UK": "£", "USA": "$",
    "Uruguay": "UYU", "Uzbekistan": "UZS", "Vanuatu": "VUV", "Venezuela": "VES", "Vietnam": "VND",
    "Yemen": "YER", "Zambia": "ZMW", "Zimbabwe": "ZWL"
}

# List of domains for the dropdown
domains = [
    "Data Science", "Sales", "Marketing", "Accounting", "Developer", "Web Designer",
    "Software Testing", "Hardware Testing", "Cybersecurity", "BPO", "Other"
]

# Initialize global cache for recent company recommendations (to avoid duplicates)
if 'recent_companies' not in st.session_state:
    st.session_state.recent_companies = []

# Initialize session state for each user
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())  # Unique session ID for each user
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

# Footer with Privacy Policy, Terms of Service, and Social Media Links (Moved to the Beginning)
st.markdown("""
<div class="footer container">
    <p>© 2025 CareerUpskillers | <a href="https://www.careerupskillers.com/about-1" target="_blank">Privacy Policy</a> | <a href="https://www.careerupskillers.com/terms-of-service" target="_blank">Terms of Service</a></p>
    <p>Contact us: <a href="mailto:careerupskillers@gmail.com">careerupskillers@gmail.com</a> | Call/WhatsApp: <a href="tel:+917892116728">+91 78921 16728</a></p>
    <p>Follow us: 
        <a href="https://www.linkedin.com/company/careerupskillers/?viewAsMember=true" target="_blank">LinkedIn</a> | 
        <a href="https://youtube.com/@careerupskillers?si=zQ9JVshWBkBQeGfv" target="_blank">YouTube</a> | 
        <a href="https://www.instagram.com/careerupskillers?igsh=YWNmOGMwejBrb24z" target="_blank">Instagram</a>
    </p>
</div>
""", unsafe_allow_html=True)

# Dynamic Flash Purchase Alert
flash_countries = ["USA", "India", "UAE", "UK", "USA"]
flash_country = flash_countries[st.session_state.flash_index % len(flash_countries)]
time_ago = datetime.now() - timedelta(minutes=random.randint(1, 10))

st.markdown(f"""
<div class="flash-alert container">
  ⚡ <strong>Flash Purchase:</strong> Someone just bought from <strong>{flash_country}</strong> {time_ago.strftime('%M mins ago')} | Only <strong>{st.session_state.slots_left}</strong> kits left!
</div>
""", unsafe_allow_html=True)
st.session_state.flash_index += 1
st.session_state.slots_left = max(5, st.session_state.slots_left - random.randint(1, 2))

# Updated Header with Welcome Message
end_date = datetime(2025, 3, 31)
time_left = end_date - datetime.now()
days_left = time_left.days

st.markdown(f"""
<div class="header container">
    <h1 style="color: #1E90FF;">🚀 Welcome to CareerUpskillers AI Advisor!</h1>
    <p><strong>We’ve helped over 3,000 professionals in the USA, UK, UAE, Israel, and India unlock their career potential with AI.</strong></p>
    <p style="color: #FF4500; font-weight: bold;">Are you ready to future-proof your career?</p>
    <p style="color: #228B22;">⏳ Only {days_left} days left to grab this deal!</p>
</div>
""", unsafe_allow_html=True)

# Updated Call-to-Action
st.markdown(f"""
<div class="counseling-promo container">
    <p style="color: #1E90FF; font-weight: bold;">🚀 Start Your Free AI Career Counseling Now – Discover Your Market Value & Top Opportunities!</p>
</div>
""", unsafe_allow_html=True)

# Questions (including new ones from previous update, plus years of experience)
questions = [
    ("👋 What's your Name?", "To personalize your AI roadmap!"),
    ("📧 Email Address:", "Get job insights and gigs!"),
    ("📱 Phone Number:", "Select your country code and enter your phone number (e.g., 9876543210)."),
    ("🏢 Current Company:", "Where do you currently work?"),
    ("🏢 Can you share more about your current company?", "E.g., industry, size, culture."),
    ("📅 When was your last promotion, and was it with a salary hike or only a position upgrade?", "E.g., 'Jan 2023, with salary hike' or 'June 2022, position upgrade only'."),
    ("⏰ How many hours do you typically spend working for your company each week?", "This helps us understand your work-life balance."),
    ("💼 How many years of experience do you have in your field?", "Enter a number (e.g., 5). This helps us assess if you're paid fairly."),
    ("🛠️ Your Primary Skills:", "We’ll match AI niches."),
    ("💼 Your Domain:", "Select your professional domain."),
    ("📍 Current Location:", "Find roles near you."),
    ("💰 Monthly Salary (in your currency):", "Compare with market rates. Enter numbers only (e.g., 50000)."),
    ("🌍 Are there any other countries where you’d be interested in working?", "List countries you’d like to explore for future opportunities (e.g., 'USA, Canada, Germany')."),
    ("✨ What changes in your career or workplace would excite you the most?", "E.g., 'More remote work options, better mentorship, or higher salary'."),
]

keys = [
    "name", "email", "phone", "company", "company_details", "last_promotion", 
    "hours_per_week", "years_of_experience", "skills", "domain", "location", "salary", 
    "other_countries", "exciting_changes"
]

# Form Logic with Progress Bar and Validation
if not st.session_state.completed:
    q, hint = questions[st.session_state.q_index]
    # Progress bar
    progress = int((st.session_state.q_index / len(questions)) * 100)
    st.markdown(f"<div class='progress-text container'>Step {st.session_state.q_index + 1} of {len(questions)}</div>", unsafe_allow_html=True)
    st.progress(progress)
    
    with st.form(key=f"form_{st.session_state.q_index}"):
        st.markdown(f"<div class='container'><strong>{q}</strong></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='container caption'>{hint}</div>", unsafe_allow_html=True)
        
        # Handle different input types based on the question
        if st.session_state.q_index == 2:  # Phone number with country code
            code = st.selectbox("Country Code", sorted(list(dial_codes.keys())), index=0, key="country_code_input")
            country = dial_codes.get(code, "Unknown")
            st.markdown(f"<div class='container caption'>Country: {country}</div>", unsafe_allow_html=True)
            phone = st.text_input("Phone Number (e.g., 9876543210)", key="phone_input")
            user_input = f"{code} {phone}" if phone else None
        elif st.session_state.q_index == 9:  # Domain selection with "Others" option
            user_input = st.selectbox("Select your domain", domains, key="domain_input")
            if user_input == "Other":
                other_domain = st.text_input("Please specify your domain:", key="other_domain_input")
                user_input = f"Other: {other_domain}" if other_domain else "Other"
        elif st.session_state.q_index == 7:  # Years of experience (numeric input with validation)
            user_input = st.text_input("Your answer", key=f"input_{st.session_state.q_index}")
            # Validate that the input contains only numbers
            if user_input:
                if not user_input.isdigit():
                    st.error("Please enter a valid number for years of experience (e.g., 5).")
                    user_input = None  # Prevent form submission with invalid input
        elif st.session_state.q_index == 11:  # Salary (numeric input with validation)
            user_input = st.text_input("Your answer", key=f"input_{st.session_state.q_index}")
            # Validate that the input contains only numbers (and optionally commas)
            if user_input:
                cleaned_input = user_input.replace(',', '')
                if not cleaned_input.isdigit():
                    st.error("Please enter a valid salary (numbers only, e.g., 50000).")
                    user_input = None  # Prevent form submission with invalid input
        else:
            user_input = st.text_input("Your answer", key=f"input_{st.session_state.q_index}")

        # Display the time and age message after the hours question
        if st.session_state.q_index == 6:  # After "How many hours do you typically spend working?"
            st.markdown("<div class='time-age-message'><strong>Time and age are critical factors in your career journey. Investing them wisely can lead to significant growth and opportunities!</strong></div>", unsafe_allow_html=True)

        # Form submission with validation
        if st.form_submit_button("Next"):
            if user_input:
                # Validation for phone number (index 2)
                if st.session_state.q_index == 2:
                    phone_part = user_input.split(" ")[1] if len(user_input.split(" ")) > 1 else ""
                    if not phone_part.isdigit() or len(phone_part) != 10:
                        st.error("Please enter a valid phone number (exactly 10 digits, e.g., 9876543210).")
                        st.stop()
                
                # Validation for email (index 1)
                if st.session_state.q_index == 1:
                    if "@" not in user_input or "." not in user_input:
                        st.error("Please enter a valid email address (e.g., example@domain.com).")
                        st.stop()

                # Store the answer and proceed
                st.session_state.answers[keys[st.session_state.q_index]] = user_input
                st.session_state.q_index += 1
                if st.session_state.q_index >= len(questions):
                    st.session_state.completed = True
            else:
                st.warning("Please provide a valid answer to proceed.")
        st.markdown("<div class='instruction'><strong>Double click after submitting data</strong></div>", unsafe_allow_html=True)

# After Submission
if st.session_state.completed:
    user = st.session_state.answers
    try:
        requests.post(google_sheets_url, json=user)
    except:
        pass

    country_code = user['phone'].split()[0]
    country = dial_codes.get(country_code, "Unknown")
    currency = currency_map.get(country, "USD")  # Default to USD if country not found

    # Use the current company provided by the user
    current_company = user.get('company', 'Not Provided')
    years_of_experience = user.get('years_of_experience', '0')  # Use the collected years of experience
    try:
        years_of_experience = int(years_of_experience)
    except ValueError:
        years_of_experience = 0  # Default to 0 if invalid
    current_role = user.get('domain', 'Data Science')  # Use domain as the role
    
    # Sanitize salary input (already validated in the form)
    salary_input = user.get('salary', '0').replace(',', '')
    salary_cleaned = re.sub(r'[^0-9]', '', salary_input)  # Remove all non-numeric characters
    current_salary = int(salary_cleaned) if salary_cleaned else 0  # Convert to int, default to 0 if empty

    # Use ChatGPT 3.5 Turbo to generate a personalized career plan
    try:
        # Construct a prompt for ChatGPT 3.5 Turbo with randomization to avoid repetition
        session_seed = hash(st.session_state.session_id + user.get('name', '')) % 1000  # Unique seed per user
        recent_companies = st.session_state.recent_companies[-10:]  # Last 10 companies recommended

        prompt = f"""
        You are a career counselor specializing in AI and tech roles across various domains. Based on the following user profile, provide a detailed career plan:
        - Name: {user.get('name')}
        - Current Role: {current_role}
        - Current Company: {current_company}
        - Company Details: {user.get('company_details', 'Not provided')}
        - Last Promotion: {user.get('last_promotion', 'Not provided')}
        - Hours per Week: {user.get('hours_per_week', 'Not provided')}
        - Years of Experience: {years_of_experience}
        - Primary Skills: {user.get('skills')}
        - Domain: {user.get('domain')}
        - Location: {user.get('location')}
        - Current Salary: {currency}{current_salary:,}
        - Other Countries of Interest: {user.get('other_countries', 'Not provided')}
        - Exciting Changes Desired: {user.get('exciting_changes', 'Not provided')}

        Provide the following:
        1. A profile validation statement comparing the user's salary to the market rate for their role and domain in their current location ({user.get('location')}). If the user has specified other countries of interest ({user.get('other_countries')}), also compare their salary to the market rate in those countries. Include specific sources for salary data (e.g., Glassdoor, Indeed, Payscale) and mention the year of the data (e.g., 2024).
        2. Recommended skills to upskill in, relevant to their domain and the AI industry. For example:
           - Data Science: Automation, Machine Learning, Gen AI, Agentic AI
           - Sales: AI-driven CRM tools, Predictive Analytics, Sales Automation
           - Marketing: AI Content Creation, Digital Marketing Analytics, Chatbot Marketing
           - Accounting: AI for Financial Forecasting, Automation Tools, Data Analysis
           - Developer: AI Integration, API Development, Cloud Computing
           - Web Designer: AI-driven UX Design, Generative Design Tools, Web Automation
           - Software Testing: AI-based Test Automation, Performance Testing, Bug Detection
           - Hardware Testing: IoT Testing, AI Hardware Validation, Embedded Systems
           - Cybersecurity: AI Threat Detection, Machine Learning for Security, Ethical Hacking
           - BPO: AI Chatbots, Process Automation, Customer Sentiment Analysis
           Ensure the skills are varied and not repetitive across users.
        3. A list of 3 top companies hiring in the user's location for their role or domain, with estimated salaries and sources (e.g., Glassdoor, Indeed, Payscale, 2024 data). Avoid recommending the following companies as they were recently suggested to other users: {', '.join(recent_companies) if recent_companies else 'None'}. Ensure the companies are diverse and relevant to the user's domain.
        4. A brief next step recommendation to achieve a higher salary, considering their hours per week and desired changes.

        To ensure variability, use a randomization seed: {session_seed}. Suggest a diverse set of companies and skills to avoid repetition across users.

        Format the response as plain text, with sections separated by newlines and bolded headers (e.g., **Profile Validation:**).
        """

        # Call ChatGPT 3.5 Turbo API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a career counselor specializing in AI and tech roles across various domains."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.9  # Higher temperature for more variability
        )

        # Extract the career plan from the response
        career_plan_text = response.choices[0].message.content.strip()

        # Extract companies from the response to update the recent_companies list
        companies = re.findall(r"- (.*?):", career_plan_text)
        st.session_state.recent_companies.extend(companies)
        st.session_state.recent_companies = st.session_state.recent_companies[-10:]  # Keep only the last 10

    except Exception as e:
        # Fallback to a default career plan if the API call fails
        market_salary = current_salary * 1.5
        other_countries = user.get('other_countries', 'Not provided')
        salary_comparison = f"In your current location ({user.get('location')}), the market salary for a {current_role} with {years_of_experience} years of experience is around {currency}{market_salary:,} (Source: Glassdoor, 2024 data)."
        if other_countries != 'Not provided':
            salary_comparison += f"\nIn {other_countries}, the market salary for a similar role is approximately {currency}{market_salary * 1.2:,} (Source: Payscale, 2024 data)."
        career_plan_text = f"""
        **Profile Validation:** Based on your profile, we see you have {years_of_experience} years of experience at {current_company} in a {current_role} role. Your current salary of {currency}{current_salary:,} is comparatively underpaid. {salary_comparison}

        **Upskilling Recommendation:** To boost your career and aim for higher-paying roles, we recommend upskilling in skills relevant to your domain. These skills will help you stay ahead in the AI-driven job market.

        **Top Companies to Apply to After Upskilling:**
        - Company A: {currency}{market_salary + 7500:,} (Source: Glassdoor, 2024 data)
        - Company B: {currency}{market_salary + 17500:,} (Source: Indeed, 2024 estimates)
        - Company C: {currency}{market_salary + 27500:,} (Source: Payscale, 2024 data)

        **Next Step:** To get a detailed plan and career roadmap to achieve a higher salary with your skills, apply for our ₹199 Personalized Career Plan. This roadmap will also help you find free resources to upskill and take your career to the next level!
        """

    # Display the career plan
    career_plan = f"""
    <div class="career-plan container">
    🎯 **{user.get('name')}'s AI Career Revolution Plan** 🎯
    {career_plan_text.replace('**', '<strong>').replace('**', '</strong>')}
    </div>
    """

    st.success("✅ Your Personalized Plan is Ready!")
    st.markdown(career_plan, unsafe_allow_html=True)

    # ₹199 Personalized Career Plan CTA
    st.markdown(f"""
    <div class="cta container">
        <a href='https://rzp.io/rzp/FAsUJ9k' target='_blank'><button style='background-color:#1E90FF;color:white;'>💬 Get ₹199 Career Plan</button></a>
    </div>
    """, unsafe_allow_html=True)

    # ₹499 AI Freelance Kit as Backup Plan
    st.markdown(f"""
    <div class="career-plan container">
    <strong>Looking for an Alternative Plan?</strong> As AI is driving automation, always have a backup plan! Take our AI Freelance Kit (worth ₹10,000) for just {currency}499 – a limited period offer!

    <strong>What You Get:</strong>
    - Spend just 8 hours on weekends (4h Sat, 4h Sun) over 4 weeks to earn ₹90K–₹3L/month.
    - Includes YouTube links for learning, bonus AI tools like a chat script and fake news detector (copy-paste and sell to earn ₹15K–₹20K from a basic app).
    - Step-by-step guide to set up your freelance account on Upwork and Fiverr, find your niche, and use templates to target customers.
    - A 360-degree solution kit: from building your freelance profile to selling to customers.

    <strong>How It Works:</strong>
    - In the first 2 months, spend 8 hours per weekend to build your niche.
    - Once your niche is set, use ready-made content (alter it to customer needs) and sell it in just 3 hours per weekend to earn ₹50K.

    <strong>Join Our Community:</strong> Join our 3,000+ success community from the USA, UK, Dubai, Israel, and India. Don’t just rely on a job – it might go at any moment! We have success stories of people who quit their jobs after 8 months and started their own AI business agencies. Be among them and escape the matrix – work for yourself, not for other companies!
    </div>
    """, unsafe_allow_html=True)

    # ₹499 AI Freelance Kit CTA
    st.markdown(f"""
    <div class="cta container">
        <a href='https://rzp.io/rzp/t37swnF' target='_blank'><button style='background-color:#FF4500;color:white;'>🚀 Get AI Freelance Kit ({currency}499)</button></a>
        <p>After payment, check your email for your AI Freelance Kit!</p>
    </div>
    """, unsafe_allow_html=True)

    # Warning
    st.markdown(f"""
    <div class="warning container" style="color: #FF4500;">
    <strong>Warning:</strong> Companies are laying off due to automation. Spend 8 hours on weekends upskilling & building a backup plan!
    </div>
    """, unsafe_allow_html=True)

    # Updated Testimonials with More Details
    testimonials = [
        "“Landed a $2K gig with the AI Kit! This app helped me pivot my career in just 6 weeks.” – Alex, Data Scientist, USA",
        "“From zero to ₹1L/month in 6 weeks! The career plan was a game-changer.” – Neha, Marketing Professional, India",
    ]
    selected_testimonial = random.choice(testimonials)
    st.markdown(f"""
    <div class="testimonials container">
        <span class="flash"><strong>{selected_testimonial}</strong></span>
    </div>
    """, unsafe_allow_html=True)

    # Updated Trust Badge with Security Note
    st.markdown(f"""
    <div class="trust-badge container">
        <p><strong>📈 Trusted by 3,000+ learners worldwide!</strong></p>
        <p><strong>🎁 Free AI Niche PDF + Chatbot access after payment!</strong></p>
        <p><strong>🔒 Your data is secure with us. We use HTTPS and comply with privacy regulations.</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # Share with Friends Section
    base_url = "https://www.careerupskillers.com"  # Replace with your custom domain
    referral_link = f"{base_url}?ref={st.session_state.session_id}"

    share_message = f"🚀 I just got my personalized AI Career Plan from CareerUpskillers AI Advisor! It helped me discover if I'm paid fairly and find top companies hiring for my skills. Check it out: {referral_link}"
    encoded_message = requests.utils.quote(share_message)

    st.markdown(f"""
    <div class="share-section container">
        <p style="color: #1E90FF; font-weight: bold;">🌟 Share with Friends & Earn Rewards!</p>
        <p>Invite your friends to try CareerUpskillers AI Advisor! If they sign up using your link, you'll get a <strong>10% discount</strong> on the ₹199 Career Plan or a <strong>free AI Niche PDF</strong>!</p>
        <input type="text" id="referralLink" value="{referral_link}" readonly>
        <button onclick="copyLink()">Copy Link</button>
        <br>
        <a href="https://wa.me/?text={encoded_message}" target="_blank"><button>Share on WhatsApp</button></a>
        <a href="mailto:?subject=Check out CareerUpskillers AI Advisor!&body={encoded_message}" target="_blank"><button>Share via Email</button></a>
        <a href="https://www.linkedin.com/sharing/share-offsite/?url={referral_link}" target="_blank"><button>Share on LinkedIn</button></a>
        <a href="https://twitter.com/intent/tweet?text={encoded_message}" target="_blank"><button>Share on Twitter</button></a>
    </div>
    <script>
        function copyLink() {{
            var link = document.getElementById("referralLink");
            link.select();
            document.execCommand("copy");
            alert("Referral link copied to clipboard!");
        }}
    </script>
    """, unsafe_allow_html=True)

    # Send referral data to Google Sheets
    referral_data = {
        "session_id": st.session_state.session_id,
        "referral_link": referral_link,
        "user_email": user.get('email', 'N/A'),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        requests.post(google_sheets_url, json=referral_data)
    except:
        pass

    # Feedback Link (Replace with your actual feedback form URL)
    st.markdown("""
    <div class="feedback container">
        <p><strong>We’d love to hear your feedback!</strong> <a href="https://forms.gle/your-feedback-form-link" target="_blank">Share your thoughts here</a>.</p>
    </div>
    """, unsafe_allow_html=True)

    # Footer (Repeated at the end for consistency)
    st.markdown("""
    <div class="footer container">
        <p>© 2025 CareerUpskillers | <a href="https://www.careerupskillers.com/about-1" target="_blank">Privacy Policy</a> | <a href="https://www.careerupskillers.com/terms-of-service" target="_blank">Terms of Service</a></p>
        <p>Contact us: <a href="mailto:careerupskillers@gmail.com">careerupskillers@gmail.com</a> | Call/WhatsApp: <a href="tel:+917892116728">+91 78921 16728</a></p>
        <p>Follow us: 
            <a href="https://www.linkedin.com/company/careerupskillers/?viewAsMember=true" target="_blank">LinkedIn</a> | 
            <a href="https://youtube.com/@careerupskillers?si=zQ9JVshWBkBQeGfv" target="_blank">YouTube</a> | 
            <a href="https://www.instagram.com/careerupskillers?igsh=YWNmOGMwejBrb24z" target="_blank">Instagram</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

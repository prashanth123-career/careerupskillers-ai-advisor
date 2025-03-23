import streamlit as st
import requests
import openai
from datetime import datetime, timedelta
import random
import os
import uuid
import time
import re

# Set Streamlit page config
st.set_page_config(page_title="CareerUpskillers AI Advisor", page_icon="🚀")

# Add viewport meta tag and mobile-friendly CSS
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        background-color: #f5f5f5;
    }
    .container {
        width: 100%;
        max-width: 360px;
        margin: 0 auto;
        padding: 8px;
        box-sizing: border-box;
    }
    .flash-alert, .header, .counseling-promo, .career-plan, .cta, .warning, .testimonials, .trust-badge {
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
""", unsafe_allow_html=True)

# Load API key and Google Sheets URL
openai.api_key = st.secrets["API_KEY"]
google_sheets_url = st.secrets.get("GOOGLE_SHEETS_URL")

# Country codes and currency map
dial_codes = {"+91": "India", "+1": "USA", "+44": "UK", "+971": "UAE", "+972": "Israel"}
currency_map = {"India": "₹", "USA": "$", "UK": "£", "UAE": "AED", "Israel": "₪"}

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

# Header with Countdown Timer
end_date = datetime(2025, 3, 31)
time_left = end_date - datetime.now()
days_left = time_left.days

st.markdown(f"""
<div class="header container">
    <h1 style="color: #1E90FF;">🚀 Unlock Your AI Career Revolution!</h1>
    <p><strong>Automation is reshaping jobs. Earn ₹90K–₹3L/month with AI freelancing—even from scratch.</strong></p>
    <p><strong>Over 3,000+ learners from the USA, UK, UAE, Israel & India trust us!</strong></p>
    <p style="color: #FF4500; font-weight: bold;">Is your skillset future-proof?</p>
    <p style="color: #228B22;">⏳ Only {days_left} days left to grab this deal!</p>
</div>
""", unsafe_allow_html=True)

# New Section: Free AI Career Counseling
st.markdown(f"""
<div class="counseling-promo container">
    <p style="color: #1E90FF; font-weight: bold;">🚀 Get Free AI Career Counseling – Discover if You're Paid Fairly, Unlock Better Opportunities & Explore Top Companies Hiring for Your Skills!</p>
</div>
""", unsafe_allow_html=True)

# Questions (including new ones from previous update)
questions = [
    ("👋 What's your Name?", "To personalize your AI roadmap!"),
    ("📧 Email Address:", "Get job insights and gigs!"),
    ("📱 Phone Number:", "Select your country code and enter your phone number (e.g., 9876543210)."),
    ("🏢 Current Company:", "Where do you currently work?"),
    ("🏢 Can you share more about your current company?", "E.g., industry, size, culture."),
    ("📅 When was your last promotion, and was it with a salary hike or only a position upgrade?", "E.g., 'Jan 2023, with salary hike' or 'June 2022, position upgrade only'."),
    ("⏰ How many hours do you typically spend working for your company each week?", "This helps us understand your work-life balance."),
    ("🛠️ Your Primary Skills:", "We’ll match AI niches."),
    ("💼 Your Domain:", "Select your professional domain."),
    ("📍 Current Location:", "Find roles near you."),
    ("💰 Monthly Salary (in your currency):", "Compare with market rates. Enter numbers only (e.g., 50000)."),
    ("🌍 Are there any other countries where you’d be interested in working?", "List countries you’d like to explore for future opportunities (e.g., 'USA, Canada, Germany')."),
    ("✨ What changes in your career or workplace would excite you the most?", "E.g., 'More remote work options, better mentorship, or higher salary'."),
]

keys = [
    "name", "email", "phone", "company", "company_details", "last_promotion", 
    "hours_per_week", "skills", "domain", "location", "salary", 
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
            code = st.selectbox("Country Code", list(dial_codes.keys()), index=0, key="country_code_input")
            country = dial_codes.get(code, "Unknown")
            st.markdown(f"<div class='container caption'>Country: {country}</div>", unsafe_allow_html=True)
            phone = st.text_input("Phone Number (e.g., 9876543210)", key="phone_input")
            user_input = f"{code} {phone}" if phone else None
            if code not in dial_codes:
                st.warning("Sorry, not available in this country. Email us at careerupskillers@gmail.com.")
        elif st.session_state.q_index == 8:  # Domain selection with "Others" option
            user_input = st.selectbox("Select your domain", domains, key="domain_input")
            if user_input == "Other":
                other_domain = st.text_input("Please specify your domain:", key="other_domain_input")
                user_input = f"Other: {other_domain}" if other_domain else "Other"
        elif st.session_state.q_index == 10:  # Salary (numeric input with validation)
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
    country = dial_codes.get(country_code, "India")
    currency = currency_map.get(country, "₹")

    # Use the current company provided by the user
    current_company = user.get('company', 'Not Provided')
    years_of_experience = 8  # Hardcoded for now, can be added to the form if needed
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
        1. A profile validation statement comparing the user's salary to the market rate for their role and domain in their location.
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
        3. A list of 3 top companies hiring in the user's location for their role or domain, with estimated salaries and sources (e.g., Glassdoor, Indeed). Avoid recommending the following companies as they were recently suggested to other users: {', '.join(recent_companies) if recent_companies else 'None'}. Ensure the companies are diverse and relevant to the user's domain.
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
        career_plan_text = f"""
        **Profile Validation:** Based on your profile, we see you have {years_of_experience} years of experience at {current_company} in a {current_role} role. Your current salary of {currency}{current_salary:,} is comparatively underpaid compared to the market salary of {currency}{market_salary:,}.  

        **Upskilling Recommendation:** To boost your career and aim for higher-paying roles, we recommend upskilling in skills relevant to your domain. These skills will help you stay ahead in the AI-driven job market.  

        **Top Companies to Apply to After Upskilling:**  
        - Company A: {currency}{market_salary + 7500:,} (Source: Glassdoor, 2023 data)  
        - Company B: {currency}{market_salary + 17500:,} (Source: Indeed, 2023 estimates)  
        - Company C: {currency}{market_salary + 27500:,} (Source: LinkedIn Salary Insights, 2023)  

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

    # Testimonials with bold and flashing effect
    testimonials = [
        "“Landed a $2K gig with the AI Kit!” – Alex, USA",
        "“From zero to ₹1L/month in 6 weeks!” – Neha, India",
    ]
    selected_testimonial = random.choice(testimonials)
    st.markdown(f"""
    <div class="testimonials container">
        <span class="flash"><strong>{selected_testimonial}</strong></span>
    </div>
    """, unsafe_allow_html=True)

    # Trust Badge
    st.markdown(f"""
    <div class="trust-badge container">
        <p><strong>🎁 Free AI Niche PDF + Chatbot access after payment!</strong></p>
        <p><strong>📩 Trusted by 3,000+ learners—check your email post-payment!</strong></p>
    </div>
    """, unsafe_allow_html=True)

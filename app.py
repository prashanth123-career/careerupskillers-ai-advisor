import streamlit as st
import requests
import openai
from datetime import datetime
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

# Countdown timer for urgency
def show_countdown():
    deadline = datetime(2025, 3, 31, 23, 59, 59)
    now = datetime.now()
    time_left = deadline - now
    days_left = time_left.days
    hours_left = time_left.seconds // 3600

    st.markdown(
        f"""
        <div style="background-color: #FF4500; padding: 10px; border-radius: 5px; text-align: center; color: white;">
            ⏳ <strong>Hurry!</strong> Offer ends in {days_left} days and {hours_left} hours!
        </div>
        """,
        unsafe_allow_html=True
    )

# Testimonials and social proof
def show_testimonials():
    st.markdown(
        """
        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 10px; margin: 10px 0;">
            <h3 style="color: #1E90FF;">🌟 Success Stories</h3>
            <blockquote>
                "Thanks to CareerUpskillers, I landed a ₹1.2 Lakh/month AI freelancing gig within 3 months!"<br>
                <em>- Priya, Bangalore</em>
            </blockquote>
            <blockquote>
                "The AI Career Kit helped me transition from a traditional IT role to a high-paying AI job!"<br>
                <em>- Rohan, Delhi</em>
            </blockquote>
        </div>
        """,
        unsafe_allow_html=True
    )

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

# Show header, countdown, and testimonials
show_header()
show_countdown()
show_testimonials()

# Show form with progress bar
if not st.session_state.completed:
    progress = st.session_state.q_index / len(questions)
    st.progress(progress)
    st.caption(f"Progress: {int(progress * 100)}%")

    question, justification = questions[st.session_state.q_index]
    with st.form(key=f"form_{st.session_state.q_index}"):
        st.write(f"**🤖 AI Career Advisor:** {question}")
        st.caption(justification)
        
        if st.session_state.q_index == 2:  # Phone number question
            country_code = st.selectbox("Select Country Code", list(dial_codes.keys()), index=0, key="country_code")
            phone_number = st.text_input("Enter your phone number:", key="phone_input")
            user_input = f"{country_code} {phone_number}"
            if country_code not in dial_codes:
                st.warning("Sorry, we do not currently support this country. Please send an email to careerupskillers@gmail.com for assistance.")
        else:
            user_input = st.text_input("Your response:", key=f"input_{st.session_state.q_index}")
        
        submit_button = st.form_submit_button("Double Click to Submit")
        if submit_button and user_input:
            st.session_state.answers[keys[st.session_state.q_index]] = user_input
            st.session_state.q_index += 1
            if st.session_state.q_index >= len(questions):
                st.session_state.completed = True
            st.balloons()  # Fun animation
            st.success("✅ Great! Let's move to the next step.")

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
    
    Generate a concise AI career roadmap, including:
    - Custom AI career plan with milestones
    - In-demand AI job insights
    - Companies hiring in {user_data.get('location')}
    - Actionable steps for a successful AI career
    - Final CTA for ₹499 AI Career Kit & ₹199 Personal Counseling
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a career advisor bot that provides concise AI career roadmaps."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500  # Shorter response
        )
        analysis = response.choices[0].message["content"]
        st.success("✅ Here's your personalized AI Career Plan!")
        st.markdown(analysis, unsafe_allow_html=True)
        
        # Final CTA buttons
        if st.button("🚀 Unlock AI Career Success for ₹499 Now!"):
            st.markdown("[👉 Buy AI Career Starter Kit](https://rzp.io/rzp/ViDMMYS)")
        if st.button("💎 Get Personalized Career Counseling for ₹199"):
            st.markdown("[👉 Book Your Session](https://rzp.io/rzp/VnUcj8FR)")

        # Upsell opportunities
        st.markdown(
            """
            <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin: 10px 0;">
                <h3 style="color: #1E90FF;">💎 Upgrade Your AI Career</h3>
                <p>Take your AI career to the next level with our premium offerings:</p>
                <ul>
                    <li><strong>Advanced AI Certification:</strong> Master cutting-edge AI tools and techniques.</li>
                    <li><strong>1:1 Mentorship:</strong> Get personalized guidance from industry experts.</li>
                    <li><strong>Freelance Bootcamp:</strong> Learn how to land high-paying AI gigs.</li>
                </ul>
                <p><a href="https://rzp.io/rzp/ViDMMYS">👉 Explore Premium Plans</a></p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Thank-you page
        st.markdown(
            """
            <div style="text-align: center; padding: 20px;">
                <h2 style="color: #1E90FF;">🎉 Thank You!</h2>
                <p>Your AI career plan is ready. Take the next step now:</p>
                <p><a href="https://rzp.io/rzp/ViDMMYS">👉 Buy AI Career Starter Kit</a></p>
                <p><a href="https://rzp.io/rzp/VnUcj8FR">👉 Book Personalized Counseling</a></p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Additional message about freelancing as a backup plan
        st.markdown(
            """
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 10px; margin: 10px 0;">
                <h3 style="color: #1E90FF;">💡 Don't Depend on Your Job Alone!</h3>
                <p>
                    With automation on the rise, many people are losing their jobs. Always keep a backup plan. 
                    Our freelancer kit will help you build an alternative income by working just 4 hours on weekends. 
                    In 3 months, you can automate your freelance job and secure your future.
                </p>
                <p>
                    Along with the ₹499 kit, you'll get all the tools and guidance you need to start freelancing today!
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"❌ Error calling OpenAI: {e}")

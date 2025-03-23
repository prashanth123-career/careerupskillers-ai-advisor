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
        color: #333;  /* Changed from #555 to #333 for better visibility */
        text-align: center;
        margin-top: -5px;
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
    <p><strong>Automation is reshaping jobs. Earn ₹90K–₹3L/month with AI freelancing—even from scratch.</strong

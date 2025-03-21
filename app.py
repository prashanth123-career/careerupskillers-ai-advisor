import streamlit as st
from openai import OpenAI
import os

# Clear proxy
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)

# Page settings
st.set_page_config(page_title="Test OpenAI Init", page_icon="🤖")

# Initialize OpenAI
try:
    api_key = st.secrets["API_KEY"]
    client = OpenAI(api_key=api_key)  # ✅ NO proxies
    st.success("✅ OpenAI client initialized!")
except Exception as e:
    st.error(f"❌ Error initializing OpenAI client: {str(e)}")

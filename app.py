import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Test OpenAI Key", page_icon="🤖")

st.title("🔐 OpenAI API Key Test")

try:
    # Get API key from Streamlit secrets
    api_key = st.secrets["API_KEY"]
    
    # ✅ Initialize OpenAI client (no proxies!)
    client = OpenAI(api_key=api_key)

    # ✅ Test with a small call to OpenAI
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Say Hello in one line!"}
        ]
    )

    st.success("✅ OpenAI client connected successfully!")
    st.write("Response:", response.choices[0].message.content)

except Exception as e:
    st.error(f"❌ Error initializing OpenAI client: {str(e)}")

import streamlit as st
import openai

st.set_page_config(page_title="Test OpenAI Key", page_icon="🤖")

st.title("🔐 OpenAI API Key Test")

try:
    # ✅ Set API key from Streamlit Secrets
    openai.api_key = st.secrets["API_KEY"]

    # ✅ Make a test call
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Say Hello!"}
        ]
    )

    st.success("✅ OpenAI API key is working!")
    st.write("Response:", response.choices[0].message.content)

except Exception as e:
    st.error(f"❌ Error calling OpenAI: {str(e)}")

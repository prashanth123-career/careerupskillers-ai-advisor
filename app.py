import streamlit as st
import openai

st.set_page_config(page_title="OpenAI Key Test", page_icon="🔐")
st.title("🔐 Testing OpenAI Key")

try:
    # ✅ Set OpenAI key using new SDK format
    client = openai.OpenAI(api_key=st.secrets["API_KEY"])

    # ✅ Make a simple test request
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Say Hello in one line!"}
        ]
    )

    st.success("✅ OpenAI API Key is working!")
    st.write("Response:", response.choices[0].message.content)

except Exception as e:
    st.error(f"❌ Error calling OpenAI: {str(e)}")

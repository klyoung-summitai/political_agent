import streamlit as st
import requests

st.title("AI Political Debate Chat")

# Create a form
with st.form(key="chat_form"):
    user_input = st.text_input("Enter a political topic:")
    submit_button = st.form_submit_button("Submit")  # Can submit by Enter

if submit_button:
    if user_input:
        # Example placeholder API call
        response = requests.post(
            "http://localhost:8000/api/v1/conversation",
            json={"user_id": "user-123", "topic": user_input}
        )
        st.write(response.json())
    else:
        st.error(f"API Error: {response.status_code}")

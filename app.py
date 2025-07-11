import streamlit as st
import os
from connect import main_chatbot

# ---- Constants ----
EXCEL_PATH = "latest_file.xlsx"

# ---- Page Configuration ----
st.set_page_config(page_title="KRISPR AI Analyst", layout="centered")

# ---- Custom CSS ----
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 2.2em;
        font-weight: bold;
        color: #3C6E71;
        margin-bottom: 0.5em;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 1em;
        padding-bottom: 6em;
    }
    .chat-bubble-user {
        align-self: flex-end;
        background-color: #DCF8C6;
        padding: 1em;
        border-radius: 1em;
        max-width: 70%;
    }
    .chat-bubble-bot {
        align-self: flex-start;
        background-color: #F1F0F0;
        padding: 1em;
        border-radius: 1em;
        max-width: 70%;
    }
    .input-box {
        position: fixed;
        bottom: 2em;
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
        max-width: 700px;
    }
</style>
""", unsafe_allow_html=True)

# ---- Title ----
st.markdown('<div class="main-title">🤖 KRISPR AI Business Analyst</div>', unsafe_allow_html=True)

# ---- Check if Excel file exists ----
if not os.path.exists(EXCEL_PATH):
    st.warning("⚠️ No Excel file found. Please ask the admin to upload it via the admin panel.")
    st.stop()

# ---- Chat History ----
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---- Display Chat History ----
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for sender, message in st.session_state.chat_history:
    bubble_class = "chat-bubble-user" if sender == "user" else "chat-bubble-bot"
    st.markdown(f'<div class="{bubble_class}">{message}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ---- Input Box ----
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message here...", key="user_input")
    submitted = st.form_submit_button("Send")

# ---- Handle Chat ----
if submitted and user_input:
    st.session_state.chat_history.append(("user", user_input))

    with st.spinner("Analyzing your data..."):
        try:
            answer = main_chatbot(user_input, EXCEL_PATH)
            st.session_state.chat_history.append(("bot", answer))
        except Exception as e:
            st.session_state.chat_history.append(("bot", f"❌ Error: {e}"))

    st.rerun()

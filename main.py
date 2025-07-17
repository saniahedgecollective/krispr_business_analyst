import streamlit as st
import os
import gdown
from connect import main_chatbot

EXCEL_PATH = "latest_file.xlsx"
ADMIN_PASSWORD = st.secrets.get("admin_password", "krispr2024")  # Set in .streamlit/secrets.toml

st.set_page_config(page_title="KRISPR Digital Business Analyst", layout="centered")

# ---- Sidebar ----
st.sidebar.image("KrisprLogo.png", width=120)  # Replace with your logo URL
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Go to", ["Chatbot", "Admin Panel"])

# ---- Shared CSS ----
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
html, body, .stApp {
    background: linear-gradient(120deg, #e0c3fc 0%, #8ec5fc 100%);
    font-family: 'Inter', sans-serif;
}
.main-title {
    text-align: center;
    font-size: 2.5em;
    font-weight: 700;
    color: #3a0ca3;
    margin-top: 2rem;
    margin-bottom: 2rem;
    letter-spacing: 1px;
    text-shadow: 0 2px 8px #fff8;
}
.chat-box {
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
    padding: 0 1rem 7rem;
    max-width: 700px;
    margin: 0 auto;
    background: rgba(255,255,255,0.45);
    border-radius: 24px;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.18);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.18);
}
.message {
    max-width: 80%;
    padding: 1rem 1.4rem;
    border-radius: 18px;
    font-size: 1.08rem;
    line-height: 1.6rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    display: flex;
    align-items: flex-end;
    animation: fadeIn 0.5s;
    transition: background 0.3s;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px);}
    to { opacity: 1; transform: translateY(0);}
}
.user {
    align-self: flex-end;
    background: linear-gradient(90deg, #a1c4fd 0%, #c2e9fb 100%);
    color: #22223b;
    border-top-right-radius: 0;
}
.bot {
    align-self: flex-start;
    background: linear-gradient(90deg, #fbc2eb 0%, #a6c1ee 100%);
    color: #3a0ca3;
    border-top-left-radius: 0;
}
.avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    margin-right: 0.9em;
    background: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5em;
    box-shadow: 0 2px 8px #0001;
}
.input-area {
    position: fixed;
    bottom: 1.5rem;
    left: 50%;
    transform: translateX(-50%);
    width: 100%;
    max-width: 700px;
    background: rgba(255,255,255,0.85);
    display: flex;
    gap: 0.5rem;
    padding: 0.85rem 1.2rem;
    box-shadow: 0 -2px 16px rgba(0,0,0,0.07);
    border-radius: 16px;
    z-index: 10;
    backdrop-filter: blur(6px);
}
input[type="text"] {
    flex-grow: 1;
    padding: 0.85rem 1.1rem;
    border-radius: 10px;
    border: 1.5px solid #bdbdbd;
    font-size: 1.08rem;
    background: #f7f7ff;
    transition: border 0.2s;
}
input[type="text"]:focus {
    border: 1.5px solid #3a0ca3;
    outline: none;
}
button {
    background: linear-gradient(90deg, #3a0ca3 0%, #7209b7 100%);
    color: #fff;
    padding: 0.85rem 1.3rem;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    cursor: pointer;
    font-size: 1.08rem;
    box-shadow: 0 2px 8px #0002;
    transition: background 0.2s, box-shadow 0.2s;
    display: flex;
    align-items: center;
    gap: 0.5em;
}
button:hover {
    background: linear-gradient(90deg, #7209b7 0%, #3a0ca3 100%);
    box-shadow: 0 4px 16px #0002;
}
.stButton>button {
    width: 100%;
}
.footer {
    text-align: center;
    color: #3a0ca3;
    font-size: 0.95em;
    margin-top: 2.5em;
    opacity: 0.7;
}
</style>
""", unsafe_allow_html=True)

# ---- Page: Chatbot ----
if page == "Chatbot":
    st.markdown('<div class="main-title">🤖 KRISPR Digital Business Analyst</div>', unsafe_allow_html=True)

    if not os.path.exists(EXCEL_PATH):
        st.warning("⚠️ Excel file not found. Please upload it from Admin Panel.")
        st.stop()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for role, msg in st.session_state.chat_history:
        css_class = "user" if role == "user" else "bot"
        avatar = "🧑" if role == "user" else "🤖"
        st.markdown(
            f'<div class="message {css_class}">'
            f'<div class="avatar">{avatar}</div>'
            f'<div>{msg}</div></div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        st.markdown('<div class="input-area">', unsafe_allow_html=True)
        user_input = st.text_input("", placeholder="Ask your business question...", label_visibility="collapsed")
        submitted = st.form_submit_button("Send")
        st.markdown('</div>', unsafe_allow_html=True)

    if submitted and user_input:
        st.session_state.chat_history.append(("user", user_input))
        with st.spinner("Analyzing..."):
            try:
                answer = main_chatbot(user_input, EXCEL_PATH)
                st.session_state.chat_history.append(("bot", answer))
            except Exception as e:
                st.session_state.chat_history.append(("bot", f"⚠️ Error: {e}"))
        st.experimental_rerun()

# ---- Page: Admin Panel ----
elif page == "Admin Panel":
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        st.markdown('<div class="main-title">🔐 Admin Login</div>', unsafe_allow_html=True)
        password = st.text_input("Enter admin password:", type="password")
        if st.button("Login"):
            if password == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.success("✅ Logged in as admin.")
                st.experimental_rerun()
            else:
                st.error("❌ Incorrect password.")
        st.stop()

    st.markdown('<div class="main-title">🔐 Admin Panel - Update Excel File</div>', unsafe_allow_html=True)
    if st.button("Logout"):
        st.session_state.admin_authenticated = False
        st.experimental_rerun()

    file_id = st.text_input("Paste Google Drive File ID here:")

    if st.button("⬇️ Download and Replace File"):
        if file_id.strip():
            try:
                url = f"https://drive.google.com/uc?id={file_id.strip()}"
                gdown.download(url, EXCEL_PATH, quiet=False)
                st.success("✅ Excel file updated successfully.")
            except Exception as e:
                st.error(f"❌ Failed to download: {e}")
        else:
            st.warning("⚠️ Please enter a valid file ID.")
    # ---- Footer ----
st.markdown("""
<hr style="margin-top: 3rem; margin-bottom: 1rem;">
<div class="footer">
    © 2025 KRISPR. All rights reserved. | Developed with 💡 by The Hedge Collective </div>
""", unsafe_allow_html=True)
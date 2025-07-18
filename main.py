import streamlit as st 
import os
import gdown
from connect import main_chatbot

EXCEL_PATH = "latest_file.xlsx"
ADMIN_PASSWORD = st.secrets.get("admin_password", "krispr2024")  # Set in .streamlit/secrets.toml

st.set_page_config(page_title="KRISPR Digital Business Analyst", layout="centered")

# ---- Sidebar ----
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Go to", ["Chatbot", "Admin Panel"])

# ---- Shared CSS ----
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');

html, body, .stApp {
    background: #fff !important;
    font-family: 'Inter', sans-serif;
}
.main-title {
    text-align: center;
    font-size: 2.5em;
    font-weight: 700;
    color: #222;
    margin-top: 2rem;
    margin-bottom: 2rem;
}
.chat-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
    max-width: 700px;
    margin: 0 auto 3rem;
    padding: 0 1rem;
}
.message {
    display: flex;
    align-items: flex-start;
    max-width: 100%;
    padding: 1rem 1.4rem;
    border-radius: 18px;
    font-size: 1.08rem;
    line-height: 1.6rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    animation: fadeIn 0.5s;
    transition: background 0.3s;
    position: relative;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px);}
    to { opacity: 1; transform: translateY(0);}
}
.user {
    align-self: flex-end;
    background: #D1F5D3;
    color: #1B5E20;
    border-top-right-radius: 0;
    width: fit-content;
}
.bot {
    align-self: flex-start;
    background: #D2995B;
    color: #fff;
    border-top-left-radius: 0;
    width: fit-content;
}
.avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    margin-right: 0.8em;
    margin-top: 0.3em;
    background: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4em;
    flex-shrink: 0;
    box-shadow: 0 2px 8px #0001;
}
.stButton>button {
    width: 100%;
    background: #D2995B;
    color: #fff;
    border-radius: 10px;
    font-weight: 600;
    padding: 0.6rem 1.2rem;
}
.stButton>button:hover {
    background: #b07a44;
}
.footer {
    text-align: center;
    color: #D2995B;
    font-size: 0.95em;
    margin-top: 3rem;
    margin-bottom: 2rem;
    opacity: 0.7;
}
</style>
""", unsafe_allow_html=True)

# ---- Page: Chatbot ----
if page == "Chatbot":
    st.markdown('<div class="main-title">KRISPR Digital Business Analyst</div>', unsafe_allow_html=True)

    if not os.path.exists(EXCEL_PATH):
        st.warning("⚠️ Excel file not found. Please upload it from Admin Panel.")
        st.stop()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "pending_user_input" not in st.session_state:
        st.session_state.pending_user_input = None

    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for role, msg in st.session_state.chat_history:
        css_class = "user" if role == "user" else "bot"
        avatar = "" if role == "user" else "🧠"
        avatar_html = f'<div class="avatar">{avatar}</div>' if avatar else ""
        st.markdown(
            f'<div class="message {css_class}">{avatar_html}<div>{msg}</div></div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Input form and chatbot response
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            label="",
            placeholder="Ask your business question...",
            key="chat_input",
            label_visibility="collapsed"
        )
        submitted = st.form_submit_button("Send")

    # Process chatbot input immediately after submission
    if submitted:
        user_text = user_input.strip()
        if user_text:
            st.session_state.chat_history.append(("user", user_text))
            try:
                with st.spinner("Analyzing..."):
                    response = main_chatbot(user_text, EXCEL_PATH)
                st.session_state.chat_history.append(("bot", response))
                st.rerun()
            except Exception as e:
                st.session_state.chat_history.append(("bot", f"⚠️ Error: {e}"))
                st.rerun()
        else:
            st.warning("⚠️ Please enter a message before sending.")

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
                st.rerun()
            else:
                st.error("❌ Incorrect password.")
        st.stop()

    st.markdown('<div class="main-title">🔐 Admin Panel - Update Excel File</div>', unsafe_allow_html=True)

    if st.button("Logout"):
        st.session_state.admin_authenticated = False
        st.rerun()

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
<hr>
<div class="footer">
    © 2025 KRISPR. All rights reserved. | Developed with 💡 by The Hedge Collective
</div>
""", unsafe_allow_html=True)

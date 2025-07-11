import streamlit as st
import gdown
import os

EXCEL_PATH = "latest_file.xlsx"

st.title("🔐 Admin Panel – Update Excel File")

file_id = st.text_input("Enter Google Drive File ID:")

if st.button("⬇️ Download and Replace Excel File"):
    if file_id.strip():
        try:
            url = f"https://drive.google.com/uc?id={file_id.strip()}"
            gdown.download(url, EXCEL_PATH, quiet=False)
            st.success("✅ File downloaded and updated successfully.")
        except Exception as e:
            st.error(f"❌ Failed to download file: {e}")
    else:
        st.warning("⚠️ Please enter a valid file ID.")

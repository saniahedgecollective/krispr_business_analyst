import pandas as pd
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
import streamlit as st
from prompt import prompt_template

def main_chatbot(question, excel_path):
    try:
        # Load all sheets from the Excel file
        sheets = pd.read_excel(excel_path, sheet_name=None)

        # Summarize data for LLM input
        summary = ""
        for name, df in sheets.items():
            summary += f"\n### Sheet: {name}\n{df.head(5).to_string(index=False)}\n"

        # Initialize LLM
        openai_api_key = st.secrets["OPENAI_API_KEY"]
        llm = ChatOpenAI(
            model="gpt-3.5-turbo-1106",
            temperature=0,
            openai_api_key=openai_api_key
        )

        # Chain with prompt
        chain = LLMChain(llm=llm, prompt=prompt_template)

        # Return response
        return chain.run(data=summary, question=question)

    except Exception as e:
        return f"⚠️ Error processing Excel file: {e}"
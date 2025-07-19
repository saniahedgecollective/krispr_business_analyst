import pandas as pd
import re
import streamlit as st
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from prompt import prompt_template
from business_logic import *  # All business logic functions are imported here

def main_chatbot(question, excel_path):
    # Handle basic greetings
    if question.strip().lower() in ["hi", "hello", "hey", "salaam", "salam", "hi there"]:
        return "👋 Hello! I'm your KRISPR Digital Analyst. How can I assist you today?"

    try:
        # ✅ Load and prepare data
        sheets = pd.read_excel(excel_path, sheet_name=None)
        raw_data = sheets.get("Raw Data - Date Wise")
        organic = sheets.get("Organic")
        media = sheets.get("Media")
        change = sheets.get("Overall Avg & Change")

        # Check if data is available
        if raw_data is None:
            return "❌ Unable to load the required data. Please check your Excel file."

        # ✅ Ensure datetime column is parsed
        raw_data["Local Order Date"] = pd.to_datetime(raw_data["Local Order Date"], errors="coerce")

        # Create a comprehensive data context for the LLM
        data_context = create_data_context(raw_data, organic, media, change)
        
        # Add business logic functions context
        functions_context = create_functions_context()
        
        # Combine contexts
        full_context = data_context + "\n\n" + functions_context
        
        # Use LLM for all business questions
        llm = ChatOpenAI(
            model="gpt-3.5-turbo-1106",
            temperature=0.1,  # Slightly higher for more natural responses
            api_key=st.secrets["OPENAI_API_KEY"]
        )

        chain = LLMChain(llm=llm, prompt=prompt_template)
        response = chain.run({"data": full_context, "question": question})
        
        return response

    except Exception as e:
        return f"⚠️ Error processing your request: {e}"

def create_data_context(raw_data, organic, media, change):
    """Create a comprehensive data context for the LLM"""
    
    context = "📊 **Available Data Overview:**\n\n"
    
    # Raw Data summary
    if raw_data is not None:
        context += f"**Sales Data:** {len(raw_data)} records\n"
        context += f"**Date Range:** {raw_data['Local Order Date'].min().strftime('%Y-%m-%d')} to {raw_data['Local Order Date'].max().strftime('%Y-%m-%d')}\n"
        context += f"**Products:** {raw_data['Item Description'].nunique()} unique products\n"
        context += f"**Vendors:** {raw_data['Vendor Name'].nunique()} locations\n"
        context += f"**Total Units Sold:** {raw_data['Sold Quantity'].sum():,}\n\n"
    
    # Organic data summary
    if organic is not None:
        context += f"**Organic Performance:** {len(organic)} records\n"
        context += f"**Organic Products:** {organic['PRODUCT NAME'].nunique()} products\n"
        context += f"**Weeks Available:** {organic['Week'].nunique()} weeks\n\n"
    
    # Media data summary
    if media is not None:
        context += f"**Media Performance:** {len(media)} records\n"
        context += f"**Media Products:** {media['Product Name'].nunique()} products\n"
        context += f"**Media Weeks:** {media['Week'].nunique()} weeks\n\n"
    
    # Change data summary
    if change is not None:
        context += f"**Overall Metrics:** {len(change)} records\n"
        context += f"**Overall Weeks:** {change['Week'].nunique()} weeks\n\n"
    
    # Add sample data for context
    context += "**Sample Products:**\n"
    if raw_data is not None:
        sample_products = raw_data['Item Description'].unique()[:5]
        context += ", ".join(sample_products) + "\n\n"
    
    context += "**Sample Vendors:**\n"
    if raw_data is not None:
        sample_vendors = raw_data['Vendor Name'].unique()[:5]
        context += ", ".join(sample_vendors) + "\n\n"
    
    return context

def create_functions_context():
    """Create context about available business logic functions"""
    
    context = """🔧 **Available Analysis Functions:**

**Sales & Units Analysis:**
- get_total_units_sold(raw_data, week) - Total units sold in a week
- get_product_units_sold(raw_data, product, week) - Units sold for specific product
- get_highest_units_sold_product(raw_data, week) - Best selling product in a week
- get_top_vendor_by_units(raw_data, week) - Top vendor by units sold
- compare_weekly_units_sold(raw_data, week1, week2) - Compare two weeks

**Performance Analysis:**
- get_top_performing_product(raw_data) - Overall best product
- get_top_n_performing_products(raw_data, n=5, week=None) - Top N products
- get_top5_vendors_july(raw_data) - Top 5 vendors in July

**Organic vs Media Analysis:**
- compare_organic_vs_media_units(organic, media, product, week) - Compare channels
- get_diff_daily_sv_media_organic(organic, media, product, week) - SV difference
- get_total_media_organic_units(organic, media, product, week) - Combined units

**Financial Analysis:**
- get_total_ni_media(media, week) - Total net income in media
- get_negative_ni_per_sku_products(media, week) - Products with negative NI
- get_positive_ni_per_sku_products(media, week) - Products with positive NI

**Share & Metrics Analysis:**
- get_week_with_highest_daily_msv(media) - Week with highest MSV
- get_avg_daily_osv(change, week) - Average daily OSV
- get_top_products_by_media_units(media, week, top_n=3) - Top media products

**Note:** Use these functions when you need to perform specific calculations. Always provide accurate results based on the actual data."""
    
    return context

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

        # ✅ Ensure datetime column is parsed and handle missing columns
        try:
            raw_data["Local Order Date"] = pd.to_datetime(raw_data["Local Order Date"], errors="coerce")
        except KeyError:
            return "❌ The Excel file is missing the 'Local Order Date' column. Please check your data format."

        # Validate required columns exist
        required_columns = ["Item Description", "Vendor Name", "Sold Quantity"]
        missing_columns = [col for col in required_columns if col not in raw_data.columns]
        if missing_columns:
            return f"❌ Missing required columns in your data: {', '.join(missing_columns)}. Please check your Excel file format."

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
        # Provide more helpful error messages
        error_msg = str(e)
        if "Item Description" in error_msg:
            return "❌ There's an issue with the product data in your Excel file. Please check that the 'Item Description' column exists and contains valid product names."
        elif "Vendor Name" in error_msg:
            return "❌ There's an issue with the vendor data in your Excel file. Please check that the 'Vendor Name' column exists and contains valid vendor names."
        elif "Sold Quantity" in error_msg:
            return "❌ There's an issue with the sales data in your Excel file. Please check that the 'Sold Quantity' column exists and contains valid numbers."
        else:
            return f"⚠️ Error processing your request: {error_msg}"

def create_data_context(raw_data, organic, media, change):
    """Create a comprehensive data context for the LLM"""
    
    context = "📊 **Available Data Overview:**\n\n"
    
    # Raw Data summary with error handling
    if raw_data is not None and not raw_data.empty:
        try:
            context += f"**Sales Data:** {len(raw_data)} records\n"
            
            # Handle date range safely
            if 'Local Order Date' in raw_data.columns:
                date_col = raw_data['Local Order Date']
                if not date_col.empty and date_col.notna().any():
                    min_date = date_col.min()
                    max_date = date_col.max()
                    if pd.notna(min_date) and pd.notna(max_date):
                        context += f"**Date Range:** {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}\n"
            
            # Handle other columns safely
            if 'Item Description' in raw_data.columns:
                context += f"**Products:** {raw_data['Item Description'].nunique()} unique products\n"
            
            if 'Vendor Name' in raw_data.columns:
                context += f"**Vendors:** {raw_data['Vendor Name'].nunique()} locations\n"
            
            if 'Sold Quantity' in raw_data.columns:
                total_units = raw_data['Sold Quantity'].sum()
                context += f"**Total Units Sold:** {total_units:,.0f}\n"
            
            context += "\n"
        except Exception as e:
            context += f"**Sales Data:** Available but some columns may have issues\n\n"
    
    # Organic data summary
    if organic is not None and not organic.empty:
        try:
            context += f"**Organic Performance:** {len(organic)} records\n"
            if 'PRODUCT NAME' in organic.columns:
                context += f"**Organic Products:** {organic['PRODUCT NAME'].nunique()} products\n"
            if 'Week' in organic.columns:
                context += f"**Weeks Available:** {organic['Week'].nunique()} weeks\n"
            context += "\n"
        except:
            context += "**Organic Performance:** Available\n\n"
    
    # Media data summary
    if media is not None and not media.empty:
        try:
            context += f"**Media Performance:** {len(media)} records\n"
            if 'Product Name' in media.columns:
                context += f"**Media Products:** {media['Product Name'].nunique()} products\n"
            if 'Week' in media.columns:
                context += f"**Media Weeks:** {media['Week'].nunique()} weeks\n"
            context += "\n"
        except:
            context += "**Media Performance:** Available\n\n"
    
    # Change data summary
    if change is not None and not change.empty:
        try:
            context += f"**Overall Metrics:** {len(change)} records\n"
            if 'Week' in change.columns:
                context += f"**Overall Weeks:** {change['Week'].nunique()} weeks\n"
            context += "\n"
        except:
            context += "**Overall Metrics:** Available\n\n"
    
    # Add sample data for context safely
    context += "**Sample Products:**\n"
    if raw_data is not None and 'Item Description' in raw_data.columns:
        try:
            sample_products = raw_data['Item Description'].dropna().unique()[:5]
            if len(sample_products) > 0:
                context += ", ".join(sample_products) + "\n\n"
            else:
                context += "No product names available\n\n"
        except:
            context += "Product data available but format may vary\n\n"
    
    context += "**Sample Vendors:**\n"
    if raw_data is not None and 'Vendor Name' in raw_data.columns:
        try:
            sample_vendors = raw_data['Vendor Name'].dropna().unique()[:5]
            if len(sample_vendors) > 0:
                context += ", ".join(sample_vendors) + "\n\n"
            else:
                context += "No vendor names available\n\n"
        except:
            context += "Vendor data available but format may vary\n\n"
    
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

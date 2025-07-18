import pandas as pd
import re
import streamlit as st
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from prompt import prompt_template
from business_logic import *  # ✅ Now it's at module level

def main_chatbot(question, excel_path):
    # your logic here

    # ✅ Handle greetings
    if question.strip().lower() in ["hi", "hello", "hey", "salaam", "salam", "hi there"]:
        return "👋 Hello! I’m your KRISPR Digital Analyst. How can I assist you today?"

    # ✅ Extract week, year, and product
    def extract_keywords(q):
        product = None
        week = None
        year = None

        week_match = re.search(r"week\s*(\d{1,2})", q.lower())
        if week_match:
            week = int(week_match.group(1))

        year_match = re.search(r"\b(20\d{2})\b", q)
        if year_match:
            year = int(year_match.group(1))

        possible_products = ["lettuce", "thyme", "rosemary", "basil", "tomato", "cucumber", "kale", "mix", "frisee", "pepper"]
        for word in possible_products:
            if word in q.lower():
                product = word.lower()
                break

        return product, week, year

    try:
        # ✅ Load Excel sheets
        sheets = pd.read_excel(excel_path, sheet_name=None)
        raw_data = sheets.get("Raw Data - Date Wise")
        organic = sheets.get("Organic")
        media = sheets.get("Media")
        change = sheets.get("Overall Avg & Change")

        product, week, year = extract_keywords(question)
        q = question.lower()

        # --------------------------------------
        # ✅ RULE-BASED BUSINESS LOGIC MATCHING
        # --------------------------------------

        if "highest units sold" in q and "week 25" in q:
            product, units = get_highest_units_sold_product(raw_data, 25)
            return f"📦 {product} had the highest units sold in Week 25: {units}"

        if "total units sold in week 23" in q:
            units = get_total_units_sold(raw_data, 23)
            return f"📊 Total units sold in Week 23: {units}"

        if "units sold of" in q and "week 21" in q and "thyme" in q:
            units = get_product_units_sold(raw_data, "krispr premium thyme", 21)
            return f"🧂 Krispr Premium Thyme sold {units} units in Week 21."

        if "compare total units sold in week 22 vs week 23" in q:
            u22, u23 = compare_weekly_units_sold(raw_data, 22, 23)
            return f"Week 22: {u22} units\nWeek 23: {u23} units"

        if "vendor with highest units sold in week 24" in q:
            vendor, units = get_top_vendor_by_units(raw_data, 24)
            return f"🏢 Top vendor in Week 24: {vendor} ({units} units)"

        if "compare organic vs media units" in q and "week 23" in q:
            org, med = compare_organic_vs_media_units(organic, media, "krispr premium thyme", 23)
            return f"🧪 Organic: {org} units | Media: {med} units"

        if "difference in daily sv" in q and "week 24" in q:
            org_sv, med_sv, diff = get_diff_daily_sv_media_organic(organic, media, "krispr premium thyme", 24)
            return f"📊 Organic SV: {org_sv:.2f}, Media SV: {med_sv:.2f}, Difference: {diff:.2f}"

        if "top 3 products by media units" in q and "week 22" in q:
            top3 = get_top_products_by_media_units(media, 22)
            return f"🏆 Top 3 Media Products in Week 22:\n{top3.to_string()}"

        if "week with highest daily msv" in q:
            wk, val = get_week_with_highest_daily_msv(media)
            return f"🚀 Week {wk} had the highest Daily MSV: {val}"

        if "change in media share" in q and "week 22" in q and "week 23" in q:
            diff = get_change_in_media_share(change, 22, 23)
            return f"🔄 Media Share % changed by {diff:.2f}% from Week 22 to Week 23"

        if "total media + organic units sold" in q and "week 23" in q:
            total = get_total_media_organic_units(organic, media, "krispr premium thyme", 23)
            return f"🧮 Total Media + Organic units: {total}"

        if "avg daily osv" in q and "week 23" in q:
            val = get_avg_daily_osv(change, 23)
            return f"📈 Avg Daily OSV in Week 23: {val:.2f}"

        if "net income in media" in q and "week 26" in q:
            ni = get_total_ni_media(media, 26)
            return f"💰 Total NI in Media for Week 26: {ni}"

        if "negative net income" in q and "week 24" in q:
            products = get_negative_ni_per_sku_products(media, 24)
            return f"❌ Products with negative NI in Week 24:\n" + ", ".join(products)
        if "top 5 performing products" in q and "week 24" in q:
            top5 = logic.get_top_n_performing_products(raw_data, n=5, week=24)
            return f"🏆 Top 5 Performing Products in Week 24:\n{top5.to_string()}"
 

        # --------------------------------------
        # FALLBACK TO LLM FOR GENERAL/NATURAL RESPONSES
        # --------------------------------------

        summary = "No business logic match. Using filtered data below for context:\n"

        if re.fullmatch(r"[A-Za-z0-9_-]{15,}", question.strip()):
            return "That doesn't appear to be a valid business question. Please ask a question related to business performance."

        llm = ChatOpenAI(
            model="gpt-3.5-turbo-1106",
            temperature=0,
            openai_api_key=st.secrets["OPENAI_API_KEY"]
        )

        chain = LLMChain(llm=llm, prompt=prompt_template)
        return chain.run({"data": summary, "question": question})

    except Exception as e:
        return f"⚠️ Error processing your request: {e}"

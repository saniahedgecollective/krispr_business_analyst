def main_chatbot(question, excel_path):
    import pandas as pd
    import re
    import streamlit as st
    from langchain.chains import LLMChain
    from langchain_openai import ChatOpenAI
    from prompt import prompt_template

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
        sheets = pd.read_excel(excel_path, sheet_name=None)

        raw_data = sheets.get("Raw Data - Date Wise")
        organic = sheets.get("Organic")
        media = sheets.get("Media")
        change = sheets.get("Overall Avg & Change")
        overall = sheets.get("Overall")

        product, week, year = extract_keywords(question)
        summary = ""

        # --- RAW ---
        if raw_data is not None and not raw_data.empty:
            raw_data.columns = raw_data.columns.str.strip()
            raw = raw_data.copy()
            if product:
                raw = raw[raw["Item Description"].str.lower().str.contains(product)]
            if week or year:
                raw["Week"] = pd.to_datetime(raw["Local Order Date"]).dt.isocalendar().week
                raw["Year"] = pd.to_datetime(raw["Local Order Date"]).dt.year
                if week:
                    raw = raw[raw["Week"] == week]
                if year:
                    raw = raw[raw["Year"] == year]
            raw = raw.head(30)
            if not raw.empty:
                summary += "\n### Raw Filtered:\n" + raw[["Item Description", "Vendor Name", "Local Order Date", "Sold Quantity"]].to_string(index=False) + "\n"

        # --- ORGANIC ---
        if organic is not None and not organic.empty:
            organic.columns = organic.columns.str.strip()
            org = organic.copy()
            if product:
                org = org[org["PRODUCT NAME"].str.lower().str.contains(product)]
            if week:
                org = org[org["Week"] == week]
            if year:
                org = org[org["Year"] == year]
            org = org.head(30)
            if not org.empty:
                summary += "\n### Organic Filtered:\n" + org[
                    ["Year", "Week", "PRODUCT NAME", "COGS", "Daily Organic SV", "Organic Share of Sales %", "Total Daily Net Income Organic (Excl. Tax)"]
                ].to_string(index=False) + "\n"

        # --- MEDIA ---
        if media is not None and not media.empty:
            media.columns = media.columns.str.strip()
            med = media.copy()
            if product:
                med = med[med["Product Name"].str.lower().str.contains(product)]
            if week:
                med = med[med["Week"] == week]
            if year:
                med = med[med["Year"] == year]
            med = med.head(30)
            if not med.empty:
                summary += "\n### Media Filtered:\n" + med[
                    ["Year", "Week", "Product Name", "COGS", "CPA", "Daily MSV", "Media Units Sold", "Media Share %", "NI per SKU", "Total Daily NI Media"]
                ].to_string(index=False) + "\n"

        # --- OVERALL ---
        if overall is not None and not overall.empty:
            overall.columns = overall.columns.str.strip()
            ov = overall.copy()
            if product:
                ov = ov[ov["Product Name"].str.lower().str.contains(product)]
            if week:
                ov = ov[ov["Week"] == week]
            if year:
                ov = ov[ov["Year"] == year]
            ov = ov.head(30)
            if not ov.empty:
                summary += "\n### Overall Filtered:\n" + ov[
                    ["Year", "Week", "Product Name", "Total Units sold", "Invoiced/ Supplied", "Overall SV", "Media Units Sold", "Daily Media SV", "Org Units sold", "Daily Org SV", "Media share of sales %", "Organic Share of sales%"]
                ].to_string(index=False) + "\n"

        # --- CHANGE ---
        if change is not None and not change.empty:
            change.columns = change.columns.str.strip()
            ch = change.copy()
            if week:
                ch = ch[ch["Week"] == week]
            if year:
                ch = ch[ch["year"] == year]
            ch = ch.head(10)  # change is wide — reduce further
            if not ch.empty:
                change_cols = [
                    "Week", "year", "Avg TCS Media", "Avg TCS Media % Change", "Avg NI  SKU Media", "Avg NI SKU Media % Change",
                    "Total Daily NI Media", "Total Daily NI Media % Change", "Avg TCS Organic (Fixed)", "Avg NI SKU Organic (Fixed)",
                    "Total Daily NI Organic", "Total Daily NI Organic % Change", "Avg Overall Daily SV", "Avg Overall Daily SV % Change",
                    "Avg Daily MSV", "Avg Daily MSV % Change", "Avg Daily OSV", "Avg Daily OSV % Change",
                    "Media Share %", "Media Share % % Change", "Organic Share %", "Organic Share % % Change"
                ]
                summary += "\n### Change Filtered:\n" + ch[change_cols].to_string(index=False) + "\n"

        if not summary.strip():
            summary = "No relevant data was matched from the sheets, but try to interpret the user's question based on general logic or respond helpfully if possible."
        # -- Check for gibberish or meaningless input like IDs or tokens --
        if re.fullmatch(r"[A-Za-z0-9_-]{15,}", question.strip()):
          return "⚠️ That doesn't appear to be a valid business question. Please rephrase your query to relate to product performance, sales, marketing, or supply chain."

        llm = ChatOpenAI(
            model="gpt-3.5-turbo-1106",
            temperature=0,
            openai_api_key=st.secrets["OPENAI_API_KEY"]
        )

        chain = LLMChain(llm=llm, prompt=prompt_template)
        return chain.run({"data": summary, "question": question})

    except Exception as e:
        return f"⚠️ Error processing file: {e}"

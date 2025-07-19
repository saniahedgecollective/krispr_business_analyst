import pandas as pd

# ---------- Shared Helper ----------
def preprocess_week(df, date_col="Local Order Date"):
    df = df.copy()
    df["Week"] = pd.to_datetime(df[date_col]).dt.isocalendar().week
    return df


# ---------- Units Sold & Quantity Insights ----------
def get_total_units_sold(raw_data, week):
    df = preprocess_week(raw_data)
    return df[df["Week"] == week]["Sold Quantity"].sum()

def get_product_units_sold(raw_data, product, week):
    df = preprocess_week(raw_data)
    mask = (df["Item Description"].str.lower() == product.lower()) & (df["Week"] == week)
    return df[mask]["Sold Quantity"].sum()

def get_vendor_units_sold(raw_data, vendor):
    return raw_data[raw_data["Vendor Name"].str.lower() == vendor.lower()]["Sold Quantity"].sum()

def compare_weekly_units_sold(raw_data, week1, week2):
    df = preprocess_week(raw_data)
    units_1 = df[df["Week"] == week1]["Sold Quantity"].sum()
    units_2 = df[df["Week"] == week2]["Sold Quantity"].sum()
    return units_1, units_2

def get_top_performing_product(raw_data):
    df = raw_data.copy()
    grouped = df.groupby("Item Description")["Sold Quantity"].sum()
    if grouped.empty:
        return None, None
    return grouped.idxmax(), grouped.max()

def get_worst_performing_product(raw_data):
    df = raw_data.copy()
    grouped = df.groupby("Item Description")["Sold Quantity"].sum()
    if grouped.empty:
        return None, None
    return grouped.idxmin(), grouped.min()

def get_top_vendor_by_units(raw_data, week):
    df = preprocess_week(raw_data)
    grouped = df[df["Week"] == week].groupby("Vendor Name")["Sold Quantity"].sum()
    if grouped.empty:
        return None, 0
    return grouped.idxmax(), grouped.max()

def get_top5_vendors_july(raw_data):
    df = raw_data.copy()
    df["Month"] = pd.to_datetime(df["Local Order Date"]).dt.month
    july_df = df[df["Month"] == 7]
    return july_df.groupby("Vendor Name")["Sold Quantity"].sum().sort_values(ascending=False).head(5)


# ---------- COGS & Performance ----------
def get_top_products_by_cogs(organic, week, top_n=5):
    return organic[organic["Week"] == week].sort_values("COGS", ascending=False).head(top_n)

def get_highest_cogs_organic(organic, week):
    df = organic[organic["Week"] == week]
    if df.empty:
        return None, None
    idx = df["COGS"].idxmax()
    return df.loc[idx, "PRODUCT NAME"], df.loc[idx, "COGS"]


# ---------- Share % and Media vs Organic ----------
def get_week_highest_organic_share(organic):
    grouped = organic.groupby("Week")["Organic Share of Sales %"].mean()
    if grouped.empty:
        return None, None
    return grouped.idxmax(), grouped.max()

def get_lowest_organic_share_product(organic, week):
    df = organic[organic["Week"] == week]
    if df.empty:
        return None, None
    idx = df["Organic Share of Sales %"].idxmin()
    return df.loc[idx, "PRODUCT NAME"], df.loc[idx, "Organic Share of Sales %"]

def compare_media_organic_share(organic, media, product, week):
    org_share = organic[(organic["PRODUCT NAME"].str.lower() == product.lower()) & (organic["Week"] == week)]["Organic Share of Sales %"].mean()
    med_share = media[(media["Product Name"].str.lower() == product.lower()) & (media["Week"] == week)]["Media Share %"].mean()
    return org_share, med_share

def get_organic_share_of_sales(organic, product, week):
    df = organic[(organic["PRODUCT NAME"].str.lower() == product.lower()) & (organic["Week"] == week)]
    return df["Organic Share of Sales %"].mean()


# ---------- Media vs Organic Units / SV ----------
def compare_organic_vs_media_units(organic, media, product, week):
    org_units = organic[(organic["PRODUCT NAME"].str.lower() == product.lower()) & (organic["Week"] == week)]["Org Units sold"].sum()
    med_units = media[(media["Product Name"].str.lower() == product.lower()) & (media["Week"] == week)]["Media Units Sold"].sum()
    return org_units, med_units

def get_diff_daily_sv_media_organic(organic, media, product, week):
    org_sv = organic[(organic["PRODUCT NAME"].str.lower() == product.lower()) & (organic["Week"] == week)]["Daily Organic SV"].mean()
    med_sv = media[(media["Product Name"].str.lower() == product.lower()) & (media["Week"] == week)]["Daily MSV"].mean()
    return org_sv, med_sv, (org_sv - med_sv if pd.notna(org_sv) and pd.notna(med_sv) else None)

def get_total_media_organic_units(organic, media, product, week):
    org_units = organic[(organic["PRODUCT NAME"].str.lower() == product.lower()) & (organic["Week"] == week)]["Org Units sold"].sum()
    med_units = media[(media["Product Name"].str.lower() == product.lower()) & (media["Week"] == week)]["Media Units Sold"].sum()
    return org_units + med_units


# ---------- Net Income ----------
def get_weekly_ni_organic(organic, product):
    df = organic[organic["PRODUCT NAME"].str.lower() == product.lower()]
    return df.groupby("Week")["Net Income Per SKU Organic (Excl. Tax)"].mean()

def get_avg_ni_sku_organic(organic, week):
    return organic[organic["Week"] == week]["Avg NI SKU Organic (Fixed)"].mean()

def get_avg_ni_per_sku_media(media, week):
    return media[media["Week"] == week]["NI per SKU"].mean()

def get_avg_ni_per_sku_media_by_product(media, product):
    return media[media["Product Name"].str.lower().str.contains(product.lower())]["NI per SKU"].mean()

def get_negative_ni_per_sku_products(media, week):
    return media[(media["Week"] == week) & (media["NI per SKU"] < 0)]["Product Name"].unique().tolist()

def get_positive_ni_per_sku_products(media, week):
    return media[(media["Week"] == week) & (media["NI per SKU"] > 0)]["Product Name"].unique().tolist()

def get_top_ni_product_in_media(media, week):
    df = media[media["Week"] == week]
    if df.empty:
        return None, 0
    idx = df["Total Daily NI Media"].idxmax()
    return df.loc[idx, "Product Name"], df.loc[idx, "Total Daily NI Media"]

def get_total_ni_media(media, week):
    return media[media["Week"] == week]["Total Daily NI Media"].sum()


# ---------- SV Metrics ----------
def get_week_with_highest_daily_msv(media):
    idx = media["Daily MSV"].idxmax()
    return media.loc[idx, "Week"], media.loc[idx, "Daily MSV"]

def get_avg_daily_osv(change, week):
    return change[change["Week"] == week]["Avg Daily OSV"].mean()

def get_total_organic_sv(organic, week):
    return organic[organic["Week"] == week]["Daily Organic SV"].sum()

def get_highest_daily_org_sv(organic, week):
    df = organic[organic["Week"] == week]
    if df.empty:
        return None, 0
    idx = df["Daily Organic SV"].idxmax()
    return df.loc[idx, "PRODUCT NAME"], df.loc[idx, "Daily Organic SV"]

def get_week_with_lowest_avg_overall_sv(change):
    idx = change["Avg Overall Daily SV"].idxmin()
    return change.loc[idx, "Week"], change.loc[idx, "Avg Overall Daily SV"]


# ---------- Product Rankings ----------
def get_highest_units_sold_product(raw_data, week):
    df = preprocess_week(raw_data)
    grouped = df[df["Week"] == week].groupby("Item Description")["Sold Quantity"].sum()
    if grouped.empty:
        return None, 0
    return grouped.idxmax(), grouped.max()

def get_top_products_by_media_units(media, week, top_n=3):
    df = media[media["Week"] == week]
    grouped = df.groupby("Product Name")["Media Units Sold"].sum()
    return grouped.sort_values(ascending=False).head(top_n)

def get_top_n_performing_products(raw_data, n=5, week=None, metric="Sold Quantity"):
    df = raw_data.copy()
    if week is not None:
        df["Week"] = pd.to_datetime(df["Local Order Date"]).dt.isocalendar().week
        df = df[df["Week"] == week]
    grouped = df.groupby("Item Description")[metric].sum().sort_values(ascending=False).head(n)
    return grouped  # Series: product name -> metric value



def get_avg_overall_daily_sv(change, week):
    """Get the average overall daily SV for a specific week"""
    df = change[change["Week"] == week]
    if df.empty:
        return None
    return df["Avg Overall Daily SV"].mean()

def get_change_in_media_share(change, week1, week2):
    """Get the change in media share percentage between two weeks"""
    df1 = change[change["Week"] == week1]
    df2 = change[change["Week"] == week2]
    
    if df1.empty or df2.empty:
        return None
    
    share1 = df1["Media Share %"].mean()
    share2 = df2["Media Share %"].mean()
    
    return share2 - share1
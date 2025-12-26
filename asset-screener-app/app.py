import streamlit as st
import pandas as pd
import numpy as np

# ======================================
# Page Config
# ======================================
st.set_page_config(
    page_title="Asset Value Stock Screener",
    layout="wide"
)

# ======================================
# Load Data
# ======================================
@st.cache_data
def load_data():
    return pd.read_csv("sp500_all.csv")

df = load_data()

# ======================================
# Title
# ======================================
st.title("📊 Asset Value Stock Screener")
st.caption("PBR・時価総額を用いた含み資産可能性スクリーニング")

# ======================================
# Sidebar – Screening Conditions
# ======================================
st.sidebar.header("🔍 Screening Conditions")

max_pbr = st.sidebar.slider(
    "Max PBR",
    min_value=0.1,
    max_value=3.0,
    value=0.8,
    step=0.05
)

min_pbr = st.sidebar.slider(
    "Min PBR (exclude extreme values)",
    min_value=0.0,
    max_value=0.5,
    value=0.05,
    step=0.01
)

min_market_cap = st.sidebar.number_input(
    "Min Market Cap (USD)",
    value=10_000_000_000,
    step=1_000_000_000
)

top_n = st.sidebar.slider(
    "Show Top N",
    min_value=10,
    max_value=200,
    value=50,
    step=10
)

# Sector filter
sectors = sorted(df["sector"].dropna().unique())
selected_sectors = st.sidebar.multiselect(
    "Sector Filter",
    options=sectors,
    default=sectors
)

# ======================================
# Pre-processing
# ======================================
df_screen = df.copy()

df_screen = df_screen[
    (df_screen["pbr"].notna()) &
    (df_screen["market_cap"].notna()) &
    (df_screen["pbr"] >= min_pbr) &
    (df_screen["pbr"] <= max_pbr) &
    (df_screen["market_cap"] >= min_market_cap) &
    (df_screen["sector"].isin(selected_sectors))
]

# ======================================
# Asset Score Calculation
# ======================================
df_screen["asset_score"] = (1 / df_screen["pbr"]) * df_screen["market_cap"]
df_screen["asset_score_log"] = np.log10(df_screen["asset_score"])

df_screen = df_screen.sort_values("asset_score", ascending=False)

# ======================================
# Result Table
# ======================================
st.subheader("🏆 Screening Result")

st.caption(
    "asset_score = (1 / PBR) × Market Cap ｜ "
    "log10(asset_score) を表示して比較しやすくしています"
)

display_cols = [
    "ticker",
    "name",
    "sector",
    "price",
    "market_cap",
    "pbr",
    "roe",
    "asset_score_log",
]

display_cols = [c for c in display_cols if c in df_screen.columns]

st.dataframe(
    df_screen[display_cols].head(top_n),
    use_container_width=True
)

# ======================================
# CSV Download
# ======================================
st.download_button(
    label="⬇ Download CSV",
    data=df_screen[display_cols].head(top_n).to_csv(index=False),
    file_name="asset_value_screening.csv",
    mime="text/csv"
)

# ======================================
# Footer
# ======================================
st.markdown("---")
st.caption(
    "※ 本スクリーナーは財務指標に基づく簡易スクリーニングです。"
    " 実際の投資判断は自己責任で行ってください。"
)

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime

st.set_page_config(
    page_title="Global Asset Dashboard",
    layout="wide"
)

st.title("🌎 Global Asset Dashboard")
st.markdown("股票、債券、商品、REITs、避險資產績效比較")

# =========================
# ETF Universe
# =========================

EQUITY_ETFS = {
    "美國(SPY)": "SPY",
    "日本(EWJ)": "EWJ",
    "中國(MCHI)": "MCHI",
    "台灣(EWT)": "EWT",
    "韓國(EWY)": "EWY",
    "印度(INDA)": "INDA",
    "德國(EWG)": "EWG",
    "法國(EWQ)": "EWQ",
    "英國(EWU)": "EWU",
    "加拿大(EWC)": "EWC",
    "澳洲(EWA)": "EWA",
    "巴西(EWZ)": "EWZ",
    "越南(VNM)": "VNM"
}

TREASURY_ETFS = {
    "短期公債(SHY)": "SHY",
    "中期公債(IEF)": "IEF",
    "長期公債(TLT)": "TLT",
    "超短期公債(BIL)": "BIL"
}

IG_ETFS = {
    "投資級公司債(LQD)": "LQD",
    "短天期投資級債(VCSH)": "VCSH"
}

HY_ETFS = {
    "高收益債(HYG)": "HYG",
    "非投資級債(JNK)": "JNK"
}

EMD_ETFS = {
    "新興市場美元債(EMB)": "EMB",
    "新興市場美元債(VWOB)": "VWOB"
}

LOCAL_ETFS = {
    "新興市場當地貨幣債(LEMB)": "LEMB"
}

COMMODITY_ETFS = {
    "黃金(GLD)": "GLD",
    "白銀(SLV)": "SLV",
    "原油(USO)": "USO",
    "天然氣(UNG)": "UNG",
    "工業金屬(DBB)": "DBB",
    "農產品(DBA)": "DBA",
    "商品綜合(DBC)": "DBC"
}

REIT_ETFS = {
    "美國REIT(VNQ)": "VNQ",
    "全球REIT(REET)": "REET"
}

SAFE_ETFS = {
    "美元(UUP)": "UUP",
    "日圓(FXY)": "FXY",
    "瑞郎(FXF)": "FXF"
}

ASSET_GROUPS = {
    "股票": EQUITY_ETFS,
    "公債": TREASURY_ETFS,
    "投資級債": IG_ETFS,
    "非投資級債": HY_ETFS,
    "新興市場債": EMD_ETFS,
    "新興市場當地貨幣債": LOCAL_ETFS,
    "商品": COMMODITY_ETFS,
    "REITs": REIT_ETFS,
    "避險資產": SAFE_ETFS
}

# =========================
# Sidebar
# =========================

st.sidebar.header("設定")

selected_groups = st.sidebar.multiselect(
    "選擇資產類別",
    list(ASSET_GROUPS.keys()),
    default=["股票", "公債"]
)

available_assets = {}

for g in selected_groups:
    available_assets.update(ASSET_GROUPS[g])

selected_assets = st.sidebar.multiselect(
    "選擇ETF",
    list(available_assets.keys()),
    default=list(available_assets.keys())[:5]
)

period_choice = st.sidebar.selectbox(
    "觀察期間",
    [
        "MTD",
        "YTD",
        "1M",
        "3M",
        "6M",
        "1Y",
        "2Y",
        "3Y",
        "5Y"
    ],
    index=4
)

# =========================
# 期間設定
# =========================

end_date = pd.Timestamp.today()

if period_choice == "MTD":
    start_date = end_date.replace(day=1)

elif period_choice == "YTD":
    start_date = pd.Timestamp(
        year=end_date.year,
        month=1,
        day=1
    )

elif period_choice == "1M":
    start_date = end_date - pd.DateOffset(months=1)

elif period_choice == "3M":
    start_date = end_date - pd.DateOffset(months=3)

elif period_choice == "6M":
    start_date = end_date - pd.DateOffset(months=6)

elif period_choice == "1Y":
    start_date = end_date - pd.DateOffset(years=1)

elif period_choice == "2Y":
    start_date = end_date - pd.DateOffset(years=2)

elif period_choice == "3Y":
    start_date = end_date - pd.DateOffset(years=3)

else:
    start_date = end_date - pd.DateOffset(years=5)

# =========================
# 執行
# =========================

if st.button("開始分析"):

    if len(selected_assets) == 0:
        st.warning("請至少選擇1個ETF")
        st.stop()

    prices = pd.DataFrame()

    progress = st.progress(0)

    for i, asset in enumerate(selected_assets):

        ticker = available_assets[asset]

        try:
            data = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                auto_adjust=True,
                progress=False
            )

            if len(data) > 0:
                prices[asset] = data["Close"]

        except:
            pass

        progress.progress((i + 1) / len(selected_assets))

    if prices.empty:
        st.error("無法下載資料")
        st.stop()

    prices = prices.ffill()

    # =====================
    # Return
    # =====================

    returns = (
        prices.iloc[-1]
        / prices.iloc[0]
        - 1
    ) * 100

    ranking = pd.DataFrame({
        "報酬率(%)": returns
    })

    ranking = ranking.sort_values(
        "報酬率(%)",
        ascending=False
    )

    st.subheader(f"📈 {period_choice}績效排名")

    st.dataframe(
        ranking.style.format("{:.2f}")
    )

    # =====================
    # Ranking Chart
    # =====================

    fig_rank = px.bar(
        ranking,
        x="報酬率(%)",
        y=ranking.index,
        orientation="h",
        title=f"{period_choice} 報酬率排名"
    )

    st.plotly_chart(
        fig_rank,
        use_container_width=True
    )

    # =====================
    # Heatmap
    # =====================

    st.subheader("🔥 Heatmap")

    heatmap_df = ranking.T

    fig_heat = px.imshow(
        heatmap_df,
        text_auto=".1f",
        color_continuous_scale="RdYlGn",
        aspect="auto"
    )

    st.plotly_chart(
        fig_heat,
        use_container_width=True
    )

    # =====================
    # Performance Chart
    # =====================

    cumulative = (
        prices / prices.iloc[0]
    ) * 100

    st.subheader("📊 累積績效")

    fig_line = px.line(
        cumulative,
        x=cumulative.index,
        y=cumulative.columns
    )

    st.plotly_chart(
        fig_line,
        use_container_width=True
    )

    # =====================
    # Momentum
    # =====================

    st.subheader("🚀 Momentum Ranking")

    lookback = min(252, len(prices)-1)

    if lookback > 20:

        momentum = (
            prices.iloc[-1]
            / prices.iloc[-lookback]
            - 1
        ) * 100

        momentum = pd.DataFrame({
            "12M Momentum(%)": momentum
        })

        momentum = momentum.sort_values(
            "12M Momentum(%)",
            ascending=False
        )

        st.dataframe(
            momentum.style.format("{:.2f}")
        )

    # =====================
    # Export Excel
    # =====================

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter"
    ) as writer:

        ranking.to_excel(
            writer,
            sheet_name="Ranking"
        )

        cumulative.to_excel(
            writer,
            sheet_name="Performance"
        )

        prices.to_excel(
            writer,
            sheet_name="Price"
        )

    st.download_button(
        "📥下載Excel",
        data=output.getvalue(),
        file_name=f"global_asset_dashboard_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

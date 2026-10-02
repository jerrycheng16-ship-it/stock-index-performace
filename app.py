import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(
    page_title="Global Asset Dashboard",
    layout="wide"
)

st.title("🌎 Global Asset Dashboard")

# =========================================================
# ETF Universe
# =========================================================

ALL_ETFS = {

    # 美國
    "美國-SPY":"SPY",
    "美國-IVV":"IVV",
    "美國-VTI":"VTI",
    "美國科技-QQQ":"QQQ",
    "美國成長-VUG":"VUG",
    "美國價值-VTV":"VTV",
    "美國小型股-IWM":"IWM",

    # 亞洲
    "台灣-EWT":"EWT",
    "日本-EWJ":"EWJ",
    "中國-MCHI":"MCHI",
    "中國A股-CNYA":"CNYA",
    "香港-EWH":"EWH",
    "韓國-EWY":"EWY",
    "印度-INDA":"INDA",
    "印尼-EIDO":"EIDO",
    "馬來西亞-EWM":"EWM",
    "新加坡-EWS":"EWS",
    "泰國-THD":"THD",
    "越南-VNM":"VNM",
    "菲律賓-EPHE":"EPHE",

    # 歐洲
    "英國-EWU":"EWU",
    "德國-EWG":"EWG",
    "法國-EWQ":"EWQ",
    "義大利-EWI":"EWI",
    "西班牙-EWP":"EWP",
    "瑞士-EWL":"EWL",
    "瑞典-EWD":"EWD",
    "挪威-ENOR":"ENOR",
    "波蘭-EPOL":"EPOL",
    "土耳其-TUR":"TUR",

    # 美洲
    "加拿大-EWC":"EWC",
    "墨西哥-EWW":"EWW",
    "巴西-EWZ":"EWZ",
    "智利-ECH":"ECH",
    "秘魯-EPU":"EPU",

    # 中東
    "沙烏地-KSA":"KSA",
    "阿聯-UAE":"UAE",
    "卡達-QAT":"QAT",

    # 非洲
    "南非-EZA":"EZA",

    # 區域
    "全球股票-ACWI":"ACWI",
    "MSCI世界-URTH":"URTH",
    "新興市場-EEM":"EEM",
    "新興市場-VWO":"VWO",
    "亞太除日本-AAXJ":"AAXJ",
    "歐洲-VGK":"VGK",

    # 美國公債
    "超短公債-BIL":"BIL",
    "短期公債-SHY":"SHY",
    "中期公債-IEF":"IEF",
    "長期公債-TLT":"TLT",
    "超長公債-VGLT":"VGLT",

    # 投資級債
    "投資級債-LQD":"LQD",
    "短投資級債-VCSH":"VCSH",
    "中投資級債-VCIT":"VCIT",

    # 高收益債
    "高收益債-HYG":"HYG",
    "非投資級債-JNK":"JNK",

    # 新興市場債
    "新興美元債-EMB":"EMB",
    "新興美元債-VWOB":"VWOB",

    # 新興市場當地貨幣債
    "新興本幣債-LEMB":"LEMB",

    # 商品
    "黃金-GLD":"GLD",
    "黃金-IAU":"IAU",
    "白銀-SLV":"SLV",
    "原油-USO":"USO",
    "天然氣-UNG":"UNG",
    "工業金屬-DBB":"DBB",
    "農產品-DBA":"DBA",
    "商品綜合-DBC":"DBC",

    # REITs
    "美國REIT-VNQ":"VNQ",
    "全球REIT-REET":"REET",
    "國際REIT-VNQI":"VNQI",

    # 避險資產
    "美元-UUP":"UUP",
    "日圓-FXY":"FXY",
    "瑞郎-FXF":"FXF"
}

# =========================================================
# Sidebar
# =========================================================

st.sidebar.header("ETF設定")

search_text = st.sidebar.text_input(
    "搜尋 ETF 或國家"
)

available_assets = list(ALL_ETFS.keys())

if search_text:
    available_assets = [
        x for x in available_assets
        if search_text.lower() in x.lower()
    ]

selected_assets = st.sidebar.multiselect(
    "選擇ETF",
    available_assets,
    default=[
        "美國-SPY",
        "台灣-EWT",
        "長期公債-TLT",
        "黃金-GLD"
    ]
)

# =========================================================
# 日期設定
# =========================================================

st.sidebar.header("期間設定")

date_mode = st.sidebar.radio(
    "日期模式",
    ["快速期間", "自訂日期"]
)

today = pd.Timestamp.today()

if date_mode == "快速期間":

    period = st.sidebar.selectbox(
        "期間",
        [
            "WTD",
            "MTD",
            "QTD",
            "YTD",
            "1M",
            "3M",
            "6M",
            "1Y",
            "2Y",
            "3Y",
            "5Y",
            "10Y"
        ],
        index=5
    )

    if period == "WTD":
        start = today - pd.DateOffset(days=7)

    elif period == "MTD":
        start = today.replace(day=1)

    elif period == "QTD":

        current_q = (today.month-1)//3 + 1

        q_start_month = (current_q-1)*3+1

        start = pd.Timestamp(
            year=today.year,
            month=q_start_month,
            day=1
        )

    elif period == "YTD":

        start = pd.Timestamp(
            year=today.year,
            month=1,
            day=1
        )

    elif period == "1M":
        start = today - pd.DateOffset(months=1)

    elif period == "3M":
        start = today - pd.DateOffset(months=3)

    elif period == "6M":
        start = today - pd.DateOffset(months=6)

    elif period == "1Y":
        start = today - pd.DateOffset(years=1)

    elif period == "2Y":
        start = today - pd.DateOffset(years=2)

    elif period == "3Y":
        start = today - pd.DateOffset(years=3)

    elif period == "5Y":
        start = today - pd.DateOffset(years=5)

    else:
        start = today - pd.DateOffset(years=10)

    end = today

else:

    start = st.sidebar.date_input(
        "開始日期",
        today - pd.DateOffset(years=1)
    )

    end = st.sidebar.date_input(
        "結束日期",
        today
    )

    start = pd.Timestamp(start)
    end = pd.Timestamp(end)

    period = (
        start.strftime("%Y-%m-%d")
        + " ~ "
        + end.strftime("%Y-%m-%d")
    )

# =========================================================
# Execute
# =========================================================

if st.button("開始分析"):

    if len(selected_assets) == 0:
        st.warning("請至少選擇1個ETF")
        st.stop()

    st.info(
        f"觀察期間：{start.strftime('%Y-%m-%d')} ~ {end.strftime('%Y-%m-%d')}"
    )

    prices = pd.DataFrame()

    with st.spinner("下載資料中..."):

        for asset in selected_assets:

            ticker = ALL_ETFS[asset]

            try:

                data = yf.download(
                    ticker,
                    start=start,
                    end=end,
                    auto_adjust=True,
                    progress=False
                )

                if not data.empty:
                    prices[asset] = data["Close"]

            except:
                pass

    if prices.empty:
        st.error("無法下載資料")
        st.stop()

    prices = prices.ffill()

    # ==================================
    # Return Ranking
    # ==================================

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

    st.subheader(f"📈 {period} 報酬率排名")

    st.dataframe(
        ranking.style.format("{:.2f}")
    )

    # ==================================
    # Ranking Chart
    # ==================================

    fig_bar = px.bar(
        ranking,
        x="報酬率(%)",
        y=ranking.index,
        orientation="h"
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

    # ==================================
    # Heatmap
    # ==================================

    st.subheader("🔥 Heatmap")

    fig_heat = px.imshow(
        ranking.T,
        text_auto=".1f",
        color_continuous_scale="RdYlGn"
    )

    st.plotly_chart(
        fig_heat,
        use_container_width=True
    )

    # ==================================
    # Performance Chart
    # ==================================

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

    # ==================================
    # Excel Download
    # ==================================

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter"
    ) as writer:

        ranking.to_excel(
            writer,
            sheet_name="Ranking"
        )

        prices.to_excel(
            writer,
            sheet_name="Price"
        )

        cumulative.to_excel(
            writer,
            sheet_name="Performance"
        )

    file_name = (
        f"Global_Asset_Dashboard_"
        f"{start.strftime('%Y%m%d')}_"
        f"{end.strftime('%Y%m%d')}.xlsx"
    )

    st.download_button(
        "📥下載Excel",
        output.getvalue(),
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

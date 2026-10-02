import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(
    page_title="全球股市ETF報酬率比較",
    layout="wide"
)

st.title("🌎 全球股市ETF報酬率分析")

# 常用國家ETF
COUNTRY_ETFS = {
    "美國": "SPY",
    "日本": "EWJ",
    "中國": "MCHI",
    "台灣": "EWT",
    "韓國": "EWY",
    "印度": "INDA",
    "德國": "EWG",
    "法國": "EWQ",
    "英國": "EWU",
    "加拿大": "EWC",
    "巴西": "EWZ",
    "墨西哥": "EWW",
    "澳洲": "EWA",
    "新加坡": "EWS",
    "印尼": "EIDO",
    "馬來西亞": "EWM",
    "泰國": "THD",
    "越南": "VNM",
    "菲律賓": "EPHE",
    "南非": "EZA",
    "土耳其": "TUR",
    "波蘭": "EPOL",
    "瑞士": "EWL",
    "瑞典": "EWD",
    "挪威": "ENOR",
    "歐元區": "EZU",
}

st.sidebar.header("設定")

selected_countries = st.sidebar.multiselect(
    "選擇國家",
    list(COUNTRY_ETFS.keys()),
    default=["美國", "台灣", "日本"]
)

start_date = st.sidebar.date_input(
    "開始日期",
    pd.to_datetime("2020-01-01")
)

end_date = st.sidebar.date_input(
    "結束日期",
    pd.Timestamp.today()
)

if st.sidebar.button("開始分析"):

    if len(selected_countries) == 0:
        st.warning("請至少選擇一個國家")
        st.stop()

    etfs = {
        country: COUNTRY_ETFS[country]
        for country in selected_countries
    }

    price_df = pd.DataFrame()

    progress = st.progress(0)

    for i, (country, ticker) in enumerate(etfs.items()):

        try:
            data = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                auto_adjust=True,
                progress=False
            )

            if len(data) > 0:
                price_df[country] = data["Close"]

        except Exception:
            pass

        progress.progress((i + 1) / len(etfs))

    if len(price_df.columns) == 0:
        st.error("無法下載資料")
        st.stop()

    price_df = price_df.ffill()

    # 累積績效
    cumulative = price_df / price_df.iloc[0] * 100

    st.subheader("累積績效走勢")

    fig = px.line(
        cumulative,
        x=cumulative.index,
        y=cumulative.columns,
        labels={
            "value": "績效(=100起算)",
            "variable": "國家"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # 總報酬率
    returns = (
        price_df.iloc[-1]
        / price_df.iloc[0]
        - 1
    ) * 100

    result = pd.DataFrame({
        "ETF": [COUNTRY_ETFS[x] for x in returns.index],
        "報酬率(%)": returns.values
    }, index=returns.index)

    result = result.sort_values(
        "報酬率(%)",
        ascending=False
    )

    st.subheader("報酬率排行")

    st.dataframe(
        result.style.format({
            "報酬率(%)": "{:.2f}"
        }),
        use_container_width=True
    )

    # 長條圖
    fig_bar = px.bar(
        result,
        y=result.index,
        x="報酬率(%)",
        orientation="h",
        title="國家績效排名"
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

    # Excel下載
    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter"
    ) as writer:

        result.to_excel(
            writer,
            sheet_name="Return Ranking"
        )

        price_df.to_excel(
            writer,
            sheet_name="Price"
        )

        cumulative.to_excel(
            writer,
            sheet_name="Performance"
        )

    st.download_button(
        label="📥下載Excel",
        data=output.getvalue(),
        file_name="country_etf_performance.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

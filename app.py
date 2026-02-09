import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta

st.set_page_config(page_title="AI Trader Pro", layout="wide")
st.title("🚀 Scanner Top 5 - S&P 500")

investimento = st.sidebar.number_input("Valor para Investir (€)", value=1000)

@st.cache_data(ttl=3600)
def scan():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    tickers = pd.read_html(url)[0]['Symbol'].tolist()[:30]
    data = []
    for t in tickers:
        try:
            df = yf.download(t.replace('.', '-'), period="5d", interval="5m", progress=False)
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
            conf = (df['Close'] > df['VWAP']).sum() / len(df) * 100
            atr = ta.atr(df['High'], df['Low'], df['Close']).iloc[-1]
            lucro_pct = (atr / df['Close'].iloc[-1]) * 100
            data.append({"Ticker": t, "Preço": df['Close'].iloc[-1], "Confiança %": conf, "Lucro %": lucro_pct, "Score": conf + (lucro_pct * 5)})
        except: continue
    return pd.DataFrame(data).sort_values(by="Score", ascending=False).head(5)

if st.button("🔍 Analisar Mercado"):
    top = scan()
    st.table(top[['Ticker', 'Preço', 'Confiança %', 'Lucro %']])
    for _, r in top.iterrows():
        st.success(f"💰 {r.Ticker}: Ganho estimado de {(r['Lucro %']/100)*investimento:.2f}€")

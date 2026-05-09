import streamlit as st
import pandas as pd
import plotly.express as px

# Dashboard Configuration
st.set_page_config(page_title="Crypto Trading Dashboard", layout="wide")

st.title("📈 Crypto Trading & Sentiment Dashboard")

# 1. Load data
try:
    # Ensure these files are in the same 'bitcoin' folder as app.py
    df_trades = pd.read_csv("historical_data.csv")
    df_fear = pd.read_csv("fear_greed_index.csv")

    # 2. Fix Date Formats (Handling the ValueError from before)
    df_trades['Timestamp IST'] = pd.to_datetime(df_trades['Timestamp IST'], dayfirst=True)
    df_trades['date_only'] = df_trades['Timestamp IST'].dt.date
    df_fear['date_only'] = pd.to_datetime(df_fear['date'], dayfirst=True).dt.date

    # 3. Merge Sentiment with Trades
    df = pd.merge(df_trades, df_fear[['date_only', 'value', 'classification']], on='date_only', how='left')

    # 4. KPIs at the top
    total_pnl = df_trades['Closed PnL'].sum()
    total_fees = df_trades['Fee'].sum()
    net_profit = total_pnl - total_fees
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total PnL", f"${total_pnl:,.2f}")
    col2.metric("Total Fees", f"${total_fees:,.2f}")
    col3.metric("Net Profit", f"${net_profit:,.2f}", delta=f"{net_profit:,.2f}")

    # 5. Visualizations
    tab1, tab2 = st.tabs(["Performance Over Time", "Asset Analysis"])

    with tab1:
        # Cumulative PnL Chart
        df_trades = df_trades.sort_values('Timestamp IST')
        df_trades['Cumulative_PnL'] = df_trades['Closed PnL'].cumsum()
        fig_line = px.line(df_trades, x='Timestamp IST', y='Cumulative_PnL', 
                          title="Portfolio Growth (Cumulative PnL)",
                          template="plotly_dark")
        st.plotly_chart(fig_line, use_container_width=True)

    with tab2:
        # Top 10 Coins
        top_coins = df_trades.groupby('Coin')['Closed PnL'].sum().sort_values(ascending=False).head(10).reset_index()
        fig_bar = px.bar(top_coins, x='Closed PnL', y='Coin', orientation='h',
                         title="Top 10 Profitable Assets",
                         color='Closed PnL', color_continuous_scale='Viridis')
        st.plotly_chart(fig_bar, use_container_width=True)

except FileNotFoundError as e:
    st.error(f"⚠️ Error: Could not find {e.filename}. Please make sure the CSV files are in the 'bitcoin' folder.")
except Exception as e:
    st.error(f"⚠️ An error occurred: {e}")
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import threading
import api
import time

@st.cache_data(ttl=300)
def carregar_dados():
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            dict(st.secrets["google"]["credentials"]),
            ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        )
        sheet = gspread.authorize(creds).open_by_key(st.secrets["google"]["spreadsheet_id"]).sheet1
        return pd.DataFrame(sheet.get_all_records())
    except Exception as e:
        st.error(f"Sheet error: {e}")
        return pd.DataFrame()

def start_bot():
    try:
        api.main()
    except Exception as e:
        st.error(f"Bot error: {e}")

# App UI
st.title("📊 Expense Dashboard")

if not st.session_state.get('bot_started'):
    if hasattr(st.secrets, "telegram") and hasattr(st.secrets.telegram, "token"):
        threading.Thread(target=start_bot, daemon=True).start()
        st.session_state.bot_started = True
        st.success("🤖 Bot started!")
    else:
        st.error("❌ Missing Telegram token in secrets")

if hasattr(st.secrets, "google"):
    df = carregar_dados()
    
    if not df.empty:
        st.dataframe(df)
        
        if "Valor" in df.columns:
            df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
            
            st.subheader("📈 By Category")
            st.bar_chart(df.groupby("Categoria")["Valor"].sum())
            
            cols = st.columns(3)
            cols[0].metric("Total", f"R$ {df['Valor'].sum():.2f}")
            cols[1].metric("Average", f"R$ {df['Valor'].mean():.2f}")
            cols[2].metric("Entries", len(df))
    else:
        st.info("No data found")
else:
    st.error("❌ Missing Google Sheets config")
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import threading
import api

# Configuração de cache
@st.cache_data(ttl=300)
def carregar_dados():
    try:
        credentials_dict = dict(st.secrets["google"]["credentials"])
        spreadsheet_id = st.secrets["google"]["spreadsheet_id"]

        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        client = gspread.authorize(creds)
        planilha = client.open_by_key(spreadsheet_id)
        aba = planilha.sheet1

        dados = aba.get_all_records()
        return pd.DataFrame(dados)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def iniciar_bot():
    try:
        if not hasattr(st.secrets, "telegram") or not hasattr(st.secrets.telegram, "token"):
            st.error("Token do Telegram não configurado!")
            return

        api.main()
    except Exception as e:
        st.error(f"Erro no bot: {e}")

# Interface
st.title("📊 Dashboard de Gastos Pessoais")

if not hasattr(st.secrets, "telegram") or not hasattr(st.secrets.telegram, "token"):
    st.error("Configure o token do Telegram nos secrets!")
elif not hasattr(st.secrets, "google"):
    st.error("Configure as credenciais do Google Sheets nos secrets!")
else:
    threading.Thread(target=iniciar_bot, daemon=True).start()
    df = carregar_dados()

    if df.empty:
        st.info("Nenhum dado encontrado na planilha.")
    else:
        st.dataframe(df)

        if "Valor" in df.columns:
            df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")

            if "Categoria" in df.columns:
                st.subheader("📈 Gastos por Categoria")
                st.bar_chart(df.groupby("Categoria")["Valor"].sum())

            st.subheader("💰 Resumo Financeiro")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Gastos", f"R$ {df['Valor'].sum():.2f}")
            col2.metric("Média por Item", f"R$ {df['Valor'].mean():.2f}")
            col3.metric("Registros", len(df))

import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json
import threading
import api  

# Inicia o bot em thread separada
def iniciar_bot():
    api.main()

threading.Thread(target=iniciar_bot, daemon=True).start()

# Autenticação e leitura da planilha
@st.cache_data(ttl=60)  # Cache por 60 segundos
def carregar_dados():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Carrega as credenciais do secrets
    credentials_dict = json.loads(st.secrets["google"]["credentials"])
    spreadsheet_id = st.secrets["google"]["spreadsheet_id"]

    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    client = gspread.authorize(creds)

    planilha = client.open_by_key(spreadsheet_id)
    aba = planilha.sheet1

    dados = aba.get_all_records()
    df = pd.DataFrame(dados)
    return df

# Interface do Streamlit
st.title("📊 Dashboard de Gastos")

df = carregar_dados()

if df.empty:
    st.info("Nenhum dado encontrado na planilha.")
else:
    st.dataframe(df)

    # Gera gráfico de gastos por categoria
    if "Categoria" in df.columns and "Valor" in df.columns:
        df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
        st.subheader("💸 Gastos por Categoria")
        st.bar_chart(df.groupby("Categoria")["Valor"].sum())
    else:
        st.warning("Colunas 'Categoria' e 'Valor' não encontradas na planilha.")

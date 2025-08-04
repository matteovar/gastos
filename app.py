import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os
from dotenv import load_dotenv

# Carregar variáveis do .env (se usar)
load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# Autenticação Google Sheets
@st.cache_data(ttl=60)  # atualiza cache a cada 60 segundos
def carregar_dados():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('credenciais.json', scope)
    client = gspread.authorize(creds)

    planilha = client.open_by_key(SPREADSHEET_ID)
    aba = planilha.sheet1

    dados = aba.get_all_records()
    df = pd.DataFrame(dados)
    return df

st.title("Dashboard de Gastos")

df = carregar_dados()

if df.empty:
    st.info("Nenhum dado encontrado na planilha.")
else:
    st.dataframe(df)

    # Mostrar alguns gráficos simples
    st.bar_chart(df.groupby("Categoria")["Valor"].sum())

import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import threading
import api

# Configuração de cache de leitura da planilha
@st.cache_data(ttl=300)  # 5 minutos
def carregar_dados():
    try:
        credentials_dict = dict(st.secrets["google"]["credentials"])
        spreadsheet_id = st.secrets["google"]["spreadsheet_id"]

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        client = gspread.authorize(creds)
        planilha = client.open_by_key(spreadsheet_id)
        aba = planilha.sheet1

        dados = aba.get_all_records()
        return pd.DataFrame(dados)
    except Exception as e:
        st.error(f"Erro ao carregar dados da planilha: {e}")
        return pd.DataFrame()

# Inicia o bot do Telegram uma única vez por sessão
if "bot_rodando" not in st.session_state:
    st.session_state.bot_rodando = True

    def iniciar_bot():
        try:
            api.main()
        except Exception as e:
            print(f"Erro ao iniciar o bot: {e}")

    threading.Thread(target=iniciar_bot, daemon=True).start()
    st.success("🤖 Bot do Telegram iniciado com sucesso!")
else:
    st.info("🤖 Bot já está rodando.")

# Interface principal do Streamlit
st.title("📊 Dashboard de Gastos Pessoais")

# Verificação dos secrets
if not hasattr(st.secrets, "telegram") or not hasattr(st.secrets.telegram, "token"):
    st.error("🚨 Token do Telegram não está configurado corretamente em secrets.toml!")
elif not hasattr(st.secrets, "google") or not hasattr(st.secrets["google"], "credentials"):
    st.error("🚨 Credenciais do Google Sheets não configuradas corretamente!")
else:
    df = carregar_dados()

    if df.empty:
        st.info("Nenhum dado encontrado na planilha.")
    else:
        st.dataframe(df)

        # Converte a coluna de valor para numérico
        if "Valor" in df.columns:
            df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")

            # Gráfico por categoria
            if "Categoria" in df.columns:
                st.subheader("📈 Gastos por Categoria")
                st.bar_chart(df.groupby("Categoria")["Valor"].sum())

            # Resumo financeiro
            st.subheader("💰 Resumo Financeiro")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Gastos", f"R$ {df['Valor'].sum():.2f}")
            col2.metric("Média por Item", f"R$ {df['Valor'].mean():.2f}")
            col3.metric("Registros", len(df))

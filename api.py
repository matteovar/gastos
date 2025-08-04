import re
import joblib
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram import Update
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

# --- Carrega o modelo treinado ---
modelo = joblib.load('modelo_financas.pkl')

def classificar_categoria(texto):
    return modelo.predict([texto])[0]

# --- Configuração Google Sheets ---
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
except Exception as e:
    print(f"Erro ao configurar Google Sheets: {e}")
    raise

# --- Função para extrair descrição e valor ---
def extrair_dados(texto):
    match = re.match(r"(.+?)\s+(\d+(?:[\.,]\d{1,2})?)", texto.lower())
    if match:
        descricao = match.group(1).strip()
        valor_str = match.group(2).replace(",", ".")
        try:
            valor = float(valor_str)
            return descricao, valor
        except ValueError:
            return None, None
    return None, None

# --- Função para salvar despesa no Google Sheets ---
def salvar_despesa(descricao, categoria, valor):
    try:
        linha = [descricao, categoria, valor]
        aba.append_row(linha)
    except Exception as e:
        print(f"Erro ao salvar na planilha: {e}")
        raise

# --- Função que responde mensagens no Telegram ---
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        texto = update.message.text
        descricao, valor = extrair_dados(texto)

        if descricao and valor is not None:
            categoria = classificar_categoria(texto)
            salvar_despesa(descricao, categoria, valor)
            resposta = (
                f"✅ Registro adicionado!\n"
                f"📝 Descrição: {descricao}\n"
                f"📦 Categoria: {categoria}\n"
                f"💸 Valor: R$ {valor:.2f}"
            )
        else:
            resposta = "❌ Formato inválido. Use: 'descrição valor' (ex: 'mercado 150.50')"

        await update.message.reply_text(resposta)
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
        await update.message.reply_text("❌ Ocorreu um erro ao processar sua mensagem")

# --- Função principal que inicia o bot ---
def main():
    try:
        TOKEN = st.secrets.telegram.token

        if not TOKEN:
            raise ValueError("Token do Telegram não encontrado em st.secrets.telegram.token")

        print(f"✅ TOKEN carregado: {TOKEN[:5]}...")
        application = ApplicationBuilder().token(TOKEN).build()
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
        print("🤖 Bot rodando...")
        application.run_polling()

    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        raise

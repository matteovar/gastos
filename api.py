import re
import joblib
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram import Update
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

# --- Carrega o modelo treinado ---
try:
    modelo = joblib.load('modelo_financas.pkl')
    print("✅ Modelo carregado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao carregar modelo: {e}")
    modelo = None  # evita erro em classificar_categoria

def classificar_categoria(texto):
    if modelo is not None:
        return modelo.predict([texto])[0]
    return "desconhecida"

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
    print("✅ Conectado ao Google Sheets")
except Exception as e:
    print(f"❌ Erro ao configurar Google Sheets: {e}")
    aba = None  # evita exceção no salvar_despesa

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
            print("❌ Erro ao converter valor para float")
            return None, None
    print("❌ Regex não bateu com o texto")
    return None, None

# --- Função para salvar despesa no Google Sheets ---
def salvar_despesa(descricao, categoria, valor):
    if aba is None:
        print("❌ Planilha não configurada")
        return
    try:
        linha = [descricao, categoria, valor]
        aba.append_row(linha)
        print(f"✅ Despesa registrada: {linha}")
    except Exception as e:
        print(f"❌ Erro ao salvar na planilha: {e}")

# --- Função que responde mensagens no Telegram ---
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        texto = update.message.text
        print(f"📩 Mensagem recebida: {texto}")

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
        print(f"❌ Erro ao processar mensagem: {e}")
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

        print("🤖 Bot rodando com polling...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        print(f"❌ Erro fatal ao iniciar o bot: {e}")
        raise

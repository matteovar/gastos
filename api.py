import re
import joblib
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram import Update
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
from datetime import datetime
import asyncio

# Load ML model
try:
    modelo = joblib.load('modelo_financas.pkl')
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    modelo = None

def classificar_categoria(texto):
    return modelo.predict([texto])[0] if modelo else "desconhecida"


try:
    credentials_dict = dict(st.secrets["google"]["credentials"])
    spreadsheet_id = st.secrets["google"]["spreadsheet_id"]
    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    client = gspread.authorize(creds)
    planilha = client.open_by_key(spreadsheet_id)
    aba = planilha.sheet1
    print("✅ Connected to Google Sheets")
except Exception as e:
    print(f"❌ Google Sheets error: {e}")
    aba = None

def extrair_dados(texto):
    pattern_com_data = r"^(\d{1,2}/\d{1,2}/\d{4})\s+(.+?)\s+(\d+(?:[\.,]\d{1,2})?)$"
    match = re.match(pattern_com_data, texto.lower())
    if match:
        data_str = match.group(1)
        descricao = match.group(2).strip()
        valor_str = match.group(3).replace(",", ".")
        try:
            data = datetime.strptime(data_str, "%d/%m/%Y")
            valor = float(valor_str)
            return descricao, valor, data
        except ValueError:
            pass  # Se der erro na data ou valor, vai tentar o próximo pattern abaixo

    # Caso não tenha data, tenta extrair só descrição e valor
    pattern_sem_data = r"(.+?)\s+(\d+(?:[\.,]\d{1,2})?)"
    match = re.match(pattern_sem_data, texto.lower())
    if match:
        descricao = match.group(1).strip()
        valor_str = match.group(2).replace(",", ".")
        try:
            valor = float(valor_str)
            data = datetime.now()  # usa a data atual se não passar data
            return descricao, valor, data
        except ValueError:
            pass

    return None, None, None


def salvar_despesa(descricao, categoria, valor, data, tipo="despesa"):
    if aba:
        try:
            data_str = data.strftime("%d/%m/%Y")
            # Coloque a data na planilha na primeira coluna (ou onde quiser)
            aba.append_row([data_str, descricao, categoria, valor, tipo])
            print(f"✅ Saved: {data_str} - {descricao} - {valor} ({tipo})")
        except Exception as e:
            print(f"❌ Save error: {e}")


async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        texto = update.message.text
        descricao, valor, data = extrair_dados(texto)
        
        if descricao and valor and data:
            categoria = classificar_categoria(texto)
            salvar_despesa(descricao, categoria, valor, data)
            await update.message.reply_text(
                f"✅ Adicionado!\n"
                f"🗓️ {data.strftime('%d/%m/%Y')}\n"
                f"📝 {descricao}\n"
                f"📦 {categoria}\n"
                f"💸 R$ {valor:.2f}"
            )
        else:
            await update.message.reply_text("❌ Use: 'descrição valor' ou 'dd/mm/yyyy descrição valor' (ex: 'mercado 150.50' ou '15/08/2025 mercado 150.50')")
    except Exception as e:
        print(f"❌ Message error: {e}")
        await update.message.reply_text("❌ Erro ao processar")


def run_bot():
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
        TOKEN = st.secrets.telegram.token
        if not TOKEN:
            raise ValueError("Missing Telegram token")
        application = ApplicationBuilder().token(TOKEN).build()
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
        print("🤖 Bot started polling...")
        application.run_polling(stop_signals=[])
    except Exception as e:
        print(f"❌ Bot crashed: {e}")
        raise

def main():
    run_bot()

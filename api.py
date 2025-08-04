import re
import joblib
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram import Update
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import asyncio
from threading import Thread
import time

# Load ML model
try:
    modelo = joblib.load('modelo_financas.pkl')
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    modelo = None

def classificar_categoria(texto):
    return modelo.predict([texto])[0] if modelo else "desconhecida"

# Google Sheets setup
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
    match = re.match(r"(.+?)\s+(\d+(?:[\.,]\d{1,2})?)", texto.lower())
    if match:
        try:
            descricao = match.group(1).strip()
            valor = float(match.group(2).replace(",", "."))
            return descricao, valor
        except ValueError:
            pass
    return None, None

def salvar_despesa(descricao, categoria, valor):
    if aba:
        try:
            aba.append_row([descricao, categoria, valor])
            print(f"✅ Saved: {descricao} - {valor}")
        except Exception as e:
            print(f"❌ Save error: {e}")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        texto = update.message.text
        descricao, valor = extrair_dados(texto)
        
        if descricao and valor:
            categoria = classificar_categoria(texto)
            salvar_despesa(descricao, categoria, valor)
            await update.message.reply_text(
                f"✅ Added!\n"
                f"📝 {descricao}\n"
                f"📦 {categoria}\n"
                f"💸 R$ {valor:.2f}"
            )
        else:
            await update.message.reply_text("❌ Use: 'description value' (ex: 'market 150.50')")
    except Exception as e:
        print(f"❌ Message error: {e}")
        await update.message.reply_text("❌ Processing error")

def run_bot():
    try:
        # Create new event loop for this thread
        asyncio.set_event_loop(asyncio.new_event_loop())
        
        TOKEN = st.secrets.telegram.token
        if not TOKEN:
            raise ValueError("Missing Telegram token")
            
        application = ApplicationBuilder().token(TOKEN).build()
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
        
        print("🤖 Bot started polling...")
        application.run_polling()
    except Exception as e:
        print(f"❌ Bot crashed: {e}")
        raise

def main():
    print("🔍 Starting bot thread...")
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Keep thread alive
    while True:
        time.sleep(10)
        print("🤖 Bot still running...")
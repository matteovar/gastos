import re
import joblib
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
from datetime import datetime
import asyncio

# Carregar modelo
try:
    modelo = joblib.load('modelo_financas.pkl')
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    modelo = None

def classificar_categoria(texto):
    return modelo.predict([texto])[0] if modelo else "desconhecida"

# Configurar Google Sheets
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
    # Tenta extrair data dd/mm/yyyy no início
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
            pass

    # Sem data, só descrição e valor
    pattern_sem_data = r"(.+?)\s+(\d+(?:[\.,]\d{1,2})?)"
    match = re.match(pattern_sem_data, texto.lower())
    if match:
        descricao = match.group(1).strip()
        valor_str = match.group(2).replace(",", ".")
        try:
            valor = float(valor_str)
            data = datetime.now()
            return descricao, valor, data
        except ValueError:
            pass

    return None, None, None

def salvar_despesa(descricao, categoria, valor, data, tipo="despesa"):
    if aba:
        try:
            data_str = data.strftime("%d/%m/%Y")
            # Adiciona na planilha: data, descrição, categoria, valor, tipo
            aba.append_row([data_str, descricao, categoria, valor, tipo])
            print(f"✅ Saved: {data_str} - {descricao} - {valor} ({tipo})")
        except Exception as e:
            print(f"❌ Save error: {e}")

# Variável para guardar dados pendentes de confirmação por chat_id
confirmacoes_pendentes = {}

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    descricao, valor, data = extrair_dados(texto)
    if descricao and valor and data:
        categoria = classificar_categoria(texto)
        chat_id = update.message.chat_id
        confirmacoes_pendentes[chat_id] = (descricao, categoria, valor, data)

        texto_confirm = (
            f"Você quer adicionar esta despesa?\n"
            f"🗓️ {data.strftime('%d/%m/%Y')}\n"
            f"📝 {descricao}\n"
            f"📦 {categoria}\n"
            f"💸 R$ {valor:.2f}"
        )
        teclado = [
            [InlineKeyboardButton("✅ Confirmar", callback_data='confirmar')],
            [InlineKeyboardButton("❌ Cancelar", callback_data='cancelar')]
        ]
        markup = InlineKeyboardMarkup(teclado)
        await update.message.reply_text(texto_confirm, reply_markup=markup)
    else:
        await update.message.reply_text(
            "❌ Use: 'descrição valor' ou 'dd/mm/yyyy descrição valor' "
            "(ex: 'mercado 150.50' ou '15/08/2025 mercado 150.50')"
        )

async def resposta_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    if chat_id not in confirmacoes_pendentes:
        await query.edit_message_text("❌ Nenhuma ação pendente para confirmar.")
        return

    if query.data == 'confirmar':
        descricao, categoria, valor, data = confirmacoes_pendentes.pop(chat_id)
        salvar_despesa(descricao, categoria, valor, data)
        await query.edit_message_text("✅ Despesa adicionada com sucesso!")
    elif query.data == 'cancelar':
        confirmacoes_pendentes.pop(chat_id)
        await query.edit_message_text("❌ Operação cancelada.")

def run_bot():
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
        TOKEN = st.secrets.telegram.token
        if not TOKEN:
            raise ValueError("Missing Telegram token")
        application = ApplicationBuilder().token(TOKEN).build()
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
        application.add_handler(CallbackQueryHandler(resposta_callback))
        print("🤖 Bot started polling...")
        application.run_polling(stop_signals=[])
    except Exception as e:
        print(f"❌ Bot crashed: {e}")
        raise

def main():
    run_bot()

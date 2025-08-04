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

# Guardar estado e dados pendentes
usuarios_estado = {}  # chat_id -> {"fase": "confirmacao"|"editando", "campo": campo_editando, "dados": {...}}

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    texto = update.message.text

    estado = usuarios_estado.get(chat_id)
    if estado and estado["fase"] == "editando":
        # Usuário está editando algum campo, recebe o novo valor aqui
        campo = estado["campo"]
        dados = estado["dados"]
        novo_valor = texto.strip()

        if campo == "dia":
            try:
                nova_data = datetime.strptime(novo_valor, "%d/%m/%Y")
                dados["data"] = nova_data
            except:
                await update.message.reply_text("Formato de data inválido. Use dd/mm/aaaa")
                return
        elif campo == "valor":
            try:
                valor_float = float(novo_valor.replace(",", "."))
                dados["valor"] = valor_float
            except:
                await update.message.reply_text("Valor inválido. Envie um número.")
                return
        elif campo == "descricao":
            dados["descricao"] = novo_valor
        elif campo == "categoria":
            dados["categoria"] = novo_valor  # Se quiser, pode fazer reclassificação automática

        # Volta para confirmação com dados atualizados
        usuarios_estado[chat_id] = {"fase": "confirmacao", "dados": dados}
        texto_confirm = (
            f"Atualizado! Confirma essa despesa?\n"
            f"🗓️ {dados['data'].strftime('%d/%m/%Y')}\n"
            f"📝 {dados['descricao']}\n"
            f"📦 {dados['categoria']}\n"
            f"💸 R$ {dados['valor']:.2f}"
        )
        teclado = [
            [InlineKeyboardButton("✅ Confirmar", callback_data='confirmar')],
            [InlineKeyboardButton("❌ Editar", callback_data='editar')]
        ]
        markup = InlineKeyboardMarkup(teclado)
        await update.message.reply_text(texto_confirm, reply_markup=markup)
        return

    # Se não está editando, processa mensagem nova normalmente (igual antes)
    descricao, valor, data = extrair_dados(texto)
    if descricao and valor and data:
        categoria = classificar_categoria(texto)
        usuarios_estado[chat_id] = {
            "fase": "confirmacao",
            "dados": {"descricao": descricao, "categoria": categoria, "valor": valor, "data": data}
        }
        texto_confirm = (
            f"Você quer adicionar esta despesa?\n"
            f"🗓️ {data.strftime('%d/%m/%Y')}\n"
            f"📝 {descricao}\n"
            f"📦 {categoria}\n"
            f"💸 R$ {valor:.2f}"
        )
        teclado = [
            [InlineKeyboardButton("✅ Confirmar", callback_data='confirmar')],
            [InlineKeyboardButton("❌ Editar", callback_data='editar')]
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
    estado = usuarios_estado.get(chat_id)

    if not estado:
        await query.edit_message_text("❌ Nenhuma ação pendente para confirmar.")
        return

    dados = estado["dados"]

    if query.data == 'confirmar':
        salvar_despesa(dados["descricao"], dados["categoria"], dados["valor"], dados["data"])
        usuarios_estado.pop(chat_id)
        await query.edit_message_text("✅ Despesa adicionada com sucesso!")
    elif query.data == 'editar':
        usuarios_estado[chat_id]["fase"] = "escolhendo_campo"
        teclado_campos = [
            [InlineKeyboardButton("📅 Data", callback_data="edit_dia")],
            [InlineKeyboardButton("📝 Descrição", callback_data="edit_descricao")],
            [InlineKeyboardButton("💸 Valor", callback_data="edit_valor")],
            [InlineKeyboardButton("📦 Categoria", callback_data="edit_categoria")],
        ]
        markup = InlineKeyboardMarkup(teclado_campos)
        await query.edit_message_text("O que você quer editar?", reply_markup=markup)
    elif query.data.startswith("edit_"):
        campo = query.data.split("_")[1]
        usuarios_estado[chat_id]["fase"] = "editando"
        usuarios_estado[chat_id]["campo"] = campo
        await query.edit_message_text(f"Envie o novo valor para *{campo}*:", parse_mode="Markdown")

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

import re
import joblib
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from telegram import Update
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv

load_dotenv()

# --- Carrega o modelo treinado ---
modelo = joblib.load('modelo_financas.pkl')

def classificar_categoria(texto):
    return modelo.predict([texto])[0]

# --- Configuração Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('credenciais.json', scope)
client = gspread.authorize(creds)
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
planilha = client.open_by_key(SPREADSHEET_ID)
aba = planilha.sheet1  # primeira aba

# --- Função para extrair descrição e valor ---
def extrair_dados(texto):
    match = re.match(r"(.+?)\s+(\d+(?:[\.,]\d{1,2})?)", texto.lower())
    if match:
        descricao = match.group(1).strip()
        valor_str = match.group(2).replace(",", ".")
        try:
            valor = float(valor_str)
            return descricao, valor
        except:
            return None, None
    else:
        return None, None

# --- Função para salvar despesa no Google Sheets ---
def salvar_despesa(descricao, categoria, valor):
    linha = [descricao, categoria, valor]
    aba.append_row(linha)

# --- Função que responde mensagens no Telegram ---
def responder(update: Update, context: CallbackContext):
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
        resposta = "❌ Não entendi. Por favor, envie no formato: descrição + valor (ex: 'água de coco 14')"
    update.message.reply_text(resposta)

# --- Função principal que inicia o bot ---
def main():
    TOKEN = os.getenv("TOKEN")
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, responder))

    print("Bot rodando...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

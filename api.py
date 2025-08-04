import re
import joblib
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram import Update
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import streamlit as st

# --- Carrega o modelo treinado ---
modelo = joblib.load('modelo_financas.pkl')

def classificar_categoria(texto):
    return modelo.predict([texto])[0]

# --- Configuração Google Sheets ---
credentials_dict = json.loads(st.secrets["google"]["credentials"])
spreadsheet_id = st.secrets["google"]["spreadsheet_id"]

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(creds)
planilha = client.open_by_key(spreadsheet_id)
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
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    await update.message.reply_text(resposta)

# --- Função principal que inicia o bot ---
def main():
    TOKEN = st.secrets.token  # Acessa diretamente o token definido no secrets.toml

    if not TOKEN:
        raise ValueError("❌ TOKEN do Telegram não foi encontrado! Verifique seu secrets.toml")

    print(f"✅ TOKEN carregado: {TOKEN[:5]}...")

    # Configuração do bot usando a nova API v20.x
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Adiciona handler para mensagens de texto
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    
    print("🤖 Bot rodando...")
    application.run_polling()

if __name__ == '__main__':
    main()
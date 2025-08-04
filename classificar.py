import joblib

# Carrega o modelo treinado
modelo = joblib.load('modelo_financas.pkl')

# Função para prever a categoria
def classificar_categoria(texto):
    return modelo.predict([texto])[0]

# Exemplo de teste manual
if __name__ == "__main__":
    entrada = input("Digite sua despesa: ")
    categoria = classificar_categoria(entrada)
    print(f"📦 Categoria prevista: {categoria}")

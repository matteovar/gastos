from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib
from dados import frases, categorias

# Pipeline: vetorizador + classificador
modelo = Pipeline([
    ('vectorizer', TfidfVectorizer()),
    ('classifier', LogisticRegression())
])

# Treina o modelo com nossos dados
modelo.fit(frases, categorias)

# Salva o modelo treinado num arquivo
joblib.dump(modelo, 'modelo_financas.pkl')

print("✅ Modelo treinado e salvo como 'modelo_financas.pkl'")

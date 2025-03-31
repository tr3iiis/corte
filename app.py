from flask import Flask, request, jsonify
import joblib
import numpy as np
import os
from flask_cors import CORS

app = Flask(__name__)

# Configuração do CORS para permitir requisições do seu site no GitHub Pages
# Aplica a regra para todas as rotas (/*) vindas da origem especificada
CORS(app, resources={r"/*": {"origins": "https://tr3iiis.github.io"}})

# Carrega seu modelo, scaler e labels (verifique se os nomes dos arquivos estão corretos)
try:
    model = joblib.load("modelo_cartas.pkl")
    scaler = joblib.load("scaler.pkl")
    labels = joblib.load("labels.pkl")
except FileNotFoundError as e:
    print(f"Erro ao carregar arquivos .pkl: {e}")
    # Você pode querer tratar isso de forma mais robusta,
    # talvez retornando um erro 500 nas rotas se os arquivos não forem carregados.
    model = None
    scaler = None
    labels = None

@app.route("/")
def home():
    return "API de Classificação de Músicas com Tarot! Use /predict para previsões."

@app.route("/predict", methods=["POST"])
def predict():
    # Verifica se os modelos foram carregados
    if not all([model, scaler, labels]):
         return jsonify({"error": "Modelo não carregado no servidor."}), 500

    try:
        data = request.json
        # Certifique-se que as chaves correspondem exatamente ao que o JS envia
        features = [
            data["Duration"], data["Popularity"], data["Danceability"], data["Energy"],
            data["Key"], data["Loudness"], data["Mode"], data["Speechiness"],
            data["Acousticness"], data["Instrumentalness"], data["Liveness"],
            data["Valence"], data["Tempo"], data["Time Signature"] # Note a chave "Time Signature" com espaço
        ]
        features = np.array(features).reshape(1, -1)
        features = scaler.transform(features)
        prediction = model.predict(features)[0]
        # Certifique-se que 'labels' é um dicionário ou lista que pode ser indexado por 'prediction'
        return jsonify({"carta_prevista": labels[prediction]})
    except KeyError as e:
         # Erro se alguma chave esperada não for encontrada no JSON recebido
         return jsonify({"error": f"Dado faltando na requisição: {str(e)}"}), 400
    except Exception as e:
         # Erro genérico durante o processamento
         print(f"Erro durante a previsão: {e}") # Log do erro no servidor ajuda a debugar
         return jsonify({"error": f"Erro interno no servidor: {str(e)}"}), 500

# Este bloco é executado apenas se você rodar 'python app.py' localmente.
# O Gunicorn/Render não usa este bloco diretamente, mas não atrapalha.
if __name__ == "__main__":
    # Render define a variável de ambiente PORT
    port = int(os.environ.get("PORT", 10000))
    # host='0.0.0.0' permite conexões externas (necessário para o container)
    app.run(host='0.0.0.0', port=port, debug=False) # debug=False é mais seguro para produção

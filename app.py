from flask import Flask, request, jsonify
import joblib
import numpy as np
import os
from flask_cors import CORS

app = Flask(__name__)

# Configuração do CORS para permitir requisições do seu site no GitHub Pages
CORS(app, resources={r"/*": {"origins": "https://tr3iiis.github.io"}})

# Carrega seu modelo, scaler e labels
try:
    model = joblib.load("modelo_cartas.pkl")
    scaler = joblib.load("scaler.pkl")
    labels = joblib.load("labels.pkl")
    print("Modelo, scaler e labels carregados com sucesso.") # Log de sucesso
except FileNotFoundError as e:
    print(f"Erro ao carregar arquivos .pkl: {e}")
    model = None
    scaler = None
    labels = None

@app.route("/")
def home():
    return "API de Classificação de Músicas com Tarot! Use /predict para previsões."

@app.route("/predict", methods=["POST"])
def predict():
    # Verifica se os objetos foram carregados corretamente (CORRIGIDO)
    if model is None or scaler is None or labels is None:
        print("Erro: Tentativa de previsão mas modelo/scaler/labels não está(ão) carregado(s).") # Log no servidor
        return jsonify({"error": "Modelo, scaler ou labels não carregado(s) corretamente no servidor."}), 500

    try:
        data = request.json
        features = [
            data["Duration"], data["Popularity"], data["Danceability"], data["Energy"],
            data["Key"], data["Loudness"], data["Mode"], data["Speechiness"],
            data["Acousticness"], data["Instrumentalness"], data["Liveness"],
            data["Valence"], data["Tempo"], data["Time Signature"]
        ]
        features = np.array(features).reshape(1, -1)
        features = scaler.transform(features)
        prediction = model.predict(features)[0]
        return jsonify({"carta_prevista": labels[prediction]})
    except KeyError as e:
         return jsonify({"error": f"Dado faltando na requisição: {str(e)}"}), 400
    except Exception as e:
         print(f"Erro durante a previsão: {e}")
         return jsonify({"error": f"Erro interno no servidor: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

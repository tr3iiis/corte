from flask import Flask, request, jsonify
import joblib
import numpy as np
import os  # <--- Adicione esta linha

app = Flask(__name__)

# Carregar o modelo, scaler e labels (substitua pelos seus arquivos)
model = joblib.load("modelo_cartas.pkl")
scaler = joblib.load("scaler.pkl")
labels = joblib.load("labels.pkl")

@app.route("/")
def home():
    return "API de Classificação de Músicas com Tarot! Use /predict para previsões."  # <--- Rota raiz opcional

@app.route("/predict", methods=["POST"])
def predict():
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
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # <--- Linha nova
    app.run(host='0.0.0.0', port=port)  # <--- Linha modificada

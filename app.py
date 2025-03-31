from flask import Flask, request, jsonify
import joblib
import numpy as np
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load your model and scaler
model = joblib.load("modelo_cartas.pkl")
scaler = joblib.load("scaler.pkl")
labels = joblib.load("labels.pkl")

@app.route("/")
def home():
    return "API de Classificação de Músicas com Tarot! Use /predict para previsões."

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
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

import os
from flask import Flask, request, jsonify
import joblib
import numpy as np
from flask_cors import CORS

app = Flask(__name__)

# Configuração do CORS para permitir requisições do GitHub Pages
# Mantendo a permissão genérica caso você use outros repositórios no tr3iiis.github.io
CORS(app, resources={r"/*": {"origins": "https://tr3iiis.github.io"}})

# --- Carregamento de Modelos e Labels ---
try:
    model = joblib.load("modelo_cartas.pkl")
    scaler = joblib.load("scaler.pkl")
    labels = joblib.load("labels.pkl")
    print("Modelo, scaler e labels carregados com sucesso.")
except FileNotFoundError as e:
    print(f"Erro CRÍTICO ao carregar arquivos .pkl: {e}")
    print("API não funcionará corretamente sem os arquivos .pkl.")
    model = None
    scaler = None
    labels = None
except Exception as e: # Pega outros erros de load
    print(f"Erro CRÍTICO inesperado ao carregar arquivos .pkl: {e}")
    model = None
    scaler = None
    labels = None


# --- Rotas da API ---

@app.route("/")
def home():
    # Mensagem indicando que só a previsão manual está ativa
    return "API de Classificação de Músicas com Tarot! Use /predict para previsões manuais."

@app.route("/predict", methods=["POST"])
def predict_manual():
    """Rota para previsão com entrada manual das 14 features."""

    # Verifica se os objetos foram carregados corretamente
    if model is None or scaler is None or labels is None:
        print("Erro: Tentativa de previsão mas modelo/scaler/labels não está(ão) carregado(s).")
        return jsonify({"error": "Modelo, scaler ou labels não carregado(s) corretamente no servidor."}), 500

    data = request.json
    if not data:
        return jsonify({"error": "Requisição sem corpo JSON."}), 400

    # Verifica se todas as 14 chaves esperadas estão presentes
    expected_keys = [
        "Duration", "Popularity", "Danceability", "Energy", "Key", "Loudness",
        "Mode", "Speechiness", "Acousticness", "Instrumentalness", "Liveness",
        "Valence", "Tempo", "Time Signature"
    ]
    ordered_features = [] # Inicializa a lista de features

    # Tenta extrair todas as features garantindo que as chaves existem
    try:
        for key in expected_keys:
            if key not in data:
                 # Se alguma chave estiver faltando, retorna erro imediatamente
                 missing = [k for k in expected_keys if k not in data]
                 print(f"LOG: Dados faltando na requisição: {missing}")
                 return jsonify({"error": f"Dados faltando na requisição manual: {missing}"}), 400
            ordered_features.append(data[key]) # Adiciona à lista na ordem correta

    except Exception as e: # Pega outros erros inesperados ao acessar 'data'
        print(f"Erro ao processar dados de entrada: {e}")
        return jsonify({"error": "Erro ao ler os dados da requisição."}), 400


    # Realiza a previsão
    try:
        features_array = np.array(ordered_features).reshape(1, -1)
        features_scaled = scaler.transform(features_array)
        prediction_index = model.predict(features_scaled)[0]

        # Verifica se o índice da previsão é válido
        if isinstance(prediction_index, (int, np.integer)) and 0 <= prediction_index < len(labels):
             predicted_card = labels[prediction_index]
             return jsonify({"carta_prevista": predicted_card})
        else:
             print(f"Erro: Índice de previsão ({prediction_index}, tipo: {type(prediction_index)}) fora do range dos labels (tamanho: {len(labels)}).")
             return jsonify({"error": "Erro ao mapear previsão para label."}), 500

    except ValueError as e: # Erro comum se os dados não puderem ser convertidos para float/int pelo numpy
        print(f"Erro de valor durante scaling/prediction: {e}")
        return jsonify({"error": f"Erro nos valores numéricos fornecidos: {e}"}), 400
    except Exception as e: # Pega outros erros (ex: no transform, predict)
         print(f"Erro durante a previsão interna: {e}")
         import traceback
         traceback.print_exc() # Imprime traceback completo no log do Render para debug
         return jsonify({"error": f"Erro interno durante a previsão: {str(e)}"}), 500


# --- Bloco de execução local (Não essencial para Render) ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

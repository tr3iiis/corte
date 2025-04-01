import os
import base64
import requests # Necessário para fazer chamadas à API do Spotify
from flask import Flask, request, jsonify
import joblib
import numpy as np
from flask_cors import CORS

app = Flask(__name__)

# Configuração do CORS (já deve estar assim)
CORS(app, resources={r"/*": {"origins": "https://tr3iiis.github.io"}})

# --- Carregamento de Modelos e Labels ---
try:
    model = joblib.load("modelo_cartas.pkl")
    scaler = joblib.load("scaler.pkl")
    labels = joblib.load("labels.pkl")
    print("Modelo, scaler e labels carregados com sucesso.") # Log de sucesso
except FileNotFoundError as e:
    print(f"Erro CRÍTICO ao carregar arquivos .pkl: {e}")
    print("API não funcionará corretamente sem os arquivos .pkl.")
    model = None
    scaler = None
    labels = None

# --- Lógica para interagir com API do Spotify ---

SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')

def get_spotify_token():
    """Obtém um token de acesso da API do Spotify usando Client Credentials."""
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        print("Erro: SPOTIFY_CLIENT_ID ou SPOTIFY_CLIENT_SECRET não definidos nas variáveis de ambiente.")
        return None

    auth_url = 'https://accounts.spotify.com/api/token'
    # Codifica ID:SECRET em Base64
    auth_header = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    auth_data = {'grant_type': 'client_credentials'}
    headers = {'Authorization': f'Basic {auth_header}'}

    try:
        response = requests.post(auth_url, data=auth_data, headers=headers)
        response.raise_for_status() # Levanta erro para status >= 400
        token_info = response.json()
        return token_info.get('access_token')
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter token do Spotify: {e}")
        return None
    except Exception as e:
        print(f"Erro inesperado ao processar resposta do token: {e}")
        return None

def get_track_features(track_id, token):
    """Busca as features de áudio e detalhes da faixa no Spotify."""
    if not track_id or not token:
        return None, "Track ID ou Token inválido."

    headers = {'Authorization': f'Bearer {token}'}
    features_url = f'https://api.spotify.com/v1/audio-features/{track_id}'
    track_url = f'https://api.spotify.com/v1/tracks/{track_id}'

    try:
        # Busca Audio Features
        features_response = requests.get(features_url, headers=headers)
        features_response.raise_for_status()
        audio_features = features_response.json()

        # Busca Detalhes da Faixa (Popularidade, Duração)
        track_response = requests.get(track_url, headers=headers)
        track_response.raise_for_status()
        track_details = track_response.json()

        # Monta o dicionário com as 14 features necessárias para o modelo
        required_features = {
            "Duration": track_details.get('duration_ms'),
            "Popularity": track_details.get('popularity'),
            "Danceability": audio_features.get('danceability'),
            "Energy": audio_features.get('energy'),
            "Key": audio_features.get('key'),
            "Loudness": audio_features.get('loudness'),
            "Mode": audio_features.get('mode'),
            "Speechiness": audio_features.get('speechiness'),
            "Acousticness": audio_features.get('acousticness'),
            "Instrumentalness": audio_features.get('instrumentalness'),
            "Liveness": audio_features.get('liveness'),
            "Valence": audio_features.get('valence'),
            "Tempo": audio_features.get('tempo'),
            "Time Signature": audio_features.get('time_signature')
        }

        # Verifica se alguma feature essencial veio como None
        if None in required_features.values():
             missing = [k for k, v in required_features.items() if v is None]
             print(f"Aviso: Features faltando na resposta do Spotify para track {track_id}: {missing}")
             return None, f"Features faltando do Spotify: {missing}"

        return required_features, None # Retorna features e None para erro

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição à API do Spotify para track {track_id}: {e}")
        return None, f"Erro ao buscar dados no Spotify: {e}"
    except Exception as e:
        print(f"Erro inesperado ao processar dados do Spotify para track {track_id}: {e}")
        return None, f"Erro inesperado ao buscar dados do Spotify: {e}"


# --- Lógica de Previsão (Refatorada) ---

def perform_prediction(feature_dict):
    """Recebe um dicionário com as 14 features, escala e retorna a previsão."""
    if not all([model, scaler, labels]):
        print("Erro interno: Tentativa de previsão sem modelo/scaler/labels carregados.")
        return None, "Modelo não carregado no servidor."

    try:
        # Garante a ordem correta das features como o scaler espera
        ordered_features = [
            feature_dict["Duration"], feature_dict["Popularity"], feature_dict["Danceability"],
            feature_dict["Energy"], feature_dict["Key"], feature_dict["Loudness"],
            feature_dict["Mode"], feature_dict["Speechiness"], feature_dict["Acousticness"],
            feature_dict["Instrumentalness"], feature_dict["Liveness"], feature_dict["Valence"],
            feature_dict["Tempo"], feature_dict["Time Signature"]
        ]

        features_array = np.array(ordered_features).reshape(1, -1)
        features_scaled = scaler.transform(features_array)
        prediction_index = model.predict(features_scaled)[0]

        # Verifica se prediction_index é válido para 'labels'
        # Assumindo que 'labels' pode ser numpy array ou list
        if isinstance(prediction_index, (int, np.integer)) and 0 <= prediction_index < len(labels):
             predicted_card = labels[prediction_index]
             return predicted_card, None # Retorna carta e None para erro
        else:
             print(f"Erro: Índice de previsão ({prediction_index}, tipo: {type(prediction_index)}) fora do range dos labels (tamanho: {len(labels)}).")
             return None, "Erro ao mapear previsão para label."

    except KeyError as e:
         print(f"Erro interno: Chave faltando no dicionário de features: {e}")
         return None, f"Feature interna faltando: {str(e)}"
    except Exception as e:
         print(f"Erro durante a previsão interna: {e}")
         return None, f"Erro interno durante a previsão: {str(e)}"


# --- Rotas da API ---

@app.route("/")
def home():
    return "API de Classificação de Músicas com Tarot v2! Use /predict (manual) ou /buscar_e_prever (automático)."

@app.route("/predict", methods=["POST"])
def predict_manual():
    """Rota para previsão com entrada manual das 14 features."""
    data = request.json
    if not data:
        return jsonify({"error": "Requisição sem corpo JSON."}), 400

    # Verifica se todas as 14 chaves esperadas estão presentes
    expected_keys = [
        "Duration", "Popularity", "Danceability", "Energy", "Key", "Loudness",
        "Mode", "Speechiness", "Acousticness", "Instrumentalness", "Liveness",
        "Valence", "Tempo", "Time Signature"
    ]
    if not all(key in data for key in expected_keys):
         missing = [key for key in expected_keys if key not in data]
         return jsonify({"error": f"Dados faltando na requisição manual: {missing}"}), 400

    # Chama a função de previsão refatorada
    predicted_card, error_msg = perform_prediction(data)

    if error_msg:
        return jsonify({"error": error_msg}), 500
    else:
        return jsonify({"carta_prevista": predicted_card})


@app.route("/buscar_e_prever", methods=["POST"])
def search_and_predict():
    """Nova rota para buscar música no Spotify e prever."""
    data = request.json
    if not data or 'song_name' not in data:
        return jsonify({"error": "Nome da música ('song_name') não fornecido."}), 400

    song_name = data['song_name']
    artist_name = data.get('artist_name', '') # Pega o artista se fornecido, senão usa vazio

    print("LOG: Tentando obter token do Spotify...") # Mensagem antes de tentar
    token = get_spotify_token()
    if not token:
        print("LOG: Falha ao obter token do Spotify.") # Mensagem se falhar
        return jsonify({"error": "Não foi possível autenticar com o Spotify."}), 503

    # --- Linha de Debug Adicionada ---
    print(f"LOG: Token obtido com sucesso (início): {token[:10]}...") # Imprime só o começo do token!
    # ---------------------------------

    # Monta a query de busca
    search_query = f"track:{song_name}"
    if artist_name:
        search_query += f" artist:{artist_name}"

    search_url = 'https://api.spotify.com/v1/search'
    headers = {'Authorization': f'Bearer {token}'}
    params = {'q': search_query, 'type': 'track', 'limit': 1} # Pega só o primeiro resultado

    try:
        search_response = requests.get(search_url, headers=headers, params=params)
        search_response.raise_for_status()
        search_results = search_response.json()

        tracks = search_results.get('tracks', {}).get('items', [])
        if not tracks:
            return jsonify({"error": f"Música '{song_name}' {('por ' + artist_name) if artist_name else ''} não encontrada no Spotify."}), 404

        track_id = tracks[0].get('id')
        track_name_found = tracks[0].get('name') # Para mostrar qual música foi usada
        artist_names_found = ', '.join([artist['name'] for artist in tracks[0].get('artists', [])])

        # Busca as features da música encontrada
        features_dict, error_msg = get_track_features(track_id, token)
        if error_msg:
             # Não retorna imediatamente, vamos logar o erro que veio de get_track_features
             print(f"LOG: Erro retornado por get_track_features: {error_msg}")
             return jsonify({"error": error_msg}), 500 # Retorna o erro original

        # Faz a previsão com as features obtidas
        predicted_card, error_msg = perform_prediction(features_dict)
        if error_msg:
            return jsonify({"error": error_msg}), 500
        else:
            # Retorna a previsão E qual música/artista foi usada
            return jsonify({
                "carta_prevista": predicted_card,
                "musica_encontrada": f"{track_name_found} por {artist_names_found}"
            })

    except requests.exceptions.RequestException as e:
        print(f"Erro na busca do Spotify para '{song_name}': {e}")
        # Verifica se o erro foi 403 especificamente na busca
        if e.response is not None and e.response.status_code == 403:
             print("LOG: Erro 403 recebido durante a busca no Spotify. Verificar token/credenciais.")
             return jsonify({"error": "Erro de permissão ao buscar no Spotify (verificar token)."}), 403
        return jsonify({"error": f"Erro ao buscar no Spotify: {e}"}), 502 # Bad Gateway
    except Exception as e:
        print(f"Erro inesperado no processamento da busca/previsão: {e}")
        # Adiciona log do traceback para depuração mais profunda
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Erro interno inesperado: {e}"}), 500


# --- Execução (para teste local ou requerido por alguns PaaS) ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    # debug=False é importante para produção
    app.run(host='0.0.0.0', port=port, debug=False)
